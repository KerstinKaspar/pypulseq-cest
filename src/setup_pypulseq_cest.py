from setuptools import setup

setup(
    name='pypulseq_cest',
    author='Kerstin Heinecke, Patrick Schuenke',
    author_email='kerstin.heinecke@ptb.de',
    version='0.1',
    # description='A python tool to perform Bloch-McConnell (BMC) simulations.',
    #url='https://github.com/schuenke/BMCTool',
    install_requires=[
        'bmctool>=0.4.0'
    ],
    keywords='MRI, Bloch, CEST, simulations',
    packages=['pypulseq_cest'],
    package_dir={'pypulseq_cest': '..'},
    #include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        # 'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    # python_requires='>=3.6'
)
