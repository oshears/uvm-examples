import numpy as np
import matplotlib.pyplot as plt


from fpga_fir_toolkit.filter_design import design_fir_lowpass, apply_fir_filter
from fpga_fir_toolkit.fixed_point import float_to_fixed_point, apply_fixed_point_filter, apply_fixed_point_filter_8bit_adc
from fpga_fir_toolkit.adc_simulation import simulate_8bit_adc


# Generate a test signal
sample_rate = 1000  # Hz
duration = 1.0      # seconds
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 100 * t) + 0.2 * np.random.randn(len(t))

# Design the filter
# num_taps = 51
num_taps = 13
cutoff_freq = 50  # Hz
fir_coefficients = design_fir_lowpass(cutoff_freq, sample_rate, num_taps)

# Apply the filter
filtered_signal = apply_fir_filter(signal, fir_coefficients)

# Plotting results
plt.figure(figsize=(10, 6))
plt.plot(t, signal, label='Original Signal', alpha=0.7)
# Adjust time axis for filtered signal due to 'valid' mode in convolve
plt.plot(t, filtered_signal, label='Filtered Signal', color='red')
plt.title('FIR Low-Pass Filter Example')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
# plt.show()
# plt.savefig("filtered.png")


# Convert coefficients to 16-bit fixed point (Q1.15 format)
fixed_coeffs, conversion_info = float_to_fixed_point(fir_coefficients)
scale = conversion_info['scale_factor']
print(f"Scale factor: {scale}")
print(f"Fixed-point coefficients (16-bit signed integers):")
print(fixed_coeffs)
print(f"\nCoefficient range: {np.min(fixed_coeffs)} to {np.max(fixed_coeffs)}")

# Verify conversion by converting back to float
recovered_coeffs = fixed_coeffs.astype(np.float64) / scale
max_error = np.max(np.abs(fir_coefficients - recovered_coeffs))
print(f"Maximum quantization error: {max_error:.2e}")


# Test the fixed-point filter
fixed_filtered, info = apply_fixed_point_filter(signal, fixed_coeffs, scale)
float_filtered = apply_fir_filter(signal, fir_coefficients)

# Compare results
plt.figure(figsize=(12, 8))

plt.subplot(2, 1, 1)
plt.plot(t, signal, label='Original Signal', alpha=0.7)
plt.plot(t, float_filtered, label='Float Filter', color='red', linewidth=2)
plt.plot(t, fixed_filtered, label='Fixed-Point Filter', color='green', linestyle='--', linewidth=2)
plt.title('Comparison: Floating-Point vs Fixed-Point Filter')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)

plt.subplot(2, 1, 2)
error = float_filtered - fixed_filtered
plt.plot(t, error)
plt.title('Error between Float and Fixed-Point Filters')
plt.xlabel('Time (s)')
plt.ylabel('Error')
plt.grid(True)

plt.tight_layout()
# plt.show()
# plt.save("")

print(f"Maximum error between float and fixed-point filters: {np.max(np.abs(error)):.2e}")
print(f"RMS error: {np.sqrt(np.mean(error**2)):.2e}")


# Analyze current signal characteristics
print("Current signal characteristics:")
print(f"Signal range: {np.min(signal):.3f} to {np.max(signal):.3f}")
print(f"Signal mean: {np.mean(signal):.3f}")
print(f"Signal std: {np.std(signal):.3f}")
print(f"Signal length: {len(signal)}")

# Create 8-bit ADC version of signal
# First, scale and offset the signal to fit in ADC range
signal_scaled = signal * 0.6  # Scale down to prevent clipping
signal_offset = 1.65  # Add DC offset (middle of 3.3V range)

adc_signal, info = simulate_8bit_adc(signal_scaled)
adc_codes = adc_signal

print(f"\nAfter scaling and offset for 8-bit ADC:")
print(f"Scaled signal range: {np.min(signal_scaled + signal_offset):.3f} to {np.max(signal_scaled + signal_offset):.3f}")
print(f"ADC codes range: {np.min(adc_codes)} to {np.max(adc_codes)}")
print(f"Quantized signal range: {np.min(adc_signal):.3f}V to {np.max(adc_signal):.3f}V")

# Plot comparison
plt.figure(figsize=(14, 10))

