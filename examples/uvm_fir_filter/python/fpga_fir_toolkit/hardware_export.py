"""
Hardware Export Module

This module provides functions to export FIR filter coefficients and test data
in formats suitable for FPGA implementation and verification.
"""

import numpy as np
import os
from typing import List, Union, Tuple, Optional
from pathlib import Path


def export_coefficients_for_hardware(
    coefficients: np.ndarray,
    output_dir: str = "hardware_export",
    project_name: str = "fir_filter",
    int_bits: int = 1,
    frac_bits: int = 15,
    create_verilog: bool = True,
    create_c_header: bool = True,
    create_hex: bool = True,
    create_binary: bool = True
) -> dict:
    """
    Export FIR filter coefficients in multiple hardware-friendly formats.
    
    Parameters:
    -----------
    coefficients : np.ndarray
        FIR filter coefficients (floating-point)
    output_dir : str, optional
        Output directory for generated files
    project_name : str, optional
        Base name for generated files
    int_bits : int, optional
        Integer bits for fixed-point conversion
    frac_bits : int, optional
        Fractional bits for fixed-point conversion
    create_verilog : bool, optional
        Generate SystemVerilog parameter file
    create_c_header : bool, optional
        Generate C header file
    create_hex : bool, optional
        Generate hexadecimal text file
    create_binary : bool, optional
        Generate binary file
        
    Returns:
    --------
    dict
        Dictionary containing file paths and conversion information
        
    Examples:
    ---------
    >>> from filter_design import design_fir_lowpass
    >>> coeffs = design_fir_lowpass(1000, 8000, 31)
    >>> files = export_coefficients_for_hardware(coeffs, "my_filter")
    >>> print(f"Generated {len(files['created_files'])} files")
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Convert to fixed-point
    from .fixed_point import float_to_fixed_point
    fixed_coeffs, conversion_info = float_to_fixed_point(coefficients, int_bits, frac_bits)
    
    created_files = []
    
    # 1. SystemVerilog parameter file
    if create_verilog:
        sv_file = output_path / f"{project_name}_coeffs.sv"
        _create_systemverilog_file(fixed_coeffs, sv_file, project_name, conversion_info)
        created_files.append(str(sv_file))
    
    # 2. C header file  
    if create_c_header:
        c_file = output_path / f"{project_name}_coeffs.h"
        _create_c_header_file(fixed_coeffs, c_file, project_name, conversion_info)
        created_files.append(str(c_file))
    
    # 3. Hexadecimal text file
    if create_hex:
        hex_file = output_path / f"{project_name}_coeffs.hex"
        _create_hex_file(fixed_coeffs, hex_file, conversion_info)
        created_files.append(str(hex_file))
    
    # 4. Binary file
    if create_binary:
        bin_file = output_path / f"{project_name}_coeffs.bin"
        _create_binary_file(fixed_coeffs, bin_file, conversion_info)
        created_files.append(str(bin_file))
    
    # Create README with information
    readme_file = output_path / "README.txt"
    _create_readme_file(readme_file, project_name, coefficients, conversion_info, created_files)
    created_files.append(str(readme_file))
    
    return {
        'created_files': created_files,
        'output_directory': str(output_path),
        'conversion_info': conversion_info,
        'original_coefficients': coefficients,
        'fixed_point_coefficients': fixed_coeffs
    }


def _create_systemverilog_file(fixed_coeffs: np.ndarray, file_path: Path, 
                             project_name: str, conversion_info: dict) -> None:
    """Create SystemVerilog parameter file with FIR coefficients."""
    total_bits = conversion_info['total_bits']
    
    with open(file_path, 'w') as f:
        f.write(f"// FIR Filter Coefficients for {project_name}\n")
        f.write(f"// Generated automatically from Python design\n")
        f.write(f"// Format: Q{conversion_info['int_bits']}.{conversion_info['frac_bits']}\n")
        f.write(f"// Total bits: {total_bits}\n")
        f.write(f"// Number of taps: {len(fixed_coeffs)}\n\n")
        
        f.write(f"package {project_name}_pkg;\n\n")
        
        f.write(f"    // Filter parameters\n")
        f.write(f"    parameter int NUM_TAPS = {len(fixed_coeffs)};\n")
        f.write(f"    parameter int COEFF_WIDTH = {total_bits};\n")
        f.write(f"    parameter int INT_BITS = {conversion_info['int_bits']};\n")
        f.write(f"    parameter int FRAC_BITS = {conversion_info['frac_bits']};\n\n")
        
        f.write(f"    // Filter coefficients\n")
        f.write(f"    parameter logic signed [COEFF_WIDTH-1:0] COEFFS [NUM_TAPS] = '{{\n")
        
        for i, coeff in enumerate(fixed_coeffs):
            # Handle negative numbers in two's complement
            if coeff < 0:
                coeff_hex = f"{total_bits}'h{(2**total_bits + coeff):0{(total_bits+3)//4}X}"
            else:
                coeff_hex = f"{total_bits}'h{coeff:0{(total_bits+3)//4}X}"
            
            comma = "," if i < len(fixed_coeffs) - 1 else ""
            f.write(f"        {coeff_hex}{comma}  // Tap {i}: {conversion_info['reconstructed_coeffs'][i]:.6f}\n")
        
        f.write(f"    }};\n\n")
        f.write(f"endpackage\n")


def _create_c_header_file(fixed_coeffs: np.ndarray, file_path: Path,
                         project_name: str, conversion_info: dict) -> None:
    """Create C header file with FIR coefficients."""
    total_bits = conversion_info['total_bits']
    
    with open(file_path, 'w') as f:
        f.write(f"/* FIR Filter Coefficients for {project_name} */\n")
        f.write(f"/* Generated automatically from Python design */\n")
        f.write(f"/* Format: Q{conversion_info['int_bits']}.{conversion_info['frac_bits']} */\n")
        f.write(f"/* Total bits: {total_bits} */\n\n")
        
        f.write(f"#ifndef {project_name.upper()}_COEFFS_H\n")
        f.write(f"#define {project_name.upper()}_COEFFS_H\n\n")
        
        f.write(f"#include <stdint.h>\n\n")
        
        f.write(f"// Filter parameters\n")
        f.write(f"#define NUM_TAPS {len(fixed_coeffs)}\n")
        f.write(f"#define COEFF_WIDTH {total_bits}\n")
        f.write(f"#define INT_BITS {conversion_info['int_bits']}\n")
        f.write(f"#define FRAC_BITS {conversion_info['frac_bits']}\n")
        f.write(f"#define SCALE_FACTOR {conversion_info['scale_factor']}\n\n")
        
        # Choose appropriate integer type
        if total_bits <= 8:
            int_type = "int8_t"
        elif total_bits <= 16:
            int_type = "int16_t"
        elif total_bits <= 32:
            int_type = "int32_t"
        else:
            int_type = "int64_t"
        
        f.write(f"// Filter coefficients\n")
        f.write(f"static const {int_type} fir_coeffs[NUM_TAPS] = {{\n")
        
        for i, coeff in enumerate(fixed_coeffs):
            comma = "," if i < len(fixed_coeffs) - 1 else ""
            f.write(f"    {coeff}{comma}  /* Tap {i}: {conversion_info['reconstructed_coeffs'][i]:.6f} */\n")
        
        f.write(f"}};\n\n")
        f.write(f"#endif /* {project_name.upper()}_COEFFS_H */\n")


def _create_hex_file(fixed_coeffs: np.ndarray, file_path: Path, conversion_info: dict) -> None:
    """Create hexadecimal text file."""
    total_bits = conversion_info['total_bits']
    
    with open(file_path, 'w') as f:
        f.write(f"// FIR Filter Coefficients in Hexadecimal\n")
        f.write(f"// Format: Q{conversion_info['int_bits']}.{conversion_info['frac_bits']}\n")
        f.write(f"// Total bits: {total_bits}\n")
        f.write(f"// One coefficient per line\n\n")
        
        for i, coeff in enumerate(fixed_coeffs):
            if coeff < 0:
                coeff_hex = f"{(2**total_bits + coeff):0{(total_bits+3)//4}X}"
            else:
                coeff_hex = f"{coeff:0{(total_bits+3)//4}X}"
            f.write(f"{coeff_hex}\n")


def _create_binary_file(fixed_coeffs: np.ndarray, file_path: Path, conversion_info: dict) -> None:
    """Create binary file with coefficients."""
    total_bits = conversion_info['total_bits']
    
    # Choose appropriate numpy datatype
    if total_bits <= 8:
        dtype = np.int8
    elif total_bits <= 16:
        dtype = np.int16  
    elif total_bits <= 32:
        dtype = np.int32
    else:
        dtype = np.int64
    
    # Convert to appropriate datatype and save
    coeff_array = fixed_coeffs.astype(dtype)
    coeff_array.tofile(file_path)


def _create_readme_file(file_path: Path, project_name: str, original_coeffs: np.ndarray,
                       conversion_info: dict, created_files: List[str]) -> None:
    """Create README file with design information."""
    with open(file_path, 'w') as f:
        f.write(f"FIR Filter Coefficient Export\n")
        f.write(f"============================\n\n")
        f.write(f"Project: {project_name}\n")
        f.write(f"Generated: {np.datetime64('today')}\n\n")
        
        f.write(f"Filter Specifications:\n")
        f.write(f"- Number of taps: {len(original_coeffs)}\n")
        f.write(f"- Fixed-point format: Q{conversion_info['int_bits']}.{conversion_info['frac_bits']}\n")
        f.write(f"- Total bits: {conversion_info['total_bits']}\n")
        f.write(f"- Scale factor: {conversion_info['scale_factor']}\n")
        f.write(f"- Max quantization error: {conversion_info['max_quantization_error']:.8f}\n")
        f.write(f"- Mean quantization error: {conversion_info['mean_quantization_error']:.8f}\n")
        f.write(f"- Overflow coefficients: {conversion_info['overflow_count']}\n\n")
        
        f.write(f"Generated Files:\n")
        for file_name in created_files:
            f.write(f"- {file_name}\n")
        
        f.write(f"\nFile Descriptions:\n")
        f.write(f"- .sv files: SystemVerilog parameter packages\n")
        f.write(f"- .h files: C header files\n") 
        f.write(f"- .hex files: Hexadecimal text (one coefficient per line)\n")
        f.write(f"- .bin files: Binary coefficient data\n")
        f.write(f"- README.txt: This file\n")


def generate_fpga_testbench_data(
    input_signal: np.ndarray,
    expected_output: np.ndarray,
    output_dir: str = "testbench_data",
    project_name: str = "fir_test",
    signal_bits: int = 16,
    output_bits: int = 24,
    hex_format: bool = True
) -> dict:
    """
    Generate test vectors for FPGA testbench simulation.
    
    Parameters:
    -----------
    input_signal : np.ndarray
        Test input signal (floating-point)
    expected_output : np.ndarray
        Expected filter output (floating-point)
    output_dir : str, optional
        Output directory for test files
    project_name : str, optional
        Base name for test files
    signal_bits : int, optional
        Bit width for input signal quantization
    output_bits : int, optional
        Bit width for output signal quantization
    hex_format : bool, optional
        Use hexadecimal format (otherwise decimal)
        
    Returns:
    --------
    dict
        Dictionary with generated test file information
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Quantize signals to appropriate bit widths
    input_scale = 2**(signal_bits-1)
    output_scale = 2**(output_bits-1)
    
    input_int = (input_signal * input_scale).astype(np.int32)
    output_int = (expected_output * output_scale).astype(np.int64)
    
    # Clip to prevent overflow
    input_int = np.clip(input_int, -(2**(signal_bits-1)), 2**(signal_bits-1)-1)
    output_int = np.clip(output_int, -(2**(output_bits-1)), 2**(output_bits-1)-1)
    
    created_files = []
    
    # Generate input test vector
    input_file = output_path / f"{project_name}_input.txt"
    with open(input_file, 'w') as f:
        f.write(f"// FIR Filter Test Input Data\n")
        f.write(f"// {len(input_int)} samples, {signal_bits} bits each\n\n")
        for sample in input_int:
            if hex_format:
                if sample < 0:
                    hex_val = f"{(2**signal_bits + sample):0{(signal_bits+3)//4}X}"
                else:
                    hex_val = f"{sample:0{(signal_bits+3)//4}X}"
                f.write(f"{hex_val}\n")
            else:
                f.write(f"{sample}\n")
    created_files.append(str(input_file))
    
    # Generate expected output vector
    output_file = output_path / f"{project_name}_expected.txt"
    with open(output_file, 'w') as f:
        f.write(f"// FIR Filter Expected Output Data\n")
        f.write(f"// {len(output_int)} samples, {output_bits} bits each\n\n")
        for sample in output_int:
            if hex_format:
                if sample < 0:
                    hex_val = f"{(2**output_bits + sample):0{(output_bits+3)//4}X}"
                else:
                    hex_val = f"{sample:0{(output_bits+3)//4}X}"
                f.write(f"{hex_val}\n")
            else:
                f.write(f"{sample}\n")
    created_files.append(str(output_file))
    
    # Generate SystemVerilog testbench template
    tb_file = output_path / f"{project_name}_tb.sv"
    _create_testbench_template(tb_file, project_name, len(input_int), signal_bits, output_bits)
    created_files.append(str(tb_file))
    
    return {
        'created_files': created_files,
        'input_samples': len(input_int),
        'input_bits': signal_bits,
        'output_bits': output_bits,
        'input_range': (np.min(input_int), np.max(input_int)),
        'output_range': (np.min(output_int), np.max(output_int)),
        'hex_format': hex_format
    }


