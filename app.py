import os
import spacy
from spacy.cli import download
from flask import Flask, request, jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
SPACY_MODEL = os.environ.get('SPACY_MODEL', 'en_core_web_sm')
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'

# Ensure the spaCy model is downloaded
try:
    nlp = spacy.load(SPACY_MODEL)
    logger.info(f"Loaded spaCy model: {SPACY_MODEL}")
except OSError:
    logger.info(f"Downloading spaCy model: {SPACY_MODEL}")
    download(SPACY_MODEL)
    nlp = spacy.load(SPACY_MODEL)

# Function to generate feedback based on band score
def generate_band_feedback(band_score):
    feedback = {
        5: {"summary": "...", "strengths": "...", "areas_for_improvement": "..."},
        6: {"summary": "...", "strengths": "...", "areas_for_improvement": "..."},
        7: {"summary": "...", "strengths": "...", "areas_for_improvement": "..."},
        8: {"summary": "...", "strengths": "...", "areas_for_improvement": "..."},
    }
    return feedback.get(band_score, {"summary": "Band score not recognized.", "strengths": "N/A", "areas_for_improvement": "N/A"})

# Function to classify user level using spaCy
def classify_user_level(text):
    doc = nlp(text)
    num_sentences = len(list(doc.sents))
    avg_sentence_length = sum(len(sent) for sent in doc.sents) / num_sentences if num_sentences > 0 else 0
    if avg_sentence_length > 15:
        return "Advanced"
    elif avg_sentence_length > 10:
        return "Intermediate"
    else:
        return "Beginner"

# API route to evaluate user responses
@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        user_responses = data.get('user_responses', [])
        criteria = data.get('criteria', {})

        if not user_responses or not criteria:
            return jsonify({"error": "Missing user_responses or criteria"}), 400

        band_score = int((criteria.get("TaskAchievement", 0) + criteria.get("Coherence", 0) +
                          criteria.get("LexicalResource", 0) + criteria.get("Grammar", 0)) / 4)
        feedback = generate_band_feedback(band_score)
        user_level = classify_user_level(" ".join(user_responses))
        
        result = {"band_score": band_score, "feedback": feedback, "user_level": user_level}
        logger.info(f"Evaluation completed for user. Band score: {band_score}, Level: {user_level}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in evaluate endpoint: {str(e)}")
        return jsonify({"error": "An error occurred during evaluation"}), 500

# API route to plot user progress
@app.route('/plot_progress', methods=['POST'])
def plot_progress():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        band_scores = data.get('band_scores', [])
        if not band_scores:
            return jsonify({"error": "No band scores provided"}), 400

        sessions = list(range(1, len(band_scores) + 1))
        plt.figure(figsize=(10, 6))
        plt.plot(sessions, band_scores, marker='o')
        plt.title("User Progress Over Time")
        plt.xlabel("Session")
        plt.ylabel("Band Score")
        plt.grid(True)
        
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        
        plot_url = base64.b64encode(img.getvalue()).decode()
        logger.info(f"Progress plot generated for {len(band_scores)} sessions")
        return jsonify({"plot_url": plot_url})
    except Exception as e:
        logger.error(f"Error in plot_progress endpoint: {str(e)}")
        return jsonify({"error": "An error occurred while generating the progress plot"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)
