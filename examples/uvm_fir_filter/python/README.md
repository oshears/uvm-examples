# FPGA FIR Filter Toolkit

A comprehensive Python package for designing, simulating, and generating hardware-ready FIR filters for FPGA implementations.

## Features

### 🎯 **FIR Filter Design**
- Windowed sinc method with multiple window types (Hamming, Hanning, Blackman, etc.)
- Automatic DC normalization and filter analysis
- Frequency and impulse response visualization
- Performance metrics calculation

### 🔢 **Fixed-Point Processing**
- Configurable Q-format conversion (e.g., Q1.15, Q1.23)
- Quantization error analysis and overflow detection
- Hardware-realistic fixed-point arithmetic simulation
- Precision requirement analysis for different bit widths

### 📡 **ADC/DAC Simulation**
- 8-bit ADC simulation with DC bias and quantization effects
- Dual ADC simulation for IQ processing with mismatch modeling
- Complete ADC→Processing→DAC chain simulation
- Digital DC removal and high-pass filtering

### 🛠 **Hardware Export**
- SystemVerilog parameter packages with coefficients
- C header files for embedded processors
- Hexadecimal and binary coefficient files
- FPGA testbench generation with test vectors
- Comprehensive documentation generation

### 📶 **Signal Processing**
- IQ signal generation (CW, QPSK, 16-QAM, chirp)
- Dual-channel IQ filtering with fixed-point support
- RF transmission chain simulation (noise, multipath, frequency offset)
- Constellation analysis and EVM calculation

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fpga-fir-toolkit.git
cd fpga-fir-toolkit

# Install in development mode
pip install -e .

# Or install from PyPI (when published)
pip install fpga-fir-toolkit
```

## Quick Start

### Basic FIR Filter Design

```python
from fpga_fir_toolkit import design_fir_lowpass, plot_filter_response

# Design a 31-tap lowpass filter
coeffs = design_fir_lowpass(
    cutoff_freq=1000,    # Hz
    sampling_rate=8000,  # Hz  
    num_taps=31,
    window='hamming'
)

# Plot frequency response
fig, axes = plot_filter_response(coeffs, 8000)
```

### Fixed-Point Conversion

```python
from fpga_fir_toolkit import float_to_fixed_point, apply_fixed_point_filter

# Convert to Q1.15 format
fixed_coeffs, info = float_to_fixed_point(coeffs, int_bits=1, frac_bits=15)

print(f"Max quantization error: {info['max_quantization_error']:.6f}")
print(f"Overflow coefficients: {info['overflow_count']}")

# Apply fixed-point filtering
signal = np.sin(2*np.pi*500*np.linspace(0, 1, 8000))  # 500 Hz test signal
filtered, sim_info = apply_fixed_point_filter(signal, fixed_coeffs)
```

### Hardware Export

```python
from fpga_fir_toolkit import export_coefficients_for_hardware

# Export in multiple formats
files = export_coefficients_for_hardware(
    coeffs, 
    output_dir="my_filter_export",
    project_name="lowpass_filter_1k",
    create_verilog=True,
    create_c_header=True,
    create_hex=True
)

print(f"Generated files: {files['created_files']}")
```

### ADC Simulation

```python
from fpga_fir_toolkit import simulate_8bit_adc, plot_adc_characteristics

# Simulate 8-bit ADC with DC bias
signal = 0.8 * np.sin(2*np.pi*1000*np.linspace(0, 1, 8000))
digitized, adc_info = simulate_8bit_adc(
    signal,
    adc_range=(0.0, 2.5),
    dc_bias=1.25,
    bits=8
)

print(f"ADC SNR: {adc_info['snr_db']:.1f} dB")
print(f"ENOB: {adc_info['enob']:.1f} bits")

# Plot ADC characteristics
fig = plot_adc_characteristics(adc_info, signal, digitized)
```

### IQ Signal Processing

```python
from fpga_fir_toolkit import generate_iq_signal, apply_dual_iq_filter

# Generate QPSK signal
t, i_sig, q_sig = generate_iq_signal(
    frequency=1000,
    sampling_rate=8000, 
    duration=0.1,
    modulation_type='qpsk',
    symbol_rate=250
)

# Apply IQ filtering
i_filt, q_filt, iq_info = apply_dual_iq_filter(
    i_sig, q_sig, coeffs,
    use_fixed_point=True
)

