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

        # Extract character traits from the analysis
        character_traits = analysis.get('character_traits', [])

        # Store the analysis in database
        image_analysis = ImageAnalysis(
            image_url=image_url,
            analysis_result=analysis,
            character_traits=character_traits,
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
        selected_image_id = request.form.get('selected_image_id')

        # Get custom inputs if provided
        custom_conflict = request.form.get('custom_conflict')
        custom_setting = request.form.get('custom_setting')
        custom_narrative = request.form.get('custom_narrative')
        custom_mood = request.form.get('custom_mood')

        # Get the selected image's data if provided
        selected_image = None
        if selected_image_id:
            selected_image = ImageAnalysis.query.get(selected_image_id)
            if selected_image:
                # Add character information to the story generation
                character_info = {
                    'name': selected_image.analysis_result.get('name', ''),
                    'traits': selected_image.character_traits,
                    'description': selected_image.analysis_result.get('style', '')
                }
            else:
                character_info = None
        else:
            character_info = None

        # Generate the story
        result = generate_story(
            conflict=conflict,
            setting=setting,
            narrative_style=narrative_style,
            mood=mood,
            custom_conflict=custom_conflict,
            custom_setting=custom_setting,
            custom_narrative=custom_narrative,
            custom_mood=custom_mood,
            character_info=character_info
        )

        # Store the generated story in database
        story = StoryGeneration(
            primary_conflict=result['conflict'],
            setting=result['setting'],
            narrative_style=result['narrative_style'],
            mood=result['mood'],
            generated_story=result['story']  # This is now a JSON string, not a dict
        )

        # If an image was selected, associate it with the story
        if selected_image:
            story.images.append(selected_image)

        db.session.add(story)
        db.session.commit()

        # Parse the JSON string back to a Python object for proper display
        story_data = json.loads(result['story'])
        return jsonify({
            'success': True,
            'story': story_data
        })

    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_random_images', methods=['GET'])
def get_random_images():
    """Get 3 random images from the database with their analysis"""
    try:
        # Get 3 random images from the database
        images = ImageAnalysis.query.order_by(db.func.random()).limit(3).all()

        image_data = []
        for img in images:
            analysis = img.analysis_result
            image_data.append({
                'id': img.id,
                'image_url': img.image_url,
                'name': analysis.get('name', ''),
                'style': analysis.get('style', ''),
                'story': analysis.get('story', ''),
                'character_traits': img.character_traits or []
            })

        return jsonify({
            'success': True,
            'images': image_data
        })

    except Exception as e:
        logger.error(f"Error getting random images: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reroll_image/<int:index>', methods=['GET'])
def reroll_image(index):
    """Get a new random image to replace one at the specified index"""
    try:
        # Get a random image excluding those that might be currently displayed
        excluded_ids = request.args.getlist('excluded_ids[]', type=int)
        image = ImageAnalysis.query.filter(
            ~ImageAnalysis.id.in_(excluded_ids)
        ).order_by(db.func.random()).first()

        if not image:
            return jsonify({'error': 'No more images available'}), 404

        analysis = image.analysis_result
        image_data = {
            'id': image.id,
            'image_url': image.image_url,
            'name': analysis.get('name', ''),
            'style': analysis.get('style', ''),
            'story': analysis.get('story', ''),
            'character_traits': image.character_traits or []
        }

        return jsonify({
            'success': True,
            'image': image_data
        })

    except Exception as e:
        logger.error(f"Error rerolling image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    """Analyze an image URL without Yorkshire terrier specification"""
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        instruction_id = data.get('instruction_id')

        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400

        # Get instruction if provided, otherwise create a generic one
        if instruction_id:
            instruction = AIInstruction.query.get(instruction_id)
            if not instruction:
                return jsonify({'error': 'Invalid instruction ID'}), 400
        else:
            # Create a generic art analysis instruction
            instruction = AIInstruction(
                name="Generic Art Analysis",
                system_prompt="You are an art critic. "
                            "Analyze the image and provide: "
                            "1. Art style description "
                            "2. A creative name for the character "
                            "3. A brief, engaging story about the character "
                            "4. List 3-5 character traits that define this character "
                            "Respond in JSON format with keys: 'style', 'name', 'story', 'character_traits'",
                user_prompt="Please analyze this artwork:"
            )

        # Analyze the artwork using OpenAI with instruction
        analysis = analyze_artwork(image_url, instruction)

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_instructions', methods=['GET'])
def get_instructions():
    """Get all available AI instructions"""
    try:
        instructions = AIInstruction.query.all()
        return jsonify({
            'success': True,
            'instructions': [{'id': i.id, 'name': i.name} for i in instructions]
        })
    except Exception as e:
        logger.error(f"Error getting instructions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/manage/instructions', methods=['GET', 'POST', 'DELETE'])
def manage_instructions():
    """Manage AI instructions"""
    try:
        if request.method == 'DELETE':
            data = request.get_json()
            instruction_id = data.get('id')
            
            if not instruction_id:
                return jsonify({'error': 'No instruction ID provided'}), 400
                
            instruction = AIInstruction.query.get(instruction_id)
            if not instruction:
                return jsonify({'error': 'Instruction not found'}), 404
                
            # Don't allow deleting the default instruction
            if instruction.is_default:
                return jsonify({'error': 'Cannot delete default instruction'}), 400
                
            # Delete the instruction
            db.session.delete(instruction)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Instruction "{instruction.name}" deleted successfully'
            })
            
        elif request.method == 'POST':
            data = request.get_json()
            instruction = AIInstruction(
                name=data['name'],
                system_prompt=data['system_prompt'],
                user_prompt=data['user_prompt'],
                is_default=data.get('is_default', False)
            )

            if instruction.is_default:
                # Unset any existing default
                AIInstruction.query.filter_by(is_default=True).update({'is_default': False})

            db.session.add(instruction)
            db.session.commit()

            return jsonify({
                'success': True,
                'instruction': {
                    'id': instruction.id,
                    'name': instruction.name,
                    'is_default': instruction.is_default
                }
            })

        # GET: Return all instructions
        instructions = AIInstruction.query.all()
        return jsonify({
            'success': True,
            'instructions': [{
                'id': i.id,
                'name': i.name,
                'system_prompt': i.system_prompt,
                'user_prompt': i.user_prompt,
                'is_default': i.is_default
            } for i in instructions]
        })

    except Exception as e:
        logger.error(f"Error managing instructions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/manage/hashtags', methods=['GET', 'POST'])
def manage_hashtags():
    """Manage hashtag collections"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            # Process hashtags string into array
            hashtags = [tag.strip() for tag in data['hashtags'].replace('\n', ',').split(',')
                       if tag.strip() and tag.strip().startswith('#')]

            collection = HashtagCollection(
                name=data['name'],
                hashtags=hashtags,
                is_default=data.get('is_default', False)
            )

            if collection.is_default:
                # Unset any existing default
                HashtagCollection.query.filter_by(is_default=True).update({'is_default': False})

            db.session.add(collection)
            db.session.commit()

            return jsonify({
                'success': True,
                'collection': {
                    'id': collection.id,
                    'name': collection.name,
                    'is_default': collection.is_default
                }
            })

        # GET: Return all collections
        collections = HashtagCollection.query.all()
        return jsonify({
            'success': True,
            'collections': [{
                'id': c.id,
                'name': c.name,
                'hashtags': c.hashtags,
                'is_default': c.is_default
            } for c in collections]
        })

    except Exception as e:
        logger.error(f"Error managing hashtags: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)