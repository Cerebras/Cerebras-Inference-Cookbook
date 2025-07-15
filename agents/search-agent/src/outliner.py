import os
import json
from cerebras_client import get_client
from config_loader import get_config

def create_report_outline(summaries: list, model: str = None) -> dict:
    """
    Generates a structured report outline from a list of article summaries.

    Args:
        summaries: A list of dictionaries, where each dict has 'title', 'url', and 'summary'.
        model: The Cerebras model to use.

    Returns:
        A dictionary containing the structured report outline.
    """
    print("Generating report outline...")

    try:
        config = get_config()
        if model is None:
            model = config['models']['outliner_model']
        client = get_client()

        # Define the detailed JSON schema for the report outline
        outline_schema = {
            "type": "object",
            "properties": {
                "report_title": {
                    "type": "string",
                    "description": "A compelling and informative title for the news report."
                },
                "introduction": {
                    "type": "string",
                    "description": "An introductory paragraph summarizing the report's key themes and findings."
                },
                "body_sections": {
                    "type": "array",
                    "description": "A list of the main sections of the report.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "section_heading": {
                                "type": "string",
                                "description": "A descriptive heading for this section."
                            },
                            "bullet_points": {
                                "type": "array",
                                "description": "A list of key points, facts, or arguments for this section.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "content": {
                                            "type": "string",
                                            "description": "The text of the bullet point."
                                        },
                                        "sources": {
                                            "type": "array",
                                            "description": "A list of 1-based integer indices referencing the source summaries.",
                                            "items": {"type": "integer"}
                                        }
                                    },
                                    "required": ["content", "sources"]
                                }
                            }
                        },
                        "required": ["section_heading", "bullet_points"]
                    }
                },
                "conclusion": {
                    "type": "string",
                    "description": "A concluding paragraph that summarizes the report and offers final thoughts."
                }
            },
            "required": ["report_title", "introduction", "body_sections", "conclusion"]
        }

        # Prepare the context by concatenating all summaries
        context = ""
        for i, article in enumerate(summaries, 1):
            context += f"--- Source {i} ---\n"
            context += f"Title: {article['title']}\n"
            context += f"URL: {article['url']}\n"
            context += f"Summary:\n{article['summary']}\n\n"

        system_prompt = (
            "You are an expert editor and report strategist. Your task is to synthesize the provided "
            f"research summaries into a detailed, structured outline for an {config['report']['outline_word_count']['min']}-{config['report']['outline_word_count']['max']} word news report. "
            "Analyze all sources, identify the main themes, and create a logical narrative flow. "
            "For each bullet point in the outline, you MUST cite the integer index of the source(s) it came from."
        )
        user_prompt = f"Here is the research content from all sources:\n\n{context}"

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "report_outline_generator",
                    "strict": True,
                    "schema": outline_schema
                }
            },
            max_tokens=config['api']['max_tokens']['extended'],
        )

        response_content = completion.choices[0].message.content
        report_outline = json.loads(response_content)
        
        print("   - ✅ Successfully generated report outline.")
        return report_outline

    except Exception as e:
        print(f"   - An error occurred: {e}")
        return {}

# --- Main Execution Block for Phase 3 ---
if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("CEREBRAS_API_KEY"):
        print("\nError: CEREBRAS_API_KEY environment variable not set.")
        exit()

    # Load the summarized articles from Phase 2
    try:
        with open("summarized_articles.json", "r") as f:
            summarized_articles = json.load(f)
        print("Successfully loaded 'summarized_articles.json'.")
    except FileNotFoundError:
        print("\nError: 'summarized_articles.json' not found.")
        print("Please run the Phase 2 script first to generate this file.")
        exit()
    
    if not summarized_articles:
        print("'summarized_articles.json' is empty. Cannot generate an outline.")
        exit()

    # Generate the report outline
    outline = create_report_outline(summarized_articles)

    # Save the final outline to a file for Phase 4
    if outline:
        with open("report_outline.json", "w") as f:
            json.dump(outline, f, indent=2)
        print("\nPhase 3 complete!")
        print("Successfully saved the report structure to 'report_outline.json'.")
    else:
        print("\nCould not generate a report outline. Please check the error message above.")