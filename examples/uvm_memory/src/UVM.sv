import uvm_pkg::*;

class MemoryTransaction extends uvm_sequence_item;

    //     Error-[TMAFTC] Too many arguments to function/task call
    // ./src/UVM.sv, 5
    // "MemoryTransaction::new(name)"
    //   The above function/task call is done with more arguments than needed.
    `uvm_object_utils(MemoryTransaction)

  function new(string name = "MemoryTransaction");
    super.new(name);
  endfunction

    rand bit [7:0]  waddr;
    rand bit [31:0] wdata;
    rand bit [7:0]  raddr;
    rand bit [31:0] rdata;
    rand bit        we;

    virtual function string convert2str();
        return $sformatf(
          "waddr=%0d, wdata=%0d, raddr=%0d, rdata=%0d, we=%0d", waddr, wdata, raddr, rdata, we
        );
    endfunction

    constraint address_constraint {
        waddr inside {[0:255]};
        waddr % 4 == 0;
        raddr inside {[0:255]};
        raddr % 4 == 0;
        wdata inside {[0:15]};
    };

endclass

interface MemoryInterface (input bit clk);
    logic [7:0] waddr;
    logic [7:0] raddr;
    logic [31:0] rdata;
    logic [31:0] wdata;
    logic we;

    modport BRAM (
        input clk,
        input waddr,
        input raddr,
        output rdata,
        input wdata,
        input we
    );

    clocking cb @(posedge clk);
      default input #1step output #3ns;
    //input out;
    //output in;
    output waddr;
    output raddr;
    input rdata;
    output wdata;
    output we;

    endclocking
endinterface

class MemoryDriver extends uvm_driver #(MemoryTransaction);

  `uvm_component_utils(MemoryDriver)

  function new(string name = "MemoryDriver", uvm_component parent=null);
    super.new(name, parent);
  endfunction

  virtual MemoryInterface vif;

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if (!uvm_config_db#(virtual MemoryInterface)::get(this, "", "MemoryInterface", vif))
      `uvm_fatal("DRV", "Could not get MemoryInterface")
  endfunction

  virtual task run_phase(uvm_phase phase);
    super.run_phase(phase);
    forever begin
      MemoryTransaction m_item;
      `uvm_info("DRV", $sformatf("Wait for item from sequencer"), UVM_HIGH)
      seq_item_port.get_next_item(m_item);
      DriveTransaction(m_item);
      seq_item_port.item_done();
    end
  endtask

  virtual task DriveTransaction(MemoryTransaction m_item);
    @(vif.cb);
    vif.cb.waddr <= m_item.waddr;
    vif.cb.wdata <= m_item.wdata;
    vif.cb.we <= m_item.we;
    vif.cb.raddr <= m_item.raddr;
    @(vif.cb);
    vif.cb.waddr <= 0;
    vif.cb.wdata <= 0;
    vif.cb.we <= 0;
    vif.cb.raddr <= 0;

  endtask
endclass

class MemoryAgent extends uvm_agent;

    `uvm_component_utils(MemoryAgent)

      function new(string name="MemoryAgent", uvm_component parent=null);
        super.new(name, parent);
      endfunction

    MemoryDriver driver; // Driver handle
        //   monitor m0; // Monitor handle
    uvm_sequencer #(MemoryTransaction) sequencer; // Sequencer Handle

    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        sequencer = uvm_sequencer#(MemoryTransaction)::type_id::create("sequencer", this);
        driver = MemoryDriver::type_id::create("driver", this);
    endfunction

    virtual function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        driver.seq_item_port.connect(sequencer.seq_item_export);
    endfunction

endclass

class MemoryEnvironment extends uvm_env;
  `uvm_component_utils(MemoryEnvironment)

  function new(string name="env", uvm_component parent=null);
    super.new(name, parent);
  endfunction

  MemoryAgent agent; // Agent handle
//   MemoryScoreboard scoreboard; // Scoreboard handle

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    agent = MemoryAgent::type_id::create("agent", this);
    // scoreboard = MemoryScoreboard::type_id::create("MemoryScoreboard", this);
  endfunction

  virtual function void connect_phase(uvm_phase phase);
    super.connect_phase(phase);
    // agent.m0.mon_analysis_port.connect(scoreboard.m_analysis_imp);
  endfunction
endclass

class MemoryTestSequence extends uvm_sequence;
    `uvm_object_utils(MemoryTestSequence)

  function new(string name="MemoryTestSequence");
    super.new(name);
  endfunction

    rand int num; // Config total number of items to be sent

//   constraint c1 { soft num inside {[10:10]}; }
    constraint c1 { soft num == 10;}

    virtual task body();
        for (int i = 0; i < num; i ++) begin
            MemoryTransaction m_item = MemoryTransaction::type_id::create("m_item");
            start_item(m_item);
            m_item.randomize();
            `uvm_info("SEQ", $sformatf("Generate new item: %s", m_item.convert2str()), UVM_HIGH)
            finish_item(m_item);
        end
        `uvm_info("SEQ", $sformatf("Done generation of %0d items", num), UVM_LOW)
  endtask
endclass

class BaseMemoryTest extends uvm_test;

  `uvm_component_utils(BaseMemoryTest)

  function new(string name = "BaseMemoryTest", uvm_component parent=null);
    super.new(name, parent);
  endfunction

  MemoryEnvironment env;
  MemoryTestSequence seq;
  virtual MemoryInterface vif;

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);

    // Create the environment
    env = MemoryEnvironment::type_id::create("env", this);

    // Get virtual IF handle from top level and pass it to everything
    // in env level
    if (!uvm_config_db#(virtual MemoryInterface)::get(this, "", "vif", vif))
      `uvm_fatal("TEST", "Did not get vif")
    uvm_config_db#(virtual MemoryInterface)::set(this, "env.agent.*", "vif", vif);

    // Setup pattern queue and place into config db
    // uvm_config_db#(bit[`LENGTH-1:0])::set(this, "*", "ref_pattern", pattern);

    // Create sequence and randomize it

  endfunction

  virtual task run_phase(uvm_phase phase);
    phase.raise_objection(this);
    // apply_reset();
    seq.start(env.agent.sequencer);
    #200;
    phase.drop_objection(this);
  endtask

  virtual task initialize_memory();
  endtask;

//   virtual task apply_reset();
//     vif.rstn <= 0;
//     vif.in <= 0;
//     repeat(5) @ (posedge vif.clk);
//     vif.rstn <= 1;
//     repeat(10) @ (posedge vif.clk);
//   endtask
endclass

class RandomMemoryTest extends BaseMemoryTest;
  `uvm_component_utils(RandomMemoryTest)

  function new(string name="RandomMemoryTest", uvm_component parent=null);
    // super.new(name, parent);
    super.new(name, parent);
    seq = MemoryTestSequence::type_id::create("seq");
    seq.randomize();
  endfunction

//   virtual function void build_phase(uvm_phase phase);
//     // pattern = 4'b1011;
//     super.build_phase(phase);
//     // seq.randomize() with { num inside {[300:500]}; };
//   endfunction
endclass