plt.subplot(3, 1, 1)
plt.plot(t, signal, label='Original Signal', alpha=0.7)
plt.plot(t, signal_scaled + signal_offset, label='Scaled + Offset Signal', alpha=0.7)
plt.title('Original vs Scaled Signal for ADC')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude (V)')
plt.legend()
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(t, adc_codes, label='8-bit ADC Codes', color='red', linewidth=1)
plt.title('8-bit ADC Output Codes (0-255)')
plt.xlabel('Time (s)')
plt.ylabel('ADC Code')
plt.legend()
plt.grid(True)

plt.subplot(3, 1, 3)
plt.plot(t, signal_scaled + signal_offset, label='Analog Signal', alpha=0.7)
plt.plot(t, adc_signal, label='Quantized Signal', color='green', linewidth=1.5)
plt.title('Analog vs Quantized Signal')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid(True)

plt.tight_layout()
# plt.show()

# Calculate quantization noise
quantization_error = (signal_scaled + signal_offset) - adc_signal
print(f"\nQuantization characteristics:")
print(f"Quantization step size: {3.3/255:.4f}V")
print(f"Max quantization error: {np.max(np.abs(quantization_error)):.4f}V")
print(f"RMS quantization error: {np.sqrt(np.mean(quantization_error**2)):.4f}V")



# Test the 8-bit ADC fixed-point filter
vref = 3.3  # ADC reference voltage
filtered_adc_voltage, info = apply_fixed_point_filter_8bit_adc(adc_signal, fixed_coeffs, adc_range=(0, 2.5))
filtered_adc_codes = filtered_adc_voltage

# For comparison, also filter the quantized signal using floating point
float_filtered_adc = apply_fir_filter(adc_signal, fir_coefficients)

# Compare results
plt.figure(figsize=(15, 12))

plt.subplot(4, 1, 1)
plt.plot(t, adc_codes, label='Original ADC Codes', alpha=0.7, linewidth=1)
plt.plot(t, filtered_adc_codes, label='Filtered ADC Codes', color='red', linewidth=2)
plt.title('8-bit ADC Codes: Original vs Filtered')
plt.xlabel('Time (s)')
plt.ylabel('ADC Code (0-255)')
plt.legend()
plt.grid(True)

plt.subplot(4, 1, 2)
plt.plot(t, adc_signal, label='Original Quantized Signal', alpha=0.7)
plt.plot(t, float_filtered_adc, label='Float Filter', color='red', linewidth=2)
plt.plot(t, filtered_adc_voltage, label='Fixed-Point Filter (8-bit ADC)', color='green', linestyle='--', linewidth=2)
plt.title('Voltage Comparison: Float vs Fixed-Point Filter (8-bit ADC)')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid(True)

plt.subplot(4, 1, 3)
adc_error = float_filtered_adc - filtered_adc_voltage
plt.plot(t, adc_error)
plt.title('Error between Float and Fixed-Point Filters (8-bit ADC)')
plt.xlabel('Time (s)')
plt.ylabel('Voltage Error (V)')
plt.grid(True)

plt.subplot(4, 1, 4)
# Show frequency response by plotting power spectral density
from scipy import signal as scipy_signal
f_orig, psd_orig = scipy_signal.welch(adc_signal, sample_rate, nperseg=256)
f_filt, psd_filt = scipy_signal.welch(filtered_adc_voltage, sample_rate, nperseg=min(256, len(filtered_adc_voltage)))

plt.loglog(f_orig, psd_orig, label='Original ADC Signal', alpha=0.7)
plt.loglog(f_filt, psd_filt, label='Filtered Signal', color='red', linewidth=2)
plt.axvline(cutoff_freq, color='black', linestyle='--', label=f'Cutoff: {cutoff_freq} Hz')
plt.title('Power Spectral Density')
plt.xlabel('Frequency (Hz)')
plt.ylabel('PSD (V²/Hz)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

print(f"8-bit ADC Filter Results:")
print(f"Maximum error between float and fixed-point filters: {np.max(np.abs(adc_error)):.4f}V")
print(f"RMS error: {np.sqrt(np.mean(adc_error**2)):.4f}V")
print(f"Error as percentage of signal range: {np.max(np.abs(adc_error))/vref*100:.2f}%")

# Show some sample values for hardware verification
print(f"\nSample ADC processing (first 10 samples):")
print(f"Original ADC codes: {adc_codes[:10]}")
print(f"Filtered ADC codes: {filtered_adc_codes[:10]}")
print(f"Original voltage: {adc_signal[:10]}")
print(f"Filtered voltage: {filtered_adc_voltage[:10]}")