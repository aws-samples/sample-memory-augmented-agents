"""
Summarizing Memory Agent - Intelligent Context Compression

Demonstrates how to use summarization to preserve important context
when the conversation grows too long. Instead of dropping old messages,
the agent summarizes them to retain key information.

Prerequisites:
    pip install -r requirements.txt

Learning objectives:
- Understand summarization-based memory management
- See how context is compressed without losing key information
- Compare summarization vs sliding window approaches
"""

import time
from shared.model import get_model
from shared.input_utils import get_multiline_input
from shared.streaming import StreamingCallbackHandler
from strands import Agent
from strands.agent.conversation_manager.summarizing_conversation_manager import (
    SummarizingConversationManager,
)


SYSTEM_PROMPT = """You are a helpful assistant with intelligent memory management.

When our conversation gets long, older messages are automatically summarized
to preserve the key points while staying within context limits. This means
you can remember important facts from earlier in the conversation even after
many exchanges.

Be conversational, reference earlier context when relevant, and let the user
know if you're working from a summary rather than exact recall."""


def main():
    """Run the summarizing memory agent."""
    print("Summarizing Memory Agent")
    print("=" * 40)
    print("This agent summarizes older messages instead of dropping them.")
    print("Key facts are preserved even as the conversation grows long.")
    print("Type 'quit' to exit")
    print("Tip: You can paste multi-line prompts!\n")

    print("Example prompts to try:")
    print("  - My name is Jordan. I'm a data engineer at a fintech company.")
    print("  - We're migrating from Spark to Flink for real-time processing.")
    print("  - Our biggest challenge is exactly-once semantics.")
    print("  - (After many messages) Summarize what you know about my project.\n")

    # Create agent with summarizing conversation manager
    # - summary_ratio: 0.3 means summarize when 30% of context is used
    # - preserve_recent_messages: keep the last 10 messages verbatim
    # Streaming handler so each response shows up as the model generates it.
    stream_handler = StreamingCallbackHandler()
    agent = Agent(
        model=get_model(),
        system_prompt=SYSTEM_PROMPT,
        conversation_manager=SummarizingConversationManager(
            summary_ratio=0.3,
            preserve_recent_messages=10,
        ),
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