print(f"I/Q correlation: {iq_info['iq_correlation']:.3f}")
```

## Package Structure

```
fpga_fir_toolkit/
├── __init__.py              # Package initialization and exports
├── filter_design.py         # FIR filter design and analysis
├── fixed_point.py          # Fixed-point conversion and arithmetic
├── adc_simulation.py       # ADC/DAC simulation and modeling
├── hardware_export.py      # Hardware file generation
└── signal_processing.py    # IQ processing and RF simulation
```

## Key Functions

### Filter Design (`filter_design.py`)
- `design_fir_lowpass()` - Design lowpass FIR filter
- `apply_fir_filter()` - Apply filter using convolution
- `plot_filter_response()` - Visualize frequency/impulse response
- `analyze_filter_performance()` - Calculate performance metrics

### Fixed-Point (`fixed_point.py`)
- `float_to_fixed_point()` - Convert to fixed-point representation
- `apply_fixed_point_filter()` - Fixed-point filtering simulation
- `apply_fixed_point_filter_8bit_adc()` - Complete ADC+filter chain
- `analyze_fixed_point_precision()` - Precision requirement analysis

### ADC Simulation (`adc_simulation.py`)
- `simulate_8bit_adc()` - Single ADC with quantization
- `simulate_dual_8bit_adc()` - Dual ADC for IQ processing
- `simulate_adc_dac_with_dc_removal()` - Complete conversion chain
- `plot_adc_characteristics()` - ADC performance visualization

### Hardware Export (`hardware_export.py`)
- `export_coefficients_for_hardware()` - Multi-format coefficient export
- `generate_fpga_testbench_data()` - Test vector generation
- `generate_dual_adc_testbench()` - IQ testbench generation

### Signal Processing (`signal_processing.py`)
- `generate_iq_signal()` - IQ signal generation with various modulations
- `apply_dual_iq_filter()` - Dual-channel IQ filtering
- `simulate_transmission_chain()` - RF transmission effects
- `analyze_iq_constellation()` - Constellation analysis and EVM

## Advanced Usage

### Custom Window Functions

```python
# Use different window types
coeffs_hamming = design_fir_lowpass(1000, 8000, 31, window='hamming')
coeffs_blackman = design_fir_lowpass(1000, 8000, 31, window='blackman')
coeffs_rectangular = design_fir_lowpass(1000, 8000, 31, window='rectangular')
```

### Multi-Bit Width Analysis

```python
from fpga_fir_toolkit import analyze_fixed_point_precision

# Compare different bit widths
precision_analysis = analyze_fixed_point_precision(
    coeffs, 
    bit_widths=[8, 10, 12, 16, 18, 24]
)

for bits, metrics in precision_analysis.items():
    print(f"{bits}-bit: SNR={metrics['snr_db']:.1f}dB, Max Error={metrics['max_error']:.6f}")
```

### IQ Mismatch Simulation

```python
# Simulate ADC mismatches
(i_digital, q_digital), iq_info = simulate_dual_8bit_adc(
    i_signal, q_signal,
    mismatch_gain=0.05,      # 5% gain mismatch
    mismatch_offset=0.02,    # 20mV offset mismatch  
    mismatch_phase=0.01      # 0.01 rad phase mismatch
)

print(f"Phase error RMS: {iq_info['iq_metrics']['phase_error_rms_deg']:.2f}°")
```

## SystemVerilog Integration

The exported SystemVerilog files can be directly used in your FPGA projects:

```systemverilog
// Import the generated package
import lowpass_filter_1k_pkg::*;

// Use in your FIR filter module
module fir_filter (
    input  logic clk,
    input  logic signed [INPUT_WIDTH-1:0] data_in,
    output logic signed [OUTPUT_WIDTH-1:0] data_out
);

    // Use the exported coefficients
    logic signed [COEFF_WIDTH-1:0] coeffs [NUM_TAPS] = COEFFS;
    
    // Your FIR implementation here...

endmodule
```

## Dependencies

- **NumPy** (≥1.19.0) - Numerical computing
- **SciPy** (≥1.5.0) - Signal processing functions
- **Matplotlib** (≥3.3.0) - Plotting and visualization

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black fpga_fir_toolkit/

# Type checking
mypy fpga_fir_toolkit/
```

## Examples and Tutorials

See the `examples/` directory for comprehensive tutorials covering:

- Basic FIR filter design workflow
- FPGA implementation guidelines  
- ADC/DAC system design
- IQ processing for communications
- Fixed-point optimization techniques

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the MIT License - see `LICENSE` file for details.

## Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{fpga_fir_toolkit,
  title={FPGA FIR Filter Toolkit},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/fpga-fir-toolkit}
}
```