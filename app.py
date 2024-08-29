from flask import Flask, request, jsonify
import spacy
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

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
    data = request.json
    user_responses = data.get('user_responses', [])
    criteria = data.get('criteria', {})
    band_score = int((criteria.get("TaskAchievement", 0) + criteria.get("Coherence", 0) +
                      criteria.get("LexicalResource", 0) + criteria.get("Grammar", 0)) / 4)
    feedback = generate_band_feedback(band_score)
    user_level = classify_user_level(" ".join(user_responses))
    result = {"band_score": band_score, "feedback": feedback, "user_level": user_level}
    return jsonify(result)

# API route to plot user progress
@app.route('/plot_progress', methods=['POST'])
def plot_progress():
    data = request.json
    band_scores = data.get('band_scores', [])
    sessions = list(range(1, len(band_scores) + 1))
    plt.plot(sessions, band_scores, marker='o')
    plt.title("User Progress Over Time")
    plt.xlabel("Session")
    plt.ylabel("Band Score")
    plt.grid(True)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return jsonify({"plot_url": plot_url})

if __name__ == '__main__':
    app.run(debug=True)
