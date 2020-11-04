from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove


def convert_seq_12_to_pseudo_13(file_path: str):
    """
    Converts version 1.2 seq-files to pseudo version 1.3 seq-files.
    """

    # create a temp file
    tmp, abs_path = mkstemp()

    in_blocks = False
    with fdopen(tmp, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                if line.startswith('minor'):
                    if int(line[len('minor '):]) == 2:
                        new_file.write(line.replace('2', '3'))
                    else:
                        raise Exception(f'Version of seq-file (v. 1.{int(line[len("minor "):])}) '
                                        f'differs from expected version 1.2. Conversion aborted!')
                elif all(x in line for x in ['RF', 'GX', 'GY', 'GZ', 'ADC']):
                    new_file.write(''.join([line.strip(), ' EXT\n']))
                elif line.startswith('[BLOCKS]'):
                    new_file.write(line)
                    in_blocks = True
                else:
                    if in_blocks and line.strip() != '':
                        new_file.write(''.join([line.strip(), '  0\n']))
                    else:
                        new_file.write(line)
                        in_blocks = False

    # copy permissions from old file to new file
    copymode(file_path, abs_path)
    # remove old file
    remove(file_path)
    # move new file
    move(abs_path, file_path)
