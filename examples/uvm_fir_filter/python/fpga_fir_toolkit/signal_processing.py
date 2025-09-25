"""
Signal Processing Module

This module provides functions for IQ signal generation, processing, 
and transmission chain simulation for communications applications.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional, Union


def generate_iq_signal(
    frequency: float,
    sampling_rate: float,
    duration: float,
    amplitude: float = 1.0,
    phase_offset: float = 0.0,
    modulation_type: str = 'cw',
    **kwargs
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate IQ signal for testing and simulation.
    
    Parameters:
    -----------
    frequency : float
        Signal frequency in Hz
    sampling_rate : float
        Sampling rate in Hz
    duration : float
        Signal duration in seconds
    amplitude : float, optional
        Signal amplitude
    phase_offset : float, optional
        Phase offset in radians
    modulation_type : str, optional
        Modulation type ('cw', 'qpsk', 'qam16', 'chirp')
    **kwargs
        Additional parameters for specific modulation types
        
    Returns:
    --------
    tuple
        (time_vector, i_signal, q_signal)
        
    Examples:
    ---------
    >>> t, i, q = generate_iq_signal(1000, 8000, 0.1)
    >>> print(f"Generated {len(i)} IQ samples")
    """
    # Generate time vector
    num_samples = int(duration * sampling_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    if modulation_type.lower() == 'cw':
        # Continuous wave
        i_signal = amplitude * np.cos(2 * np.pi * frequency * t + phase_offset)
        q_signal = amplitude * np.sin(2 * np.pi * frequency * t + phase_offset)
        
    elif modulation_type.lower() == 'qpsk':
        # QPSK modulation
        symbol_rate = kwargs.get('symbol_rate', frequency / 4)
        symbols_per_sample = sampling_rate / symbol_rate
        
        # Generate random QPSK symbols
        num_symbols = int(num_samples / symbols_per_sample) + 1
        qpsk_symbols = np.random.choice([1+1j, 1-1j, -1+1j, -1-1j], num_symbols)
        
        # Upsample and pulse shape
        upsampled = np.repeat(qpsk_symbols, int(symbols_per_sample))[:num_samples]
        
        # Apply carrier
        carrier_i = np.cos(2 * np.pi * frequency * t + phase_offset)
        carrier_q = np.sin(2 * np.pi * frequency * t + phase_offset)
        
        i_signal = amplitude * np.real(upsampled) * carrier_i - amplitude * np.imag(upsampled) * carrier_q
        q_signal = amplitude * np.real(upsampled) * carrier_q + amplitude * np.imag(upsampled) * carrier_i
        
    elif modulation_type.lower() == 'qam16':
        # 16-QAM modulation
        symbol_rate = kwargs.get('symbol_rate', frequency / 8)
        symbols_per_sample = sampling_rate / symbol_rate
        
        # 16-QAM constellation points
        qam16_points = np.array([
            -3-3j, -3-1j, -3+1j, -3+3j,
            -1-3j, -1-1j, -1+1j, -1+3j,
            +1-3j, +1-1j, +1+1j, +1+3j,
            +3-3j, +3-1j, +3+1j, +3+3j
        ]) / 3.0  # Normalize
        
        num_symbols = int(num_samples / symbols_per_sample) + 1
        qam_symbols = np.random.choice(qam16_points, num_symbols)
        
        upsampled = np.repeat(qam_symbols, int(symbols_per_sample))[:num_samples]
        
        carrier_i = np.cos(2 * np.pi * frequency * t + phase_offset)
        carrier_q = np.sin(2 * np.pi * frequency * t + phase_offset)
        
        i_signal = amplitude * np.real(upsampled) * carrier_i - amplitude * np.imag(upsampled) * carrier_q
        q_signal = amplitude * np.real(upsampled) * carrier_q + amplitude * np.imag(upsampled) * carrier_i
        
    elif modulation_type.lower() == 'chirp':
        # Linear frequency chirp
        f_start = kwargs.get('f_start', frequency)
        f_end = kwargs.get('f_end', frequency * 2)
        
        # Instantaneous frequency
        inst_freq = f_start + (f_end - f_start) * t / duration
        
        # Integrate to get phase
        phase = 2 * np.pi * np.cumsum(inst_freq) / sampling_rate + phase_offset
        
        i_signal = amplitude * np.cos(phase)
        q_signal = amplitude * np.sin(phase)
        
    else:
        raise ValueError(f"Unknown modulation type: {modulation_type}")
    
    return t, i_signal, q_signal


def apply_dual_iq_filter(
    i_signal: np.ndarray,
    q_signal: np.ndarray,
    filter_coefficients: np.ndarray,
    use_fixed_point: bool = False,
    **kwargs
) -> Tuple[np.ndarray, np.ndarray, dict]:
    """
    Apply FIR filtering to IQ signal pair.
    
    Parameters:
    -----------
    i_signal : np.ndarray
        I channel signal
    q_signal : np.ndarray
        Q channel signal
    filter_coefficients : np.ndarray
        FIR filter coefficients
    use_fixed_point : bool, optional
        Use fixed-point arithmetic simulation
    **kwargs
        Additional parameters for fixed-point processing
        
    Returns:
    --------
    tuple
        (i_filtered, q_filtered, processing_info)
        
    Examples:
    ---------
    >>> from filter_design import design_fir_lowpass
    >>> t, i, q = generate_iq_signal(1000, 8000, 0.1)
    >>> h = design_fir_lowpass(2000, 8000, 31)
    >>> i_filt, q_filt, info = apply_dual_iq_filter(i, q, h)
    """
    if use_fixed_point:
        from .fixed_point import float_to_fixed_point, apply_fixed_point_filter
        
        # Convert coefficients to fixed-point
        int_bits = kwargs.get('int_bits', 1)
        frac_bits = kwargs.get('frac_bits', 15)
        fixed_coeffs, conv_info = float_to_fixed_point(filter_coefficients, int_bits, frac_bits)
        
        # Apply fixed-point filtering
        i_filtered, i_info = apply_fixed_point_filter(i_signal, fixed_coeffs, frac_bits)
        q_filtered, q_info = apply_fixed_point_filter(q_signal, fixed_coeffs, frac_bits)
        
        processing_info = {
            'filter_type': 'fixed_point',
            'conversion_info': conv_info,
            'i_channel_info': i_info,
            'q_channel_info': q_info
        }
        
    else:
        from .filter_design import apply_fir_filter
        
        # Apply floating-point filtering
        i_filtered = apply_fir_filter(i_signal, filter_coefficients)
        q_filtered = apply_fir_filter(q_signal, filter_coefficients)
        
        processing_info = {
            'filter_type': 'floating_point',
            'num_taps': len(filter_coefficients)
        }
    
    # Calculate IQ-specific metrics
    original_power = np.mean(i_signal**2 + q_signal**2)
    filtered_power = np.mean(i_filtered**2 + q_filtered**2)
    
    original_magnitude = np.sqrt(i_signal**2 + q_signal**2)
    filtered_magnitude = np.sqrt(i_filtered**2 + q_filtered**2)
    
    processing_info.update({
        'power_ratio_db': 10 * np.log10(filtered_power / original_power) if original_power > 0 else float('-inf'),
        'magnitude_correlation': np.corrcoef(original_magnitude, filtered_magnitude)[0,1],
        'i_correlation': np.corrcoef(i_signal, i_filtered)[0,1],
        'q_correlation': np.corrcoef(q_signal, q_filtered)[0,1]
    })
    
    return i_filtered, q_filtered, processing_info


def simulate_transmission_chain(
    signal: np.ndarray,
    sampling_rate: float,
    carrier_freq: float,
    channel_noise_db: float = -40,
    phase_noise_std: float = 0.01,
    frequency_offset: float = 0.0,
    add_multipath: bool = False,
    **kwargs
) -> Tuple[np.ndarray, dict]:
    """
    Simulate RF transmission chain effects on baseband signal.
    
    Parameters:
    -----------
    signal : np.ndarray
        Input baseband signal
    sampling_rate : float
        Sampling rate in Hz
    carrier_freq : float
        Carrier frequency in Hz
    channel_noise_db : float, optional
        Channel noise power in dB relative to signal
    phase_noise_std : float, optional
        Phase noise standard deviation in radians
    frequency_offset : float, optional
        Frequency offset in Hz
    add_multipath : bool, optional
        Add multipath effects
    **kwargs
        Additional multipath parameters
        
    Returns:
    --------
    tuple
        (received_signal, transmission_info)
        
    Examples:
    ---------
    >>> signal = np.sin(2*np.pi*1000*np.linspace(0,1,8000))
    >>> rx_signal, info = simulate_transmission_chain(signal, 8000, 10000)
    """
    t = np.arange(len(signal)) / sampling_rate
    
    # Step 1: Modulation (upconvert to RF)
    carrier_phase = 2 * np.pi * carrier_freq * t
    if frequency_offset != 0:
        carrier_phase += 2 * np.pi * frequency_offset * t
    
    # Add phase noise
    if phase_noise_std > 0:
        phase_noise = np.cumsum(np.random.normal(0, phase_noise_std, len(signal)))
        carrier_phase += phase_noise
    else:
        phase_noise = np.zeros_like(signal)
    
    # Modulate
    rf_signal = signal * np.cos(carrier_phase)
    
    # Step 2: Channel effects
    channel_signal = rf_signal.copy()
    
    # Add AWGN
    signal_power = np.mean(rf_signal**2)
    noise_power_linear = signal_power * (10**(channel_noise_db/10))
    channel_noise = np.sqrt(noise_power_linear) * np.random.normal(0, 1, len(rf_signal))
    channel_signal += channel_noise
    
    # Multipath (simple 2-path model)
    if add_multipath:
        delay_samples = kwargs.get('multipath_delay_samples', 10)
        attenuation_db = kwargs.get('multipath_attenuation_db', -6)
        
        if delay_samples < len(signal):
            multipath_signal = np.zeros_like(channel_signal)
            multipath_signal[delay_samples:] = channel_signal[:-delay_samples]
            attenuation_linear = 10**(attenuation_db/20)
            channel_signal += attenuation_linear * multipath_signal
    
    # Step 3: Demodulation (downconvert)
    # Local oscillator (may have offset)
    lo_phase = 2 * np.pi * carrier_freq * t
    received_signal = 2 * channel_signal * np.cos(lo_phase)
    
    # Low-pass filter to remove double frequency components
    # (Simple moving average for demonstration)
    filter_taps = kwargs.get('demod_filter_taps', 21)
    if filter_taps > 1:
        lpf_kernel = np.ones(filter_taps) / filter_taps
        received_signal = np.convolve(received_signal, lpf_kernel, mode='same')
    
    # Calculate metrics
    snr_estimate = 10 * np.log10(signal_power / np.var(channel_noise))
    
    transmission_info = {
        'carrier_frequency': carrier_freq,
        'frequency_offset': frequency_offset,
        'phase_noise_std': phase_noise_std,
        'channel_noise_db': channel_noise_db,
        'estimated_snr_db': snr_estimate,
        'signal_power': signal_power,
        'noise_power': np.var(channel_noise),
        'multipath_enabled': add_multipath,
        'demod_filter_taps': filter_taps
    }
    
    if add_multipath:
        transmission_info['multipath_delay_samples'] = kwargs.get('multipath_delay_samples', 10)
        transmission_info['multipath_attenuation_db'] = kwargs.get('multipath_attenuation_db', -6)
    
    return received_signal, transmission_info


def analyze_iq_constellation(
    i_signal: np.ndarray,
    q_signal: np.ndarray,
    reference_constellation: Optional[np.ndarray] = None,
    plot_results: bool = True
) -> dict:
    """
    Analyze IQ constellation diagram and calculate metrics.
    
    Parameters:
    -----------
    i_signal : np.ndarray
        I channel samples
    q_signal : np.ndarray
        Q channel samples
    reference_constellation : np.ndarray, optional
        Reference constellation points for EVM calculation
    plot_results : bool, optional
        Generate constellation plot
        
    Returns:
    --------
    dict
        Constellation analysis results
        
    Examples:
    ---------
    >>> t, i, q = generate_iq_signal(1000, 8000, 0.1, modulation_type='qpsk')
    >>> metrics = analyze_iq_constellation(i, q)
    >>> print(f"Signal magnitude: {metrics['magnitude_mean']:.3f}")
    """
    # Convert to complex representation
    iq_complex = i_signal + 1j * q_signal
    
    # Basic metrics
    magnitude = np.abs(iq_complex)
    phase = np.angle(iq_complex)
    
    metrics = {
        'num_samples': len(iq_complex),
        'magnitude_mean': np.mean(magnitude),
        'magnitude_std': np.std(magnitude),
        'magnitude_range': (np.min(magnitude), np.max(magnitude)),
        'phase_mean': np.mean(phase),
        'phase_std': np.std(phase),
        'phase_range': (np.min(phase), np.max(phase)),
        'i_mean': np.mean(i_signal),
        'i_std': np.std(i_signal),
        'q_mean': np.mean(q_signal),
        'q_std': np.std(q_signal),
        'iq_correlation': np.corrcoef(i_signal, q_signal)[0,1]
    }
    
    # EVM calculation if reference provided
    if reference_constellation is not None:
        evm_values = []
        for sample in iq_complex:
            # Find closest reference point
            distances = np.abs(reference_constellation - sample)
            closest_ref = reference_constellation[np.argmin(distances)]
            error_vector = sample - closest_ref
            evm_values.append(np.abs(error_vector))
        
        evm_rms = np.sqrt(np.mean(np.array(evm_values)**2))
        ref_power = np.mean(np.abs(reference_constellation)**2)
        evm_percent = (evm_rms / np.sqrt(ref_power)) * 100
        
        metrics['evm_rms'] = evm_rms
        metrics['evm_percent'] = evm_percent
        metrics['evm_db'] = 20 * np.log10(evm_percent / 100)
    
    # Generate constellation plot
    if plot_results:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Constellation diagram
        ax1.scatter(i_signal[::10], q_signal[::10], alpha=0.6, s=1)
        ax1.set_xlabel('I Channel')
        ax1.set_ylabel('Q Channel')
        ax1.set_title('IQ Constellation')
        ax1.grid(True, alpha=0.3)
        ax1.axis('equal')
        
        if reference_constellation is not None:
            ax1.scatter(np.real(reference_constellation), np.imag(reference_constellation),
                       c='red', s=50, marker='x', linewidth=2, label='Reference')
            ax1.legend()
        
        # Magnitude histogram
        ax2.hist(magnitude, bins=50, alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Magnitude')
        ax2.set_ylabel('Count')
        ax2.set_title('Magnitude Distribution')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        metrics['constellation_plot'] = fig
    
    return metrics


def plot_iq_signals(
    time_vector: np.ndarray,
    i_signal: np.ndarray,
    q_signal: np.ndarray,
    title: str = "IQ Signals",
    plot_constellation: bool = True,
    figsize: Tuple[int, int] = (15, 10)
) -> plt.Figure:
    """
    Plot IQ signals in time and frequency domains.
    
    Parameters:
    -----------
    time_vector : np.ndarray
        Time vector in seconds
    i_signal : np.ndarray
        I channel signal
    q_signal : np.ndarray
        Q channel signal
    title : str, optional
        Plot title
    plot_constellation : bool, optional
        Include constellation diagram
    figsize : tuple, optional
        Figure size
        
    Returns:
    --------
    plt.Figure
        Figure containing IQ analysis plots
    """
    if plot_constellation:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
    else:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize)
        ax4 = None
    
    # Time domain plots
    ax1.plot(time_vector * 1000, i_signal, 'b-', label='I Channel', alpha=0.8)
    ax1.plot(time_vector * 1000, q_signal, 'r-', label='Q Channel', alpha=0.8)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title(f'{title} - Time Domain')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Frequency domain
    sampling_rate = 1 / (time_vector[1] - time_vector[0])
    freqs = np.fft.fftfreq(len(i_signal), 1/sampling_rate)
    i_fft = np.fft.fft(i_signal)
    q_fft = np.fft.fft(q_signal)
    
    # Plot positive frequencies only
    pos_mask = freqs >= 0
    ax2.plot(freqs[pos_mask], 20*np.log10(np.abs(i_fft[pos_mask]) + 1e-10), 'b-', label='I Channel', alpha=0.8)
    ax2.plot(freqs[pos_mask], 20*np.log10(np.abs(q_fft[pos_mask]) + 1e-10), 'r-', label='Q Channel', alpha=0.8)
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude (dB)')
    ax2.set_title(f'{title} - Frequency Domain')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Magnitude and phase
    magnitude = np.sqrt(i_signal**2 + q_signal**2)
    phase = np.arctan2(q_signal, i_signal)
    
    ax3.plot(time_vector * 1000, magnitude, 'g-', label='Magnitude', alpha=0.8)
    ax3_phase = ax3.twinx()
    ax3_phase.plot(time_vector * 1000, np.degrees(phase), 'm-', label='Phase', alpha=0.8)
    ax3.set_xlabel('Time (ms)')
    ax3.set_ylabel('Magnitude', color='g')
    ax3_phase.set_ylabel('Phase (degrees)', color='m')
    ax3.set_title(f'{title} - Magnitude and Phase')
    ax3.grid(True, alpha=0.3)
    
    # Constellation diagram
    if plot_constellation and ax4 is not None:
        # Subsample for cleaner plot
        subsample = max(1, len(i_signal) // 1000)
        ax4.scatter(i_signal[::subsample], q_signal[::subsample], alpha=0.6, s=1)
        ax4.set_xlabel('I Channel')
        ax4.set_ylabel('Q Channel')
        ax4.set_title(f'{title} - Constellation')
        ax4.grid(True, alpha=0.3)
        ax4.axis('equal')
    
    plt.tight_layout()
    return fig