module BRAM(
  input wire clk,
  input wire [7:0] raddr,
  input wire [7:0] waddr,
  output reg [31:0] rdata,
  input wire [31:0] wdata,
  input wire we
);


reg [31:0] mem [0:255];

always @(posedge clk) begin
  rdata <= mem[raddr];
  if (we)
    mem[waddr] <= wdata;
end

endmodule

module BRAM_WRAPPER(MemoryInterface.BRAM vif);

  BRAM u_bram (
    .clk(vif.clk),
    .raddr(vif.raddr),
    .waddr(vif.waddr),
    .rdata(vif.rdata),
    .wdata(vif.wdata),
    .we(vif.we)
  );
endmodule