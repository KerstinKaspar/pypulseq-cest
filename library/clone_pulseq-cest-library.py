"""
    clone_pulseq-cest-library.py
    Python file to clone the latest version of the pulseq-cest-library GitHub repository.
"""
import os
from pathlib import Path

from ..install import clone_library

library_path = Path(os.path.abspath(__file__)).parent

if __name__ == "__main__":
    clone_library(library_path=library_path)
