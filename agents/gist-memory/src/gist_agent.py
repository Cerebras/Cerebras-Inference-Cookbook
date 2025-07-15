import os
import re
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Union

# Cerebras SDK - ensure you have it installed: pip install cerebras_cloud_sdk
from cerebras.cloud.sdk import Cerebras

# The arxiv_parser.py file is required in the same directory
from arxiv_parser import (
    get_ar5iv_link,
    get_html_page,
    get_paragraphs_from_html,
    get_title_from_html,
)

# --- Core Gist Memory Prompts ---

PROMPT_PAGINATION_TEMPLATE = """
You are given a passage that is taken from a larger text (article, book, ...) and some numbered labels between the paragraphs in the passage.
Numbered label are in angeled brackets. For example, if the label number is 19, it shows as <19> in text.
Please choose one label that it is natural to break reading.
Such point can be scene transition, end of a dialogue, end of an argument, narrative transition, etc.
Please answer the break point label and explain.
For example, if <57> is a good point to break, answer with \"Break point: <57>\n Because ...\"

Passage:

{0}
{1}
{2}
"""

PROMPT_SHORTEN_TEMPLATE = """
Please shorten the following passage.
Just give me a shortened version. DO NOT explain your reason.

Passage:
{}
"""

PROMPT_LOOKUP_TEMPLATE = """
The following text is what you remembered from reading an article and a multiple choice question related to it.
You may read 1 to 6 page(s) of the article again to refresh your memory to prepare yourself for the question.
Please respond with which page(s) you would like to read.
For example, if your only need to read Page 8, respond with \"I want to look up Page [8] to ...\";
if your would like to read Page 7 and 12, respond with \"I want to look up Page [7, 12] to ...\";
if your would like to read Page 2, 3, 7, 15 and 18, respond with \"I want to look up Page [2, 3, 7, 15, 18] to ...\".
if your would like to read Page 3, 4, 5, 12, 13 and 16, respond with \"I want to look up Page [3, 3, 4, 12, 13, 16] to ...\".
DO NOT select more pages if you don't need to.
DO NOT answer the question yet.

Text:
{}

Question:
{}

Take a deep breath and tell me: Which page(s) would you like to read again?
"""

PROMPT_FREE_ANSWER_TEMPLATE = """
Read the following article and then answer the question.

Article:
{}

Question:
{}
"""

@dataclass
class ClientContainer:
    """A simple data class to hold the LLM client and model name."""
    client: Cerebras
    model: str

