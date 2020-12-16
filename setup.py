import os
import shutil
import subprocess
import sys
import pip
from pathlib import Path

# Paths
root_path = Path(os.path.abspath(__file__)).parent
library_path = root_path / 'library'
ext_library_path = library_path / 'pulseq-cest-library'
seq_library_readme = ext_library_path / 'seq-library/Readme.md'
sim_path = root_path / 'sim/src/compile'
setup_filepath = sim_path / 'setup.py'


def check_sim_package_exists() -> bool:
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
    if 'pySimPulseqSBB' in installed_packages:
        return True
    else:
        print(f'pySimPulseqSBB not installed. If installation does not start automatically, please refer to '
              f'sim/src/readme.md.')
        return False


def sim_setup():
    if check_sim_package_exists():
        print(f'pySimPulseqSBB installed. You can start your simulations.')
        return
    else:
        print(f'Starting pySimPulseqSBB setup. Please refer to sim/src/readme.md and check the prerequisites.')
        if not setup_filepath.exists():
            raise Exception(f'Setup file for pySimPulseqSBB not found. Please check you have the latest pypulseq-cest '
                            f'version. \n See also sim/src/readme.md')
        if not shutil.which('swig'):
            raise Exception(f'SWIG is not installed on your system. Please refer to sim/src/readme.md, then install '
                            f'SWIG and re-run this file or use a precompiled installation.')
        try:
            subprocess.run([sys.executable, 'setup.py', 'build_ext', '--inplace'], cwd=sim_path)
            subprocess.run([sys.executable, 'setup.py', 'install'], cwd=sim_path)
        except BaseException:
            print(f'Could not install pySimPulseqSBB automatically. Please check the prerequisites and refer to '
                  f'sim/src/readme.md.')
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
        print(f'pulseq-cest-library not found. If cloning does not start automatically, please refer to '
              f'library/readme.md.')
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
    if not directory:
        directory = Path(os.getcwd())
    subprocess.check_output(['git', 'clone', repo_url], cwd=directory).strip().decode('ascii')


def clone_library():
    if not check_library_exists():
        print(f'Starting to clone pulseq-cest-library automatically. Please refer to library/readme.md.')
        clone_pulseq_cest_library(directory=library_path)
        if check_library_exists():
            print(f'Successfully cloned pulseq-cest-library.')
    else:
        print('pulseq-cest-library already exists in folder \'library\'.')


def final_check():
    if check_sim_package_exists() and check_library_exists():
        print('You\'re all set up. You can now access the sim-pulseq-library and start your simulations.')
        return
    elif not seq_library_readme.exists():
        raise Exception(f'Found pulseq-cest-library but not seq-library/Readme.md. Check if your folder is empty, delete'
                        f'it and run this script again.')
    else:
        raise Exception(f'Could not setup automatically. Please refer to library/Readme.md and sim/src/readme.md.')


def setup_lib_sim():
    print('Starting automatic setup. Please refer to the Readme.md for further information.')
    clone_library()
    sim_setup()
    final_check()


if __name__ == '__main__':
    setup_lib_sim()
