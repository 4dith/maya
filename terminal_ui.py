from gemini_client import invoke_gemini_client

while True:
    user_input = input(">>> ")

    if user_input.lower() == "exit":
        break

    stream = invoke_gemini_client(input_text=user_input)

    for event in stream:
        if event.event_type == "step.delta":
            if event.delta.type == "text":
                print(event.delta.text, end="", flush=True)

    print()