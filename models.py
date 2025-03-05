from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from app import db

class ImageAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(512), nullable=False)
    analysis_result = db.Column(JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    instruction_id = db.Column(db.Integer, db.ForeignKey('ai_instruction.id'))
    hashtag_collection_id = db.Column(db.Integer, db.ForeignKey('hashtag_collection.id'))

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
    hashtags = db.Column(db.ARRAY(db.String), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses = db.relationship('ImageAnalysis', backref='hashtag_collection', lazy=True)

    @staticmethod
    def get_default():
        return HashtagCollection.query.filter_by(is_default=True).first()

class StoryGeneration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primary_conflict = db.Column(db.String(100), nullable=False)
    setting = db.Column(db.String(100), nullable=False)
    narrative_style = db.Column(db.String(100), nullable=False)
    mood = db.Column(db.String(100), nullable=False)
    generated_story = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
