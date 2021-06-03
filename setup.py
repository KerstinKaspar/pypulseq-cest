import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Union


def call_subprocess(call: list, str_options: str = None, **kwargs):
    if str_options:
        call += [str_options]
    return subprocess.call(call, **kwargs)


def check_library_exists(library_path: Union[str, Path]):
    ext_library_path = library_path / 'pulseq-cest-library'
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


def check_sim_package_exists() -> bool:
    reqs = subprocess.call([sys.executable, '-m', 'pip', 'show', 'pySimPulseqSBB'])
    if not reqs:
        return True
    else:
        return False


def clone_library(library_path: Union[str, Path] = None):
    if not library_path:
        library_path = Path('library')
    if not check_library_exists(library_path=library_path):
        print(f'Starting to clone pulseq-cest-library automatically. Please refer to library/readme.md.')
        clone_pulseq_cest_library(directory=library_path)
        if check_library_exists(library_path=library_path):
            print(f'Successfully cloned pulseq-cest-library.')
    else:
        print('pulseq-cest-library already exists in folder \'library\'.')


def clone_pulseq_cest_library(repo_url: str = 'https://github.com/kherz/pulseq-cest-library.git',
                              directory: Union[str, Path]  = None):
    """
    Function to clone the pulseq-cest-library into a subfolder of the current directory.
    :param repo_url: URL of the pulseq-cest-library repository
    """
    if not directory:
        directory = Path('library')
    if not (shutil.which('git')):
        print(f'Git is not installed on your system. Please install Git and re-run this file or download the'
              f'pulseq-cest-library manually from {repo_url}.')
        return
    else:
        loc = shutil.which('git')
        ver = subprocess.check_output(["git", "--version"]).strip().decode('ascii')
        print(f'Using {ver} installed at {loc} to clone the pulseq-cest-library GitHub repository.')
    subprocess.check_output(['git', 'clone', repo_url], cwd=directory).strip().decode('ascii')


def pypulseq_cest_setup(setup_filepath: Union[str, Path], str_options: str = None):
    print(f'pypulseq_cest: start installation')
    if not str_options:
        check_install = subprocess.call([sys.executable, 'install_pypulseq_cest.py', 'install'], cwd=setup_filepath)
    else:
        check_install = subprocess.call([sys.executable, 'install_pypulseq_cest.py', 'install', str_options],
                                        cwd=setup_filepath, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if check_install == 0:
        print('pypulseq_cest: package successfully installed.')


def sim_setup(sim_path: Union[str, Path], setup_filepath: Union[str, Path], str_options: str = None):
    print(f'pySimPulseqSBB: start installation')
    if check_sim_package_exists():
        print(f'pySimPulseqSBB: package already installed. Proceeding to next step.')
    else:
        dist_path = sim_path / 'dist'
        check_dist = 1
        for dist in [d.name for d in dist_path.iterdir()]:
            if not str_options:
                check_dist = subprocess.call(['pip', 'install', dist], cwd=dist_path, stdout=subprocess.DEVNULL,
                                             stderr=subprocess.STDOUT)
            else:
                check_dist = subprocess.call(['pip', 'install', dist, str_options], cwd=dist_path,
                                             stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if check_dist == 0:
                print('pySimPulseqSBB: package successfully installed.')
                return

        print('pySimPulseqSBB: no matching pre-compiled distribution found. Trying to install via SWIG and distutils.')
        if not setup_filepath.exists():
            raise Exception(f'pySimPulseqSBB: Setup file for pySimPulseqSBB not found. Please ensure you have the latest '
                            f'pypulseq-cest version. \n See "/src/readme.md" for more information.')
        if not shutil.which('swig'):
            raise Exception(f'pySimPulseqSBB: SWIG is not installed on your system. Please refer to "src/readme.md, '
                            f'install SWIG and re-run this file.')

        check_build = subprocess.call([sys.executable, 'setup.py', 'build_ext', '--inplace'], cwd=sim_path,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if not str_options:
            check_install = subprocess.call([sys.executable, 'setup.py', 'install'], cwd=sim_path,
                                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        else:
            check_install = subprocess.call([sys.executable, 'setup.py', 'install', str_options], cwd=sim_path,
                                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if 1 in [check_build, check_install]:
            print(f'pySimPulseqSBB: Could not install pySimPulseqSBB. Please check the troubleshooting section under'
                  f'https://github.com/KerstinHut/pypulseq-cest.')
        else:
            print('pySimPulseqSBB: package successfully installed.')


if __name__ == '__main__':
    root_path = Path(os.path.abspath(__file__)).parent
    library_path = root_path / 'library'
    ext_library_path = library_path / 'pulseq-cest-library'
    seq_library_readme = ext_library_path / 'seq-library/readme.md'
    sim_path = root_path / 'src/compile'
    setup_filepath = sim_path / 'setup.py'

    print('Starting automatic setup. Please refer to the readme.md for further information.')
    clone_library(library_path=library_path)
    str_options = None
    if len(sys.argv) > 1:
        str_options = str(sys.argv[1])
    sim_setup(sim_path=sim_path, setup_filepath=setup_filepath, str_options=str_options)
    pypulseq_cest_setup(setup_filepath=root_path, str_options=str_options)
