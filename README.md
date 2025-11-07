# 🤖 Autonomous AI Agent System

A secure, production-ready AI agent system with tool usage, self-learning memory, and local LLM execution.

## ⚡ Quick Start

```bash
# 1. Install dependencies
python install.py

# 2. Download a model (e.g., Llama 3.2) and place in ~/AI_Agent_System/models/

# 3. Launch
python launch.py              # CLI mode
python launch.py --web        # Web interface
```

## ✨ Features

- 🧠 **Self-Learning Memory** - Vector database with semantic search
- 🛠️ **Tool Integration** - Web search, Wikipedia, file ops, and more
- 🔒 **Security-First** - Sandboxed execution, disabled by default
- 🌐 **Web Interface** - Beautiful Gradio UI
- 🚀 **Local Execution** - Runs entirely on your machine

## 📚 Documentation

- [Full Documentation](README_FULL.md) - Complete setup guide
- [Security Policy](SECURITY.md) - Security best practices
- [Test Setup](test_setup.py) - Validate your installation

## 🔧 Requirements

- Python 3.8+
- 8GB+ RAM (16GB+ recommended)
- Optional: NVIDIA GPU with CUDA

## 📖 Usage

### CLI Mode
```bash
python launch.py
```

### Web Mode
```bash
python launch.py --web
```

### Check Installation
```bash
python test_setup.py
```

## ⚙️ Configuration

Edit `~/AI_Agent_System/config.json` to customize:
- Model settings
- Security restrictions
- Tool behavior
- Web interface options

## 🔒 Security

**All dangerous features are DISABLED by default:**
- ❌ Command execution
- ❌ Python code execution
- ✅ File access (restricted to safe directories only)

See [SECURITY.md](SECURITY.md) for details.

## 📝 Project Structure

```
├── agent.py           # Main agent implementation
├── config.py          # Configuration management
├── launch.py          # Launch script
├── install.py         # Installation script
├── test_setup.py      # Setup validation
├── requirements.txt   # Dependencies
└── README_FULL.md     # Complete documentation
```

## 🐛 Troubleshooting

**Import errors?**
```bash
pip install -r requirements.txt
```

**Model not found?**
- Download a GGUF model
- Place in `~/AI_Agent_System/models/`
- Update `config.json` with correct path

**Port in use?**
```bash
python launch.py --web  # Change port in config.json
```

## 📄 License

MIT License - see LICENSE file

## 🤝 Contributing

Contributions welcome! Please read the full documentation first.

---

**For complete documentation, see [README_FULL.md](README_FULL.md)**
