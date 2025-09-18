// Simple transaction class
class MuxTransaction;
    rand bit [1:0] sel;
    rand bit [3:0] din;
    bit dout;
endclass

// Generator
class MuxGenerator;
    MuxTransaction tr;
    function void create();
        tr = new();
        tr.randomize();
    endfunction
endclass

// Driver
class MuxDriver;
    virtual mux_if vif;
    function void drive(MuxTransaction tr);
        vif.sel <= tr.sel;
        vif.din <= tr.din;
    endfunction
endclass

// Monitor
class MuxMonitor;
    virtual mux_if vif;
    MuxTransaction tr;
    function void monitor();
        tr = new();
        tr.sel = vif.sel;
        tr.din = vif.din;
        tr.dout = vif.dout;
    endfunction
endclass

// Scoreboard
class MuxScoreboard;
    function void check(MuxTransaction tr);
        bit expected = tr.din[tr.sel];
        if (tr.dout !== expected)
            $error("Mismatch: sel=%0d din=%0b dout=%0b expected=%0b", tr.sel, tr.din, tr.dout, expected);
    endfunction
endclass

// Interface for mux DUT
interface mux_if;
    logic [1:0] sel;
    logic [3:0] din;
    logic dout;
endinterface

// Example usage in a module
module Testbench;
    mux_if mux_if_inst();
    MuxGenerator gen;
    MuxDriver drv;
    MuxMonitor mon;
    MuxScoreboard sb;

    initial begin
        gen = new();
        drv = new();
        drv.vif = mux_if_inst;
        mon = new();
        mon.vif = mux_if_inst;
        sb = new();

        // Generate, drive, monitor, and check
        for (int i = 0; i < 10; i++) begin
            gen.create();
            drv.drive(gen.tr);
            #1; // Wait for DUT to respond
            mon.monitor();
            sb.check(mon.tr);
        end
    end
endmodule