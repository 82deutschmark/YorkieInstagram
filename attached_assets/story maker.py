import openai

openai.api_key = "YOUR_API_KEY"  # Replace with your actual API key

# Multiple-choice options for story elements
multiple_choices = {
    "Which primary conflict do you want for this episode?": [
        ("🐿️", "Squirrel gang's mischief"),
        ("🧙‍♂️", "Rat wizard's devious plots"),
        ("🦃", "Turkey's clumsy adventures"),
        ("🐔", "Chicken's clever conspiracies")
    ],
    "Which setting should dominate the story?": [
        ("🌳", "Deep Forest"),
        ("🌾", "Sunny Pasture"),
        ("🏡", "Homestead"),
        ("🌲", "Mysterious Woods")
    ],
    "Choose a narrative style": [
        ("😎", "GenZ fresh style"),
        ("✌️", "Old hippie 1960s vibe"),
        ("🤘", "Mix of both")
    ],
    "What mood do you want the story to evoke?": [
        ("😄", "Joyful and playful"),
        ("😲", "Thrilling and mysterious"),
        ("😎", "Cool and laid-back"),
        ("😂", "Funny and quirky")
    ]
}

def ask_multiple_choice(question, options):
    print(f"Storyteller: {question}")
    # List given options
    for i, (emoji, label) in enumerate(options, start=1):
        print(f"  {i}. {emoji} = {label}")
    # Append extra option for custom input
    custom_option = len(options) + 1
    print(f"  {custom_option}. ✍️ Write your own")
    
    while True:
        user_input = input("You: ")
        if user_input.isdigit():
            index = int(user_input)
            if 1 <= index <= len(options):
                return options[index-1]
            elif index == custom_option:
                custom_text = input("Please enter your custom answer: ")
                # Using a pencil emoji to denote custom input.
                return ("✍️", custom_text)
        print("Storyteller: Please enter a valid number from the list above.")

def generate_story(prompt):
    # Note: The parameters 'model', 'temperature', and 'max_tokens' below are placeholders.
    # They might be problematic or out of date for recent models and should be updated if needed.
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Placeholder: This model may be replaced in future releases.
        messages=[
            {"role": "system", "content": (
                "You are a master storyteller for kids. Create a captivating Netflix-series–style story set in Uncle Mark's forest farm. "
                "The main characters are two courageous Yorkshire terriers, Pawel (male, impulsive) and Pawleen (female, thoughtful). "
                "Include vivid, detailed descriptions of each character and scene with plenty of emojis. Alternate the narrative tone between a GenZ fresh style and an old hippie 1960s vibe. "
                "The enemies are mean, evil squirrels, a devious rat wizard, mischievous mice, and clumsy moles. Also include the antics of Big Red the rooster, his clever hens, and the clumsy white turkeys. "
                "Each scene should be so descriptive that an artist could easily illustrate it. End the episode with an unresolved cliffhanger that invites more adventures."
            )},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,  # Placeholder: Adjust as needed for the desired creativity level.
        max_tokens=500    # Placeholder: This may need to be updated depending on the current model's capabilities.
    )
    return response.choices[0].message["content"]

def main():
    print("Welcome to Uncle Mark's Forest Farm Story Generator! 🌲🐾")
    
    # Ask multiple choice questions for key story elements (episode title and plot description are no longer requested)
    conflict_choice = ask_multiple_choice(
        "Which primary conflict do you want for this episode?",
        multiple_choices["Which primary conflict do you want for this episode?"]
    )
    setting_choice = ask_multiple_choice(
        "Which setting should dominate the story?",
        multiple_choices["Which setting should dominate the story?"]
    )
    narrative_choice = ask_multiple_choice(
        "Choose a narrative style",
        multiple_choices["Choose a narrative style"]
    )
    mood_choice = ask_multiple_choice(
        "What mood do you want the story to evoke?",
        multiple_choices["What mood do you want the story to evoke?"]
    )
    
    # Build the story prompt with all collected variables
    prompt = (
        f"Primary Conflict: {conflict_choice[1]}\n"
        f"Setting: {setting_choice[1]}\n"
        f"Narrative Style: {narrative_choice[1]}\n"
        f"Mood: {mood_choice[1]}\n\n"
        "Tell a story set on Uncle Mark's forest farm with vivid descriptions of every scene and character. "
        "Include Pawel and Pawleen, the fearless Yorkshire terriers, who face off against mean squirrels and a cunning rat wizard. "
        "Make sure to mention the quirky chickens led by Big Red, the clever hens, and the clumsy white turkeys. "
        "Switch the narrative tone between a modern GenZ vibe and an old-school 1960s hippie style, and sprinkle in lots of emojis. "
        "End the episode with an unresolved cliffhanger to set up future episodes."
    )
    
    print("\nGenerating your story... 🎬\n")
    story = generate_story(prompt)
    print("Here is your story:\n")
    print(story)
    
    print("\nWould you like to generate another episode? (yes/no)")
    answer = input("You: ")
    if answer.lower().startswith("y"):
        main()
    else:
        print("Thanks for using Uncle Mark's Forest Farm Story Generator! Stay tuned for more adventures! 😎🌳")

if __name__ == "__main__":
    main()
