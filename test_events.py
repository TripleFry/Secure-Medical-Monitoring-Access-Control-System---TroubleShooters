from event_engine import EventEngine
import time

engine = EventEngine()

events = [
    "authorized",
    "intruder",
    "fall",
    "abnormal_vitals"
]

for event in events:
    state = engine.process_event(event)
    print("Current State:", state)
    print("----------------------")
    time.sleep(2)
