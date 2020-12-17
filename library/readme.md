# Config and seq-file library
This folder contains one [config file](config_example.yaml), one [(py)pulseq-cest seq-file](seq_example.seq) and the
corresponding [python file](write_seq_example.py) to create the seq-file. More information about the pulseq-cest-library
folder can be found below.

## pulseq-cest-library
The [pulseq-cest-library](https://github.com/kherz/pulseq-cest-library) is a separate GitHub repository that contains 
several pre-defined and approved pre-saturation schemes 
([seq-library](https://github.com/kherz/pulseq-cest-library/tree/master/seq-library)) as well as several pre-defined 
and approved simulation settings ([sim-library](https://github.com/kherz/pulseq-cest-library/tree/master/sim-library)).
More information about the structure and the content of these files can be found in the corresponding 
[seq-library readme](https://github.com/kherz/pulseq-cest-library/blob/master/seq-library/Readme.md) and 
[sim-library readme](https://github.com/kherz/pulseq-cest-library/blob/master/sim-library/Readme.md) files.

### How to dowload the pulse-cest-library in case it's empty
The [pulseq-cest-library](https://github.com/kherz/pulseq-cest-library) is automatically cloned if you run the installation from the [pypulseq-cest readme](../readme.md). If your 
If the [pulseq-cest-library](pulseq-cest-library) folder ist empty, you can still get the files using one of these two options:

**Recommended:** Run the clone_pulseq-cest-library.py file.
You can do that from your terminal (in the [library](.) subdirectory):
```
python clone_pulseq-cest-library.py
```
Troubleshoot denied permissions by running it with administrative rights (Windows: start the terminal with administrative rights, Linux: ```sudo python install.py```)
You might need to adapt your python executable, e.g. ```python3```

**Option 2:** Use the following GitHub command (in the [library](.) subdirectory) to initialize your local configuration file and to fetch all data:
```
git clone https://github.com/kherz/pulseq-cest-library
``` 
**Option 3:** Download the [pulseq-cest-library](https://github.com/kherz/pulseq-cest-library) as a 
[ZIP file](https://github.com/kherz/pulseq-cest-library/archive/master.zip) and extract it into the 
[pulseq-cest-library](pulseq-cest-library).