def _create_testbench_template(file_path: Path, project_name: str, 
                             num_samples: int, input_bits: int, output_bits: int) -> None:
    """Create SystemVerilog testbench template."""
    with open(file_path, 'w') as f:
        f.write(f"""// FIR Filter Testbench Template
// Project: {project_name}

`timescale 1ns/1ps

module {project_name}_tb;

    // Parameters
    parameter int INPUT_WIDTH = {input_bits};
    parameter int OUTPUT_WIDTH = {output_bits};
    parameter int NUM_SAMPLES = {num_samples};
    
    // Clock and reset
    logic clk = 0;
    logic rst_n = 1;
    
    // Test signals
    logic signed [INPUT_WIDTH-1:0] test_input;
    logic signed [OUTPUT_WIDTH-1:0] dut_output;
    logic signed [OUTPUT_WIDTH-1:0] expected_output;
    logic input_valid = 0;
    logic output_valid;
    
    // Test data arrays
    logic signed [INPUT_WIDTH-1:0] input_data [NUM_SAMPLES];
    logic signed [OUTPUT_WIDTH-1:0] expected_data [NUM_SAMPLES];
    
    // Test control
    int sample_count = 0;
    int error_count = 0;
    
    // Clock generation
    always #5 clk = ~clk;  // 100 MHz clock
    
    // Load test vectors
    initial begin
        $readmemh("{project_name}_input.txt", input_data);
        $readmemh("{project_name}_expected.txt", expected_data);
    end
    
    // DUT instantiation (replace with your FIR filter module)
    /*
    fir_filter #(
        .INPUT_WIDTH(INPUT_WIDTH),
        .OUTPUT_WIDTH(OUTPUT_WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .data_in(test_input),
        .data_in_valid(input_valid),
        .data_out(dut_output),
        .data_out_valid(output_valid)
    );
    */
    
    // Test stimulus
    initial begin
        // Reset sequence
        rst_n = 0;
        repeat(10) @(posedge clk);
        rst_n = 1;
        repeat(5) @(posedge clk);
        
        // Apply test vectors
        for (int i = 0; i < NUM_SAMPLES; i++) begin
            @(posedge clk);
            test_input = input_data[i];
            input_valid = 1;
            sample_count++;
        end
        
        input_valid = 0;
        
        // Wait for processing to complete
        repeat(100) @(posedge clk);
        
        // Report results
        if (error_count == 0) begin
            $display("TEST PASSED: All outputs match expected values");
        end else begin
            $display("TEST FAILED: %0d errors out of %0d samples", error_count, sample_count);
        end
        
        $finish;
    end
    
    // Output checking
    always @(posedge clk) begin
        if (output_valid && sample_count > 0) begin
            expected_output = expected_data[sample_count - 1];
            if (dut_output !== expected_output) begin
                $error("Sample %0d: Expected %0h, Got %0h", 
                       sample_count-1, expected_output, dut_output);
                error_count++;
            end
        end
    end

endmodule
""")


