from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__)

# Register routes
from routes.speech_gen import speech_bp
app.register_blueprint(speech_bp)

@app.route("/")
def home():
    return "✅ Media Generation API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
