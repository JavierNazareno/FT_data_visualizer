# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 12:40:05 2025

@author: javie
"""
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import butter, filtfilt


class signal_analysis:
    def __init__(self, time, amplitude):
        self.t = np.array(time)
        self.x = np.array(amplitude)

    def damped_cosine(self, t, A, zeta, omega_n, phi):
        wd = omega_n * np.sqrt(1 - zeta**2)
        return A * np.exp(-zeta * omega_n * t) * np.cos(wd * t + phi)

    def fit(self, p0=None, remove_static=False, cutoff_ratio=0.01):
        """
        Fit the damped cosine model. Optionally remove static offset with high-pass filtering.
        """
        x_input = self.x.copy()
    
        if remove_static:
            fs = 1 / np.median(np.diff(self.t))
            cutoff = cutoff_ratio * fs  # e.g., 1% of Nyquist
            x_input = butter_highpass_filter(x_input, cutoff=cutoff, fs=fs)
    
        if p0 is None:
            A0 = np.max(np.abs(x_input))
            omega_guess = 2 * np.pi / (self.t[-1] - self.t[0])
            p0 = [A0, 0.1, omega_guess, 0.0]
    
        popt, _ = curve_fit(self.damped_cosine, self.t, x_input, p0=p0, maxfev=10000)
        approx = self.damped_cosine(self.t, *popt)
    
        # Derived quantities
        A_fit, zeta_fit, omega_n_fit, phi_fit = popt
        wd = omega_n_fit * np.sqrt(1 - zeta_fit**2)
        T = 2 * np.pi / wd
        delta = 2 * zeta_fit * omega_n_fit
        t2 = np.log(2) / (zeta_fit * omega_n_fit) if zeta_fit * omega_n_fit != 0 else np.inf
    
        results = {
            "A": A_fit,
            "zeta": zeta_fit,
            "omega_n": omega_n_fit,
            "phi": phi_fit,
            "omega_d": wd,
            "delta": delta,
            "T": T,
            "t2 (half/double)": t2
        }
    
        return approx, x_input, results  # include filtered signal


def butter_highpass_filter(data, cutoff, fs, order=8):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return filtfilt(b, a, data)