import os
import shutil
import subprocess
import sys
from pathlib import Path

# Paths
root_path = Path(os.path.abspath(__file__)).parent
library_path = root_path / 'library'
ext_library_path = library_path / 'pulseq-cest-library'
seq_library_readme = ext_library_path / 'seq-library/readme.md'
sim_path = root_path / 'sim/src/compile'
setup_filepath = sim_path / 'setup.py'


def check_sim_package_exists() -> bool:
    reqs = subprocess.call([sys.executable, '-m', 'pip', 'show', 'pySimPulseqSBB'])
    if not reqs:
        return True
    else:
        return False


def sim_setup():
    if check_sim_package_exists():
        print(f'pySimPulseqSBB already installed. You can start your simulations.')
    else:
        print(f'Starting pySimPulseqSBB setup. Please refer to sim/src/readme.md and check the prerequisites.')
        if not setup_filepath.exists():
            raise Exception(f'Setup file for pySimPulseqSBB not found. Please check you have the latest pypulseq-cest '
                            f'version. \n See also sim/src/readme.md')
        if not shutil.which('swig'):
            raise Exception(f'SWIG is not installed on your system. Please refer to sim/src/readme.md, then install '
                            f'SWIG and re-run this file or use a precompiled installation.')
        check_build = subprocess.call([sys.executable, 'setup.py', 'build_ext', '--inplace'], cwd=sim_path)
        check_install = subprocess.call([sys.executable, 'setup.py', 'install'], cwd=sim_path)
        if 1 in [check_build, check_install]:
            print(f'Could not install pySimPulseqSBB automatically. Please check the prerequisites and refer to '
                  f'sim/src/readme.md.')
        else:
            print('Successfully installed pySimPulseqSBB.')


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


if __name__ == '__main__':
    print('Starting automatic setup. Please refer to the readme.md for further information.')
    clone_library()
    sim_setup()
