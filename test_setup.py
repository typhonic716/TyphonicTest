"""
Simple test script to validate installation and basic functionality
Run with: python test_setup.py
"""

import sys
import os
from pathlib import Path

def print_test(name, passed):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {name}")
    return passed

def test_python_version():
    """Test Python version"""
    version = sys.version_info
    return print_test(
        f"Python version >= 3.8 (found {version.major}.{version.minor})",
        version.major >= 3 and version.minor >= 8
    )

def test_imports():
    """Test that critical imports work"""
    results = []

    # Core imports
    try:
        import langchain
        results.append(print_test("langchain import", True))
    except ImportError:
        results.append(print_test("langchain import", False))

    try:
        import langgraph
        results.append(print_test("langgraph import", True))
    except ImportError:
        results.append(print_test("langgraph import", False))

    try:
        import chromadb
        results.append(print_test("chromadb import", True))
    except ImportError:
        results.append(print_test("chromadb import", False))

    try:
        from sentence_transformers import SentenceTransformer
        results.append(print_test("sentence_transformers import", True))
    except ImportError:
        results.append(print_test("sentence_transformers import", False))

    # Optional imports
    try:
        import gradio
        results.append(print_test("gradio import (optional)", True))
    except ImportError:
        results.append(print_test("gradio import (optional) - SKIPPED", True))

    try:
        from duckduckgo_search import DDGS
        results.append(print_test("duckduckgo_search import (optional)", True))
    except ImportError:
        results.append(print_test("duckduckgo_search import (optional) - SKIPPED", True))

    return all(results)

def test_config():
    """Test configuration"""
    try:
        from config import get_config
        config = get_config()
        return print_test("Configuration loading", True)
    except Exception as e:
        print(f"  Error: {e}")
        return print_test("Configuration loading", False)

def test_directories():
    """Test directory structure"""
    base_dir = Path.home() / "AI_Agent_System"

    required_dirs = ['models', 'memory', 'logs', 'data']
    results = []

    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        results.append(print_test(f"Directory: {dir_name}", exists))

    return all(results)

def test_model_path():
    """Test if model file exists"""
    try:
        from config import get_config
        config = get_config()
        model_path = Path(config.get('model', 'path'))

        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            return print_test(f"Model file exists ({size_mb:.1f} MB)", True)
        else:
            print(f"  Model path: {model_path}")
            print("  You need to download a model!")
            return print_test("Model file exists", False)
    except Exception as e:
        print(f"  Error: {e}")
        return print_test("Model path check", False)

def test_agent_initialization():
    """Test agent can be initialized (without model)"""
    try:
        # Just test imports, not actual initialization
        from agent import ToolFramework, MemorySystem
        from config import get_config

        config = get_config()

        # Test memory system
        memory = MemorySystem(config)
        print_test("Memory system initialization", True)

        # Test tool framework
        tools = ToolFramework(memory, config)
        return print_test("Tool framework initialization", len(tools.tools) > 0)

    except Exception as e:
        print(f"  Error: {e}")
        return print_test("Agent initialization", False)

def test_security_defaults():
    """Test that security settings are safe by default"""
    try:
        from config import get_config
        config = get_config()

        cmd_exec = config.get('security', 'enable_command_execution', default=True)
        py_exec = config.get('security', 'enable_python_exec', default=True)

        safe = (not cmd_exec) and (not py_exec)

        if not safe:
            print("  WARNING: Dangerous features are enabled!")
            print(f"  - Command execution: {cmd_exec}")
            print(f"  - Python execution: {py_exec}")

        return print_test("Security defaults are safe", safe)

    except Exception as e:
        print(f"  Error: {e}")
        return print_test("Security defaults check", False)

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 AI Agent System - Setup Validation")
    print("=" * 60)
    print()

    results = []

    print("📋 Basic Requirements:")
    results.append(test_python_version())
    print()

    print("📦 Python Packages:")
    results.append(test_imports())
    print()

    print("⚙️  Configuration:")
    results.append(test_config())
    print()

    print("📁 Directories:")
    results.append(test_directories())
    print()

    print("🤖 Model:")
    model_ok = test_model_path()
    # Don't count model as failure - it's expected to be missing initially
    print()

    print("🔧 Components:")
    results.append(test_agent_initialization())
    print()

    print("🔒 Security:")
    results.append(test_security_defaults())
    print()

    # Summary
    print("=" * 60)
    total = len(results)
    passed = sum(results)

    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        if not model_ok:
            print("\n⚠️  Note: Model file not found (expected)")
            print("   Download a model to use the agent")
        print("\n🚀 You're ready to go! Run: python launch.py")
        return 0
    else:
        failed = total - passed
        print(f"❌ Some tests failed ({failed}/{total} failed)")
        print("\n🔧 Please fix the issues above before running the agent")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
