# undeploy_agent.py

import vertexai
import os
from dotenv import load_dotenv
# --- CRITICAL FIX: Use the V1 client submodule ---
from google.cloud.aiplatform_v1.services.reasoning_engine_service import ReasoningEngineServiceClient
from google.api_core import client_options
# -------------------------------------------------

load_dotenv()

# -----------------------------
# CONFIGURATION
# -----------------------------
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
AGENT_RESOURCE_NAME = os.getenv("AGENT_RESOURCE_NAME")

def undeploy_agent():
    if not all([PROJECT_ID, REGION, AGENT_RESOURCE_NAME]):
        print("Error: Ensure PROJECT_ID, REGION, and AGENT_RESOURCE_NAME are set in your .env file.")
        exit()
        
    print(f"\n▶ Initializing Vertex AI in {REGION}...")
    # Initialization is still needed for context, but the client will handle the deletion
    vertexai.init(
        project=PROJECT_ID,
        location=REGION,
    )

    print(f"▶ Attempting to delete resource: {AGENT_RESOURCE_NAME}")
    try:
        # 1. Define the client options (required for correct region targeting)
        api_endpoint = f"{REGION}-aiplatform.googleapis.com"
        options = client_options.ClientOptions(api_endpoint=api_endpoint)
        
        # 2. Instantiate the V1 GAPIC Client
        client = ReasoningEngineServiceClient(client_options=options)
        
        # 3. Call the delete method using the full resource name
        client.delete_reasoning_engine(name=AGENT_RESOURCE_NAME)
        
        print("\n===============================================")
        print("✅ SUCCESS — Agent Undeployed and Deleted")
        print("NOTE: The operation is asynchronous and may take a moment to reflect in the console.")
        print("===============================================")
        
    except Exception as e:
        # Check for the common 'not found' exception
        if "not found" in str(e).lower():
            print(f"⚠️ Agent already deleted or resource name is incorrect. Details: {e}")
        else:
            print(f"\n❌ ERROR: Failed to undeploy agent.")
            print(f"Please check your permissions or network connection. Details: {e}")


if __name__ == "__main__":
    undeploy_agent()