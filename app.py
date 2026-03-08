"""
Flask Web App for Phishing Detection Tool
Run with: python app.py
Then open http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from detector import analyse

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyse", methods=["POST"])
def analyse_input():
    data = request.get_json()
    user_input = data.get("input", "").strip()

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    result = analyse(user_input)

    return jsonify({
        "input_value": result.input_value,
        "input_type": result.input_type,
        "risk_score": result.risk_score,
        "risk_level": result.risk_level,
        "flags": result.flags,
        "details": result.details,
    })


if __name__ == "__main__":
    app.run(debug=True)
