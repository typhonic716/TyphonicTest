"""
Installation and setup script for AI Agent System
Handles dependency installation, model download, and configuration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import urllib.request
import json
from typing import Optional, List, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print styled header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}")
    print(f"{text}")
    print(f"{'=' * 60}{Colors.END}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

def check_python_version() -> bool:
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_cuda_available() -> Tuple[bool, Optional[str]]:
    """Check if CUDA is available"""
    try:
        result = subprocess.run(
            ['nvidia-smi'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Try to extract CUDA version
            for line in result.stdout.split('\n'):
                if 'CUDA Version' in line:
                    cuda_version = line.split('CUDA Version:')[1].strip().split()[0]
                    return True, cuda_version
            return True, "Unknown"
        return False, None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, None

def install_requirements(requirements_file: str = 'requirements.txt') -> bool:
    """Install Python dependencies from requirements.txt"""
    if not os.path.exists(requirements_file):
        print_error(f"Requirements file not found: {requirements_file}")
        return False

    print_info(f"Installing dependencies from {requirements_file}...")

    try:
        # Upgrade pip first
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            check=True,
            capture_output=True
        )

        # Install requirements
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
            check=True,
            capture_output=False  # Show output to user
        )

        print_success("All dependencies installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def create_directory_structure():
    """Create necessary directories"""
    print_info("Creating directory structure...")

    base_dir = Path.home() / "AI_Agent_System"
    directories = {
        'models': base_dir / 'models',
        'memory': base_dir / 'memory',
        'logs': base_dir / 'logs',
        'data': base_dir / 'data',
    }

    try:
        for name, path in directories.items():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created {name} directory: {path}")

        return True, base_dir

    except Exception as e:
        print_error(f"Failed to create directories: {e}")
        return False, None

def download_model(model_url: str = None, model_name: str = None) -> bool:
    """
    Download LLM model if not present

    Default: Small Llama model for testing
    """
    if model_url is None:
        print_warning("No model URL provided")
        print_info("You'll need to manually download a model")
        print_info("Recommended: Llama 3.2 or similar GGUF format model")
        print_info("Place it in: ~/AI_Agent_System/models/")
        return True

    base_dir = Path.home() / "AI_Agent_System" / "models"
    model_path = base_dir / (model_name or "model.gguf")

    if model_path.exists():
        print_success(f"Model already exists at {model_path}")
        return True

    print_info(f"Downloading model from {model_url}")
    print_warning("This may take a while depending on model size...")

    try:
        def download_progress(block_num, block_size, total_size):
            """Show download progress"""
            downloaded = block_num * block_size
            percent = min(downloaded / total_size * 100, 100)
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f'\r{bar} {percent:.1f}%', end='', flush=True)

        urllib.request.urlretrieve(model_url, model_path, download_progress)
        print()  # New line after progress bar
        print_success(f"Model downloaded to {model_path}")
        return True

    except Exception as e:
        print_error(f"Failed to download model: {e}")
        if model_path.exists():
            model_path.unlink()  # Clean up partial download
        return False

def create_default_config(base_dir: Path) -> bool:
    """Create default configuration file"""
    print_info("Creating default configuration...")

    config_path = base_dir / "config.json"

    # Check for GPU
    has_cuda, cuda_version = check_cuda_available()

    config = {
        "model": {
            "path": str(base_dir / "models" / "llama-3.2-3b-instruct.gguf"),
            "n_gpu_layers": 50 if has_cuda else 0,
            "n_batch": 512,
            "n_ctx": 8192,
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 2048
        },
        "memory": {
            "persist_directory": str(base_dir / "memory"),
            "embedding_model": "all-MiniLM-L6-v2",
            "learning_threshold": 0.75,
            "max_conversations": 1000
        },
        "security": {
            "enable_command_execution": False,
            "enable_python_exec": False,
            "allowed_file_paths": [str(base_dir / "data")],
            "blocked_commands": ["format", "del", "rm -rf", "shutdown", "reboot", "mkfs"]
        },
        "web": {
            "host": "127.0.0.1",
            "port": 7860,
            "share": False,
            "auth": None
        },
        "logging": {
            "level": "INFO",
            "file": str(base_dir / "logs" / "agent.log"),
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "tools": {
            "web_search_max_results": 5,
            "wikipedia_summary_length": 1000,
            "command_timeout": 30,
            "file_read_limit": 2000
        }
    }

    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print_success(f"Configuration saved to {config_path}")

        if has_cuda:
            print_success(f"CUDA detected (version {cuda_version}) - GPU acceleration enabled")
        else:
            print_warning("CUDA not detected - using CPU only")

        return True

    except Exception as e:
        print_error(f"Failed to create config: {e}")
        return False

def verify_installation() -> Tuple[bool, List[str]]:
    """Verify that all components are properly installed"""
    print_info("Verifying installation...")

    issues = []
    all_ok = True

    # Check required packages
    required_packages = [
        'langchain',
        'langchain_community',
        'langgraph',
        'chromadb',
        'sentence_transformers',
        'psutil',
    ]

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not found")
            issues.append(f"Missing package: {package}")
            all_ok = False

    # Check optional packages
    optional_packages = [
        'duckduckgo_search',
        'wikipediaapi',
        'gradio',
        'torch',
    ]

    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} installed (optional)")
        except ImportError:
            print_warning(f"{package} not found (optional - some features may be limited)")

    # Check directories
    base_dir = Path.home() / "AI_Agent_System"
    if base_dir.exists():
        print_success(f"Base directory exists: {base_dir}")
    else:
        print_error(f"Base directory not found: {base_dir}")
        issues.append("Base directory missing")
        all_ok = False

    return all_ok, issues

def main():
    """Main installation process"""
    print_header("🤖 AI Agent System - Installation")

    print_info(f"Platform: {platform.system()} {platform.machine()}")
    print_info(f"Python: {sys.version.split()[0]}")

    # Step 1: Check Python version
    print_header("Step 1: Checking Python Version")
    if not check_python_version():
        print_error("Installation cannot continue with incompatible Python version")
        sys.exit(1)

    # Step 2: Create directory structure
    print_header("Step 2: Creating Directory Structure")
    success, base_dir = create_directory_structure()
    if not success:
        print_error("Failed to create directory structure")
        sys.exit(1)

    # Step 3: Install dependencies
    print_header("Step 3: Installing Dependencies")
    if os.path.exists('requirements.txt'):
        if not install_requirements():
            print_warning("Some dependencies failed to install")
            print_info("You may need to install them manually")
    else:
        print_warning("requirements.txt not found - skipping dependency installation")

    # Step 4: Create configuration
    print_header("Step 4: Creating Configuration")
    if not create_default_config(base_dir):
        print_error("Failed to create configuration")
        sys.exit(1)

    # Step 5: Model download (optional)
    print_header("Step 5: Model Setup")
    print_info("Model download skipped - please download manually")
    print_info("Recommended models:")
    print_info("  - Llama 3.2 3B (lightweight, good for testing)")
    print_info("  - Llama 3.1 8B (better quality, requires more resources)")
    print_info("  - Mistral 7B (balanced performance)")
    print_info(f"\nPlace your GGUF model file in: {base_dir / 'models'}")
    print_info("Then update the 'model.path' in config.json")

    # Step 6: Verify installation
    print_header("Step 6: Verifying Installation")
    all_ok, issues = verify_installation()

    # Final summary
    print_header("Installation Summary")

    if all_ok:
        print_success("Installation completed successfully!")
        print()
        print_info("Next steps:")
        print_info(f"  1. Download a model and place it in {base_dir / 'models'}")
        print_info(f"  2. Update configuration if needed: {base_dir / 'config.json'}")
        print_info("  3. Run: python launch.py")
        print()
        print_success("You're ready to go! 🚀")
    else:
        print_warning("Installation completed with issues:")
        for issue in issues:
            print_warning(f"  - {issue}")
        print()
        print_info("Please resolve the issues above before running the agent")

    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error during installation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
