import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from .fake_calendar import list_events, create_event, cancel_event


from dotenv import load_dotenv
load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
llm = ChatOpenAI(
    model="openrouter/auto",  # Auto-selects best chat model
    temperature=0,
    openai_api_key=openrouter_api_key,
    openai_api_base="https://openrouter.ai/api/v1"
)

# === Tool Functions ===

def check_availability():
    events = list_events()
    if not events:
        return "No events scheduled. All slots are available."
    formatted = [f"{e['summary']} from {e['start']} to {e['end']} (id: {e['id']})" for e in events]
    return "Scheduled events:\n" + "\n".join(formatted)


def book_appointment():
    event = {
        "summary": "Sample Appointment",
        "start": "2025-07-09T10:00:00",
        "end": "2025-07-09T11:00:00"
    }
    created = create_event(event)
    return f"Appointment booked: {created['summary']} from {created['start']} to {created['end']} (id: {created['id']})"


def cancel_appointment():
    events = list_events()
    if not events:
        return "No events to cancel."
    event_id = events[0]['id']
    cancel_event(event_id)
    return f"Cancelled event with id {event_id}."


# === LangChain Tools ===
tools = [
    Tool(name="CheckAvailability", func=check_availability, description="Check calendar availability"),
    Tool(name="BookAppointment", func=book_appointment, description="Book a new appointment"),
    Tool(name="CancelAppointment", func=cancel_appointment, description="Cancel an appointment"),
]

# === Initialize LangChain Agent ===
from langchain.agents import AgentType

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent="zero-shot-react-description",
#     verbose=True
# )

# === Async Chat Handler ===
async def process_message(message: str) -> str:
    return agent.invoke({"input": message})
