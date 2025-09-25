"""
ADC/DAC Simulation Module

This module simulates analog-to-digital and digital-to-analog converters
commonly found in FPGA designs, including quantization effects and DC bias.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional, Union


def simulate_8bit_adc(
    signal: np.ndarray,
    adc_range: Tuple[float, float] = (0.0, 2.5),
    dc_bias: float = 1.25,
    bits: int = 8,
    add_noise: bool = False,
    noise_std: float = 0.001
) -> Tuple[np.ndarray, dict]:
    """
    Simulate an 8-bit ADC with DC bias for unipolar operation.
    
    Parameters:
    -----------
    signal : np.ndarray
        Input bipolar signal (typically -1 to +1 range)
    adc_range : tuple, optional
        ADC input voltage range (min_voltage, max_voltage)  
    dc_bias : float, optional
        DC bias voltage to shift bipolar signal to unipolar
    bits : int, optional
        ADC resolution in bits
    add_noise : bool, optional
        Whether to add ADC noise
    noise_std : float, optional
        Standard deviation of ADC noise
        
    Returns:
    --------
    tuple
        (digitized_signal, adc_info)
        - digitized_signal: Signal after ADC processing and bias removal
        - adc_info: Dictionary with ADC performance metrics
        
    Examples:
    ---------
    >>> t = np.linspace(0, 1, 1000)  
    >>> signal = np.sin(2*np.pi*10*t)
    >>> digital, info = simulate_8bit_adc(signal)
    >>> print(f"ADC SNR: {info['snr_db']:.1f} dB")
    """
    # Add DC bias to make signal unipolar
    biased_signal = signal + dc_bias
    
    # Clip to ADC input range
    adc_min, adc_max = adc_range
    clipped_signal = np.clip(biased_signal, adc_min, adc_max)
    
    # Track clipping
    clipped_samples = np.sum((biased_signal < adc_min) | (biased_signal > adc_max))
    
    # Quantization
    num_levels = 2 ** bits
    lsb = (adc_max - adc_min) / num_levels
    
    # Normalize to 0-1 range
    normalized = (clipped_signal - adc_min) / (adc_max - adc_min)
    
    # Quantize
    quantized_levels = np.floor(normalized * num_levels)
    # Avoid overflow on maximum value
    quantized_levels = np.clip(quantized_levels, 0, num_levels - 1)
    
    # Convert back to voltage
    quantized_voltage = (quantized_levels / num_levels) * (adc_max - adc_min) + adc_min
    
    # Add ADC noise if requested
    if add_noise:
        quantized_voltage += np.random.normal(0, noise_std, len(quantized_voltage))
    
    # Remove DC bias digitally  
    digitized_signal = quantized_voltage - dc_bias
    
    # Calculate performance metrics
    original_power = np.var(signal)
    quantization_error = signal - digitized_signal
    noise_power = np.var(quantization_error)
    
    snr_db = 10 * np.log10(original_power / noise_power) if noise_power > 0 else float('inf')
    enob = (snr_db - 1.76) / 6.02  # Effective Number of Bits
    
    # Calculate utilization
    utilized_levels = np.max(quantized_levels) - np.min(quantized_levels) + 1
    utilization = utilized_levels / num_levels
    
    adc_info = {
        'bits': bits,
        'adc_range': adc_range,
        'dc_bias': dc_bias,
        'lsb_voltage': lsb,
        'num_levels': num_levels,
        'utilized_levels': utilized_levels,
        'utilization': utilization,
        'clipped_samples': clipped_samples,
        'clipping_rate': clipped_samples / len(signal),
        'snr_db': snr_db,
        'enob': enob,
        'signal_range': (np.min(signal), np.max(signal)),
        'biased_range': (np.min(biased_signal), np.max(biased_signal)),
        'quantized_levels_range': (np.min(quantized_levels), np.max(quantized_levels))
    }
    
    return digitized_signal, adc_info


def simulate_dual_8bit_adc(
    i_signal: np.ndarray,
    q_signal: np.ndarray,
    adc_range: Tuple[float, float] = (0.0, 2.5),
    dc_bias: float = 1.25,
    bits: int = 8,
    mismatch_gain: float = 0.0,
    mismatch_offset: float = 0.0,
    mismatch_phase: float = 0.0
) -> Tuple[Tuple[np.ndarray, np.ndarray], dict]:
    """
    Simulate dual 8-bit ADCs for IQ signal processing.
    
    Models I/Q ADC pairs commonly used in communications systems,
    including gain/offset mismatches between channels.
    
    Parameters:
    -----------
    i_signal : np.ndarray
        In-phase signal component
    q_signal : np.ndarray  
        Quadrature signal component
    adc_range : tuple, optional
        ADC input voltage range
    dc_bias : float, optional
        DC bias for unipolar ADCs
    bits : int, optional
        ADC resolution in bits
    mismatch_gain : float, optional
        Gain mismatch between I and Q channels (fractional)
    mismatch_offset : float, optional
        DC offset mismatch between channels
    mismatch_phase : float, optional
        Phase mismatch in radians
        
    Returns:
    --------
    tuple
        ((i_digital, q_digital), iq_adc_info)
        
    Examples:
    ---------
    >>> t = np.linspace(0, 1, 1000)
    >>> i_sig = np.cos(2*np.pi*10*t)
    >>> q_sig = np.sin(2*np.pi*10*t) 
    >>> (i_dig, q_dig), info = simulate_dual_8bit_adc(i_sig, q_sig)
    """
    # Apply I/Q mismatches
    i_modified = i_signal * (1 + mismatch_gain) + mismatch_offset
    q_modified = q_signal * np.cos(mismatch_phase) + i_signal * np.sin(mismatch_phase)
    
    # Process through individual ADCs
    i_digital, i_info = simulate_8bit_adc(i_modified, adc_range, dc_bias, bits)
    q_digital, q_info = simulate_8bit_adc(q_modified, adc_range, dc_bias, bits)
    
    # Calculate IQ-specific metrics
    original_magnitude = np.sqrt(i_signal**2 + q_signal**2)
    digital_magnitude = np.sqrt(i_digital**2 + q_digital**2)
    
    original_phase = np.arctan2(q_signal, i_signal)
    digital_phase = np.arctan2(q_digital, i_digital)
    
    magnitude_error = np.mean(np.abs(original_magnitude - digital_magnitude))
    phase_error_rms = np.sqrt(np.mean((original_phase - digital_phase)**2))
    
    iq_adc_info = {
        'i_channel': i_info,
        'q_channel': q_info,
        'mismatches': {
            'gain': mismatch_gain,
            'offset': mismatch_offset,  
            'phase_rad': mismatch_phase,
            'phase_deg': np.degrees(mismatch_phase)
        },
        'iq_metrics': {
            'magnitude_error_mean': magnitude_error,
            'phase_error_rms_rad': phase_error_rms,
            'phase_error_rms_deg': np.degrees(phase_error_rms),
            'iq_snr_db': min(i_info['snr_db'], q_info['snr_db'])
        }
    }
    
    return (i_digital, q_digital), iq_adc_info


def simulate_adc_dac_with_dc_removal(
    signal: np.ndarray,
    adc_bits: int = 8,
    dac_bits: int = 12,
    adc_range: Tuple[float, float] = (0.0, 2.5),
    dac_range: Tuple[float, float] = (-1.0, 1.0),
    dc_bias: float = 1.25,
    hpf_cutoff: float = 0.01,
    sampling_rate: float = 1000.0
) -> Tuple[np.ndarray, dict]:
    """
    Simulate complete ADC -> Digital Processing -> DAC chain with DC removal.
    
    Models a complete signal processing chain including DC bias for ADC,
    digital high-pass filtering for DC removal, and DAC output.
    
    Parameters:
    -----------
    signal : np.ndarray
        Input bipolar signal
    adc_bits : int, optional
        ADC resolution in bits
    dac_bits : int, optional
        DAC resolution in bits  
    adc_range : tuple, optional
        ADC input voltage range
    dac_range : tuple, optional
        DAC output voltage range
    dc_bias : float, optional
        DC bias voltage for ADC
    hpf_cutoff : float, optional
        High-pass filter cutoff (normalized frequency)
    sampling_rate : float, optional
        Sampling rate for filter design
        
    Returns:
    --------
    tuple
        (output_signal, processing_chain_info)
        
    Examples:
    ---------
    >>> t = np.linspace(0, 2, 2000)
    >>> signal = np.sin(2*np.pi*10*t) + 0.1*np.sin(2*np.pi*60*t)
    >>> output, info = simulate_adc_dac_with_dc_removal(signal)
    """
    # Step 1: ADC simulation
    adc_output, adc_info = simulate_8bit_adc(signal, adc_range, dc_bias, adc_bits)
    
    # Step 2: Digital DC removal using simple high-pass filter
    # Simple first-order IIR high-pass filter: y[n] = a*y[n-1] + (1-a)*(x[n] - x[n-1])
    alpha = 1 - 2 * np.pi * hpf_cutoff
    dc_removed = np.zeros_like(adc_output)
    
    for n in range(1, len(adc_output)):
        dc_removed[n] = alpha * dc_removed[n-1] + (adc_output[n] - adc_output[n-1])
    
    # Step 3: DAC simulation
    dac_min, dac_max = dac_range
    dac_levels = 2 ** dac_bits
    dac_lsb = (dac_max - dac_min) / dac_levels
    
    # Clip to DAC range
    clipped_for_dac = np.clip(dc_removed, dac_min, dac_max)
    
    # Quantize for DAC
    normalized_dac = (clipped_for_dac - dac_min) / (dac_max - dac_min)
    quantized_dac_levels = np.round(normalized_dac * (dac_levels - 1))
    dac_output = (quantized_dac_levels / (dac_levels - 1)) * (dac_max - dac_min) + dac_min
    
    # Calculate chain performance metrics
    total_error = signal - dac_output
    chain_snr = 10 * np.log10(np.var(signal) / np.var(total_error)) if np.var(total_error) > 0 else float('inf')
    
    # DC content analysis
    signal_dc = np.mean(signal)
    adc_dc = np.mean(adc_output)
    removed_dc = np.mean(dc_removed)
    final_dc = np.mean(dac_output)
    
    processing_chain_info = {
        'adc_info': adc_info,
        'dac_info': {
            'bits': dac_bits,
            'range': dac_range,
            'lsb': dac_lsb,
            'levels': dac_levels,
            'clipped_samples': np.sum((dc_removed < dac_min) | (dc_removed > dac_max))
        },
        'dc_removal': {
            'hpf_cutoff': hpf_cutoff,
            'alpha': alpha,
            'original_dc': signal_dc,
            'adc_dc': adc_dc,
            'after_hpf_dc': removed_dc,
            'final_dc': final_dc,
            'dc_suppression_db': 20 * np.log10(abs(signal_dc / final_dc)) if final_dc != 0 else float('inf')
        },
        'overall_metrics': {
            'chain_snr_db': chain_snr,
            'total_thd': np.sqrt(np.mean(total_error**2)) / np.sqrt(np.mean(signal**2)),
            'effective_bits': (chain_snr - 1.76) / 6.02
        }
    }
    
    return dac_output, processing_chain_info


def plot_adc_characteristics(
    adc_info: dict,
    signal_before: Optional[np.ndarray] = None,
    signal_after: Optional[np.ndarray] = None,
    time_vector: Optional[np.ndarray] = None,
    figsize: Tuple[int, int] = (12, 8)
) -> plt.Figure:
    """
    Plot ADC characteristics and performance metrics.
    
    Parameters:
    -----------
    adc_info : dict
        ADC information from simulate_8bit_adc
    signal_before : np.ndarray, optional
        Original signal before ADC
    signal_after : np.ndarray, optional  
        Signal after ADC processing
    time_vector : np.ndarray, optional
        Time vector for plotting
    figsize : tuple, optional
        Figure size
        
    Returns:
    --------
    plt.Figure
        Figure containing ADC analysis plots
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Plot 1: Signal comparison
    if signal_before is not None and signal_after is not None:
        if time_vector is None:
            time_vector = np.arange(len(signal_before))
        
        axes[0,0].plot(time_vector[:500], signal_before[:500], 'b-', label='Original', alpha=0.7)
        axes[0,0].plot(time_vector[:500], signal_after[:500], 'r-', label='After ADC', alpha=0.7)
        axes[0,0].set_title('Signal Comparison (First 500 samples)')
        axes[0,0].set_xlabel('Time')
        axes[0,0].set_ylabel('Amplitude')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
    
    # Plot 2: ADC transfer function
    adc_min, adc_max = adc_info['adc_range']
    input_range = np.linspace(adc_min, adc_max, 1000)
    num_levels = adc_info['num_levels']
    
    # Simulate ADC transfer
    normalized = (input_range - adc_min) / (adc_max - adc_min)
    quantized_levels = np.floor(normalized * num_levels)
    quantized_levels = np.clip(quantized_levels, 0, num_levels - 1)
    quantized_output = (quantized_levels / num_levels) * (adc_max - adc_min) + adc_min
    
    axes[0,1].plot(input_range, quantized_output, 'g-', linewidth=2)
    axes[0,1].plot(input_range, input_range, 'k--', alpha=0.5, label='Ideal')
    axes[0,1].set_title(f'{adc_info["bits"]}-bit ADC Transfer Function')
    axes[0,1].set_xlabel('Input Voltage')
    axes[0,1].set_ylabel('Output Voltage')
    axes[0,1].grid(True, alpha=0.3)
    axes[0,1].legend()
    
    # Plot 3: Quantization error histogram
    if signal_before is not None and signal_after is not None:
        error = signal_before - signal_after
        axes[1,0].hist(error, bins=50, alpha=0.7, edgecolor='black')
        axes[1,0].set_title('Quantization Error Distribution')
        axes[1,0].set_xlabel('Error')
        axes[1,0].set_ylabel('Count')
        axes[1,0].grid(True, alpha=0.3)
    
    # Plot 4: ADC metrics text
    axes[1,1].axis('off')
    metrics_text = f"""
    ADC Performance Metrics:
    
    Resolution: {adc_info['bits']} bits
    LSB: {adc_info['lsb_voltage']:.4f} V
    SNR: {adc_info['snr_db']:.1f} dB
    ENOB: {adc_info['enob']:.1f} bits
    
    Range Utilization: {adc_info['utilization']:.1%}
    Clipping Rate: {adc_info['clipping_rate']:.2%}
    
    Signal Range: [{adc_info['signal_range'][0]:.3f}, {adc_info['signal_range'][1]:.3f}]
    ADC Range: [{adc_info['adc_range'][0]:.3f}, {adc_info['adc_range'][1]:.3f}]
    DC Bias: {adc_info['dc_bias']:.3f} V
    """
    axes[1,1].text(0.1, 0.9, metrics_text, transform=axes[1,1].transAxes, 
                   fontsize=10, verticalalignment='top', fontfamily='monospace')
    
    plt.tight_layout()
    return fig