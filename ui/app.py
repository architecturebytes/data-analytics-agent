from flask import Flask, request, jsonify, send_from_directory
import vertexai
from vertexai.agent_engines import AgentEngine
import os
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# CONFIGURATION
# -----------------------------
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
AGENT_RESOURCE_NAME = os.getenv("AGENT_RESOURCE_NAME")

# CRITICAL FIX: The build folder is now ADJACENT to app.py within the 'ui' directory.
FRONTEND_DIST_DIR = os.path.join(os.path.dirname(__file__), 'dist_frontend') 
# -----------------------------

# Initialize Flask, configuring it to serve static files from the ADJACENT 'dist_frontend' folder
app = Flask(__name__, static_folder=FRONTEND_DIST_DIR, static_url_path='') 
CORS(app) 

# --- Pre-flight checks for required environment variables ---
if not all([PROJECT_ID, REGION, AGENT_RESOURCE_NAME]):
    @app.route("/", defaults={'path': ''})
    @app.route("/<path:path>")
    @app.route("/chat", methods=["GET", "POST"])
    def missing_env_vars(path=''):
        error_message = "Server configuration error: Ensure PROJECT_ID, REGION, and AGENT_RESOURCE_NAME are set in the backend environment."
        print(f"ERROR: {error_message}")
        # Return a 500 internal server error for any request
        return jsonify({
            "type": "text",
            "content": error_message,
        }), 500
else:
    # Initialize Vertex AI SDK once
    vertexai.init(
        project=PROJECT_ID,
        location=REGION
    )

# --- 1. FRONTEND ROUTE: Serves the main React application ---
# This serves index.html and all built assets (JS, CSS)
@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def serve_react_app(path):
    # If the path is a file (JS, CSS, etc.) in the build directory, serve it.
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    # Otherwise, serve the main entry point (index.html) for React routing.
    return send_from_directory(app.static_folder, 'index.html')


# --- 2. API ROUTE: Handles Agent interaction ---
@app.route("/chat", methods=["POST"])
def chat_endpoint():
    payload = request.get_json()
    message = payload.get("message")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        engine = AgentEngine(AGENT_RESOURCE_NAME)
        
        # VERSION FIX: The reported error ('AgentEngine' object has no attribute 'query') 
        # indicates the deployment environment is using an older SDK version where the 
        # method 'execute' is required instead of 'query'.
        # agent_response = engine.run(message)
        
        agent_response = engine.query(
            input={
                "message": message
            }
        )

        # The agent's response is a dict-like object that can be directly
        # converted to JSON.
        return jsonify(agent_response)

    except Exception as e:
        # Log the full error on the server side
        app.logger.error(f"Agent interaction failed: {e}")
        
        # Return a simple error message to the client
        return jsonify({
            "type": "text",
            "content": f"Error communicating with Agent Engine. Server logs show: {e.__class__.__name__}: {str(e)}",
        }), 500


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0", debug=True)