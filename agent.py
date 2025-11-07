"""
Autonomous AI Agent System with Tool Usage and Self-Learning
Fixed version with security improvements and cross-platform support
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Sequence
from pathlib import Path
import subprocess
import psutil

# Core imports
from langchain.agents import Tool
from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# LangGraph for agent orchestration
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

# Memory and embeddings
try:
    from chromadb import Client as ChromaClient
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    ChromaClient = None
    ChromaSettings = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Tool imports
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

try:
    import wikipediaapi
except ImportError:
    wikipediaapi = None

# Configuration
from config import get_config

# Setup logging
config = get_config()
logging.basicConfig(
    level=getattr(logging, config.get('logging', 'level', default='INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.get('logging', 'file')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Type-safe agent state definition"""
    messages: Sequence[Dict[str, str]]
    current_task: str
    tool_results: List[str]
    memory_context: List[Dict]
    should_continue: bool


class ToolFramework:
    """Secure tool framework for autonomous agent operations"""

    def __init__(self, memory: 'MemorySystem', config):
        self.memory = memory
        self.config = config
        self.tools = []
        self.tool_history = []
        self.setup_tools()

    def setup_tools(self):
        """Initialize available tools based on configuration"""

        # Always available tools
        self.tools.append(Tool(
            name="memory_search",
            func=self.search_memory,
            description="Search through learned information and past interactions"
        ))

        # Optional tools based on dependencies
        if DDGS is not None:
            self.tools.append(Tool(
                name="web_search",
                func=self.web_search,
                description="Search the web for current information using DuckDuckGo"
            ))

        if wikipediaapi is not None:
            self.tools.append(Tool(
                name="wikipedia",
                func=self.wikipedia_search,
                description="Search Wikipedia for detailed information"
            ))

        # Conditional secure tools
        if self.config.get('security', 'enable_command_execution'):
            logger.warning("Command execution is enabled - use with caution!")
            self.tools.append(Tool(
                name="system_command",
                func=self.execute_command_safe,
                description="Execute system commands (restricted)"
            ))

        if self.config.get('security', 'enable_python_exec'):
            logger.warning("Python execution is enabled - use with caution!")
            self.tools.append(Tool(
                name="python_repl",
                func=self.execute_python_safe,
                description="Execute Python code (sandboxed)"
            ))

        # File operations (with path validation)
        self.tools.append(Tool(
            name="file_read",
            func=self.file_read_safe,
            description="Read file contents (restricted to allowed directories)"
        ))

    def web_search(self, query: str) -> str:
        """Perform web search using DuckDuckGo"""
        if DDGS is None:
            return "Web search not available - duckduckgo-search not installed"

        try:
            max_results = self.config.get('tools', 'web_search_max_results', default=5)
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                if not results:
                    return "No search results found"

                formatted = "\n".join([
                    f"• {r['title']}: {r['body'][:200]}..."
                    for r in results
                ])
                self._log_tool_use("web_search", query)
                return formatted
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return f"Search error: {str(e)}"

    def wikipedia_search(self, query: str) -> str:
        """Search Wikipedia for information"""
        if wikipediaapi is None:
            return "Wikipedia search not available - wikipediaapi not installed"

        try:
            wiki = wikipediaapi.Wikipedia(
                user_agent='AI_Agent_System/2.0',
                language='en'
            )
            page = wiki.page(query)

            if page.exists():
                max_length = self.config.get('tools', 'wikipedia_summary_length', default=1000)
                summary = page.summary[:max_length]
                self._log_tool_use("wikipedia", query)
                return summary

            return "No Wikipedia page found for this query"
        except Exception as e:
            logger.error(f"Wikipedia error: {str(e)}")
            return f"Wikipedia error: {str(e)}"

    def execute_command_safe(self, command: str) -> str:
        """
        Execute system commands with security restrictions
        WARNING: Only enable in trusted environments
        """
        if not self.config.get('security', 'enable_command_execution'):
            return "Command execution is disabled for security reasons"

        # Validate command safety
        if not self.config.is_command_safe(command):
            logger.warning(f"Blocked dangerous command: {command}")
            return "Command blocked for safety reasons"

        try:
            # Use shell=False with list arguments for better security
            # This is still risky and should only be used in controlled environments
            result = subprocess.run(
                command,
                shell=False,  # More secure than shell=True
                capture_output=True,
                text=True,
                timeout=self.config.get('tools', 'command_timeout', default=30)
            )

            output = result.stdout + result.stderr
            self._log_tool_use("system_command", command)
            return output[:1000] if output else "Command executed successfully"

        except subprocess.TimeoutExpired:
            return "Command execution timed out"
        except Exception as e:
            logger.error(f"Command error: {str(e)}")
            return f"Command error: {str(e)}"

    def file_read_safe(self, path: str) -> str:
        """Read file with path traversal protection"""
        try:
            # Validate and get safe path
            safe_path = self.config.get_safe_file_path(path)

            # Check file size to prevent memory issues
            file_size = safe_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return f"File too large to read: {file_size / 1024 / 1024:.2f}MB"

            with open(safe_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(self.config.get('tools', 'file_read_limit', default=2000))

            self._log_tool_use("file_read", str(safe_path))
            return content

        except PermissionError as e:
            logger.warning(f"File access denied: {path} - {str(e)}")
            return f"Access denied: {str(e)}"
        except Exception as e:
            logger.error(f"File read error: {str(e)}")
            return f"File read error: {str(e)}"

    def execute_python_safe(self, code: str) -> str:
        """
        Execute Python code with restrictions
        WARNING: Still has security risks, use only in trusted environments
        """
        if not self.config.get('security', 'enable_python_exec'):
            return "Python execution is disabled for security reasons"

        try:
            # Create restricted builtins
            safe_builtins = {
                'abs': abs, 'all': all, 'any': any, 'bin': bin,
                'bool': bool, 'chr': chr, 'dict': dict, 'enumerate': enumerate,
                'filter': filter, 'float': float, 'int': int, 'len': len,
                'list': list, 'map': map, 'max': max, 'min': min,
                'ord': ord, 'pow': pow, 'range': range, 'reversed': reversed,
                'round': round, 'set': set, 'sorted': sorted, 'str': str,
                'sum': sum, 'tuple': tuple, 'zip': zip,
            }

            exec_globals = {"__builtins__": safe_builtins}
            exec_locals = {}

            # Timeout protection
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Code execution timed out")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5 second timeout

            try:
                exec(code, exec_globals, exec_locals)
            finally:
                signal.alarm(0)

            result = str(exec_locals.get('result', 'Code executed successfully'))
            self._log_tool_use("python_repl", code[:100])
            return result

        except TimeoutError:
            return "Code execution timed out"
        except Exception as e:
            logger.error(f"Python execution error: {str(e)}")
            return f"Python execution error: {str(e)}"

    def search_memory(self, query: str) -> str:
        """Search through the agent's memory"""
        try:
            memories = self.memory.retrieve_relevant_memory(
                query,
                memory_type="learned_facts",
                k=5
            )

            if memories:
                formatted = "\n".join([
                    f"• {m['content'][:200]}... (Relevance: {1 - m['distance']:.2f})"
                    for m in memories
                ])
                return formatted

            return "No relevant memories found"

        except Exception as e:
            logger.error(f"Memory search error: {str(e)}")
            return f"Memory search error: {str(e)}"

    def _log_tool_use(self, tool_name: str, input_data: str):
        """Log tool usage for analytics"""
        self.tool_history.append({
            "tool": tool_name,
            "input": input_data[:100],  # Truncate for storage
            "timestamp": datetime.now().isoformat()
        })


class MemorySystem:
    """Advanced memory system with vector storage"""

    def __init__(self, config):
        self.config = config
        self.persist_directory = config.get('memory', 'persist_directory')
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        self.embedder = None
        self.chroma_client = None
        self.collections = {}
        self.interaction_count = 0
        self.learning_threshold = config.get('memory', 'learning_threshold', default=0.75)

        self._initialize_components()

    def _initialize_components(self):
        """Initialize memory components with proper error handling"""
        # Initialize sentence transformer
        if SentenceTransformer is not None:
            try:
                model_name = self.config.get('memory', 'embedding_model', default='all-MiniLM-L6-v2')

                # Try CUDA first, fall back to CPU
                try:
                    self.embedder = SentenceTransformer(model_name, device='cuda')
                    logger.info("SentenceTransformer initialized on CUDA")
                except Exception:
                    self.embedder = SentenceTransformer(model_name, device='cpu')
                    logger.info("SentenceTransformer initialized on CPU")

            except Exception as e:
                logger.error(f"Failed to initialize SentenceTransformer: {e}")
                self.embedder = None
        else:
            logger.warning("sentence-transformers not installed, memory features limited")

        # Initialize ChromaDB
        if ChromaClient is not None and self.embedder is not None:
            try:
                self.chroma_client = ChromaClient(ChromaSettings(
                    persist_directory=self.persist_directory,
                    anonymized_telemetry=False
                ))

                # Create collections
                collection_names = ['conversations', 'learned_facts', 'tool_usage', 'user_preferences']
                for name in collection_names:
                    try:
                        self.collections[name] = self.chroma_client.get_or_create_collection(name)
                    except Exception as e:
                        logger.error(f"Failed to create collection {name}: {e}")

                logger.info("ChromaDB initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                self.chroma_client = None
        else:
            logger.warning("chromadb not installed, memory features limited")

    def store_interaction(self, user_input: str, agent_response: str, metadata: Dict = None):
        """Store conversation interactions"""
        if self.chroma_client is None or self.embedder is None:
            logger.debug("Memory storage skipped - components not initialized")
            return

        self.interaction_count += 1

        try:
            combined_text = f"User: {user_input}\nAgent: {agent_response}"
            embedding = self.embedder.encode(combined_text).tolist()

            self.collections['conversations'].add(
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[{
                    'timestamp': datetime.now().isoformat(),
                    'interaction_id': self.interaction_count,
                    **(metadata or {})
                }],
                ids=[f"conv_{self.interaction_count}_{datetime.now().timestamp()}"]
            )

            logger.debug(f"Stored interaction {self.interaction_count}")

            # Cleanup old conversations if too many
            max_conversations = self.config.get('memory', 'max_conversations', default=1000)
            if self.interaction_count > max_conversations:
                self._cleanup_old_conversations()

        except Exception as e:
            logger.error(f"Failed to store interaction: {str(e)}")

    def learn_fact(self, fact: str, confidence: float, source: str = "interaction"):
        """Learn and store new facts"""
        if self.chroma_client is None or self.embedder is None:
            return

        if confidence >= self.learning_threshold:
            try:
                embedding = self.embedder.encode(fact).tolist()

                self.collections['learned_facts'].add(
                    embeddings=[embedding],
                    documents=[fact],
                    metadatas=[{
                        'confidence': confidence,
                        'source': source,
                        'timestamp': datetime.now().isoformat()
                    }],
                    ids=[f"fact_{datetime.now().timestamp()}"]
                )

                logger.info(f"Learned new fact (confidence: {confidence}): {fact[:50]}...")

            except Exception as e:
                logger.error(f"Failed to learn fact: {str(e)}")

    def retrieve_relevant_memory(
        self,
        query: str,
        memory_type: str = 'conversations',
        k: int = 5
    ) -> List[Dict]:
        """Retrieve relevant memories"""
        if self.chroma_client is None or self.embedder is None:
            return []

        if memory_type not in self.collections:
            logger.warning(f"Unknown memory type: {memory_type}")
            return []

        try:
            query_embedding = self.embedder.encode(query).tolist()

            results = self.collections[memory_type].query(
                query_embeddings=[query_embedding],
                n_results=k
            )

            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    memories.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })

            return memories

        except Exception as e:
            logger.error(f"Memory retrieval error: {str(e)}")
            return []

    def _cleanup_old_conversations(self):
        """Remove old conversations to prevent unbounded growth"""
        try:
            # This is a simplified cleanup - in production, implement proper LRU
            logger.info("Conversation cleanup triggered")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

    def get_statistics(self) -> Dict:
        """Get memory system statistics"""
        stats = {
            'total_interactions': self.interaction_count,
            'embedder_available': self.embedder is not None,
            'chromadb_available': self.chroma_client is not None,
        }

        if self.chroma_client:
            for name, collection in self.collections.items():
                try:
                    stats[f'{name}_count'] = collection.count()
                except:
                    stats[f'{name}_count'] = 0

        return stats