def generate_dual_adc_testbench(
    i_signal: np.ndarray,
    q_signal: np.ndarray,
    output_dir: str = "dual_adc_testbench",
    project_name: str = "dual_adc_test",
    adc_bits: int = 8
) -> dict:
    """
    Generate testbench data for dual ADC IQ processing.
    
    Parameters:
    -----------
    i_signal : np.ndarray
        I channel test signal
    q_signal : np.ndarray
        Q channel test signal  
    output_dir : str, optional
        Output directory
    project_name : str, optional
        Project base name
    adc_bits : int, optional
        ADC resolution
        
    Returns:
    --------
    dict
        Generated file information
    """
    from .adc_simulation import simulate_dual_8bit_adc
    
    # Simulate dual ADC processing
    (i_digital, q_digital), adc_info = simulate_dual_8bit_adc(
        i_signal, q_signal, bits=adc_bits
    )
    
    # Generate test files for both channels
    i_info = generate_fpga_testbench_data(
        i_signal, i_digital, output_dir, f"{project_name}_i_channel", adc_bits, 16
    )
    
    q_info = generate_fpga_testbench_data(
        q_signal, q_digital, output_dir, f"{project_name}_q_channel", adc_bits, 16
    )
    
    return {
        'i_channel_files': i_info,
        'q_channel_files': q_info,
        'adc_simulation_info': adc_info,
        'dual_adc_bits': adc_bits
    }