class GistAgent:
    """
    An AI agent that uses Gist Memory to process and answer questions about long documents.
    This implementation is stripped of UI components and focuses on the core logic for Cerebras models.
    """

    def __init__(self, api_key: str, model: str = "llama-3.3-70b"):
        """
        Initializes the GistAgent.

        Args:
            api_key (str): Your Cerebras API key.
            model (str): The model ID to use for inference.
        """
        if not api_key:
            raise ValueError("Cerebras API key is required.")
        
        print(f"Initializing agent with model: {model}")
        self.client_container = self._get_client(model, api_key)
        self.title = ""
        self.pages: List[List[str]] = []
        self.shortened_pages: List[str] = []
        self.llm_metrics: Dict[str, Any] = self._get_initial_metrics()

    def _get_client(self, model: str, api_key: str) -> ClientContainer:
        """
        Initializes and returns the Cerebras client.
        """
        try:
            client = Cerebras(api_key=api_key)
            print("Cerebras client initialized successfully.")
            return ClientContainer(client, model)
        except Exception as e:
            print(f"Failed to initialize Cerebras client: {e}")
            raise

    def _get_initial_metrics(self) -> Dict[str, Any]:
        """Returns the initial structure for tracking LLM metrics."""
        return {
            "llm_calls": 0,
            "completion_time": 0,
            "prompt_tokens": 0,
            "response_tokens": 0,
            "total_tokens": 0,
            "avg_tokens_per_second": 0,
        }

    def _update_llm_metrics(self, response: Any, delta_time: float):
        """Updates the LLM metrics after a call."""
        # FIX: Correctly access attributes from the response object instead of treating it like a dict.
        if hasattr(response, "time_info") and response.time_info:
            time_taken = response.time_info.completion_time
        else:
            time_taken = delta_time

        self.llm_metrics["llm_calls"] += 1
        self.llm_metrics["completion_time"] += time_taken
        
        if hasattr(response, "usage") and response.usage:
            self.llm_metrics["prompt_tokens"] += response.usage.prompt_tokens
            self.llm_metrics["response_tokens"] += response.usage.completion_tokens
            self.llm_metrics["total_tokens"] += response.usage.total_tokens
        
        if self.llm_metrics["completion_time"] > 0 and self.llm_metrics["response_tokens"] > 0:
            self.llm_metrics["avg_tokens_per_second"] = (
                self.llm_metrics["response_tokens"] / self.llm_metrics["completion_time"]
            )

    def _run_llm(self, messages: List[Dict[str, str]], stream: bool = False) -> Union[str, None]:
        """
        Runs an LLM inference call and updates metrics.

        Args:
            messages (List[Dict[str, str]]): The message history for the prompt.
            stream (bool): Whether to use streaming.

        Returns:
            The LLM's response content as a string, or None if an error occurs.
        """
        start_time = time.time()
        try:
            response = self.client_container.client.chat.completions.create(
                model=self.client_container.model,
                messages=messages,
                stream=stream,
            )
            
            if not stream:
                end_time = time.time()
                self._update_llm_metrics(response, end_time - start_time)
                return response.choices[0].message.content
            else:
                full_response = ""
                final_chunk = None
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                    if chunk.choices[0].finish_reason is not None:
                        final_chunk = chunk
                
                if final_chunk:
                    end_time = time.time()
                    self._update_llm_metrics(final_chunk, end_time - start_time)
                return full_response

        except Exception as e:
            print(f"An error occurred during LLM call: {e}")
            return None

    def _get_next_page_break(self, paragraphs: List[str], start_paragraph: int) -> int:
        """
        Determines the next natural break point in the document.

        Args:
            paragraphs (List[str]): The list of all paragraphs in the document.
            start_paragraph (int): The index of the paragraph to start from.

        Returns:
            The index of the paragraph that marks the end of the new page.
        """
        word_limit = 600
        start_threshold = 280
        
        i = start_paragraph
        preceding = "" if i == 0 else "...\n" + '\n'.join(self.pages[-1])
        
        passage = [paragraphs[i]]
        wcount = len(paragraphs[i].split())
        j = i + 1
        
        while wcount < word_limit and j < len(paragraphs):
            wcount += len(paragraphs[j].split())
            if wcount >= start_threshold:
                passage.append(f"<{j}>")
            passage.append(paragraphs[j])
            j += 1
        passage.append(f"<{j}>")
        
        end_tag = "" if j == len(paragraphs) else paragraphs[j] + "\n..."

        if wcount < 350:
            return len(paragraphs)

        prompt = PROMPT_PAGINATION_TEMPLATE.format(preceding, '\n'.join(passage), end_tag)
        response = self._run_llm([{"role": "user", "content": prompt}])
        
        if response:
            pause_point = self._parse_pause_point(response)
            if pause_point and (pause_point > i and pause_point <= j):
                return pause_point
        
        # Fallback to the max paragraph count in this chunk
        return j

    def _parse_pause_point(self, text: str) -> Union[int, None]:
        """Parses the pause point label (e.g., '<57>') from the LLM response."""
        match = re.search(r"<(\d+)>", text)
        if match:
            return int(match.group(1))
        return None

    def _post_process_summary(self, text: str) -> str:
        """Removes conversational prefixes from summaries."""
        match = re.match(r"(here[a-z ]+ shortened.*?:)", text.lower())
        if match:
            text = text[len(match.group(1)) :].strip()
        return text

    def _create_summary(self, page: List[str]) -> str:
        """
        Creates a summary (gist) for a given page of text.
        """
        prompt = PROMPT_SHORTEN_TEMPLATE.format('\n'.join(page))
        response = self._run_llm([{"role": "user", "content": prompt}])
        
        if response:
            shortened_text = response.strip()
            return self._post_process_summary(shortened_text)
        return "Failed to generate summary."

    def process_document(self, url: str):
        """
        Processes an entire document from a URL, paginating and summarizing it.

        Args:
            url (str): The ArXiv URL of the paper to process.
        """
        print(f"Processing document from: {url}")
        ar5iv_url = get_ar5iv_link(url)
        html_page = get_html_page(ar5iv_url)
        
        self.title = get_title_from_html(html_page)
        if not self.title:
            print(f"Error: Could not parse title from {ar5iv_url}. The paper might not be supported by ar5iv.")
            return

        print("\n" + "="*20)
        print(f"Title: {self.title}")
        print("="*20 + "\n")
        
        paragraphs, _ = get_paragraphs_from_html(html_page)
        
        pause_point = 0
        total_paragraphs = len(paragraphs)

        while pause_point < total_paragraphs:
            page_num = len(self.pages) + 1
            print(f"Processing Page {page_num}...")
            
            old_pause_point = pause_point
            new_pause_point = self._get_next_page_break(paragraphs, old_pause_point)
            
            current_page = paragraphs[old_pause_point:new_pause_point]
            self.pages.append(current_page)
            
            summary = self._create_summary(current_page)
            self.shortened_pages.append(summary)
            
            pause_point = new_pause_point
            print(f"Completed Page {page_num}. Progress: {pause_point}/{total_paragraphs} paragraphs processed.")

        print("\nDocument processing complete.\n")
        self.print_metrics()

    def answer(self, question: str):
        """
        Answers a question based on the processed document's gist memory.

        Args:
            question (str): The user's question.
        """
        if not self.pages:
            print("Error: No document has been processed. Please call `process_document` first.")
            return

        print("\n" + "="*20)
        print(f"Question: {question}")
        print("="*20 + "\n")

        shortened_pages_pidx = [f"\nPage {i}:\n{gist}" for i, gist in enumerate(self.shortened_pages)]
        shortened_article = '\n'.join(shortened_pages_pidx)

        # Step 1: Ask the model which pages to look up
        prompt_lookup = PROMPT_LOOKUP_TEMPLATE.format(shortened_article, question)
        print("Asking model for page lookup rationale...")
        intermediate_response = self._run_llm([{"role": "user", "content": prompt_lookup}])

        if not intermediate_response:
            print("Failed to get lookup response from LLM.")
            return

        print("\n--- Model's Lookup Rationale ---")
        print(intermediate_response.strip())
        print("--------------------------------\n")

        page_ids = []
        try:
            match = re.search(r'\[([\d,\s]+)\]', intermediate_response)
            if match:
                page_ids_str = match.group(1).split(',')
                for p in page_ids_str:
                    if p.strip().isnumeric():
                        page_id = int(p.strip())
                        if 0 <= page_id < len(self.pages):
                            page_ids.append(page_id)
                        else:
                            print(f"  - (Model requested invalid page index: {page_id})")
        except Exception as e:
            print(f"Could not parse page IDs from response: {e}")
        
        chosen_pages = sorted(list(set(page_ids))) if page_ids else 'None'
        print(f"Model chose to re-read page(s): {chosen_pages}\n")

        # Step 2: Construct the final context with expanded pages
        expanded_shortened_pages = self.shortened_pages[:]
        if page_ids:
            for page_id in page_ids:
                expanded_shortened_pages[page_id] = '\n'.join(self.pages[page_id])

        expanded_article = '\n'.join(expanded_shortened_pages)

        # Step 3: Ask the final question
        prompt_answer = PROMPT_FREE_ANSWER_TEMPLATE.format(expanded_article, question)
        
        print("Generating final answer...")
        final_answer = self._run_llm([{"role": "user", "content": prompt_answer}])

        if final_answer:
            print("\n--- Final Answer ---")
            print(final_answer.strip())
            print("--------------------\n")
        else:
            print("Failed to generate a final answer.")
        
        self.print_metrics()

    def print_metrics(self):
        """Prints the collected LLM metrics to the console."""
        print("\n--- LLM Performance Metrics ---")
        for key, value in self.llm_metrics.items():
            metric_name = key.replace('_', ' ').title()
            if isinstance(value, float):
                print(f"{metric_name:<25}: {value:.2f}")
            else:
                print(f"{metric_name:<25}: {value}")
        print("-----------------------------\n")


if __name__ == "__main__":
    try:
        print("--- Gist Memory Agent ---")
        
        CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY")

        if not CEREBRAS_API_KEY:
            print("\nError: CEREBRAS_API_KEY environment variable not set.")
            print("Please set the environment variable before running the script.")
            print("Example: export CEREBRAS_API_KEY='your_key_here'")
        else:
            # --- Initialization ---
            agent = GistAgent(api_key=CEREBRAS_API_KEY)
            
            # --- Document Processing ---
            arxiv_url = input("Enter an ArXiv paper URL (e.g., https://arxiv.org/pdf/1706.03762): ")
            if not arxiv_url:
                 arxiv_url = "https://arxiv.org/pdf/2402.09727" # Gist Memory paper
                 print(f"No URL provided, using default: {arxiv_url}")

            agent.process_document(arxiv_url)

            # --- Q&A Loop ---
            if agent.pages:
                while True:
                    user_question = input("\nAsk a question about the paper (or type 'exit' to quit): ")
                    if user_question.lower() == 'exit':
                        break
                    if user_question:
                        agent.answer(user_question)

    except (ValueError, Exception) as e:
        print(f"\nAn error occurred: {e}")
    except KeyboardInterrupt:
        print("\nExiting agent.")