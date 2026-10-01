"""
Persistent Session Agent - Cross-Session Memory

Demonstrates how to persist conversation state across sessions using
Strands' FileSessionManager. The agent remembers previous conversations
even after the script is restarted.

Prerequisites:
    pip install -r requirements.txt

Learning objectives:
- Understand session persistence for long-term memory
- See how to save and restore conversation state
- Learn the difference between in-memory and persistent sessions
"""

import sys
import time
import uuid
from pathlib import Path
from shared.model import get_model
from shared.input_utils import get_multiline_input
from shared.streaming import StreamingCallbackHandler
from strands import Agent
from strands.session.file_session_manager import FileSessionManager


SYSTEM_PROMPT = """You are a personal assistant with persistent memory.

You remember everything from previous conversations with this user.
When the user returns, greet them and reference what you discussed before.
If this is a new conversation, introduce yourself and ask how you can help.

Be warm, personalized, and reference prior context when relevant."""


# Pin session storage to this lab's folder regardless of where the script was
# launched from, so the state lands where the README and .gitignore expect it.
SESSION_DIR = str(Path(__file__).resolve().parent / ".sessions")


def main():
    """Run the persistent session agent."""
    print("Persistent Session Agent")
    print("=" * 40)
    print("This agent remembers conversations across restarts.")
    print(f"Sessions stored in: {SESSION_DIR}/")
    print("Type 'quit' to exit | 'new' for a fresh session")
    print("Tip: You can paste multi-line prompts!\n")

    print("Example prompts to try:")
    print("  - Hi, I'm Sam. I'm working on a machine learning project.")
    print("  - (quit and restart) Do you remember me?")
    print("  - What were we talking about last time?\n")

    # Ask for session ID or generate one
    session_input = get_multiline_input("Enter session ID (or press Enter for default): ").strip()
    session_id = session_input if session_input else "default-user"

    # Initialize session manager with file-based persistence
    print(f"\n    ⟳ Loading session '{session_id}'...")
    init_start = time.time()
    session_manager = FileSessionManager(
        session_id=session_id,
        storage_dir=SESSION_DIR,
    )

    # Streaming handler so each response streams as the model generates it.
    stream_handler = StreamingCallbackHandler()

    agent = Agent(
        model=get_model(),
        system_prompt=SYSTEM_PROMPT,
        session_manager=session_manager,
        callback_handler=stream_handler,
    )
    duration = time.time() - init_start
    sys.stdout.write("\033[1A")
    sys.stdout.write(f"\r    ✓ Session loaded ({duration:.1f}s)\033[K\n\n")
    sys.stdout.flush()

    while True:
        user_input = get_multiline_input("You: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Session saved. Goodbye!")
            break

        if user_input.lower() == "new":
            new_id = f"session-{uuid.uuid4().hex[:8]}"
            session_manager = FileSessionManager(
                session_id=new_id,
                storage_dir=SESSION_DIR,
            )
            agent = Agent(
                model=get_model(),
                system_prompt=SYSTEM_PROMPT,
                session_manager=session_manager,
                callback_handler=stream_handler,
            )
            print(f"Started new session: {new_id}\n")
            continue

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
