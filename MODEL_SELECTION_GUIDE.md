# Easy Model Selection Guide

**No more config file editing!** 🎉

## 🚀 Quick Start - 3 Ways to Use Models

### 1. Interactive Selection (Easiest!)

Just run the launcher and pick from a menu:

```bash
python launch.py
```

You'll see:
```
🔍 Selecting model...

============================================================
📚 Available Models
============================================================

1. llama-3.2-3b-instruct.Q4_K_M.gguf
   Size: 1893 MB
   Path: /Users/you/AI_Agent_System/models/llama-3.2-3b-instruct.Q4_K_M.gguf

2. mistral-7b-instruct-v0.2.Q5_K_M.gguf
   Size: 4368 MB
   Path: /Users/you/AI_Agent_System/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf

============================================================

👉 Select model number (or 'q' to quit): 1

✅ Selected: llama-3.2-3b-instruct.Q4_K_M.gguf (1893 MB)
```

### 2. Specify Model by Path

Use any model file directly:

```bash
# Full path
python launch.py --model /path/to/your/model.gguf

# Or on Windows
python launch.py --model "C:\Models\llama-3.2.gguf"
```

### 3. Specify Model by Name

Just type part of the model name:

```bash
# Finds first model matching "llama"
python launch.py --model llama

# Finds first model matching "mistral"
python launch.py --model mistral
```

---

## 📋 Useful Commands

### List All Available Models

```bash
python launch.py --list-models
```

Output:
```
============================================================
📚 Found 3 model(s)
============================================================

1. llama-3.2-3b-instruct.Q4_K_M.gguf
   Size: 1,893 MB
   Path: ~/AI_Agent_System/models/llama-3.2-3b-instruct.Q4_K_M.gguf

2. mistral-7b-instruct-v0.2.Q5_K_M.gguf
   Size: 4,368 MB
   Path: ~/AI_Agent_System/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf

3. phi-3-mini-4k-instruct.Q4_K_M.gguf
   Size: 2,391 MB
   Path: ~/AI_Agent_System/models/phi-3-mini-4k-instruct.Q4_K_M.gguf

============================================================
📁 Models directory: ~/AI_Agent_System/models
============================================================
```

### Get Download Information

```bash
python launch.py --model-info
```

Shows you:
- Where to download models
- Recommended models for different use cases
- Installation instructions

---

## 🎯 Complete Examples

### Example 1: CLI with Interactive Selection
```bash
python launch.py
```
- Shows menu of available models
- Pick one with number
- Starts CLI interface

### Example 2: Web UI with Specific Model
```bash
python launch.py --web --model llama
```
- Finds model matching "llama"
- Starts web interface

### Example 3: Use Model from Different Location
```bash
python launch.py --model ~/Downloads/new-model.gguf
```
- Uses model from Downloads folder
- No need to move it!

### Example 4: Web UI with Full Path (Windows)
```bash
python launch.py --web --model "D:\AI\Models\llama-3.2.gguf"
```
- Works with any drive/path on Windows
- Starts web interface

---

## 📥 Where to Get Models

### Recommended Sources

1. **Hugging Face** (Best option)
   - https://huggingface.co/models?library=gguf
   - Search for "GGUF" format models

2. **TheBloke's Collections** (Curated)
   - https://huggingface.co/TheBloke
   - Pre-quantized GGUF models

### Recommended Models by Use Case

#### 🔰 Beginner / Testing (2-4 GB)
- **Llama 3.2 3B Instruct** - Fast, good quality
- **Phi-3 Mini** - Very efficient
- **TinyLlama 1.1B** - Ultra-light

#### ⚖️ Balanced (4-6 GB)
- **Mistral 7B Instruct** ⭐ Most popular
- **Llama 3.1 8B Instruct** - High quality
- **Qwen 7B** - Excellent coding

#### 🚀 Advanced (8+ GB, needs good GPU)
- **Llama 3.1 70B** (quantized) - Best quality
- **Mixtral 8x7B** - Mixture of experts
- **Command R+** - Long context

---

## 🔧 Model Management

### Check What Models You Have

```bash
python launch.py --list-models
```

### Download a New Model

1. Go to Hugging Face
2. Search for "[model name] GGUF"
3. Download the `.gguf` file
4. Place it in `~/AI_Agent_System/models/`
5. Run `python launch.py` - it will show up automatically!

### Organize Multiple Models

You can organize models in subdirectories:

```
~/AI_Agent_System/models/
├── llama/
│   ├── llama-3.2-3b.gguf
│   └── llama-3.1-8b.gguf
├── mistral/
│   └── mistral-7b.gguf
└── phi/
    └── phi-3-mini.gguf
```

The selector will find them all!

---

## ⚙️ Configuration (Optional)

You can still use the config file if you want a default model:

Edit `~/AI_Agent_System/config.json`:

```json
{
  "model": {
    "path": "~/AI_Agent_System/models/llama-3.2-3b.gguf",
    "n_gpu_layers": 50,
    "n_ctx": 8192
  }
}
```

But now you don't have to! Command-line selection overrides the config.

---

## 🎓 Tips & Tricks

### Tip 1: Quick Model Switching
```bash
# Try different models easily
python launch.py --model llama     # Test Llama
python launch.py --model mistral   # Test Mistral
python launch.py --model phi       # Test Phi
```

### Tip 2: Use Aliases (Linux/Mac)
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias agent-llama="python ~/TyphonicTest/launch.py --model llama"
alias agent-mistral="python ~/TyphonicTest/launch.py --model mistral"
alias agent-web="python ~/TyphonicTest/launch.py --web"
```

Then just type: `agent-llama`

### Tip 3: Keep Models Separate
Keep different sized models:
- Small model for testing
- Medium model for daily use
- Large model for important tasks

### Tip 4: Model Naming
Name your models descriptively:
- `llama-3.2-3b-Q4.gguf` (quantization type)
- `mistral-7b-instruct.gguf` (purpose)
- `phi-3-mini-4k.gguf` (context size)

---

## 🚫 Troubleshooting

### "No models found"

**Solution:**
```bash
python launch.py --model-info
```
This shows you where to download models and where to place them.

### "Model not found: xyz"

**Problem:** Model name doesn't match any files

**Solution:** List models to see exact names:
```bash
python launch.py --list-models
```

### "Multiple models match 'llama'"

**Problem:** You have several Llama models

**Solution:** Be more specific:
```bash
python launch.py --model llama-3.2      # More specific
python launch.py --model llama-3.2-3b   # Even more specific
```

Or use full path:
```bash
python launch.py --model ~/AI_Agent_System/models/llama-3.2-3b-instruct.gguf
```

### Model loads but performs poorly

**Problem:** Model too small or wrong quantization

**Solutions:**
- Try a larger model
- Try higher quantization (Q5, Q6, Q8)
- Increase GPU layers in config: `"n_gpu_layers": 50`

---

## 🔥 Quick Reference

| Task | Command |
|------|---------|
| Interactive selection | `python launch.py` |
| List available models | `python launch.py --list-models` |
| Download guide | `python launch.py --model-info` |
| Use specific model | `python launch.py --model path/to/model.gguf` |
| Find model by name | `python launch.py --model llama` |
| Web UI + model | `python launch.py --web --model mistral` |
| Test a model | `python launch.py --model test.gguf` |

---

## 📚 Learn More

- **Full Documentation**: `README_FULL.md`
- **Security**: `SECURITY.md`
- **Configuration**: `~/AI_Agent_System/config.json`

---

**No more config file editing! Just run and choose! 🎉**
