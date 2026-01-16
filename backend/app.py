from flask import Flask, render_template
from flask_cors import CORS
from routes.documents import documents_bp
from routes.ai import ai_bp
from routes.voice import voice_bp
from routes.sessions import sessions_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

app.register_blueprint(documents_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(voice_bp, url_prefix='/api/voice')
app.register_blueprint(sessions_bp, url_prefix='/api/sessions')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
