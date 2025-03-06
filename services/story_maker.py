import os
import json
from openai import OpenAI
import logging
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)

# Get OpenAI API key from environment variables
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logger.warning("OpenAI API key not found in environment variables")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Default story options
STORY_OPTIONS = {
    "conflicts": [
        ("🐿️", "Squirrel gang's mischief"),
        ("🧙‍♂️", "Rat wizard's devious plots"),
        ("🦃", "Turkey's clumsy adventures"),
        ("🐔", "Chicken's clever conspiracies")
    ],
    "settings": [
        ("🌳", "Deep Forest"),
        ("🌾", "Sunny Pasture"),
        ("🏡", "Homestead"),
        ("🌲", "Mysterious Woods")
    ],
    "narrative_styles": [
        ("😎", "GenZ fresh style"),
        ("✌️", "Old hippie 1960s vibe"),
        ("🤘", "Mix of both")
    ],
    "moods": [
        ("😄", "Joyful and playful"),
        ("😲", "Thrilling and mysterious"),
        ("😎", "Cool and laid-back"),
        ("😂", "Funny and quirky")
    ]
}

def get_story_options() -> Dict[str, List[Tuple[str, str]]]:
    """Return available story options for UI display"""
    return STORY_OPTIONS

def generate_story(
    conflict: str,
    setting: str,
    narrative_style: str,
    mood: str,
    character_info: Optional[Dict[str, Any]] = None,
    custom_conflict: Optional[str] = None,
    custom_setting: Optional[str] = None,
    custom_narrative: Optional[str] = None,
    custom_mood: Optional[str] = None
) -> Dict[str, str]:
    """Generate a story based on selected or custom parameters and optional character info"""
    if not api_key:
        raise ValueError("OpenAI API key not found. Please add it to your environment variables.")

    # Use custom values if provided, otherwise use selected options
    final_conflict = custom_conflict or conflict
    final_setting = custom_setting or setting
    final_narrative = custom_narrative or narrative_style
    final_mood = custom_mood or mood

    # Build the story prompt
    character_prompt = ""
    if character_info:
        character_prompt = (
            f"\nInclude the character '{character_info['name']}' in the story. "
            f"This character has the following traits: {', '.join(character_info['traits'])}. "
            f"Their appearance is described as: {character_info['description']}"
        )

    prompt = (
        f"Primary Conflict: {final_conflict}\n"
        f"Setting: {final_setting}\n"
        f"Narrative Style: {final_narrative}\n"
        f"Mood: {final_mood}\n"
        f"{character_prompt}\n\n"
        "Tell a story set on Uncle Mark's forest farm with vivid descriptions of every scene and character. "
        "Include Pawel and Pawleen, the fearless Yorkshire terriers, who face off against mean squirrels and a cunning rat wizard. "
        "Make sure to mention the quirky chickens led by Big Red, the clever hens, and the clumsy white turkeys. "
        "Switch the narrative tone between a modern GenZ vibe and an old-school 1960s hippie style, and sprinkle in lots of emojis. "
        "End the episode with an unresolved cliffhanger to set up future episodes."
    )

    try:
        # Call OpenAI API to generate the story using new client syntax
        response = client.chat.completions.create(
            model="gpt-4o",  # Using the latest model as of May 13, 2024
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a master storyteller for kids. Create a captivating Netflix-series–style story "
                        "set in Uncle Mark's forest farm. The main characters are two courageous Yorkshire terriers, "
                        "Pawel (male, impulsive) and Pawleen (female, thoughtful). Include vivid, detailed descriptions "
                        "of each character and scene with plenty of emojis. Provide your response in JSON format."
                    )
                },
                {"role": "user", "content": prompt + "\n\nFormat your response as a JSON object with 'title', 'story', and 'characters' fields."}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        # Parse and return the generated story
        result = json.loads(response.choices[0].message.content)
        return {
            "story": result,
            "conflict": final_conflict,
            "setting": final_setting,
            "narrative_style": final_narrative,
            "mood": final_mood
        }

    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        raise Exception(f"Failed to generate story: {str(e)}")