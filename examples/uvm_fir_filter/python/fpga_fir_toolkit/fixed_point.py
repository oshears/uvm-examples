"""
Fixed-Point Processing Module

This module handles conversion of floating-point FIR coefficients to fixed-point
representation and implements fixed-point filtering for FPGA simulation.
"""

import numpy as np
from typing import Tuple, Union, Optional


def float_to_fixed_point(
    coeffs: np.ndarray, 
    int_bits: int = 1, 
    frac_bits: int = 15
) -> Tuple[np.ndarray, dict]:
    """
    Convert floating-point FIR coefficients to fixed-point representation.
    
    This function converts coefficients to Q(int_bits).(frac_bits) format,
    commonly used in FPGA implementations.
    
    **Q1.15**: 
    - This configuration allows for a range from -1 (represented as 0x8000) to +0.99996337890625 (represented as 0x7FFF). 
    -
    
    Parameters:
    -----------
    coeffs : np.ndarray
        Floating-point filter coefficients
    int_bits : int, optional
        Number of integer bits (default 1 for Q1.15)
    frac_bits : int, optional  
        Number of fractional bits (default 15 for Q1.15)
        
    Returns:
    --------
    tuple
        (fixed_point_coeffs, conversion_info)
        - fixed_point_coeffs: Integer representation of coefficients
        - conversion_info: Dictionary with scaling and overflow information
        
    Examples:
    ---------
    >>> coeffs = np.array([0.1, 0.5, -0.3])
    >>> fixed_coeffs, info = float_to_fixed_point(coeffs)
    >>> print(f"Scale factor: {info['scale_factor']}")
    """
    total_bits = int_bits + frac_bits
    
    # Calculate scale factor for fractional bits
    scale_factor = 2 ** frac_bits
    
    # Maximum representable value
    max_val = 2**(total_bits-1) - 1  # For signed representation
    min_val = -2**(total_bits-1)
    
    # Scale coefficients
    scaled_coeffs = coeffs * scale_factor
    
    # Check for overflow
    overflow_indices = np.where((scaled_coeffs > max_val) | (scaled_coeffs < min_val))[0]
    
    # Saturate overflowed values
    saturated_coeffs = np.clip(scaled_coeffs, min_val, max_val)
    
    # Convert to integers
    fixed_point_coeffs = np.round(saturated_coeffs).astype(np.int32)
    
    # Calculate quantization error
    reconstructed = fixed_point_coeffs.astype(np.float64) / scale_factor
    quantization_error = np.abs(coeffs - reconstructed)
    
    conversion_info = {
        'int_bits': int_bits,
        'frac_bits': frac_bits,
        'total_bits': total_bits,
        'scale_factor': scale_factor,
        'max_representable': max_val / scale_factor,
        'min_representable': min_val / scale_factor,
        'overflow_count': len(overflow_indices),
        'overflow_indices': overflow_indices,
        'max_quantization_error': np.max(quantization_error),
        'mean_quantization_error': np.mean(quantization_error),
        'original_coeffs': coeffs,
        'reconstructed_coeffs': reconstructed
    }
    
    return fixed_point_coeffs, conversion_info


def apply_fixed_point_filter(
    signal: np.ndarray, 
    fixed_point_coeffs: np.ndarray,
    coeff_frac_bits: int = 15,
    accumulator_bits: int = 32,
    output_shift: int = 15,
    input_scaling: float = 1.0
) -> Tuple[np.ndarray, dict]:
    """
    Apply fixed-point FIR filter with realistic FPGA arithmetic.
    
    Simulates the behavior of an FPGA FIR filter implementation including
    quantization, overflow handling, and bit growth management.
    
    Parameters:
    -----------
    signal : np.ndarray
        Input signal (floating-point)
    fixed_point_coeffs : np.ndarray
        Fixed-point filter coefficients (integers)
    coeff_frac_bits : int, optional
        Number of fractional bits in coefficients
    accumulator_bits : int, optional
        Width of accumulator in bits
    output_shift : int, optional
        Right shift for output scaling
    input_scaling : float, optional
        Scale factor for input signal
        
    Returns:
    --------
    tuple
        (filtered_signal, simulation_info)
        
    Examples:
    ---------
    >>> signal = np.random.randn(1000)
    >>> coeffs = np.array([0.1, 0.5, 0.4])
    >>> fixed_coeffs, _ = float_to_fixed_point(coeffs)
    >>> filtered, info = apply_fixed_point_filter(signal, fixed_coeffs)
    """
    # Scale input signal to fixed-point range (assume 16-bit ADC)
    input_scale = int(input_scaling * (2**15))
    scaled_input = (signal * input_scale).astype(np.int32)
    
    # Initialize output
    N = len(signal)
    M = len(fixed_point_coeffs)
    filtered_signal = np.zeros(N, dtype=np.float64)
    
    # Accumulator overflow tracking
    accumulator_max = 2**(accumulator_bits-1) - 1
    accumulator_min = -2**(accumulator_bits-1)
    overflow_count = 0
    
    # Apply filter with fixed-point arithmetic
    for n in range(N):
        # Compute FIR output
        # accumulator = 0
        accumulator = np.int64(0)
        
        for k in range(M):
            if (n - k) >= 0:
                # Multiply and accumulate
                product = scaled_input[n - k] * fixed_point_coeffs[k]
                accumulator += product
        
        # Check for accumulator overflow
        if accumulator > accumulator_max or accumulator < accumulator_min:
            overflow_count += 1
            accumulator = np.clip(accumulator, accumulator_min, accumulator_max)
        
        # Apply output shift and convert back to float
        output_sample = accumulator >> output_shift
        filtered_signal[n] = output_sample / (2**15)  # Scale back to normalized range
    
    simulation_info = {
        'input_scaling': input_scaling,
        'coefficient_bits': coeff_frac_bits,
        'accumulator_bits': accumulator_bits,
        'output_shift': output_shift,
        'overflow_count': overflow_count,
        'overflow_rate': overflow_count / N,
        'effective_snr_db': -20 * np.log10(np.std(signal - filtered_signal) / np.std(filtered_signal)) if np.std(filtered_signal) > 0 else float('inf')
    }
    
    return filtered_signal, simulation_info


