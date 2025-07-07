import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.tools import StructuredTool
from .fake_calendar import list_events, create_event, cancel_event

# Load Together API Key (recommended to use environment variable)
together_api_key ="5ab86d3cfb9631ebc27ec689f01b25a6cbedeb45f8f579247862f7941e92d735" # Replace with actual or use .env

# Initialize Chat LLM from Together.ai
llm = ChatOpenAI(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0,
    openai_api_key=together_api_key,
    openai_api_base="https://api.together.xyz/v1"
)

# === Tool Functions ===


# Accept **kwargs to support tool calling with arguments
def check_availability(date: str = None, time_range: str = None, **kwargs):
    events = list_events()
    if not events:
        return "No events scheduled. All slots are available."
    filtered = events
    # Optionally filter by date or time_range if provided
    if date:
        filtered = [e for e in filtered if date in e['start']]
    # (You can add more sophisticated time_range filtering here)
    formatted = [f"{e['summary']} from {e['start']} to {e['end']} (id: {e['id']})" for e in filtered]
    return "Scheduled events:\n" + "\n".join(formatted) if formatted else "No events found for the specified criteria."



def book_appointment(summary: str = "Sample Appointment", start: str = "2025-07-09T10:00:00", end: str = "2025-07-09T11:00:00", **kwargs):
    event = {
        "summary": summary,
        "start": start,
        "end": end
    }
    created = create_event(event)
    return f"Appointment booked: {created['summary']} from {created['start']} to {created['end']} (id: {created['id']})"



def cancel_appointment(**kwargs):
    events = list_events()
    if not events:
        return "No events to cancel."
    event_id = events[0]['id']
    cancel_event(event_id)
    return f"Cancelled event with id {event_id}."


# === Tools for Agent ===
tools = [
    StructuredTool.from_function(
        check_availability,
        name="CheckAvailability",
        description="Check calendar availability. Accepts optional 'date' and 'time_range' arguments.",
    ),
    StructuredTool.from_function(
        book_appointment,
        name="BookAppointment",
        description="Book a new appointment. Accepts optional details as arguments.",
    ),
    StructuredTool.from_function(
        cancel_appointment,
        name="CancelAppointment",
        description="Cancel an appointment. Accepts optional details as arguments.",
    ),
]

# === LangChain Agent Setup ===
from langchain.agents import AgentType

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# === Async handler used by FastAPI endpoint ===
async def process_message(message: str) -> str:
    result = agent.invoke({"input": message})
    # If result is a dict (as with function-calling agents), extract the output string
    if isinstance(result, dict) and "output" in result:
        return result["output"]
    return str(result)
