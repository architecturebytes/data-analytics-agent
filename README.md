# Retail Analytics Assistant

This project is a retail analytics assistant that leverages Google Cloud's Vertex AI Agent Builder, BigQuery, and a React frontend to provide insights into retail data through a conversational interface.

## Features

-   **Conversational AI:** Interact with your retail data using natural language.
-   **Data Analysis & Visualization:** Generate SQL queries, retrieve data from BigQuery, and visualize results (tables, charts) in response to chat prompts like: 'Show sales data as bar chart'.
-   **Speech-to-Text & Text-to-Speech:** Seamless interaction with voice commands and spoken responses.
-   **Scalable Backend:** Built with Python, Flask, and Vertex AI Agent Builder for robust data processing.
-   **Interactive Frontend:** A modern React application for a user-friendly experience.

## Project Structure

-   `agent/`: Contains the Python code for the Vertex AI retail agent, including deployment scripts.
-   `ui/`: Houses the React frontend application (`ui/src`) and the Flask backend (`ui/app.py`) that serves the React app and handles API requests to the agent.
-   `create_bq_data.py`: A utility script to create a BigQuery dataset and table, and populate it with sample retail data.
-   `requirements.txt`: Python dependencies for the backend.

## Setup and Installation

### 1. Prerequisites

Before you begin, ensure you have the following installed:

-   [Python 3.8+](https://www.python.org/downloads/) (It is recommended to use a Python [virtual environment](https://docs.python.org/3/library/venv.html) for this project.)
-   [Node.js (LTS)](https://nodejs.org/en/download/)
-   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (gcloud CLI)
-   [Terraform](https://www.terraform.io/downloads.html) (if deploying infrastructure with Terraform)

### 2. Google Cloud Setup

1.  **Authenticate `gcloud`:**
    ```bash
    gcloud auth application-default login
    ```
    This will open a browser window for you to log in to your Google account.

2.  **Enable necessary APIs:**
    ```bash
    gcloud services enable \\
        aiplatform.googleapis.com \\
        bigquery.googleapis.com \\
        storage.googleapis.com \\
        cloudbuild.googleapis.com \\
        iam.googleapis.com \\
        cloudresourcemanager.googleapis.com
    ```

3.  **Create Staging Bucket:**
    A Cloud Storage bucket is required as a staging area for Vertex AI Agent Builder.
    ```bash
    gsutil mb -l us-central1 gs://YOUR_PROJECT_ID-vertex-staging-agent/
    ```
    (Replace `YOUR_PROJECT_ID` with your actual GCP Project ID)

4.  **Check Bucket (Optional):**
    ```bash
    gsutil ls
    ```

### 3. Environment Configuration

Create a `.env` file in the root directory of the project based on the `.env.example` template:

```bash
cp .env.example .env
```

Edit the `.env` file and fill in your specific Google Cloud project details:

```ini
# Google Cloud
PROJECT_ID="your-gcp-project-id" # e.g., my-retail-project-12345
REGION="us-central1" # e.g., us-central1
STAGING_BUCKET="gs://your-gcp-project-id-vertex-staging-agent" # Must be unique globally, e.g., gs://my-retail-project-12345-vertex-staging-agent
AGENT_RESOURCE_NAME="projects/your-project-number/locations/your-region/reasoningEngines/your-agent-id" # This will be generated after deploying the agent.

# BigQuery
DATASET_ID="bytes_dataset"
TABLE_ID="retail_data"

# Frontend API Endpoint (for Vite)
VITE_API_ENDPOINT="http://localhost:8080/chat"
```

**Note:** The `AGENT_RESOURCE_NAME` will be obtained after you deploy your Vertex AI Agent (see step 5). For initial setup, you can leave it empty or use a placeholder.

### 4. BigQuery Data Setup

Run the script to create your BigQuery dataset and table, and populate it with sample data:

```bash
python create_bq_data.py
```

### 5. Deploy the Vertex AI Agent

1.  **Clear Staging Bucket (if re-deploying):**
    It's often good practice to clear the staging bucket before a new deployment to avoid conflicts or stale artifacts.
    ```bash
    gsutil rm -r gs://YOUR_PROJECT_ID-vertex-staging-agent/agent_engine/
    ```
    (Replace `YOUR_PROJECT_ID` with your actual GCP Project ID)

2.  From the project's root directory, run the deployment script as a module:
    ```bash
    python -m agent.deploy_agent
    ```

3.  After successful deployment, the script will print the `AGENT_RESOURCE_NAME`. **Update this value in your `.env` file.**

4.  **Grant BigQuery Permissions to Agent Service Account:**
    The deployed agent needs permission to read data from BigQuery. You must grant the appropriate IAM roles to the agent's service account. The service account name typically follows the pattern: `service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com`. You can find your `PROJECT_NUMBER` in the Google Cloud Console Dashboard or by running `gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"`.

    Replace `YOUR_PROJECT_ID` and `YOUR_PROJECT_NUMBER` in the commands below:

    ```bash
    gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \\
        --member="serviceAccount:service-YOUR_PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \\
        --role="roles/bigquery.user"

    gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \\
        --member="serviceAccount:service-YOUR_PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \\
        --role="roles/bigquery.dataViewer"
    ```
    The `bigquery.user` role allows the service account to run jobs, and `bigquery.dataViewer` allows it to read data.

### 6. Running the Web Application

To run the full web application (both frontend and backend), follow these steps from within the `ui/` directory:

1.  **Navigate to the UI directory:**
    ```bash
    cd ui
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Build the React frontend:**
    This command compiles the React application into a set of static files in the `dist_frontend` directory. This build must complete before the Flask server can serve the frontend.
    ```bash
    npm run build
    ```

4.  **Install Python dependencies (for Flask server):**
    Install Flask and other required Python packages from the root `requirements.txt` file.
    ```bash
    pip install -r ../requirements.txt
    ```

5.  **Start the Flask Backend Server:**
    This command starts the backend server, which will serve the static frontend files you just built and handle API calls to the agent.
    ```bash
    python app.py
    ```

## Usage

Once both the agent is deployed and the Flask server is running, open your web browser and navigate to `http://localhost:8080`. You can then start interacting with the Retail Analytics Assistant by typing your questions or using the microphone for voice input.

## Important Notes


-   **Vertex AI Quotas:** Ensure your Google Cloud project has sufficient quotas for Vertex AI services.
-   **Cost:** Be mindful of the costs associated with Google Cloud services, especially Vertex AI and BigQuery.
