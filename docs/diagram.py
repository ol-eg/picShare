import runpy
from pathlib import Path

diagrams_dir = Path(__file__).parent / "diagram_scripts"

if __name__ == "__main__":
    for script in sorted(diagrams_dir.glob("*.py")):
        print(f"Generating {script.stem}...")
        runpy.run_path(str(script))
    print("Done.")