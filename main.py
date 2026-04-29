"""
main.py — Entry Point for NeuroCare AI

CLI modes:
    python main.py --ingest     # Process documents → build FAISS index
    python main.py --chat       # Run chatbot in terminal (for testing)
    python main.py --server     # Start FastAPI server at localhost:5001
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        prog='NeuroCare AI',
        description='Agentic RAG Chatbot for Dementia Care',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ingest              # Build FAISS index from documents
  python main.py --chat                # Test chatbot in terminal
  python main.py --server              # Start FastAPI server
  python main.py --server --host 0.0.0.0 --port 8000  # Custom host/port
        """
    )
    
    # Main mode arguments
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--ingest',
        action='store_true',
        help='Process documents and build FAISS vector index'
    )
    mode_group.add_argument(
        '--chat',
        action='store_true',
        help='Run chatbot in terminal mode (for testing)'
    )
    mode_group.add_argument(
        '--server',
        action='store_true',
        help='Start FastAPI server for React frontend'
    )
    
    # Optional arguments for server mode
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Server host (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Server port (default: 5001)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the selected mode
    try:
        if args.ingest:
            _mode_ingest()
        elif args.chat:
            _mode_chat()
        elif args.server:
            _mode_server(args.host, args.port)
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _mode_ingest():
    """Ingestion mode: Process documents and build FAISS index."""
    print("\n🔄 Entering INGEST mode...\n")
    from ingestion import main as ingest_main
    ingest_main()


def _mode_chat():
    """Chat mode: Run chatbot in terminal with conversation memory."""
    print("\n🔄 Entering CHAT mode...\n")
    print("=" * 70)
    print("🧠 NeuroCare AI Chatbot — Terminal Mode (with Conversation Memory)")
    print("=" * 70)
    print("Type 'exit' or 'quit' to end conversation")
    print("Type 'help' for information")
    print("Type 'clear' to clear conversation history")
    print("=" * 70 + "\n")
    
    try:
        from chatbot import ChatHandler
        
        # Initialize chatbot
        print("⏳ Initializing chatbot...")
        chatbot = ChatHandler()
        print("✓ Chatbot ready!\n")
        
        # Create a new session for this conversation
        session_id = chatbot.create_session()
        print(f"📌 Session ID: {session_id}\n")
        print("=" * 70 + "\n")
        
        # Chat loop
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == 'clear':
                    chatbot.clear_session(session_id)
                    print("🧹 Conversation history cleared.\n")
                    continue
                
                if user_input.lower() == 'help':
                    print("""
Commands:
  exit / quit   - End conversation
  clear         - Clear conversation history
  help          - Show this message
  
Ask any dementia-related question and the chatbot will respond
with relevant information. The chatbot remembers previous questions
in this session for context-aware answers!
                    """)
                    continue
                
                # Get response from chatbot with session context
                print("\n⏳ Thinking...\n")
                response = chatbot.chat(user_input, session_id=session_id)
                
                # Show spell corrections if any
                corrected_question = response.get('corrected_question', '').strip()
                if corrected_question and corrected_question.lower() != user_input.lower():
                    print(f"✏️  (Corrected: '{corrected_question}')\n")
                
                print(f"Bot: {response['reply']}\n")
                
                # Show if context from history was used
                if response.get('has_context'):
                    print("📝 (Using context from conversation history)")
                
                if response['references']:
                    print("📚 Sources:")
                    for ref in response['references']:
                        print(f"  - {ref['source']} (Page {ref.get('page', 'N/A')})")
                
                print(f"\n💭 Tone detected: {response['tone_detected']}")
                if response['used_web_search']:
                    print("🌐 (Web search was used to supplement answers)")
                
                # Show conversation turn count
                turn = response.get('turn_number', 0)
                print(f"📊 (Turn #{turn} in this session)")
                
                print("-" * 70 + "\n")
                
            except KeyboardInterrupt:
                break
    
    except ImportError:
        print("✗ ChatHandler not available yet. Run Phase 3-4 first.")
        sys.exit(1)


def _mode_server(host: str, port: int):
    """Server mode: Start FastAPI server."""
    print("\n🔄 Entering SERVER mode...\n")
    print("=" * 60)
    print("🧠 NeuroCare AI — FastAPI Server")
    print("=" * 60)
    print(f"Starting server at http://{host}:{port}")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    try:
        import uvicorn
        from server import app  # FastAPI app
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
    
    except ImportError:
        print("✗ Server not available yet. Run Phase 4-5 first.")
        sys.exit(1)


if __name__ == "__main__":
    main()
