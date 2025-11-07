# Quick Reference Card

## 🚀 Most Common Commands

```bash
# Start with menu (pick your model)
python launch.py

# Start web interface with menu
python launch.py --web

# Use specific model
python launch.py --model llama

# See all available models
python launch.py --list-models

# Get help downloading models
python launch.py --model-info
```

## 📝 All Commands

| Command | What It Does |
|---------|-------------|
| `python launch.py` | Interactive model selection + CLI |
| `python launch.py --web` | Interactive model selection + Web UI |
| `python launch.py --model NAME` | Use model matching NAME |
| `python launch.py --model /path/to/model.gguf` | Use specific model file |
| `python launch.py --list-models` | Show all available models |
| `python launch.py --model-info` | Show download guide |
| `python launch.py --web --share` | Web UI with public link |
| `python launch.py --help` | Show all options |

## 🎯 Examples

```bash
# Example 1: Just run it (easiest!)
python launch.py
# → Shows menu of models
# → Pick one
# → Start chatting

# Example 2: Use Llama
python launch.py --model llama

# Example 3: Web interface with Mistral
python launch.py --web --model mistral

# Example 4: Use model from Downloads
python launch.py --model ~/Downloads/new-model.gguf

# Example 5: Windows - use model from D: drive
python launch.py --model "D:\Models\llama.gguf"
```

## 📥 Getting Models

1. Go to https://huggingface.co/models?library=gguf
2. Search for model + "GGUF" (e.g., "Llama 3.2 GGUF")
3. Download the `.gguf` file
4. Put it in `~/AI_Agent_System/models/`
5. Run `python launch.py` - it appears in menu!

### Recommended Models

| Size | Model | Use Case |
|------|-------|----------|
| 2-4 GB | Llama 3.2 3B | Testing, fast responses |
| 4-6 GB | Mistral 7B | Daily use, balanced |
| 8+ GB | Llama 3.1 8B | High quality responses |

## 🌐 Web Interface

```bash
# Basic
python launch.py --web

# With specific model
python launch.py --web --model llama

# Public sharing (creates shareable link)
python launch.py --web --share

# Custom port
python launch.py --web --model mistral
# (Change port in config: ~/AI_Agent_System/config.json)
```

## ⚙️ Configuration (Optional)

Config file: `~/AI_Agent_System/config.json`

```json
{
  "model": {
    "n_gpu_layers": 50,    // Use GPU (0 for CPU only)
    "n_ctx": 8192,         // Context window
    "temperature": 0.7     // Creativity (0-1)
  },
  "web": {
    "port": 7860           // Web interface port
  }
}
```

## 🔧 Troubleshooting

### No models found?
```bash
python launch.py --model-info
# Shows where to download and how to install
```

### Model won't load?
- Check file is `.gguf` format
- Make sure you have enough RAM (model size + 2GB)
- Try reducing `n_gpu_layers` in config

### "Multiple models match 'llama'"?
Be more specific:
```bash
python launch.py --model llama-3.2
# or
python launch.py --model llama-3.2-3b
```

## 💡 Tips

### Switch models easily
```bash
python launch.py --model llama      # Try Llama
python launch.py --model mistral    # Try Mistral
python launch.py --model phi        # Try Phi
```

### Keep different models for different tasks
- **Small model** (2-3GB) → Quick questions
- **Medium model** (5-7GB) → Normal use
- **Large model** (8GB+) → Important work

### Test before downloading large models
Start with a 2-3GB model to make sure everything works!

## 🆘 Need Help?

- **Full Guide**: `MODEL_SELECTION_GUIDE.md`
- **Complete Docs**: `README_FULL.md`
- **Security**: `SECURITY.md`

## 🎉 That's It!

**No config editing needed - just run and choose!**

```bash
python launch.py
```
