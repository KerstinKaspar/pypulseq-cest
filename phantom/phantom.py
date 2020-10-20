"""
phantom.py
    define a phantom with simulation parameters for CEST or WASABI simulations
"""

import numpy as np
from phantom.tissue_library import get_t1, get_t2


def phantom_ellipses(npx: int, ellipses: np.array = None) -> np.array:
    """
    converts the ellipse definitions into ellipses with the specified intensities on the array grid
    :param npx: number of pixels for the phantom
    :param ellipses: list of ellipse definitions
    :return p: array of size npx x npx
    """
    # Create blank image
    p = np.zeros((npx, npx))

    # Create the pixel grid
    ygrid, xgrid = np.mgrid[-1:1:(1j * npx), -1:1:(1j * npx)]

    for e in ellipses:
        I = e[0]
        a2 = e[1] ** 2
        b2 = e[2] ** 2
        x0 = e[3]
        y0 = e[4]
        phi = e[5] * np.pi / 180  # Rotation angle in radians

        # Create the offset x and y values for the grid
        x = xgrid - x0
        y = ygrid - y0

        cos_p = np.cos(phi)
        sin_p = np.sin(phi)

        # Find the pixels within the ellipse
        locs = (((x * cos_p + y * sin_p) ** 2) / a2
                + ((y * cos_p - x * sin_p) ** 2) / b2) <= 1

        # Add the ellipse intensity to those pixels
        p[locs] += I

    return p


def phantom_tissues(npx: int = 128, b0: float = 3, f_tissue: (str, None) = 'wm', noise_tissue: (str, None) = 'wm') -> np.array:
    """
    creates a phantom_examples for the stated tissue types (gm: gray matter, wm: white matter and csf: cerebrospinal fluid)
    with the according t1 and t2 values from tissue_library.py and optionally a range of pool-fraction-parameters for
    one of the tissue types (if f_matter = "gm", "wm" or "csf").
    :param  npx: int (pixel size of the phantom_examples, default = 128)
    :param  f_tissue: str (optional tissue type to create a fraction range, default = "wm", set to None for no
            fraction range in the phantom)
    :param noise_tissue: str (optional tissue type to create a noise range, default = "wm", set to None for no
            noise range in the phantom)
    :param b0: float (field strength in T, default = 3)
    :return phantom_t: np.array (size [2, npx, npx] with phantom_examples[0] containing T1 and phantom_examples[1]
    containing T2 values for each pixel
    """
    tissues = ["gm", "wm", "csf"]
    phantom_t = np.zeros([2, npx, npx])
    phantom_base = [[0., .6900, .920, 0., 0., 0.]]
    compartments = [[0, .6624, .874, 0., -.0184, 0.],
                    [0, .16, .41, -.22, -.2, 18],  # [0.5, .16, .41, -.22, -.2, 18],
                    [0, .12, .31, .22, -.12, -12]]  # [0.4, .11, .31, .22, -.12, -12]]
    for t in range(2):
        phantom_temp = phantom_base.copy()
        for i in range(len(tissues)):
            t_comp = compartments[i]
            if t == 0:
                t_comp[0] = get_t1(tissue=tissues[i], b0=0)
            elif t == 1:
                t_comp[0] = get_t2(tissue=tissues[i], b0=0)
            phantom_temp.append(t_comp)
        phantom_t[t, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_temp)
    # TODO wm t1
    if f_tissue:
        phantom_t[0, 84:90, 44:84] = get_t1(tissue=f_tissue, b0=b0)
        phantom_t[1, 84:90, 44:84] = get_t2(tissue=f_tissue, b0=b0)
    if noise_tissue:
        phantom_t[0, 94:100, 44:84] = get_t1(tissue=noise_tissue, b0=b0)
        phantom_t[1, 94:100, 44:84] = get_t2(tissue=noise_tissue, b0=b0)
    return phantom_t


