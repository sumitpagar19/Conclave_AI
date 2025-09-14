from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import asyncio
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from conclave import ConclaveAI

app = Flask(__name__)
CORS(app)

# Initialize Conclave AI
conclave_ai = ConclaveAI()

@app.route('/')
def index():
    """Serve the frontend HTML"""
    try:
        with open('frontend.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return render_template_string("""
        <!DOCTYPE html>
        <html><head><title>Conclave AI</title></head>
        <body style='font-family: Arial; text-align: center; padding: 50px;'>
            <h1>🚀 Conclave AI Backend is Live!</h1>
            <p>API endpoint: <code>/api/analyze</code></p>
            <p>Status: <a href="/api/health">Health Check</a></p>
        </body></html>
        """)

@app.route('/api/analyze', methods=['POST'])
def analyze_question():
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400
            
        question = data['question'].strip()
        
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400
            
        # Run Conclave AI debate
        result = asyncio.run(conclave_ai.run_conclave_debate(question))
        
        return jsonify({
            'success': True,
            'question': result['question'],
            'consensus': result['consensus'],
            'timestamp': result['timestamp'].isoformat(),
            'models_consulted': ['ChatGPT', 'Gemini', 'Claude']
        })
        
    except Exception as e:
        app.logger.error(f"Error in analyze_question: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Conclave AI Backend',
        'models': list(conclave_ai.models.keys()),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)