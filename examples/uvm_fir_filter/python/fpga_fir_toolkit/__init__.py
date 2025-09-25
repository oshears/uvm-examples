"""
FPGA FIR Filter Toolkit

A comprehensive Python package for designing, simulating, and generating 
hardware-ready FIR filters for FPGA implementations.

This toolkit provides:
- FIR filter design with various window functions
- Fixed-point coefficient conversion
- Hardware-realistic ADC/DAC simulation
- SystemVerilog testbench generation
- Signal transmission/reception modeling
- IQ processing for communications applications

Author: Generated from Jupyter notebook analysis
Version: 1.0.0
"""

from .filter_design import (
    design_fir_lowpass,
    apply_fir_filter,
    plot_filter_response
)

from .fixed_point import (
    float_to_fixed_point,
    apply_fixed_point_filter,
    apply_fixed_point_filter_8bit_adc
)

from .hardware_export import (
    export_coefficients_for_hardware,
    generate_fpga_testbench_data,
    generate_dual_adc_testbench
)

from .adc_simulation import (
    simulate_8bit_adc,
    simulate_dual_8bit_adc,
    simulate_adc_dac_with_dc_removal
)

from .signal_processing import (
    generate_iq_signal,
    apply_dual_iq_filter,
    simulate_transmission_chain
)

__version__ = "1.0.0"
__author__ = "FPGA FIR Toolkit"
__email__ = "your.email@domain.com"

__all__ = [
    # Filter design
    'design_fir_lowpass',
    'apply_fir_filter', 
    'plot_filter_response',
    
    # Fixed-point processing
    'float_to_fixed_point',
    'apply_fixed_point_filter',
    'apply_fixed_point_filter_8bit_adc',
    
    # Hardware export
    'export_coefficients_for_hardware',
    'generate_fpga_testbench_data',
    'generate_dual_adc_testbench',
    
    # ADC simulation
    'simulate_8bit_adc',
    'simulate_dual_8bit_adc',
    'simulate_adc_dac_with_dc_removal',
    
    # Signal processing
    'generate_iq_signal',
    'apply_dual_iq_filter',
    'simulate_transmission_chain'
]