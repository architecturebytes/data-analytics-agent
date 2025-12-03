# deploy_agent.py
import vertexai
from vertexai import agent_engines
from agent.retail_agent import RetailAgent
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# CONFIGURATION
# -----------------------------
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")
DATASET_ID = os.getenv("DATASET_ID")
TABLE_ID = os.getenv("TABLE_ID")

DATASET = f"{DATASET_ID}.{TABLE_ID}" if DATASET_ID and TABLE_ID else None
REQUIREMENTS_FILE = "requirements.txt"  # your local requirements

def deploy_agent():
    if not all([PROJECT_ID, REGION, STAGING_BUCKET, DATASET]):
        print("Error: Ensure PROJECT_ID, REGION, STAGING_BUCKET, DATASET_ID, and TABLE_ID are set in your .env file.")
        exit()

    print("\n▶ Initializing Vertex AI")
    vertexai.init(
        project=PROJECT_ID,
        location=REGION,
        staging_bucket=STAGING_BUCKET
    )

    print("▶ Creating RetailAgent instance")
    agent_instance = RetailAgent(
        model="gemini-2.5-flash",
        name="retail_analytics_agent",
        dataset=DATASET
    )

    # Read requirements.txt for deployment
    try:
        with open(REQUIREMENTS_FILE) as f:
            requirements = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"⚠️ {REQUIREMENTS_FILE} not found. Using empty requirements list.")
        requirements = []

    print("▶ Deploying agent to Vertex AI")
    remote_agent = agent_engines.create(
        agent_instance,
        requirements=requirements,
        extra_packages=["agent"]
    )

    print("\n===============================================")
    print("🎉 SUCCESS — Agent Deployed")
    print("Agent Resource Name:")
    print(remote_agent.name)
    print("===============================================")

if __name__ == "__main__":
    deploy_agent()