def apply_fixed_point_filter_8bit_adc(
    signal: np.ndarray,
    fixed_point_coeffs: np.ndarray,
    adc_bits: int = 8,
    adc_range: Tuple[float, float] = (-1.0, 1.0),
    dc_bias: float = 1.25,
    coeff_frac_bits: int = 15
) -> Tuple[np.ndarray, dict]:
    """
    Apply fixed-point FIR filter with 8-bit ADC simulation.
    
    This function simulates the complete signal chain from ADC quantization
    through fixed-point FIR filtering, as would occur in an FPGA.
    
    Parameters:
    -----------
    signal : np.ndarray
        Input analog signal 
    fixed_point_coeffs : np.ndarray
        Fixed-point filter coefficients
    adc_bits : int, optional
        ADC resolution in bits
    adc_range : tuple, optional
        ADC input voltage range (min, max)
    dc_bias : float, optional
        DC bias voltage for unipolar ADC
    coeff_frac_bits : int, optional
        Fractional bits in coefficients
        
    Returns:
    --------
    tuple
        (filtered_signal, processing_info)
        
    Examples:
    ---------
    >>> t = np.linspace(0, 1, 1000)
    >>> signal = 0.5 * np.sin(2*np.pi*10*t)
    >>> coeffs, _ = float_to_fixed_point(design_fir_lowpass(50, 1000, 31))
    >>> filtered, info = apply_fixed_point_filter_8bit_adc(signal, coeffs)
    """
    # Step 1: Add DC bias for unipolar ADC
    biased_signal = signal + dc_bias
    
    # Step 2: ADC quantization
    adc_levels = 2 ** adc_bits
    adc_min, adc_max = adc_range
    
    # Clip to ADC range
    clipped_signal = np.clip(biased_signal, adc_min, adc_max)
    
    # Quantize
    normalized = (clipped_signal - adc_min) / (adc_max - adc_min)
    quantized_levels = np.round(normalized * (adc_levels - 1))
    adc_output = quantized_levels / (adc_levels - 1) * (adc_max - adc_min) + adc_min
    
    # Step 3: Remove DC bias digitally
    dc_removed = adc_output - dc_bias
    
    # Step 4: Convert to fixed-point for filtering
    input_scale = 2**(adc_bits-1)  # Scale to use full ADC range
    scaled_input = (dc_removed * input_scale).astype(np.int32)
    
    # Step 5: Apply fixed-point FIR filter
    N = len(scaled_input)
    M = len(fixed_point_coeffs)
    filtered_output = np.zeros(N, dtype=np.int64)
    
    # Calculate shift for 'same' mode behavior to match np.convolve
    shift = (M - 1) // 2
    
    for n in range(N):
        accumulator = 0
        for k in range(M):
            sample_idx = n - k + shift
            if 0 <= sample_idx < N:
                accumulator += scaled_input[sample_idx] * fixed_point_coeffs[k]
        filtered_output[n] = accumulator
    
    # Step 6: Scale output back to floating-point
    output_shift = coeff_frac_bits + np.log2(input_scale).astype(int)
    final_output = filtered_output.astype(np.float64) / (2**output_shift)
    
    # Calculate metrics
    quantization_noise_power = np.mean((signal - dc_removed)**2)
    snr_db = 10 * np.log10(np.var(signal) / quantization_noise_power) if quantization_noise_power > 0 else float('inf')
    
    processing_info = {
        'adc_bits': adc_bits,
        'adc_range': adc_range,
        'dc_bias': dc_bias,
        'quantization_levels': adc_levels,
        'input_scaling': input_scale,
        'output_shift': output_shift,
        'estimated_snr_db': snr_db,
        'clipping_samples': np.sum((biased_signal < adc_min) | (biased_signal > adc_max)),
        'signal_range': (np.min(signal), np.max(signal)),
        'adc_utilization': (np.max(quantized_levels) - np.min(quantized_levels)) / (adc_levels - 1)
    }
    
    return final_output, processing_info


def analyze_fixed_point_precision(
    float_coeffs: np.ndarray,
    bit_widths: list = [8, 10, 12, 16, 18, 24],
    int_bits: int = 1
) -> dict:
    """
    Analyze precision requirements for different fixed-point bit widths.
    
    Parameters:
    -----------
    float_coeffs : np.ndarray
        Original floating-point coefficients
    bit_widths : list, optional
        List of total bit widths to analyze
    int_bits : int, optional
        Number of integer bits
        
    Returns:
    --------
    dict
        Analysis results for each bit width
    """
    results = {}
    
    for total_bits in bit_widths:
        frac_bits = total_bits - int_bits
        if frac_bits <= 0:
            continue
            
        fixed_coeffs, info = float_to_fixed_point(
            float_coeffs, int_bits, frac_bits
        )
        
        results[total_bits] = {
            'max_error': info['max_quantization_error'],
            'mean_error': info['mean_quantization_error'], 
            'overflow_count': info['overflow_count'],
            'snr_db': -20 * np.log10(info['mean_quantization_error']) if info['mean_quantization_error'] > 0 else float('inf')
        }
    
    return results