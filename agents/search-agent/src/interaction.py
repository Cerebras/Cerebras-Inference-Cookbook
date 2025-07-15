import os
import json
from cerebras_client import get_client
from config_loader import get_config

def ask_follow_up_questions(topic: str, model: str = None) -> list:
    """
    Generates insightful follow-up questions for a given topic using the Cerebras API.
    """
    print(f"\n🧠 Generating follow-up questions for topic: '{topic}'...")
    try:
        config = get_config()
        if model is None:
            model = config['models']['question_generator']
        client = get_client()
        questions_schema = {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "description": f"A list of {config['research']['num_follow_up_questions']} insightful, open-ended follow-up questions.",
                    "items": {"type": "string"}
                }
            },
            "required": ["questions"]
        }
        system_prompt = (
            "You are a helpful research assistant. Your primary goal is to better understand what the user "
            f"is specifically looking for. Based on their topic, generate exactly {config['research']['num_follow_up_questions']} insightful "
            "follow-up questions to help them narrow down their request and clarify the exact "
            "angle they want for a news report."
        )
        user_prompt = f"The user wants a report on the following topic: '{topic}'."
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "follow_up_questions", "strict": True, "schema": questions_schema}
            },
            max_tokens=config['api']['max_tokens']['default'],
        )
        response_content = completion.choices[0].message.content
        parsed_response = json.loads(response_content)
        print("   - ✅ Successfully generated questions.")
        return parsed_response.get("questions", [])
    except Exception as e:
        print(f"   - ❌ An error occurred: {e}")
        return []

def capture_user_answers(questions: list) -> dict:
    """
    Prompts the user to answer a list of questions and captures their responses.
    """
    print("\n--- To help me understand what you're looking for, please answer these questions: ---")
    answers = {}
    for i, question in enumerate(questions, 1):
        # Prompt the user for an answer to the current question
        user_answer = input(f"❓ {question}\n> ")
        answers[question] = user_answer
    print("-------------------------------------------------------------------------------------\n")
    return answers

# --- Main Execution Block ---
if __name__ == "__main__":
    if not os.environ.get("CEREBRAS_API_KEY"):
        print("\nError: CEREBRAS_API_KEY environment variable not set.")
        print("Please set your API key before running: export CEREBRAS_API_KEY=\"your-key\"")
    else:
        # 1. Get the initial topic from the user
        user_topic = input("Please enter the topic for your news report: ")
        
        if not user_topic.strip():
            print("No topic entered. Exiting.")
        else:
            # 2. Generate follow-up questions
            generated_questions = ask_follow_up_questions(user_topic)

            if generated_questions:
                # 3. Capture the user's answers to the questions
                user_answers = capture_user_answers(generated_questions)

                # 4. Assemble the final "Research Brief"
                research_brief = {
                    "initial_topic": user_topic,
                    "clarifying_questions": generated_questions,
                    "user_answers": user_answers
                }

                print("✅ Research brief assembled! This will be used to guide the next steps.")
                print("\n--- Research Brief ---")
                print(json.dumps(research_brief, indent=2))
                print("----------------------")

                try:
                    with open("research_brief.json", "w") as f:
                        json.dump(research_brief, f, indent=2)
                    print("\n✅ Successfully saved brief to research_brief.json")
                except Exception as e:
                    print(f"\n❌ Error saving file: {e}")
