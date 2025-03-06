from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from app import db

class ImageAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(512), nullable=False)
    analysis_result = db.Column(JSON, nullable=False)
    character_traits = db.Column(ARRAY(db.String), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    instruction_id = db.Column(db.Integer, db.ForeignKey('ai_instruction.id'))
    hashtag_collection_id = db.Column(db.Integer, db.ForeignKey('hashtag_collection.id'))
    stories = db.relationship('StoryGeneration', secondary='story_images', backref='images')

    # Add relationship to StorySession for character tracking
    story_sessions = db.relationship('StorySession', secondary='session_characters', backref='characters')

class AIInstruction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    system_prompt = db.Column(db.Text, nullable=False)
    user_prompt = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses = db.relationship('ImageAnalysis', backref='instruction', lazy=True)

    @staticmethod
    def get_default():
        return AIInstruction.query.filter_by(is_default=True).first()

class HashtagCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hashtags = db.Column(ARRAY(db.String), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses = db.relationship('ImageAnalysis', backref='hashtag_collection', lazy=True)

    @staticmethod
    def get_default():
        return HashtagCollection.query.filter_by(is_default=True).first()

# Association table for StoryGeneration and ImageAnalysis
story_images = db.Table('story_images',
    db.Column('story_id', db.Integer, db.ForeignKey('story_generation.id'), primary_key=True),
    db.Column('image_id', db.Integer, db.ForeignKey('image_analysis.id'), primary_key=True)
)

class StoryGeneration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primary_conflict = db.Column(db.String(100), nullable=False)
    setting = db.Column(db.String(100), nullable=False)
    narrative_style = db.Column(db.String(100), nullable=False)
    mood = db.Column(db.String(100), nullable=False)
    generated_story = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# New models for CYOA functionality

# Association table for StorySession and ImageAnalysis (selected characters)
session_characters = db.Table('session_characters',
    db.Column('session_id', db.Integer, db.ForeignKey('story_session.id'), primary_key=True),
    db.Column('character_id', db.Integer, db.ForeignKey('image_analysis.id'), primary_key=True)
)

class StorySession(db.Model):
    """Tracks a single playthrough of the story"""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)
    current_segment_id = db.Column(db.Integer, db.ForeignKey('story_segment.id'))

    # Story parameters
    setting = db.Column(db.String(100))
    mood = db.Column(db.String(100))
    conflict = db.Column(db.String(100))

    # Relationships
    segments = db.relationship('StorySegment', backref='session', lazy=True, 
                             foreign_keys='StorySegment.session_id')
    current_segment = db.relationship('StorySegment', foreign_keys=[current_segment_id],
                                    post_update=True)
    choices = db.relationship('PlayerChoice', backref='session', lazy=True)

class StorySegment(db.Model):
    """Individual parts of the story with choices"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('story_session.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sequence_number = db.Column(db.Integer, nullable=False)

    # Available choices for this segment
    choices = db.relationship('StoryChoice', 
                            foreign_keys='StoryChoice.segment_id',
                            backref='segment', lazy=True)

    # The choice that led to this segment (null for first segment)
    parent_choice_id = db.Column(db.Integer, db.ForeignKey('story_choice.id'))
    parent_choice = db.relationship('StoryChoice', foreign_keys=[parent_choice_id],
                                  remote_side='StoryChoice.id',
                                  post_update=True)

class StoryChoice(db.Model):
    """Available choices at each decision point"""
    id = db.Column(db.Integer, primary_key=True)
    segment_id = db.Column(db.Integer, db.ForeignKey('story_segment.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # The segment this choice leads to (null until chosen)
    next_segment_id = db.Column(db.Integer, db.ForeignKey('story_segment.id'))
    next_segment = db.relationship('StorySegment', 
                                 foreign_keys=[next_segment_id],
                                 remote_side='StorySegment.id',
                                 post_update=True)

    # Reference to the player's choice if this option was selected
    player_choice = db.relationship('PlayerChoice', backref='choice', lazy=True, uselist=False)

class PlayerChoice(db.Model):
    """Tracks the choices made by the player"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('story_session.id'), nullable=False)
    choice_id = db.Column(db.Integer, db.ForeignKey('story_choice.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sequence_number = db.Column(db.Integer, nullable=False)  # Order of choices made