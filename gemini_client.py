from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

previous_interaction_id = None

def invoke_gemini_client(input_text):
    global previous_interaction_id

    stream = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=input_text,
        previous_interaction_id=previous_interaction_id,
        stream=True
    )

    for event in stream:
        if event.event_type == "interaction.created":
            previous_interaction_id = event.interaction.id
            break

    return stream

