import numpy as np


def block(steps):
    """Block/cw pulse without phase modulation"""
    x = np.linspace(0, 1, steps+1)
    amp = np.ones_like(x)
    phase = np.zeros_like(x)
    return amp, phase


def gauss_siemens(steps):
    """Gaussian shaped pulse as used on SIEMENS scanners (version VD, 20 ms, 0.6 µT)."""
    x = np.linspace(0, 1, steps+1)
    amp = 1.0*(-25.88 * x**6 + 76.88 * x**5 - 67.47 * x**4 + 8.011 * x**3 + 8.034 * x**2 + 0.4235 * x - 0.0002965)
    phase = x*0
    return amp, phase
