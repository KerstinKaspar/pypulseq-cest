"""
    clone_pulseq-cest-library.py
    Python file to clone the latest version of the pulseq-cest-library GitHub repository.
"""
import os
import shutil
import subprocess


def clone_pulseq_cest_library(repo_url: str = 'https://github.com/kherz/pulseq-cest-library.git'):
    """
    Function to clone the pulseq-cest-library into a subfolder of the current directory.
    Args:
        repo_url: URL of the pulseq-cest-library repository

    Returns:

    """
    if os.path.isdir('pulseq-cest-library'):
        raise FileExistsError('A subfolder called "pulseq-cest-library" already exists. Script aborted!')

    if not (shutil.which('git')):
        print(f'Git is not installed on your system. Please install Git and re-run this file or download the'
              f'pulseq-cest-library manually from {repo_url}.')
        return
    else:
        loc = shutil.which('git')
        ver = subprocess.check_output(["git", "--version"]).strip().decode('ascii')
        print(f'Using {ver} installed at {loc} to clone the pulseq-cest-library GitHub repository.')

    subprocess.check_output(['git', 'clone', repo_url]).strip().decode('ascii')


if __name__ == "__main__":
    clone_pulseq_cest_library()