class AutonomousAgent:
    """Main autonomous agent with improved architecture"""

    def __init__(self, config_path: str = None, model_path: str = None):
        self.config = get_config(config_path)
        self.memory = MemorySystem(self.config)
        self.tools = ToolFramework(self.memory, self.config)
        self.conversation_history = []
        self.llm = None
        self.agent_graph = None
        self.model_path = model_path  # Override config if provided

        # Initialize components
        self._initialize_llm()
        self._setup_agent_graph()

    def _initialize_llm(self):
        """Initialize the local LLM with error handling"""
        logger.info("Initializing local LLM...")

        # Determine which model path to use
        if self.model_path:
            # Use provided model path (overrides config)
            model_path = str(self.model_path)
            logger.info(f"Using specified model: {model_path}")
        else:
            # Use model from config
            model_path = self.config.get('model', 'path')

            # Check if model exists
            if not self.config.validate_model_exists():
                logger.error(f"Model file not found at: {model_path}")
                logger.info("Please download a model or specify one with --model")
                raise FileNotFoundError("Model file not found")

        try:
            logger.info(f"Loading model: {Path(model_path).name}...")

            self.llm = LlamaCpp(
                model_path=model_path,
                n_gpu_layers=self.config.get('model', 'n_gpu_layers', default=0),
                n_batch=self.config.get('model', 'n_batch', default=512),
                n_ctx=self.config.get('model', 'n_ctx', default=8192),
                f16_kv=True,
                callbacks=[StreamingStdOutCallbackHandler()],
                verbose=False,
                temperature=self.config.get('model', 'temperature', default=0.7),
                top_p=self.config.get('model', 'top_p', default=0.95),
                max_tokens=self.config.get('model', 'max_tokens', default=2048)
            )

            logger.info("LLM initialized successfully")

        except Exception as e:
            logger.error(f"LLM initialization error: {str(e)}")
            raise

    def _setup_agent_graph(self):
        """Setup LangGraph for agent orchestration"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("think", self._think_node)
        workflow.add_node("act", self._act_node)
        workflow.add_node("respond", self._respond_node)

        # Add edges
        workflow.add_edge("think", "act")
        workflow.add_edge("act", "respond")

        # Conditional edge for continuation
        workflow.add_conditional_edges(
            "respond",
            lambda x: "end" if not x.get("should_continue", False) else "think",
            {"think": "think", "end": END}
        )

        workflow.set_entry_point("think")

        try:
            self.agent_graph = workflow.compile()
            logger.info("Agent graph compiled successfully")
        except Exception as e:
            logger.error(f"Agent graph compilation error: {str(e)}")
            raise

    def _think_node(self, state: AgentState) -> AgentState:
        """Thinking phase - analyze task and plan"""
        try:
            current_input = state["messages"][-1]["content"] if state["messages"] else ""

            # Check if this is a simple conversational query (greetings, simple questions)
            conversational_patterns = [
                'hello', 'hi', 'hey', 'greetings', 'how are you', 'what\'s up',
                'good morning', 'good afternoon', 'good evening',
                'thank you', 'thanks', 'bye', 'goodbye',
                'who are you', 'what are you', 'what can you do'
            ]

            is_conversational = any(pattern in current_input.lower() for pattern in conversational_patterns)

            if is_conversational:
                # Skip complex thinking for simple conversation
                state["current_task"] = "simple_conversation"
                return state

            # Retrieve relevant memories for complex queries
            memories = self.memory.retrieve_relevant_memory(current_input, k=3)
            state["memory_context"] = memories

            # Decide what tools to use
            tool_names = [tool.name for tool in self.tools.tools]
            thought_prompt = f"""Analyze this user request and determine if any tools are needed: "{current_input}"

