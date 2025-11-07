# 🤖 Autonomous AI Agent System

A powerful, self-learning AI agent system that runs locally with tool usage capabilities, vector memory, and a web interface.

## 🌟 Features

### Core Capabilities
- **🧠 Self-Learning Memory**: Vector-based semantic memory using ChromaDB
- **🛠️ Tool Integration**: Web search, Wikipedia, file operations, and extensible tool framework
- **💬 Natural Conversations**: Context-aware dialogue with conversation history
- **🔒 Security-First**: Sandboxed execution with configurable security restrictions
- **🚀 Local Execution**: Runs entirely on your machine using local LLMs
- **🌐 Web Interface**: Beautiful Gradio-based UI with chat, tools, memory, and system monitoring

### Technical Highlights
- LangGraph-based agent orchestration
- Sentence transformers for embeddings
- Cross-platform support (Linux, macOS, Windows)
- GPU acceleration support (CUDA)
- Configurable model parameters
- Extensible tool framework

## 📋 Requirements

- Python 3.8+
- 8GB+ RAM (16GB+ recommended)
- 10GB+ disk space for models
- Optional: NVIDIA GPU with CUDA for acceleration

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-agent-system.git
cd ai-agent-system

# Run installation script
python install.py
```

The installer will:
- Check Python version
- Create directory structure
- Install dependencies
- Create default configuration
- Check for CUDA availability

### 2. Download a Model

Download a GGUF format model (e.g., Llama, Mistral):

**Recommended Models:**
- **Llama 3.2 3B** - Lightweight, good for testing
- **Llama 3.1 8B** - Better quality, more resource-intensive
- **Mistral 7B** - Balanced performance

Place the model in: `~/AI_Agent_System/models/`

Update `~/AI_Agent_System/config.json` with the correct model path.

### 3. Launch

```bash
# CLI interface
python launch.py

# Web interface
python launch.py --web

# Web interface with public sharing
python launch.py --web --share
```

## 🔧 Configuration

Configuration file: `~/AI_Agent_System/config.json`

### Key Settings

```json
{
  "model": {
    "path": "/path/to/model.gguf",
    "n_gpu_layers": 50,  // 0 for CPU-only
    "n_ctx": 8192,       // Context window size
    "temperature": 0.7   // Creativity level
  },
  "security": {
    "enable_command_execution": false,  // KEEP FALSE unless needed
    "enable_python_exec": false         // KEEP FALSE unless needed
  },
  "web": {
    "host": "127.0.0.1",  // Use "0.0.0.0" to allow network access
    "port": 7860
  }
}
```

## 🛠️ Available Tools

### Built-in Tools

1. **Web Search** - DuckDuckGo search for current information
2. **Wikipedia** - Detailed encyclopedia information
3. **Memory Search** - Query learned knowledge and past interactions
4. **File Read** - Read files (restricted to allowed directories)

### Optional Tools (Disabled by Default)

5. **System Commands** - Execute shell commands (requires security.enable_command_execution)
6. **Python REPL** - Execute Python code (requires security.enable_python_exec)

## 🧠 Memory System

The agent maintains multiple memory collections:

- **Conversations**: Full conversation history with semantic search
- **Learned Facts**: Extracted knowledge from interactions
- **Tool Usage**: History of tool executions
- **User Preferences**: Learned user preferences and patterns

### Memory Features

- Semantic search using sentence transformers
- Automatic fact extraction and learning
- Confidence-based knowledge storage
- Context-aware memory retrieval

## 💻 Usage Examples

### CLI Mode

```bash
$ python launch.py

👤 You: What is the capital of France?
🤖 Agent: The capital of France is Paris...

👤 You: stats
📊 System Statistics:
{
  "conversation_length": 2,
  "cpu_percent": 15.2,
  "memory_percent": 45.3,
  ...
}
```

### Web Mode

```bash
$ python launch.py --web
🌐 Access at: http://127.0.0.1:7860
```

Open your browser and navigate to the provided URL.

## 🔒 Security

### Default Security Posture

- Command execution: **DISABLED**
- Python execution: **DISABLED**
- File operations: **Restricted to allowed directories**
- Dangerous commands: **Blocked**

### Enabling Advanced Features

⚠️ **WARNING**: Only enable these features in trusted environments!

Edit `config.json`:

```json
{
  "security": {
    "enable_command_execution": true,  // Use with caution!
    "enable_python_exec": true,        // Use with caution!
    "allowed_file_paths": ["/safe/directory"]
  }
}
```

## 🎯 Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface                         │
│              (CLI / Web / API)                          │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│              Autonomous Agent                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Think   │→ │   Act    │→ │ Respond  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└──────────┬───────────────────────┬──────────────────────┘
           │                       │
┌──────────▼──────────┐  ┌────────▼─────────────────────┐
│   Memory System     │  │    Tool Framework            │
│  - Conversations    │  │  - Web Search                │
│  - Facts            │  │  - Wikipedia                 │
│  - Preferences      │  │  - File Ops                  │
│  - Tool History     │  │  - Custom Tools              │
└─────────────────────┘  └──────────────────────────────┘
```

### LangGraph Workflow

```python
Think (Analyze + Plan)
  ↓
Act (Execute Tools)
  ↓
Respond (Generate Answer)
```

## 🧪 Development

### Adding Custom Tools

```python
from langchain.agents import Tool

def my_custom_tool(query: str) -> str:
    # Your tool logic here
    return f"Result for {query}"

# Add to ToolFramework.setup_tools()
self.tools.append(Tool(
    name="my_tool",
    func=my_custom_tool,
    description="Description of what my tool does"
))
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black *.py

# Lint
flake8 *.py

# Type checking
mypy *.py
```

## 📊 Performance Tips

### For Better Performance

1. **Use GPU acceleration**: Enable CUDA and set `n_gpu_layers` to match your GPU
2. **Adjust context window**: Reduce `n_ctx` if you're running out of memory
3. **Choose appropriate model**: Smaller models are faster but less capable
4. **Limit memory size**: Set `max_conversations` to prevent unbounded growth

### Memory Usage

- Model: 3-8GB (depending on size)
- ChromaDB: ~100MB per 1000 conversations
- Embeddings: ~500MB (cached)
- Python overhead: ~500MB

## 🐛 Troubleshooting

### Model not loading

```
Error: Model file not found
```

**Solution**: Download a model and update `config.json` with the correct path.

### Out of memory

```
Error: CUDA out of memory
```

**Solution**: Reduce `n_gpu_layers` or `n_batch` in config.json.

### Import errors

```
ImportError: No module named 'langchain'
```

**Solution**: Run `python install.py` or `pip install -r requirements.txt`.

### Port already in use

```
Error: Port 7860 is already in use
```

**Solution**: Change `web.port` in config.json or kill the process using the port.

## 📝 File Structure

```
ai-agent-system/
├── agent.py              # Main agent implementation
├── config.py            # Configuration management
├── launch.py            # Launch script
├── install.py           # Installation script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── tests/              # Test suite (optional)
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- LangChain and LangGraph teams
- llama.cpp developers
- ChromaDB team
- Gradio team
- The open-source community

## 📞 Support

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Documentation: [Full docs](docs/)

## 🗺️ Roadmap

- [ ] Plugin system for custom tools
- [ ] Multi-agent collaboration
- [ ] Voice interface
- [ ] Mobile app
- [ ] Cloud deployment options
- [ ] Fine-tuning support
- [ ] Advanced memory management
- [ ] Performance profiling tools

---

**Built with ❤️ for the AI community**
