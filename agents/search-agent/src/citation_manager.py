import os
import json
import re

def create_final_report():
    """
    Reads the draft report and summarized articles to produce a final,
    cited report, correctly handling both single and multi-source placeholders.
    """
    print("🚀 Finalizing report and formatting citations...")

    try:
        with open("draft_report.md", "r", encoding="utf-8") as f:
            draft_text = f.read()
        
        with open("summarized_articles.json", "r", encoding="utf-8") as f:
            sources = json.load(f)

    except FileNotFoundError as e:
        print(f"❌ Error: Could not find a necessary file. Make sure '{e.filename}' exists.")
        print("Please run all previous phases before this script.")
        return

    # Use a more robust regex to find all source placeholders
    placeholder_groups = re.findall(r"\[Source ([^\]]+)\]", draft_text)
    
    if not placeholder_groups:
        print("⚠️ No source placeholders found in the draft. Saving as is.")
        with open("final_report.md", "w", encoding="utf-8") as f:
            f.write(draft_text)
        return

    # Create a definitive list of all unique sources cited
    all_source_indices = set()
    for group in placeholder_groups:
        indices = [int(s.strip()) for s in group.split(',')]
        all_source_indices.update(indices)

    sorted_unique_indices = sorted(list(all_source_indices))
    
    # Create the mapping from original index to new citation number
    citation_map = {original_index: new_index for new_index, original_index in enumerate(sorted_unique_indices, 1)}
    
    print(f"   - Found {len(sorted_unique_indices)} unique sources to cite.")

    # Define a replacer function to handle each placeholder
    def replace_match(match):
        number_string = match.group(1)
        original_indices = [int(s.strip()) for s in number_string.split(',')]
        new_numbers = sorted([citation_map[idx] for idx in original_indices])
        return f"[{', '.join(map(str, new_numbers))}]"

    # Use the robust replacer function to substitute all placeholders
    final_text = re.sub(r"\[Source ([^\]]+)\]", replace_match, draft_text)
    print("   - Replaced all placeholders.")

    # Build the final reference list
    reference_list_md = "\n\n---\n\n## References\n"
    for original_index in sorted_unique_indices:
        new_citation_number = citation_map[original_index]
        source_data = sources[original_index - 1]
        reference_list_md += f"{new_citation_number}. [{source_data['title']}]({source_data['url']})\n"
    
    print("   - Built reference list.")

    # Combine the modified text with the reference list
    final_report_text = final_text + reference_list_md
    with open("final_report.md", "w", encoding="utf-8") as f:
        f.write(final_report_text)
    
    print("\n✅ Project Complete! ✅")
    print("Successfully saved the polished report to 'final_report.md'.")


if __name__ == "__main__":
    create_final_report()