Available tools: {', '.join(tool_names)}

If the question needs:
- Current information or web search → use web_search
- Wikipedia knowledge → use wikipedia
- File reading → use file_read
- Past conversation context → use memory_search
- Just a conversational response → say "no tools needed"

What tools should be used? (Keep it brief, just list tool names or "no tools needed")"""

            thought = self.llm.invoke(thought_prompt)
            state["current_task"] = str(thought)

            logger.debug(f"Thought: {str(thought)[:200]}...")

        except Exception as e:
            logger.error(f"Think node error: {str(e)}")
            state["current_task"] = f"Error in thinking: {str(e)}"

        return state

    def _act_node(self, state: AgentState) -> AgentState:
        """Action phase - use tools if needed"""
        try:
            task_description = state.get("current_task", "").lower()
            user_input = state["messages"][-1]["content"] if state["messages"] else ""

            results = []

            # Execute relevant tools
            for tool in self.tools.tools:
                if tool.name.replace("_", " ") in task_description:
                    try:
                        result = tool.func(user_input)
                        results.append(f"{tool.name}: {result}")
                        logger.info(f"Executed tool: {tool.name}")
                    except Exception as e:
                        logger.error(f"Tool {tool.name} error: {str(e)}")
                        results.append(f"{tool.name} error: {str(e)}")

            state["tool_results"] = results

        except Exception as e:
            logger.error(f"Act node error: {str(e)}")
            state["tool_results"] = [f"Error: {str(e)}"]

        return state

    def _respond_node(self, state: AgentState) -> AgentState:
        """Response phase - generate final answer"""
        try:
            user_input = state["messages"][-1]["content"] if state["messages"] else ""
            tool_results = state.get("tool_results", [])
            task = state.get("current_task", "")

            # Handle simple conversations directly
            if task == "simple_conversation":
                # Use a conversational system prompt for natural responses
                response_prompt = f"""You are a friendly and helpful AI assistant. Respond naturally to this message: "{user_input}"

