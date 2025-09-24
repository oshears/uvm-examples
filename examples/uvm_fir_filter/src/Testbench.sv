import uvm_pkg::*;

module Testbench;

    reg clk = 0;

    localparam CLK_PERIOD = 10; // 100 MHz Clk
    always #(CLK_PERIOD/2) clk = ~clk;

    MemoryInterface mem_if (clk);

    BRAM_WRAPPER dut_bram (.vif(mem_if));

    initial begin
        uvm_config_db#(virtual MemoryInterface)::set(
            null, "uvm_test_top", "MemoryInterface", mem_if
        );
        run_test("RandomMemoryTest");
    end

    

endmodule;