import os
import json
from cerebras_client import get_client
from config_loader import get_config
from exa_py import Exa
import textwrap

# Initialize API clients
try:
    config = get_config()
    exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))
    MODEL = config['models']['main_model']
except Exception as e:
    print(f"Error initializing API clients: {e}")
    print("Please ensure your CEREBRAS_API_KEY and EXA_API_KEY are set.")
    exit()

def summarize_single_article(article_text: str, research_brief: dict) -> str:
    """
    Performs a four-step "Reflect, Elaborate, Critique, Refine" summarization.
    """
    try:
        # Step 1 & 2: Reflect and Elaborate (Generate v1 Summary)
        print("   - Step 1 & 2: Generating initial summary (v1)...")
        reflection_schema = {"type": "object", "properties": {"key_points": {"type": "array", "description": "A list of the 3-5 most important, distinct points.", "items": {"type": "string"}}}, "required": ["key_points"]}
        reflection_prompt = f"Read the following article and identify the 3-5 most important points relevant to this research brief:\n{json.dumps(research_brief, indent=2)}\n\nARTICLE:\n{article_text}"
        reflection_completion = get_client().chat.completions.create(model=MODEL, messages=[{"role": "user", "content": reflection_prompt}], response_format={"type": "json_schema", "json_schema": {"name": "key_points_extractor", "strict": True, "schema": reflection_schema}}, max_tokens=config['api']['max_tokens']['extended'])
        key_points = json.loads(reflection_completion.choices[0].message.content).get("key_points", [])

        if not key_points:
            print("   - Could not extract key points. Skipping article.")
            return ""

        elaboration_prompt = f"Write a detailed summary based on these key points, using the full article text for context.\n\nKEY POINTS:\n{json.dumps(key_points, indent=2)}\n\nFULL ARTICLE:\n{article_text}"
        elaboration_completion = get_client().chat.completions.create(model=MODEL, messages=[{"role": "user", "content": elaboration_prompt}], max_tokens=config['api']['max_tokens']['extended'])
        summary_v1 = elaboration_completion.choices[0].message.content
        print("   - v1 Summary generated.")

        # Step 3: Critique the v1 Summary
        print("   - Step 3: Critiquing the summary...")
        critique_prompt = textwrap.dedent(f"""\
            You are a meticulous editor. Read the original article and the generated summary.
            Identify any key facts, statistics, or nuances that were missed in the summary.
            Provide a specific, actionable list of feedback for improvement.

            ORIGINAL ARTICLE:
            {article_text}

            ---
            SUMMARY TO CRITIQUE:
            {summary_v1}
        """)
        critique_completion = get_client().chat.completions.create(model=config['models']['critique_model'], messages=[{"role": "user", "content": critique_prompt}], max_tokens=config['api']['max_tokens']['default'])
        critique = critique_completion.choices[0].message.content
        print("   - Critique complete.")

        # Step 4: Refine the summary based on the critique
        print("   - Step 4: Refining the summary (v2)...")
        refinement_prompt = textwrap.dedent(f"""\
            You are a writer. Rewrite the 'ORIGINAL SUMMARY' to incorporate the 'EDITOR'S FEEDBACK'.
            Use the 'ORIGINAL ARTICLE' as the ultimate source of truth.

            ORIGINAL ARTICLE:
            {article_text}

            ---
            EDITOR'S FEEDBACK:
            {critique}

            ---
            ORIGINAL SUMMARY:
            {summary_v1}
        """)
        refinement_completion = get_client().chat.completions.create(model=MODEL, messages=[{"role": "user", "content": refinement_prompt}], max_tokens=config['api']['max_tokens']['extended'])
        final_summary = refinement_completion.choices[0].message.content
        print("   - Final summary created.")
        return final_summary

    except Exception as e:
        print(f"   - An error occurred during summarization: {e}")
        return ""


