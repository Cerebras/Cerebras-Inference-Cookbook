import os
import json

# Import the main function from each phase script
# Note: Rename your files if they are different!
#from interaction import run_phase_1 # We'll create this function now
from interaction import ask_follow_up_questions, capture_user_answers
from researcher import run_research_tasks
from outliner import create_report_outline
from writer import write_report_from_outline
from citation_manager import create_final_report

# Let's create a simple function for Phase 1 to keep this file clean
def run_phase_1():
    
    user_topic = input("Please enter the topic for your news report: ")
    if not user_topic.strip():
        print("No topic entered. Exiting.")
        return None

    questions = ask_follow_up_questions(user_topic)
    if not questions:
        print("Could not generate questions. Exiting.")
        return None
        
    answers = capture_user_answers(questions)
    
    research_brief = {
        "initial_topic": user_topic,
        "clarifying_questions": questions,
        "user_answers": list(answers.values())
    }
    with open("research_brief.json", "w") as f:
        json.dump(research_brief, f, indent=2)
    print("Phase 1 Complete: Saved 'research_brief.json'\n")
    return research_brief


def main():
    """
    Runs the entire news report generation pipeline from start to finish.
    """
    print("Starting the News Report Generator...")

    # --- Phase 1: User Interaction ---
    research_brief = run_phase_1()
    if not research_brief:
        return

    # --- Phase 2: Research & Summarization ---
    print("Starting Phase 2: Research & Summarization...")
    queries, articles, raw_data = run_research_tasks(research_brief)
    # Save outputs
    with open("search_queries.json", "w") as f: json.dump(queries, f, indent=2)
    with open("summarized_articles.json", "w") as f: json.dump(articles, f, indent=2)
    with open("raw_exa_results.json", "w") as f: json.dump(raw_data, f, indent=2)
    print("Phase 2 Complete: Saved research and summaries.\n")

    # --- Phase 3: Outlining ---
    print("Starting Phase 3: Report Outlining...")
    outline = create_report_outline(articles)
    with open("report_outline.json", "w") as f: json.dump(outline, f, indent=2)
    print("Phase 3 Complete: Saved 'report_outline.json'.\n")

    # --- Phase 4: Writing the Draft ---
    print("Starting Phase 4: Writing Draft Report...")
    markdown_report = write_report_from_outline(outline)
    with open("draft_report.md", "w", encoding="utf-8") as f: f.write(markdown_report)
    print("Phase 4 Complete: Saved 'draft_report.md'.\n")

    # --- Phase 5: Formatting Citations ---
    print("Starting Phase 5: Finalizing Citations...")
    create_final_report()
    print("Phase 5 Complete.\n")

    print("All Done! Your report is ready in 'final_report.md'.")


if __name__ == "__main__":
    # Check for API keys before starting
    if not os.environ.get("CEREBRAS_API_KEY") or not os.environ.get("EXA_API_KEY"):
        print("\nError: CEREBRAS_API_KEY or EXA_API_KEY environment variable not set.")
    else:
        main()