"""
FIR Filter Design Module

This module contains functions for designing FIR filters with various
window functions and plotting their frequency responses.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz
from typing import Tuple, Optional, Union


def design_fir_lowpass(
    cutoff_freq: float,
    sampling_rate: float, 
    num_taps: int,
    window: str = 'hamming',
    normalize_dc: bool = True
) -> np.ndarray:
    """
    Design a lowpass FIR filter using the windowed sinc method.
    
    Parameters:
    -----------
    cutoff_freq : float
        Cutoff frequency in Hz
    sampling_rate : float
        Sampling rate in Hz
    num_taps : int
        Number of filter taps (filter length)
    window : str, optional
        Window function ('hamming', 'hanning', 'blackman', 'bartlett', 'rectangular')
    normalize_dc : bool, optional
        Whether to normalize DC gain to 1.0
        
    Returns:
    --------
    np.ndarray
        FIR filter coefficients
        
    Examples:
    ---------
    >>> h = design_fir_lowpass(1000, 8000, 31)
    >>> print(f"Designed {len(h)} tap lowpass filter")
    """
    # Normalize cutoff frequency (0 to 1, where 1 is Nyquist)
    normalized_cutoff = cutoff_freq / (sampling_rate / 2)
    
    # Create time indices centered around 0
    n = np.arange(num_taps)
    n_center = (num_taps - 1) / 2
    
    # Generate ideal sinc response
    h_ideal = np.sinc(normalized_cutoff * (n - n_center))
    
    # Apply window function
    if window.lower() == 'hamming':
        w = np.hamming(num_taps)
    elif window.lower() == 'hanning':
        w = np.hanning(num_taps)
    elif window.lower() == 'blackman':
        w = np.blackman(num_taps)
    elif window.lower() == 'bartlett':
        w = np.bartlett(num_taps)
    elif window.lower() == 'rectangular':
        w = np.ones(num_taps)
    else:
        raise ValueError(f"Unknown window type: {window}")
    
    # Apply window
    h = h_ideal * w
    
    # Normalize DC gain to 1.0 if requested
    if normalize_dc:
        dc_gain = np.sum(h)
        if dc_gain != 0:
            h = h / dc_gain
    
    return h


def apply_fir_filter(signal: np.ndarray, coefficients: np.ndarray, mode: str = 'causal') -> np.ndarray:
    """
    Apply FIR filter to a signal using convolution.
    
    Parameters:
    -----------
    signal : np.ndarray
        Input signal to filter
    coefficients : np.ndarray
        FIR filter coefficients
    mode : str, optional
        Convolution mode: 'same' (centered, non-causal) or 'causal' (FPGA-realistic)
        
    Returns:
    --------
    np.ndarray
        Filtered signal (same length as input)
        
    Examples:
    ---------
    >>> signal = np.random.randn(1000)
    >>> h = design_fir_lowpass(100, 1000, 31)
    >>> filtered = apply_fir_filter(signal, h, mode='causal')  # FPGA-realistic
    >>> filtered_centered = apply_fir_filter(signal, h, mode='same')  # Centered
    """
    if mode == 'causal':
        # Causal FIR filter - only uses past and current samples (FPGA-realistic)
        N = len(signal)
        M = len(coefficients)
        filtered = np.zeros(N)
        
        for n in range(N):
            for k in range(M):
                if (n - k) >= 0:
                    filtered[n] += signal[n - k] * coefficients[k]
        
        return filtered
    else:
        # Use 'same' mode to return same length as input (centered, non-causal)
        return np.convolve(signal, coefficients, mode='same')


def plot_filter_response(
    coefficients: np.ndarray,
    sampling_rate: float,
    title: str = "FIR Filter Frequency Response",
    figsize: Tuple[int, int] = (12, 8)
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
    """
    Plot the frequency and impulse response of an FIR filter.
    
    Parameters:
    -----------
    coefficients : np.ndarray
        FIR filter coefficients
    sampling_rate : float
        Sampling rate in Hz
    title : str, optional
        Plot title
    figsize : tuple, optional
        Figure size (width, height)
        
    Returns:
    --------
    tuple
        (figure, (freq_axis, impulse_axis))
        
    Examples:
    ---------
    >>> h = design_fir_lowpass(1000, 8000, 31)
    >>> fig, axes = plot_filter_response(h, 8000)
    >>> plt.show()
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    
    # Frequency response
    w, h = freqz(coefficients, worN=8000)
    frequencies = w * sampling_rate / (2 * np.pi)
    
    ax1.plot(frequencies, 20 * np.log10(np.abs(h)))
    ax1.set_title(f"{title} - Magnitude Response")
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Magnitude (dB)')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, sampling_rate/2)
    
    # Impulse response  
    ax2.stem(range(len(coefficients)), coefficients, basefmt=" ")
    ax2.set_title(f"{title} - Impulse Response")
    ax2.set_xlabel('Sample')
    ax2.set_ylabel('Amplitude')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig, (ax1, ax2)


def analyze_filter_performance(
    coefficients: np.ndarray,
    sampling_rate: float,
    cutoff_freq: float,
    stopband_freq: Optional[float] = None
) -> dict:
    """
    Analyze FIR filter performance metrics.
    
    Parameters:
    -----------
    coefficients : np.ndarray
        FIR filter coefficients
    sampling_rate : float
        Sampling rate in Hz
    cutoff_freq : float
        Design cutoff frequency in Hz
    stopband_freq : float, optional
        Stopband frequency for attenuation measurement
        
    Returns:
    --------
    dict
        Performance metrics including passband ripple, stopband attenuation, etc.
    """
    w, h = freqz(coefficients, worN=8000)
    frequencies = w * sampling_rate / (2 * np.pi)
    magnitude_db = 20 * np.log10(np.abs(h))
    
    # Find DC gain
    dc_gain_db = magnitude_db[0]
    
    # Find -3dB point
    three_db_idx = np.argmin(np.abs(magnitude_db - (dc_gain_db - 3)))
    actual_3db_freq = frequencies[three_db_idx]
    
    # Passband ripple (up to cutoff frequency)
    cutoff_idx = np.argmin(np.abs(frequencies - cutoff_freq))
    passband_mag = magnitude_db[:cutoff_idx]
    passband_ripple = np.max(passband_mag) - np.min(passband_mag)
    
    metrics = {
        'dc_gain_db': dc_gain_db,
        'actual_3db_frequency': actual_3db_freq,
        'designed_cutoff_frequency': cutoff_freq,
        'frequency_error': actual_3db_freq - cutoff_freq,
        'passband_ripple_db': passband_ripple,
        'num_taps': len(coefficients)
    }
    
    # Stopband attenuation if stopband frequency provided
    if stopband_freq:
        stopband_idx = np.argmin(np.abs(frequencies - stopband_freq))
        if stopband_idx < len(magnitude_db):
            metrics['stopband_attenuation_db'] = dc_gain_db - magnitude_db[stopband_idx]
            
    return metrics