def run_research_tasks(research_brief: dict) -> tuple[list, list, list]:
    """Orchestrates the entire research process."""
    config = get_config()
    all_queries, summarized_articles, raw_exa_results = [], [], []
    query_schema = {"type": "object", "properties": {"query": {"type": "string", "description": "A single, targeted search query."}}, "required": ["query"]}

    # General Research Task
    print(f"\n--- Starting General Research Task (1 query, {config['research']['num_search_results_per_query']} articles) ---")
    try:
        prompt = f"Generate one broad, foundational search query for the topic: \"{research_brief['initial_topic']}\""
        completion = get_client().chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], response_format={"type": "json_schema", "json_schema": {"name": "query_generator", "strict": True, "schema": query_schema}}, max_tokens=config['api']['max_tokens']['default'])
        general_query = json.loads(completion.choices[0].message.content).get("query")
        
        if general_query:
            all_queries.append(general_query)
            print(f"Generated General Query: \"{general_query}\"")
            print(f"   - Searching with Exa for top {config['research']['num_search_results_per_query']} articles...")
            search_response = exa_client.search_and_contents(general_query, num_results=config['research']['num_search_results_per_query'], text=True)
            raw_exa_results.append({"query": general_query, "results": [{"url": r.url, "title": r.title, "id": r.id, "published_date": r.published_date, "text": r.text} for r in search_response.results]})

            for i, result in enumerate(search_response.results, 1):
                print(f"\n   --- Summarizing Article {i}/{len(search_response.results)}: \"{result.title}\" ---")
                summary = summarize_single_article(result.text, research_brief)
                if summary:
                    summarized_articles.append({"url": result.url, "title": result.title, "summary": summary})
    except Exception as e:
        print(f"   - An error occurred during the general research task: {e}")

    # Specific Research Tasks
    for i in range(len(research_brief['clarifying_questions'])):
        question = research_brief['clarifying_questions'][i]
        answer = research_brief['user_answers'][i]
        print(f"\n--- Starting Specific Research Task {i+1}/{len(research_brief['clarifying_questions'])} (1 query, {config['research']['num_search_results_per_query']} articles) ---")
        try:
            prompt = f"Based ONLY on the answer to the question below, generate one highly specific search query.\nQuestion: {question}\nUser's Answer: {answer}"
            completion = get_client().chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], response_format={"type": "json_schema", "json_schema": {"name": "query_generator", "strict": True, "schema": query_schema}}, max_tokens=config['api']['max_tokens']['default'])
            specific_query = json.loads(completion.choices[0].message.content).get("query")

            if specific_query:
                all_queries.append(specific_query)
                print(f"Generated Specific Query: \"{specific_query}\"")
                print("   - Searching with Exa for top articles...")
                search_response = exa_client.search_and_contents(specific_query, num_results=config['research']['num_search_results_per_query'], text=True)
                raw_exa_results.append({"query": specific_query, "results": [{"url": r.url, "title": r.title, "id": r.id, "published_date": r.published_date, "text": r.text} for r in search_response.results]})

                for j, result in enumerate(search_response.results, 1):
                    print(f"\n   --- Summarizing Article {j}/{len(search_response.results)}: \"{result.title}\" ---")
                    summary = summarize_single_article(result.text, research_brief)
                    if summary:
                        summarized_articles.append({"url": result.url, "title": result.title, "summary": summary})
        except Exception as e:
            print(f"   - An error occurred during specific research task {i+1}: {e}")

    return all_queries, summarized_articles, raw_exa_results

if __name__ == "__main__":
    try:
        with open("research_brief.json", "r") as f:
            research_brief = json.load(f)
        print("Successfully loaded 'research_brief.json'.")
    except FileNotFoundError:
        print("\nError: 'research_brief.json' not found. Please run the Phase 1 script first.")
        exit()
    
    queries, articles, raw_data = run_research_tasks(research_brief)

    if queries:
        print(f"\nGenerated a total of {len(queries)} queries.")
        with open("search_queries.json", "w") as f: json.dump(queries, f, indent=2)
        print("Successfully saved search queries to 'search_queries.json'.")
    if articles:
        print(f"\nSuccessfully created {len(articles)} detailed, refined summaries.")
        with open("summarized_articles.json", "w") as f: json.dump(articles, f, indent=2)
        print("Successfully saved refined summaries to 'summarized_articles.json'.")
    if raw_data:
        print("\nSaving raw Exa search results...")
        with open("raw_exa_results.json", "w") as f: json.dump(raw_data, f, indent=2)
        print("Successfully saved raw Exa search results to 'raw_exa_results.json'.")

    print("\n\nPhase 2 complete!")