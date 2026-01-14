from vertexai.preview.reasoning_engines import AdkApp
from google.adk.agents import LlmAgent,SequentialAgent

from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent

llm_agent = SequentialAgent(
    name='llm_auditor',
    description=(
        'Evaluates LLM-generated answers, verifies actual accuracy using the'
        ' web, and refines the response to ensure alignment with real-world'
        ' knowledge.'
    ),
    sub_agents=[critic_agent, reviser_agent],
)

root_agent = llm_agent
