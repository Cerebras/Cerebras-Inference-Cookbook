import os
import json
from cerebras_client import get_client
from config_loader import get_config
import textwrap

def write_report_from_outline(outline: dict, model: str = None) -> str:
    """
    Generates a full-length Markdown report from a structured outline,
    with very strict instructions for citation formatting.
    """
    print("✍️  Writing full report from outline with improved style and strict citations...")

    try:
        config = get_config()
        if model is None:
            model = config['models']['writer_model']
        client = get_client()

        system_prompt = textwrap.dedent("""\
            You are an expert journalist and author with a talent for creating engaging narratives from research.
            Your task is to write a full, comprehensive news report ({config['report']['target_word_count']['min']}-{config['report']['target_word_count']['max']} words) based on the provided JSON outline.

            **Your primary goal is to transform the outline's bullet points into well-structured, flowing paragraphs.** Weave them into a compelling story.

            Follow these critical instructions:
            1.  **Narrative First**: Write in full paragraphs. The final output should read like a professional news article, not a list.
            2.  **Selective Bullet Points**: You may use bullet points sparingly, ONLY if it makes sense for clarity.
            3.  **Formatting**: Use Markdown for all formatting. The main title should be a Level 1 Heading (`#`), and all section headings should be Level 2 Headings (`##`).
            4.  **CRITICAL CITATION FORMAT**: You MUST preserve the source citation markers. The format is extremely important.
                - For a single source, use the format `[Source 1]`.
                - For multiple sources, combine them inside ONE bracket, like this: `[Source 1, 3, 5]`.
                - The word "Source" must appear only ONCE per placeholder.
                - **DO NOT** create separate placeholders like `[Source 1], [Source 3]`.
                - **DO NOT** nest placeholders like `[Source 1, [Source 3]]`.
        """)
        
        user_prompt = f"Please write the report based on the following outline:\n\n{json.dumps(outline, indent=2)}"

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=config['api']['max_tokens']['extended'],
            temperature=config['api']['temperature'] 
        )

        final_report_markdown = completion.choices[0].message.content
        
        print("   - Successfully generated draft report with clean citations.")
        return final_report_markdown

    except Exception as e:
        print(f"   - An error occurred during report generation: {e}")
        return ""

# --- Main Execution Block for Phase 4 ---
if __name__ == "__main__":
    if not os.environ.get("CEREBRAS_API_KEY"):
        print("\nError: CEREBRAS_API_KEY environment variable not set.")
        exit()

    try:
        with open("report_outline.json", "r") as f:
            report_outline = json.load(f)
        print("Successfully loaded 'report_outline.json'.")
    except FileNotFoundError:
        print("\nError: 'report_outline.json' not found. Please run the Phase 3 script first.")
        exit()
    
    if not report_outline:
        print("'report_outline.json' is empty. Cannot write a report.")
        exit()

    markdown_report = write_report_from_outline(report_outline)

    if markdown_report:
        with open("draft_report.md", "w", encoding="utf-8") as f:
            f.write(markdown_report)
        print("\nPhase 4 complete!")
        print("Successfully saved the clean draft report to 'draft_report.md'.")
    else:
        print("\nCould not generate the report. Please check the error message above.")