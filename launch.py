"""
Launch script for AI Agent System
Provides multiple interface options: CLI, Web UI, or both
Now with easy model selection!
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from typing import Optional

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )

def check_requirements(skip_model_check: bool = False):
    """Check if essential requirements are met"""
    issues = []

    # Check config
    from config import get_config
    config = get_config()

    # Check if model exists (can be skipped if we'll select one)
    if not skip_model_check and not config.validate_model_exists():
        issues.append(f"Model file not found: {config.get('model', 'path')}")
        issues.append("Use --model to specify a model or --list-models to see available models")

    # Check essential packages
    try:
        import langchain
        import langgraph
    except ImportError as e:
        issues.append(f"Missing essential package: {e.name}")
        issues.append("Run: python install.py")

    return issues

def launch_cli(config_path: Optional[str] = None, model_path: Optional[str] = None):
    """Launch CLI interface"""
    print("=" * 60)
    print("🤖 AI Agent System - CLI Mode")
    print("=" * 60)

    try:
        from agent import AutonomousAgent

        print("📦 Initializing agent...")
        agent = AutonomousAgent(config_path, model_path)
        print("✅ Agent ready!")

        print("\nCommands:")
        print("  - Type your question or request")
        print("  - 'stats' - Show system statistics")
        print("  - 'history' - Show conversation history")
        print("  - 'clear' - Clear conversation history")
        print("  - 'quit' or 'exit' - Exit the program")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break

                if user_input.lower() == 'stats':
                    stats = agent.get_system_stats()
                    print("\n📊 System Statistics:")
                    print(json.dumps(stats, indent=2))
                    continue

                if user_input.lower() == 'history':
                    print("\n💬 Conversation History:")
                    for i, msg in enumerate(agent.conversation_history[-10:]):
                        role = msg['role'].capitalize()
                        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                        print(f"{i+1}. {role}: {content}")
                    continue

                if user_input.lower() == 'clear':
                    agent.conversation_history = []
                    print("✓ Conversation history cleared")
                    continue

                print("🤖 Agent: ", end="", flush=True)
                response = agent.process_input(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error("CLI error", exc_info=True)
        sys.exit(1)

def launch_web(config_path: Optional[str] = None, model_path: Optional[str] = None, share: bool = False):
    """Launch web interface"""
    print("=" * 60)
    print("🌐 AI Agent System - Web Mode")
    print("=" * 60)

    try:
        import gradio as gr
    except ImportError:
        print("❌ Gradio not installed")
        print("Install with: pip install gradio")
        sys.exit(1)

    try:
        from agent import AutonomousAgent
        from config import get_config

        config = get_config(config_path)

        print("📦 Initializing agent...")
        agent = AutonomousAgent(config_path, model_path)
        print("✅ Agent ready!")

        print("🌐 Starting web interface...")

        # Create Gradio interface
        with gr.Blocks(
            title="AI Agent System",
            theme=gr.themes.Soft()
        ) as interface:

            gr.Markdown("# 🤖 Autonomous AI Agent System")
            gr.Markdown("Powered by Local LLM | Tool Usage | Self-Learning Memory")

            with gr.Tab("💬 Chat"):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    type="messages",
                    height=500
                )
                with gr.Row():
                    msg = gr.Textbox(
                        label="Your message",
                        placeholder="Ask me anything...",
                        scale=4
                    )
                    submit = gr.Button("Send", scale=1, variant="primary")

                with gr.Row():
                    clear = gr.Button("Clear Chat")
                    retry = gr.Button("Retry Last")

                def respond(message, history):
                    if not message.strip():
                        return "", history

                    try:
                        response = agent.process_input(message)
                        history.append({"role": "user", "content": message})
                        history.append({"role": "assistant", "content": response})
                        return "", history
                    except Exception as e:
                        logging.error(f"Chat error: {e}")
                        history.append({"role": "user", "content": message})
                        history.append({"role": "assistant", "content": f"Error: {str(e)}"})
                        return "", history

                def retry_last(history):
                    if len(history) >= 2:
                        last_user_msg = history[-2]["content"]
                        history = history[:-2]
                        return respond(last_user_msg, history)[1]
                    return history

                msg.submit(respond, [msg, chatbot], [msg, chatbot])
                submit.click(respond, [msg, chatbot], [msg, chatbot])
                clear.click(lambda: [], None, chatbot)
                retry.click(retry_last, chatbot, chatbot)

            with gr.Tab("🛠️ Tools"):
                gr.Markdown("### Available Tools")

                with gr.Row():
                    refresh_tools_btn = gr.Button("Refresh Tool History")

                tool_list_display = gr.JSON(
                    value={
                        "available_tools": [tool.name for tool in agent.tools.tools],
                        "tool_descriptions": {
                            tool.name: tool.description
                            for tool in agent.tools.tools
                        }
                    },
                    label="Available Tools"
                )

                tool_history_display = gr.JSON(
                    value=agent.tools.tool_history[-20:] if agent.tools.tool_history else [],
                    label="Recent Tool Usage (Last 20)"
                )

                def refresh_tools():
                    return agent.tools.tool_history[-20:] if agent.tools.tool_history else []

                refresh_tools_btn.click(refresh_tools, None, tool_history_display)

            with gr.Tab("🧠 Memory"):
                gr.Markdown("### Memory System")

                with gr.Row():
                    search_query = gr.Textbox(
                        label="Search Memory",
                        placeholder="Enter search query..."
                    )
                    search_btn = gr.Button("Search", variant="primary")

                search_results = gr.JSON(label="Search Results")

                memory_stats = gr.JSON(
                    value=agent.memory.get_statistics(),
                    label="Memory Statistics"
                )

                refresh_memory_btn = gr.Button("Refresh Statistics")

                def search_memory(query):
                    if not query.strip():
                        return {"error": "Please enter a search query"}

                    try:
                        results = agent.memory.retrieve_relevant_memory(
                            query,
                            memory_type="learned_facts",
                            k=10
                        )
                        if not results:
                            return {"message": "No relevant memories found"}

                        return {
                            "query": query,
                            "results": [
                                {
                                    "content": r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
                                    "relevance": f"{(1 - r['distance']) * 100:.1f}%",
                                    "metadata": r["metadata"]
                                }
                                for r in results
                            ]
                        }
                    except Exception as e:
                        return {"error": str(e)}

                def refresh_memory_stats():
                    return agent.memory.get_statistics()

                search_btn.click(search_memory, search_query, search_results)
                search_query.submit(search_memory, search_query, search_results)
                refresh_memory_btn.click(refresh_memory_stats, None, memory_stats)

            with gr.Tab("📊 System"):
                gr.Markdown("### System Performance")

                system_stats_display = gr.JSON(
                    value=agent.get_system_stats(),
                    label="System Statistics"
                )

                with gr.Row():
                    refresh_stats_btn = gr.Button("Refresh Statistics")

                gr.Markdown("### Configuration")

                config_display = gr.JSON(
                    value={
                        "model": config.get('model'),
                        "security": config.get('security'),
                        "web": config.get('web')
                    },
                    label="Current Configuration"
                )

                def refresh_stats():
                    return agent.get_system_stats()

                refresh_stats_btn.click(refresh_stats, None, system_stats_display)

            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                ## Autonomous AI Agent System

                A powerful local AI agent with:

                - 🧠 **Self-Learning**: Learns from interactions and builds knowledge
                - 🛠️ **Tool Usage**: Web search, Wikipedia, file operations, and more
                - 💾 **Vector Memory**: Semantic search through past interactions
                - 🔒 **Security**: Sandboxed execution with configurable restrictions
                - 🚀 **Local**: Runs entirely on your machine using local LLM

                ### Features

                - **Chat Interface**: Natural conversation with the AI agent
                - **Tool Integration**: Automatic tool selection and usage
                - **Memory Search**: Query the agent's learned knowledge
                - **System Monitoring**: Real-time performance statistics

                ### Security Notes

                By default, system command execution and Python code execution are **disabled**.
                Enable these features in the configuration file only if you understand the risks.

                ### Configuration

                Configuration file: `~/AI_Agent_System/config.json`

                Edit this file to customize:
                - Model settings
                - Security restrictions
                - Tool behavior
                - Memory settings

                ---

                **Version**: 2.0
                **License**: MIT
                **Platform**: {platform}
                **Python**: {python_version}
                """.format(
                    platform=sys.platform,
                    python_version=sys.version.split()[0]
                ))

        # Launch
        host = config.get('web', 'host', default='127.0.0.1')
        port = config.get('web', 'port', default=7860)

        print(f"✅ Web interface ready!")
        print(f"🌐 Access at: http://{host}:{port}")
        if share:
            print("🔗 Public link will be generated...")
        print("=" * 60)

        interface.launch(
            server_name=host,
            server_port=port,
            share=share,
            show_error=True
        )

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error("Web interface error", exc_info=True)
        sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Agent System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py                                    # Interactive model selection + CLI
  python launch.py --web                              # Interactive model selection + Web
  python launch.py --model path/to/model.gguf         # Use specific model
  python launch.py --model llama                      # Use model matching 'llama'
  python launch.py --list-models                      # Show available models
  python launch.py --model-info                       # Show model download guide
  python launch.py --web --share                      # Web with public link
  python launch.py --config ~/custom_config.json      # Use custom config
        """
    )

    parser.add_argument(
        '--web',
        action='store_true',
        help='Launch web interface instead of CLI'
    )

    parser.add_argument(
        '--share',
        action='store_true',
        help='Create public share link for web interface'
    )

    parser.add_argument(
        '--model',
        type=str,
        help='Path to model file or model name to search for'
    )

    parser.add_argument(
        '--list-models',
        action='store_true',
        help='List all available models and exit'
    )

    parser.add_argument(
        '--model-info',
        action='store_true',
        help='Show model download information and exit'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Check requirements and exit'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Handle model-related commands
    from model_selector import ModelSelector, select_model_for_launch

    if args.list_models:
        selector = ModelSelector()
        selector.list_models(verbose=True)
        sys.exit(0)

    if args.model_info:
        selector = ModelSelector()
        selector.prompt_for_model_download()
        sys.exit(0)

    # Select model
    model_path = None
    if args.model or not args.check:
        print("\n🔍 Selecting model...")
        model_path = select_model_for_launch(
            model_arg=args.model,
            config_path=args.config,
            interactive=not args.check
        )

        if not model_path and not args.check:
            print("\n❌ No model selected. Exiting.")
            print("\n💡 Try:")
            print("   python launch.py --list-models     # See available models")
            print("   python launch.py --model-info      # Get download info")
            sys.exit(1)

    # Check requirements (skip model check since we selected one)
    issues = check_requirements(skip_model_check=bool(model_path))
    if issues:
        print("\n⚠️  Issues detected:")
        for issue in issues:
            print(f"  - {issue}")

        if args.check:
            sys.exit(1)

        if not model_path:  # Only ask if we don't have a model
            response = input("\nContinue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Aborting.")
                sys.exit(1)
        print()

    if args.check:
        print("✅ All requirements met!")
        sys.exit(0)

    # Launch appropriate interface
    try:
        if args.web:
            launch_web(args.config, model_path, args.share)
        else:
            launch_cli(args.config, model_path)

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
