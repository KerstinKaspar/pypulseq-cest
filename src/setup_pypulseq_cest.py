from setuptools import setup

setup(
    name='pypulseq_cest',
    author='Kerstin Heinecke, Patrick Schuenke',
    author_email='kerstin.heinecke@ptb.de',
    version='0.2',
    description='PyPulseq-CEST simulation framework.',
    url='https://github.com/KerstinHut/pypulseq-cest',
    install_requires=['bmctool>=0.4.0'],
    keywords='MRI, Bloch, CEST, simulations',
    packages=['pypulseq_cest'],
    package_dir={'': '..'},
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        # 'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)