def phantom_fractions(npx: int = 128, f_base: float = 10e-3, n_fractions: int = 10, f_range: tuple = (0, 10e-3)) \
        -> np.array:
    """
    defining a phantom with a section of bar-shaped continouously spaced fraction parameters
    :param npx: pixel size of the phantom
    :param f_base: fraction parameter for the phantom outside the fraction bar
    :param n_fractions: number of fractions to split the fraction bar into
    :param f_range: (min, max) of the fraction parameters in the fraction bar
    :return phantom_f: array of size (1, npx, npx)
    """
    compartments = np.linspace(44, 84, n_fractions)
    fractions = np.linspace(f_range[0], f_range[1], n_fractions)
    phantom_f = np.zeros([1, npx, npx])
    phantom_base = [[f_base, .6900, .920, 0., 0., 0.]]
    phantom_f[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    for i in range(n_fractions-1):
        phantom_f[0, 84:90, int(round(compartments[i])):int(round(compartments[i+1]))] = fractions[i]
    return phantom_f


def phantom_b1_inhom(npx: int = 128, min_inhom: float = -0.3, max_inhom: float = 0.3) -> np.array:
    """
    creating a phantom with radial B1 inhomogeneities
    :param npx: pixel size of the phantom
    :param min_inhom: minimal b1 inhomogeneity in percent (factor in range -1 and 1)
    :param max_inhom: maximal b1 inhomogeneity in percent (factor in range -1 and 1)
    :return phantom_b1: array of size (1, npx, npx) with values for relative B1 of range 1-min_inhom and 1+ max_inhom
    """
    phantom_b1 = np.zeros([1, npx, npx])
    phantom_base = [[1, .6900, .920, 0., 0., 0.]]
    phantom_b1[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    inhom_range = max_inhom - min_inhom
    x = y = np.linspace(-inhom_range, inhom_range, 128)
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx ** 2 + yy ** 2)
    b1_inhom = np.ones((128, 128)) * 0.3 - r
    phantom_b1[0, :, :] = phantom_b1[0, :, :] * b1_inhom + 1
    return phantom_b1


def phantom_b0_inhom(npx: int = 128, min_inhom: float = -0.3, max_inhom: float = 0.3) -> np.array:
    """
    creating a phantom with linear B0 field inhomogeneities
    :param npx: pixel size of the phantom
    :param min_inhom: minimal B0 shift in ppm
    :param max_inhom: maximal B0 shift in ppm
    :return phantom_b1: array of size (1, npx, npx) with values for B0-shift
    """
    phantom_b0 = np.zeros([1, npx, npx])
    phantom_base = [[1, .6900, .920, 0., 0., 0.]]
    phantom_b0[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    b0_inhom = np.linspace(min_inhom, max_inhom, npx*npx).reshape(npx, npx)
    phantom_b0[0, :, :] = phantom_b0[0, :, :] * b0_inhom
    return phantom_b0


def build_default_phantom(npx: int = 128, fractions: bool = True, noise: bool = True) -> np.array:
    """
    building a default phantom at 3T with parameters for a large GM ellipse, 2 WM ellipses, 1 CSF ellipse,
    optionally with a bar of WM parameters and continuously spaced fractions
    :param npx: pixel size of the phantom
    :param fractions: bool to define the fraction option (default: True)
    :param noise: bool to define the noise option (default: True)
    :return phantom: array of size (4, npx, npx) without or (5, npx, npx) with fractions containing the T1, T2,
    B0 inhomogeneities, B1 inhomogeneities and possibly fractions for each pixel respectively
    """
    phantom_t = phantom_tissues(npx)
    phantom_b0 = phantom_b0_inhom(npx)
    phantom_b1 = phantom_b1_inhom(npx)
    phantom = np.concatenate([phantom_t, phantom_b0, phantom_b1])
    if fractions:
        phantom_f = phantom_fractions(npx)
        phantom = np.concatenate([phantom, phantom_f])
    if noise:
        phantom_n = phantom_noise(npx)
        phantom = np.concatenate([phantom, phantom_n])
    return phantom


def build_phantom(phantom_t: np.array, phantom_b0: np.array, phantom_b1: np.array, phantom_f: np.array = None):
    """
    building a phantom from the individual parameter phantoms
    :param phantom_t: array of size (2, npx, npx) containing the T1 and T2 values of the pixels
    :param phantom_b0: array of size (1, npx, npx) containing the B0 shift values for each pixel
    :param phantom_b1: array of size (1, npx, npx) containing the relative B1 values for each pixel
    :param phantom_f: optional array of size (1, npx, npx) containing the fraction values for each pixel
    :return phantom: array of size (4, npx, npx) without or (5, npx, npx) with fractions containing the T1, T2,
    B0 inhomogeneities, B1 inhomogeneities and possibly fractions for each pixel respectively
    """
    phantom = np.concatenate([phantom_t, phantom_b0, phantom_b1])
    if phantom_f.any():
        return np.concatenate([phantom, phantom_f])
    # TODO noise
    else:
        return phantom


def phantom_noise(npx: int = 128, mean: float = 0, std_base: float = 0, n: int = 10, std_max: float = 0.1) -> np.array:
    compartments = np.linspace(44, 84, n)
    # vars = np.linspace(var_base, var_max, n)
    # sigmas = vars ** 0.5
    sigmas = np.linspace(std_base, std_max, n)
    phantom_n = np.zeros([1, npx, npx])
    phantom_base = [[1, .6900, .920, 0., 0., 0.]]
    phantom_n[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    noise = np.random.normal(mean, sigmas[0], phantom_n.shape)
    phantom_n = phantom_n * noise
    for i in range(n-1):
        idx = [int(round(compartments[i])), int(round(compartments[i+1]))]
        noise = np.random.normal(mean, sigmas[i], phantom_n[0, 94:100, idx[0]:idx[1]].shape)
        phantom_n[0, 94:100, idx[0]:idx[1]] = noise
    return phantom_n

# # Phantom playground
# import matplotlib.pyplot as plt
#
# phantom_base = [[0., .6900, .920, 0., 0., 0.],
#                 [1, .6624, .874, 0., -.0184, 0.],
#                 [0.5, .16, .41, -.22, -.2, 18],  # [0.5, .16, .41, -.22, -.2, 18],
#                 [0.4, .12, .31, .22, -.12, -12]]  # [0.4, .11, .31, .22, -.12, -12]]
#
# p = phantom_ellipses(128, phantom_base)
# p[84:90, 44:84] = 0.2
# p[94:100, 44:84] = 0.1
#
#
# plt.figure()
# plt.imshow(p[0])
# plt.show()