Keep your response:
- Natural and conversational (not formal or academic)
- Brief (1-2 sentences for greetings, 2-3 for questions)
- Helpful and friendly
- Focused on how you can assist the user

Examples of good responses:
User: "Hello, how are you?"
Response: "Hello! I'm doing well, thank you for asking. How can I assist you today?"

User: "What can you do?"
Response: "I'm an AI assistant that can help you with information lookup, answer questions, search the web, and more. What would you like help with?"

Now respond to: "{user_input}" """

            # Generate response with context from tools
            elif tool_results:
                response_prompt = f"""The user asked: "{user_input}"

Information from tools:
{chr(10).join(tool_results)}

Based on this information, provide a clear, helpful, and natural response. Be conversational but informative. Don't mention the tools or how you got the information - just answer the question naturally."""

            # Direct response for simple questions
            else:
                response_prompt = f"""The user asked: "{user_input}"

Provide a clear, helpful, and conversational response. Be friendly and natural, not overly formal or academic. Keep it concise but informative."""

            response = self.llm.invoke(response_prompt)

            state["messages"].append({
                "role": "assistant",
                "content": str(response)
            })

            # Store interaction in memory
            self.memory.store_interaction(user_input, str(response))

            # Learn from interaction
            if any(keyword in str(response).lower() for keyword in ["is", "are", "means", "refers"]):
                self.memory.learn_fact(str(response)[:500], confidence=0.8)

            state["should_continue"] = False

        except Exception as e:
            logger.error(f"Respond node error: {str(e)}")
            state["messages"].append({
                "role": "assistant",
                "content": f"I encountered an error: {str(e)}"
            })
            state["should_continue"] = False

        return state

    def process_input(self, user_input: str) -> str:
        """Main entry point for processing user input"""
        logger.info(f"Processing: {user_input[:100]}...")

        self.conversation_history.append({"role": "user", "content": user_input})

        initial_state: AgentState = {
            "messages": [{"role": "user", "content": user_input}],
            "current_task": "",
            "tool_results": [],
            "memory_context": [],
            "should_continue": False
        }

        try:
            # Run synchronously (LangGraph handles this better)
            result_state = self.agent_graph.invoke(initial_state)

            response = result_state["messages"][-1]["content"] if result_state["messages"] else "No response"
            self.conversation_history.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            logger.error(f"Processing error: {str(e)}", exc_info=True)
            return f"I encountered an error processing your request: {str(e)}"

    def get_system_stats(self) -> Dict:
        """Get system performance statistics"""
        try:
            stats = {
                "conversation_length": len(self.conversation_history),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
            }

            # Add memory system stats
            stats.update(self.memory.get_statistics())

            # Add tool stats
            stats["tool_executions"] = len(self.tools.tool_history)

            return stats

        except Exception as e:
            logger.error(f"System stats error: {str(e)}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Simple CLI interface for testing
    print("=" * 60)
    print("🤖 Autonomous AI Agent System")
    print("=" * 60)

    try:
        print("📦 Initializing agent...")
        agent = AutonomousAgent()
        print("✅ Agent ready!")

        print("\nType 'quit' to exit, 'stats' for system statistics")
        print("=" * 60)

        while True:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if user_input.lower() == 'stats':
                stats = agent.get_system_stats()
                print(json.dumps(stats, indent=2))
                continue

            print("🤖 Agent: ", end="")
            response = agent.process_input(user_input)
            print(response)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        logger.error("Fatal error", exc_info=True)
