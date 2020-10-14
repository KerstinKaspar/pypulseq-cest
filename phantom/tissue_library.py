"""
tissue_library.py
    file to set the correct T1 and T2 parameters according to tissuees (gray matter, white matter, CSF) for the phantom
"""

def get_t1(tissue: str, b0: float = 3) -> float:
    """
    function to return the correct t1 time for the according field strength and matter
    :param: tissue str ("gm" for gray matter, "wm" for white matter, "csf" for CSF)
    :param: b0 float (field strength in T)
    :return: t1 float (T1 in s)
    """
    try:
        if tissue == "gm":
            if round(b0) < 4:
                t1 = 1.3 # source pulseq-cest
            elif 4 < round(b0) < 9:  # 7T
                t1 = 1.67 # source pulseq-cest
            # elif round(b0) >= 9:  # 9.4 T and above
            #     t1 = 2.0  # [Hz]
            else:
                t1 = 1.3
                print(b0, "T is not an implemented field strength. Assuming 3T for function set_t1.")
    # TODO implement correct T1 times
        elif tissue == "wm":
            if round(b0) < 4:
                t1 = 0.8 # source PMID: 10232510
            elif 4 < round(b0) < 9:  # 7T
                t1 = 1.1 # estimated, no scouce
            # elif round(b0) >= 9:  # 9.4 T and above
            #     t1 = ??
            else:
                t1 = 0.8
                print(b0, "T is not an implemented field strength. Assuming 3T for function set_t1.")
        elif tissue == "csf":
            if round(b0) < 4:
                t1 = 4.1 # estimated PMID: 31179645
            elif 4 < round(b0) < 9:  # 7T
                t1 = 4.4 # source PMID: 17260370
            # elif round(b0) >= 9:  # 9.4 T and above
            #     t1 = ??
            else:
                t1 = 1.3
                print(b0, "T is not an implemented field strength. Assuming 3T for function set_t1.")
    except ValueError:
        print(tissue, " is not implemented as a tissue type.")
    return t1


def get_t2(tissue: str, b0: float = 3) -> float:
    """
    function to return the correct t1 time for the according field strength and matter
    :param tissue: str ("gm" for gray matter, "wm" for white matter, "csf" for CSF)
    :param b0: float (field strength in T)
    :return t2: float (T2 in s)
    """
    try:
        if tissue == "gm":
            if round(b0) < 4:
                t2 = 80e-3 # source PMID: 10232510, vs. pulseq-cest 75e-3
            elif 4 < round(b0) < 9:  # 7T
                t2 = 43e-3 # source pulseq-cest
            # elif round(b0) >= 9:  # 9.4 T and above
            #     t2 = 35e-3
        # TODO implement correct T2 times
        if tissue == "wm":
            if round(b0) < 4:
                t2 = 110e-3 # source PMID: 10232510
            elif 4 < round(b0) < 9:  # 7T
                t2 = 60e-3 # estimated, no scouce
            # elif round(b0) >= 9:  # 9.4 T and above
            #     t2 = ??
        if tissue == "csf":
            if round(b0) < 4:
                t2 = 2 # source PMID: 28782676
            elif 4 < round(b0) < 9:  # 7T
                t2 = 0.9 # source PMID: 28782676
            # elif round(b0) >= 9:  # 9.4 T and above
            #     t2 = ??
    except ValueError:
        print(tissue, " is not implemented as a tissue type.")
    return t2