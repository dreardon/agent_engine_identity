# Google Cloud Agent Engine Identity Example

## Overview
This project provides a reference implementation of a **Fact Checking Decision Auditor** agent built using **Google Cloud Vertex AI Agent Engine** and the **Agent Development Kit (ADK)**. Ultimately, this is an identity-focused implementation of an example from the [Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)

The primary goal of this example is to demonstrate [Agent Engine Identity](https://docs.cloud.google.com/agent-builder/agent-engine/agent-identity), showing how to deploy an agent with a dedicated identity and manage its permissions. This allows the agent to securely interact with Google Cloud services using its own credentials.

### Architecture
The application implements a `SequentialAgent` pipeline consisting of:
1.  **Critic Agent**: Evaluates LLM-generated answers and verifies their accuracy using web resources.
2.  **Reviser Agent**: Refines the response based on the Critic's findings to ensure alignment with real-world knowledge.

### Key Technologies
*   **Google Cloud Vertex AI Agent Engine**: Managed runtime for hosting and scaling reasoning engines.
*   **Google Agent Development Kit (ADK)**: Python framework for building structured, composable agents.
*   **Google Cloud IAM**: Configurations for secure Agent Identity management.
*   **Python**: The primary development language.



## Google Disclaimer
This is not an officially supported Google product

## Setup Environment
```bash
# Setup Environment variables
export ORGANIZATION_ID= #e.g. 123456789876
export PROJECT_NAME= #e.g. agent-engine-identity
export BILLING_ACCOUNT= #e.g. 111111-222222-333333
export AGENT_ENGINE_LOCATION= #e.g. us-central1
export STAGING_BUCKET= #e.g. ae-identity-agent-code (Globally Unique)

# Create Project
gcloud config unset project
gcloud config unset billing/quota_project
printf 'Y' | gcloud projects create --name=$PROJECT_NAME --organization=$ORGANIZATION_ID
while [ -z "$PROJECT_ID" ]; do
  export PROJECT_ID=$(gcloud projects list --filter=name:$PROJECT_NAME --format 'value(PROJECT_ID)')
done
export PROJECT_NUMBER=$(gcloud projects list --filter=id:$PROJECT_ID --format 'value(PROJECT_NUMBER)')
printf 'y' |  gcloud beta billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT

gcloud config set project $PROJECT_ID
gcloud config set billing/quota_project $PROJECT_ID

# Enable APIs
printf 'y' |  gcloud services enable cloudresourcemanager.googleapis.com --project $PROJECT_ID
printf 'y' |  gcloud services enable aiplatform.googleapis.com --project $PROJECT_ID

# Create Agent Engine Staging Bucket
gcloud storage buckets create gs://$STAGING_BUCKET \
    --location=$AGENT_ENGINE_LOCATION \
    --default-storage-class=STANDARD \
    --project $PROJECT_ID
```

## Deploy the Agent

1) Verify Environment Variables

    Ensure the following variables are set.
```bash
echo "Project: $PROJECT_ID"
echo "Agent EngineLocation: $AGENT_ENGINE_LOCATION"
```

2. **Deploy Agent Engine Instance**

    Run the following code to deploy the Agent Engine instance with a dedicated identity.
```bash
# Deploy Agent Engine Stub
agent_engine_operation=$(curl -s -X POST \
    "https://$AGENT_ENGINE_LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$AGENT_ENGINE_LOCATION/reasoningEngines" \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "Content-Type: application/json; charset=utf-8" \
    --data @- <<EOF | jq -r .name
{
"displayName": 'Fact Checking Decision Auditor',
    "spec": {
    "agentFramework": "google-adk",
    "identityType": "AGENT_IDENTITY",
    }
}
EOF)

echo "Agent Engine Operation: $agent_engine_operation"

# Get Agent Name and Identity Reference
read -r agent_name agent_identity <<< $(curl -s -X GET \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "Content-Type: application/json; charset=utf-8" \
     "https://$AGENT_ENGINE_LOCATION-aiplatform.googleapis.com/v1/$agent_engine_operation" | jq -r ' .response.name, .response.spec.effectiveIdentity')

echo "Agent Identity: $agent_identity"
export AGENT_ENGINE_NAME=$agent_name

# Give Agent Identity Necessary Permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="principal://$agent_identity" \
    --role="roles/serviceusage.serviceUsageConsumer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="principal://$agent_identity" \
    --role="roles/aiplatform.user"
```

3. **Update Agent Engine Code**

    Run the python deployment script to update the Agent Engine instance with the agent code and final configuration.
```bash
python3 deploy.py
```
## Test Locally [Optional]

1. **Install Requirements**

    Ensure you have the necessary Python packages installed:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Start ADK**

    Start the ADK server below, navigate to http://localhost:8000, then select `auditor` from the list of agents.
```bash
adk web
```
