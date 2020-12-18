"""
    clone_pulseq-cest-library.py
    Python file to clone the latest version of the pulseq-cest-library GitHub repository.
"""
import os
import shutil
import subprocess


def check_library_exists():
    if ext_library_path.exists():
        if [f for f in ext_library_path.iterdir()]:
            return True
        else:
            try:
                ext_library_path.rmdir()
            except FileNotFoundError:
                print(f'pulseq-cest-library found but empty. Please remove the folder and rerun setup.')
    else:
        return False


def clone_pulseq_cest_library(repo_url: str = 'https://github.com/kherz/pulseq-cest-library.git',
                              directory: (str, Path) = None):
    """
    Function to clone the pulseq-cest-library into a subfolder of the current directory.
    Args:
        repo_url: URL of the pulseq-cest-library repository

    Returns:

    """
    if not (shutil.which('git')):
        print(f'Git is not installed on your system. Please install Git and re-run this file or download the'
              f'pulseq-cest-library manually from {repo_url}.')
        return
    else:
        loc = shutil.which('git')
        ver = subprocess.check_output(["git", "--version"]).strip().decode('ascii')
        print(f'Using {ver} installed at {loc} to clone the pulseq-cest-library GitHub repository.')
    subprocess.check_output(['git', 'clone', repo_url], cwd=directory).strip().decode('ascii')


def clone_library():
    if not check_library_exists():
        print(f'Starting to clone pulseq-cest-library automatically. Please refer to library/readme.md.')
        clone_pulseq_cest_library(directory=library_path)
        if check_library_exists():
            print(f'Successfully cloned pulseq-cest-library.')
    else:
        print('pulseq-cest-library already exists in folder \'library\'.')


if __name__ == "__main__":
    clone_pulseq_cest_library()
