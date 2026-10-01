"""
Sliding Window Memory Agent - Context Window Management

Demonstrates how to manage conversation history using a sliding window
that keeps the most recent messages and drops older ones.

Prerequisites:
    pip install -r requirements.txt

Learning objectives:
- Understand short-term memory via conversation management
- See how sliding window prevents context overflow
- Learn when to use window-based vs summarization-based memory
"""

import time
from shared.model import get_model
from shared.input_utils import get_multiline_input
from shared.streaming import StreamingCallbackHandler
from strands import Agent
from strands.agent.conversation_manager.sliding_window_conversation_manager import (
    SlidingWindowConversationManager,
)


SYSTEM_PROMPT = """You are a helpful assistant with a limited memory window.

You can only remember the most recent messages in our conversation.
If the user asks about something from earlier that you can't recall,
let them know honestly that it's outside your memory window.

Be conversational and helpful within the context you have available."""


def main():
    """Run the sliding window memory agent."""
    print("Sliding Window Memory Agent")
    print("=" * 40)
    print("This agent keeps only the last 10 messages in memory.")
    print("Older messages are dropped to stay within context limits.")
    print("Type 'quit' to exit")
    print("Tip: You can paste multi-line prompts!\n")

    print("Example prompts to try:")
    print("  - My name is Alex and I work at a startup")
    print("  - I'm building a recommendation engine")
    print("  - What do you remember about me?")
    print("  - (After many messages) Do you still remember my name?\n")

    # Create agent with sliding window — keeps last 10 message pairs.
    # Streaming handler so each response shows up as the model generates it.
    stream_handler = StreamingCallbackHandler()
    agent = Agent(
        model=get_model(),
        system_prompt=SYSTEM_PROMPT,
        conversation_manager=SlidingWindowConversationManager(window_size=10),
        callback_handler=stream_handler,
    )

    while True:
        user_input = get_multiline_input("You: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            stream_handler.reset()
            print("\nAgent: ", end="", flush=True)
            start_time = time.time()
            agent(user_input)
            elapsed = time.time() - start_time
            print(f"\n({elapsed:.1f}s)\n")
        except Exception as e:
            # NOTE: shows the error on the local console to aid debugging. A
            # production service should show users a generic message and log
            # sanitized error details separately.
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
