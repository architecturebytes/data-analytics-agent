import json
import datetime
from google.adk.agents import Agent
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import bigquery

UI_SCHEMA = {
    "type": "object",
    "properties": {
        "content": {"type": "string"},
        "type": {"type": "string"},
        "visualization": {
            "type": "object",
            "properties": {
                "chart_type": {"type": "string"},
                "x_axis": {"type": "string"},
                "y_axis": {"type": "string"}
            }
        },
        "data": {"type": "array", "items": {"type": "object"}},
        "raw_sql": {"type": "string"},
    },
    "required": ["type"], # Only type is always required. Others are optional.
}

class RetailAgent(Agent):
    def __init__(self, model: str, name: str, dataset: str):
        super().__init__(model=model, name=name)
        self._dataset = dataset

    def query(self, input: dict) -> dict:
        user_message = (input or {}).get("message", "")
        print("User message:", user_message)

        bq_client = bigquery.Client()
        model = GenerativeModel("gemini-2.5-flash")

        try:
            dataset_id, table_id = self._dataset.split('.')
            table_ref = bq_client.dataset(dataset_id).table(table_id)
            table = bq_client.get_table(table_ref)
            schema_str = ", ".join([f"{col.name}: {col.field_type}" for col in table.schema])
            schema_prompt = f"The table schema for {self._dataset} is: {schema_str}\n\n"
        except Exception as e:
            print(f"Warning: Could not get table schema. {e}")
            schema_prompt = ""

        # First call to the model to get the SQL and visualization
        system_instruction_1 = (
            "You are a Retail Analytics AI. Your first task is to analyze the user's request. If it's a general conversation, respond with only text. If it requires data analysis, generate a SQL query and a visualization object.\n"
            f"Answer questions for dataset: {self._dataset}.\n\n"
            f"{schema_prompt}"
            "Your response MUST match the required JSON schema and rules. Do not include the 'content' field in this response.\n"
            f"{json.dumps(UI_SCHEMA)}\n\n"
            "Rules:\n"
            "1. For general conversational questions (e.g., 'Hello', 'How are you?', 'Thank you', 'What can you do?', 'Wonderful'), respond by setting 'type' to 'text' and by OMITTING 'raw_sql', 'data', and 'visualization'. DO NOT generate SQL or visualization for these questions.\n"
            "2. If the user asks for a chart (e.g., 'bar chart', 'line chart', 'pie chart'), set 'type' to 'analytics' and populate the 'visualization' object with 'chart_type', 'x_axis' (the column for the x-axis or categories), and 'y_axis' (the column for the y-axis or values). For example, for a bar chart of sales by region, set `visualization: {'chart_type': 'bar_chart', 'x_axis': 'region', 'y_axis': 'total_sales'}`.\n"
            "3. If the user asks for data in a 'table', 'tabular' format, or asks a question that results in a single row or value (e.g., 'what is the highest...'), set 'type' to 'analytics' and 'visualization.chart_type' to 'table'.\n"
            "4. Always include the SQL query in `raw_sql` if a visualization is requested (i.e., when 'type' is 'analytics').\n"
            "5. When filtering by date in BigQuery SQL, use direct comparisons like `transaction_date <= 'YYYY-MM-DD'` or `EXTRACT(MONTH FROM transaction_date) = 6` if extracting date parts. Do NOT use column names as date part names (e.g., `transaction_date` in `EXTRACT(transaction_date FROM transaction_date)` is incorrect).\n"
            f"6. All table names in SQL queries MUST be fully qualified with the dataset name (e.g., {self._dataset}).\n"
            "Return ONLY valid JSON."
        )

        contents = [{"role": "user", "parts": [{"text": system_instruction_1}, {"text": user_message}]}]

        response = model.generate_content(contents=contents)
        model_output = getattr(response, "text", None)

        if not model_output:
            return {"content": "Model returned no text.", "type": "text", "visualization": {"chart_type": "none"}, "data": [], "raw_sql": ""}

        if "```json" in model_output:
            model_output = model_output.split("```json")[1].split("```")[0]

        try:
            payload = json.loads(model_output)
        except Exception as e:
            return {"content": f"Error parsing JSON: {e}. Raw output: {model_output}", "type": "text", "visualization": {"chart_type": "none"}, "data": [], "raw_sql": ""}

        # Execute the SQL and format the data
        if payload.get("raw_sql"):
            try:
                query_job = bq_client.query(payload["raw_sql"])
                results = [dict(row) for row in query_job.result()]
                
                # Format floating point numbers and date/datetime objects
                formatted_results = []
                for row in results:
                    formatted_row = {}
                    for key, value in row.items():
                        if isinstance(value, float):
                            formatted_row[key] = round(value, 2)
                        elif isinstance(value, (datetime.date, datetime.datetime)):
                            formatted_row[key] = value.isoformat()
                        else:
                            formatted_row[key] = value
                    formatted_results.append(formatted_row)
                
                payload["data"] = formatted_results
            except Exception as e:
                return {"content": f"Error executing SQL: {e}", "type": "text", "visualization": {"chart_type": "none"}, "data": [], "raw_sql": ""}
        else:
            payload["data"] = []


        # Second call to the model to get the summary
        if payload.get("raw_sql"): # Only generate summary if SQL was generated
            system_instruction_2 = (
                "You are a Retail Analytics AI. Your second task is to generate a concise, natural language summary of the provided data.\n"
                "The user's original question was: " + user_message + "\n"
                "The data is: " + json.dumps(payload["data"]) + "\n"
                "Based on the data, provide a short summary (1-2 sentences) in the 'content' field. Your response must be a valid JSON with only the 'content' field."
            )
            
            contents_2 = [{"role": "user", "parts": [{"text": system_instruction_2}]}]
            response_2 = model.generate_content(contents=contents_2)
            model_output_2 = getattr(response_2, "text", None)
            
            if model_output_2:
                try:
                    if "```json" in model_output_2:
                        model_output_2 = model_output_2.split("```json")[1].split("```")[0]
                    summary_payload = json.loads(model_output_2)
                    payload["content"] = summary_payload.get("content", "")
                except Exception as e:
                    print(f"Warning: Could not generate summary. {e}")
                    payload["content"] = ""
            else:
                payload["content"] = ""
        else: # If no raw_sql, then no data analysis was performed, so content should be a simple text response.
            # This case means payload["type"] is "text" from the first model call
            # We need to ask the model to generate a text response based on the user's input directly.
            system_instruction_text_only = (
                "You are a Retail Analytics AI assistant. The user asked a general conversational question:\n"
                "User's question: " + user_message + "\n"
                "Please provide a helpful and concise text response in the 'content' field. Your response must be a valid JSON with only the 'content' field."
            )
            contents_text_only = [{"role": "user", "parts": [{"text": system_instruction_text_only}]}]
            response_text_only = model.generate_content(contents=contents_text_only)
            model_output_text_only = getattr(response_text_only, "text", None)
            if model_output_text_only:
                try:
                    if "```json" in model_output_text_only:
                        model_output_text_only = model_output_text_only.split("```json")[1].split("```")[0]
                    text_payload = json.loads(model_output_text_only)
                    payload["content"] = text_payload.get("content", "")
                except Exception as e:
                    print(f"Warning: Could not generate text-only response. {e}")
                    payload["content"] = ""
            else:
                payload["content"] = "I'm sorry, I couldn't generate a response."


        # Normalize the final payload
        # Ensure type is text if no raw_sql or visualization is provided
        if not payload.get("raw_sql") and (not payload.get("visualization") or payload.get("visualization", {}).get("chart_type") == "none"):
            payload["type"] = "text"
            payload["raw_sql"] = ""
            payload["data"] = []
            payload["visualization"] = {"chart_type": "none"}
        elif payload.get("visualization") and payload.get("visualization", {}).get("chart_type") != "none":
            payload["type"] = "analytics"
        else:
            payload["type"] = "text" # Default to text if visualization is not explicitly analytics

        # Ensure content is always present, even if empty string
        payload["content"] = payload.get("content", "")
        # Ensure raw_sql, data, visualization are present with defaults if optional
        payload["raw_sql"] = payload.get("raw_sql", "")
        payload["data"] = payload.get("data", [])
        payload["visualization"] = payload.get("visualization", {"chart_type": "none"})

        return payload
