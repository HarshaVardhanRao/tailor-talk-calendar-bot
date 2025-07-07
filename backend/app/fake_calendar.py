# Simulated in-memory calendar for development/testing

_fake_events = [
    {"id": 1, "summary": "Team Meeting", "start": "2025-07-08T10:00:00", "end": "2025-07-08T11:00:00"},
    {"id": 2, "summary": "Doctor Appointment", "start": "2025-07-08T14:00:00", "end": "2025-07-08T15:00:00"},
]

_next_id = 3

def list_events():
    return list(_fake_events)

def create_event(event):
    global _next_id
    event["id"] = _next_id
    _next_id += 1
    _fake_events.append(event)
    return event

def cancel_event(event_id):
    global _fake_events
    _fake_events = [e for e in _fake_events if e["id"] != event_id]
    return True
