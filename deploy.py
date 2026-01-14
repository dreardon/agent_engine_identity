import os
import vertexai
from vertexai import agent_engines
from vertexai import types
from auditor import root_agent

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")
AGENT_ENGINE_LOCATION = os.getenv("AGENT_ENGINE_LOCATION")
AGENT_ENGINE_NAME = os.getenv("AGENT_ENGINE_NAME")

if not all([PROJECT_ID, AGENT_ENGINE_LOCATION, STAGING_BUCKET, AGENT_ENGINE_NAME]):
    raise ValueError("Missing required environment variables: PROJECT_ID, AGENT_ENGINE_LOCATION, STAGING_BUCKET, AGENT_ENGINE_NAME")

try:

    print(f"Deploying to Project: {PROJECT_ID}, Agent Engine Location: {AGENT_ENGINE_LOCATION}, Bucket: {STAGING_BUCKET}")

    # Create the Agent Engine instance
    client = vertexai.Client(
        project=PROJECT_ID,
        location=AGENT_ENGINE_LOCATION,
        http_options=dict(api_version="v1beta1")
    )    

    print("Updating Agent Engine Instance...")
    remote_app = client.agent_engines.update(
        name=AGENT_ENGINE_NAME,
        agent=root_agent,
        config={
            "requirements": ['google-cloud-aiplatform[adk,agent_engines]==1.132.0','pydantic==2.12.5','cloudpickle==3.1.2'],
            "staging_bucket": f"gs://{STAGING_BUCKET}",
            "agent_framework": "google-adk",
            "extra_packages": [
                "./auditor"
            ],
        }
    )

    print("\nDeployment Complete!")
except Exception as e:
    print(f"\nDeployment Failed: {e}")
    raise