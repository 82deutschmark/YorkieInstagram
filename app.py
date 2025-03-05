import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from services.openai_service import analyze_artwork, generate_instagram_post
from services.story_maker import generate_story, get_story_options

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize Flask app and database
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db = SQLAlchemy(app)

# Import models after db initialization to avoid circular imports
from models import ImageAnalysis, AIInstruction, HashtagCollection, StoryGeneration

def initialize_defaults():
    """Initialize default AI instructions and hashtags if they don't exist"""
    # Default AI instruction for art style analysis
    if not AIInstruction.get_default():
        default_instruction = AIInstruction(
            name="Default Art Style Analysis",
            system_prompt="You are an art critic specializing in dog portraits. "
                        "Analyze the image and provide: "
                        "1. Art style description "
                        "2. A creative name for the Yorkie "
                        "3. A brief, engaging story about the Yorkie "
                        "Respond in JSON format with keys: 'style', 'name', 'story'",
            user_prompt="Please analyze this Yorkie artwork:",
            is_default=True
        )
        db.session.add(default_instruction)

    # Default hashtag collection
    if not HashtagCollection.get_default():
        default_hashtags = HashtagCollection(
            name="Default Yorkie Art Hashtags",
            hashtags=[
                "#YorkshireTerrier", "#YorkieArt", "#DogArt", "#PetPortrait",
                "#YorkieLove", "#DogLover", "#PetArt", "#YorkieLife",
                "#DogPortrait", "#AnimalArt", "#YorkiesOfInstagram",
                "#DogArtist", "#PetLover", "#YorkieMom", "#DogDrawing"
            ],
            is_default=True
        )
        db.session.add(default_hashtags)

    db.session.commit()

# Create tables and initialize defaults
with app.app_context():
    db.create_all()
    initialize_defaults()

@app.route('/')
def index():
    instructions = AIInstruction.query.all()
    hashtag_collections = HashtagCollection.query.all()
    story_options = get_story_options()
    return render_template(
        'index.html',
        instructions=instructions,
        hashtag_collections=hashtag_collections,
        story_options=story_options
    )

@app.route('/generate', methods=['POST'])
def generate_post():
    image_url = request.form.get('image_url')
    instruction_id = request.form.get('instruction_id')
    hashtag_collection_id = request.form.get('hashtag_collection_id')

    if not image_url:
        return jsonify({'error': 'No image URL provided'}), 400

    try:
        # Get instruction and hashtag collection
        instruction = (AIInstruction.query.get(instruction_id) 
                      if instruction_id else AIInstruction.get_default())
        hashtag_collection = (HashtagCollection.query.get(hashtag_collection_id)
                            if hashtag_collection_id else HashtagCollection.get_default())

        if not instruction or not hashtag_collection:
            return jsonify({'error': 'Invalid instruction or hashtag collection'}), 400

        # Validate URL format
        if not image_url.startswith(('http://', 'https://')):
            return jsonify({'error': 'Invalid image URL format'}), 400

        # Analyze the artwork using OpenAI with custom instruction
        analysis = analyze_artwork(image_url, instruction)

        # Generate Instagram caption with custom hashtags
        caption = generate_instagram_post(analysis, hashtag_collection.hashtags)

        # Store the analysis in database
        image_analysis = ImageAnalysis(
            image_url=image_url,
            analysis_result=analysis,
            instruction_id=instruction.id,
            hashtag_collection_id=hashtag_collection.id
        )
        db.session.add(image_analysis)
        db.session.commit()

        return jsonify({
            'success': True,
            'caption': caption,
            'analysis': analysis
        })

    except Exception as e:
        logger.error(f"Error generating post: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate_story', methods=['POST'])
def generate_story_route():
    try:
        # Get form data
        conflict = request.form.get('conflict')
        setting = request.form.get('setting')
        narrative_style = request.form.get('narrative_style')
        mood = request.form.get('mood')

        # Get custom inputs if provided
        custom_conflict = request.form.get('custom_conflict')
        custom_setting = request.form.get('custom_setting')
        custom_narrative = request.form.get('custom_narrative')
        custom_mood = request.form.get('custom_mood')

        # Generate the story
        result = generate_story(
            conflict=conflict,
            setting=setting,
            narrative_style=narrative_style,
            mood=mood,
            custom_conflict=custom_conflict,
            custom_setting=custom_setting,
            custom_narrative=custom_narrative,
            custom_mood=custom_mood
        )

        # Store the generated story in database
        story = StoryGeneration(
            primary_conflict=result['conflict'],
            setting=result['setting'],
            narrative_style=result['narrative_style'],
            mood=result['mood'],
            generated_story=result['story']
        )
        db.session.add(story)
        db.session.commit()

        return jsonify({
            'success': True,
            'story': result['story']
        })

    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)