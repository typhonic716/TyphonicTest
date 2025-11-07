"""
Model selection utility for AI Agent System
Helps users easily select and manage LLM models
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple
import sys

class ModelSelector:
    """Utility to discover and select LLM models"""

    def __init__(self, models_dir: Optional[Path] = None):
        if models_dir is None:
            self.models_dir = Path.home() / "AI_Agent_System" / "models"
        else:
            self.models_dir = Path(models_dir)

        # Create models directory if it doesn't exist
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def find_models(self) -> List[Tuple[str, Path, int]]:
        """
        Find all GGUF model files in the models directory

        Returns:
            List of tuples: (model_name, full_path, size_in_mb)
        """
        models = []

        if not self.models_dir.exists():
            return models

        # Look for .gguf files
        for file_path in self.models_dir.rglob("*.gguf"):
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                models.append((file_path.name, file_path, int(size_mb)))

        # Also check for .bin files (some older formats)
        for file_path in self.models_dir.rglob("*.bin"):
            if file_path.is_file() and "ggml" in file_path.name.lower():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                models.append((file_path.name, file_path, int(size_mb)))

        # Sort by name
        models.sort(key=lambda x: x[0])

        return models

    def select_model_interactive(self) -> Optional[Path]:
        """
        Interactive model selection with numbered menu

        Returns:
            Path to selected model or None if cancelled
        """
        models = self.find_models()

        if not models:
            print("❌ No models found!")
            print(f"\n📁 Models directory: {self.models_dir}")
            print("\n💡 To add a model:")
            print("   1. Download a GGUF model file")
            print("   2. Place it in the models directory above")
            print("\n🔗 Recommended sources:")
            print("   - Hugging Face: https://huggingface.co/models?library=gguf")
            print("   - TheBloke models: https://huggingface.co/TheBloke")
            print("\n📚 Popular models:")
            print("   - Llama 3.2 3B (lightweight)")
            print("   - Mistral 7B (balanced)")
            print("   - Llama 3.1 8B (high quality)")
            return None

        print("\n" + "=" * 60)
        print("📚 Available Models")
        print("=" * 60)

        for i, (name, path, size) in enumerate(models, 1):
            print(f"{i}. {name}")
            print(f"   Size: {size} MB")
            print(f"   Path: {path}")
            print()

        print("=" * 60)

        while True:
            try:
                choice = input("\n👉 Select model number (or 'q' to quit): ").strip()

                if choice.lower() in ['q', 'quit', 'exit']:
                    return None

                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    selected = models[idx]
                    print(f"\n✅ Selected: {selected[0]} ({selected[2]} MB)")
                    return selected[1]
                else:
                    print(f"❌ Please enter a number between 1 and {len(models)}")

            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\n❌ Selection cancelled")
                return None

    def get_model_by_name(self, name: str) -> Optional[Path]:
        """
        Get model path by partial name match

        Args:
            name: Model name or partial name to search for

        Returns:
            Path to model if found, None otherwise
        """
        models = self.find_models()
        name_lower = name.lower()

        # Try exact match first
        for model_name, path, _ in models:
            if model_name.lower() == name_lower:
                return path

        # Try partial match
        matches = []
        for model_name, path, size in models:
            if name_lower in model_name.lower():
                matches.append((model_name, path, size))

        if len(matches) == 1:
            return matches[0][1]
        elif len(matches) > 1:
            print(f"\n⚠️  Multiple models match '{name}':")
            for i, (model_name, path, size) in enumerate(matches, 1):
                print(f"  {i}. {model_name} ({size} MB)")
            print("\nPlease be more specific or use interactive selection.")
            return None

        return None

    def list_models(self, verbose: bool = False):
        """
        List all available models

        Args:
            verbose: Show detailed information
        """
        models = self.find_models()

        if not models:
            print("❌ No models found")
            print(f"📁 Models directory: {self.models_dir}")
            return

        print("\n" + "=" * 60)
        print(f"📚 Found {len(models)} model(s)")
        print("=" * 60)

        for i, (name, path, size) in enumerate(models, 1):
            print(f"\n{i}. {name}")
            print(f"   Size: {size:,} MB")
            if verbose:
                print(f"   Path: {path}")

        print("\n" + "=" * 60)
        print(f"📁 Models directory: {self.models_dir}")
        print("=" * 60)

    def validate_model_path(self, model_path: str) -> Optional[Path]:
        """
        Validate that a model path exists and is accessible

        Args:
            model_path: Path to model file

        Returns:
            Resolved Path object if valid, None otherwise
        """
        try:
            path = Path(model_path).expanduser().resolve()

            if not path.exists():
                print(f"❌ Model file not found: {path}")
                return None

            if not path.is_file():
                print(f"❌ Path is not a file: {path}")
                return None

            # Check file size
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb < 1:
                print(f"⚠️  Warning: Model file is very small ({size_mb:.1f} MB)")
                print("   This might not be a valid model file")

            return path

        except Exception as e:
            print(f"❌ Error validating model path: {e}")
            return None

    def prompt_for_model_download(self):
        """Show helpful information about downloading models"""
        print("\n" + "=" * 60)
        print("📥 How to Download Models")
        print("=" * 60)

        print("\n🔗 Recommended Sources:")
        print("   1. Hugging Face (GGUF models)")
        print("      https://huggingface.co/models?library=gguf")
        print()
        print("   2. TheBloke's Collections")
        print("      https://huggingface.co/TheBloke")
        print()

        print("📚 Recommended Models:")
        print("\n   🔰 Beginner/Testing (2-4 GB):")
        print("      - Llama 3.2 3B Instruct")
        print("      - Phi-3 Mini")
        print()
        print("   ⚖️  Balanced (4-6 GB):")
        print("      - Mistral 7B Instruct")
        print("      - Llama 3.1 8B Instruct")
        print()
        print("   🚀 Advanced (8+ GB):")
        print("      - Llama 3.1 70B (quantized)")
        print("      - Mixtral 8x7B")
        print()

        print("💾 Installation Steps:")
        print("   1. Go to Hugging Face")
        print("   2. Search for model + 'GGUF'")
        print("   3. Download the .gguf file")
        print(f"   4. Move to: {self.models_dir}")
        print("   5. Run this launcher again")
        print()

        print("=" * 60)


def select_model_for_launch(
    model_arg: Optional[str] = None,
    config_path: Optional[str] = None,
    interactive: bool = True
) -> Optional[Path]:
    """
    Main function to select a model for launching the agent

    Args:
        model_arg: Model path/name from command line
        config_path: Path to config file
        interactive: Allow interactive selection

    Returns:
        Path to selected model or None
    """
    selector = ModelSelector()

    # If model specified on command line
    if model_arg:
        # Check if it's a full path
        if os.path.exists(model_arg):
            return selector.validate_model_path(model_arg)

        # Try to find by name
        model_path = selector.get_model_by_name(model_arg)
        if model_path:
            return model_path

        print(f"❌ Model not found: {model_arg}")
        print("\n💡 Try:")
        print("   - Use full path to model file")
        print("   - Use --list-models to see available models")
        return None

    # Try to use model from config
    if config_path or True:  # Always try config
        try:
            from config import get_config
            config = get_config(config_path)

            if config.validate_model_exists():
                model_path = Path(config.get('model', 'path'))
                print(f"✅ Using model from config: {model_path.name}")
                return model_path
        except Exception:
            pass

    # Interactive selection
    if interactive:
        print("\n💡 No model specified. Let's select one!")
        return selector.select_model_interactive()

    return None


if __name__ == "__main__":
    """Standalone model management utility"""
    import argparse

    parser = argparse.ArgumentParser(description="Model Selection Utility")
    parser.add_argument('--list', '-l', action='store_true', help='List all available models')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    parser.add_argument('--select', '-s', action='store_true', help='Interactive model selection')
    parser.add_argument('--info', '-i', action='store_true', help='Show download information')

    args = parser.parse_args()

    selector = ModelSelector()

    if args.list:
        selector.list_models(verbose=args.verbose)
    elif args.select:
        model = selector.select_model_interactive()
        if model:
            print(f"\n✅ Selected model: {model}")
    elif args.info:
        selector.prompt_for_model_download()
    else:
        # Default: show available models and download info
        selector.list_models()
        models = selector.find_models()
        if not models:
            selector.prompt_for_model_download()
