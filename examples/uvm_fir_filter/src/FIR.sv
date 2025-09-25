package FIR_PKG;

  localparam logic signed [15:0] fir_coeffs[0:12] = '{
    16'hFFA7,  // -89
    16'h0000,  // 0
    16'h0206,  // 518
    16'h079B,  // 1947
    16'h1044,  // 4164
    16'h1880,  // 6272
    16'h1BE9,  // 7145
    16'h1880,  // 6272
    16'h1044,  // 4164
    16'h079B,  // 1947
    16'h0206,  // 518
    16'h0000,  // 0
    16'hFFA7  // -89
  };

endpackage

module FIR(
  input wire clk,
  input wire en,
  input wire [7:0] data_in,
  output reg [7:0] data_out
);

  import FIR_PKG::*;

  // Shift register for input samples
  reg signed [7:0] shift_reg [13];

  // Accumulator for MAC operations
  reg signed [31:0] accumulator;

  // Output scaling and saturation
  wire signed [31:0] scaled_output;
  wire signed [7:0] saturated_output;

  integer i;

  always @(posedge clk) begin
    if (en) begin
      // Shift input samples through delay line
      for (i = 12; i > 0; i = i - 1) begin
        shift_reg[i] <= shift_reg[i-1];
      end
      shift_reg[0] <= $signed(data_in);

      // MAC (Multiply-Accumulate) operations
      accumulator <= 0;
      for (i = 0; i <= 12; i = i + 1) begin
        accumulator <= accumulator + (shift_reg[i] * fir_coeffs[i]);
      end
    end
  end

  // Scale down by coefficient scale factor (divide by 2^15 = 32768)
  // and handle saturation for 8-bit output
  assign scaled_output = accumulator >>> 15;

  // Saturate to 8-bit range (-128 to 127)
  assign saturated_output = (scaled_output > 127) ? 127 :
                           (scaled_output < -128) ? -128 :
                           scaled_output[7:0];

  always @(posedge clk) begin
    if (en) begin
      data_out <= saturated_output;
    end
  end

endmodule

module FIR_WRAPPER(MemoryInterface.BRAM vif);

  BRAM u_bram (
    .clk(vif.clk),
    .raddr(vif.raddr),
    .waddr(vif.waddr),
    .rdata(vif.rdata),
    .wdata(vif.wdata),
    .we(vif.we)
  );
endmodule
