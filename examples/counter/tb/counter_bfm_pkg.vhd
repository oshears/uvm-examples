--========================================================================================================================
-- This VVC was generated with Bitvis VVC Generator
--========================================================================================================================


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library uvvm_util;
context uvvm_util.uvvm_util_context;

--========================================================================================================================
--========================================================================================================================
package counter_bfm_pkg is

  --========================================================================================================================
  -- Types and constants for COUNTER BFM 
  --========================================================================================================================
  constant C_SCOPE : string := "COUNTER BFM";

  -- Optional interface record for BFM signals
  type t_counter_if is record
    --<USER_INPUT> Insert all BFM signals here
    Reset    : std_logic;          -- to dut
    Enable   : std_logic;          -- to dut
    Load     : std_logic;          -- to dut
    UpDn     : std_logic;          -- to dut
    Data     : std_logic_vector;   -- to dut
    Q        : std_logic_vector;   -- from dut
  end record;

  -- Configuration record to be assigned in the test harness.
  type t_counter_bfm_config is
  record
    --<USER_INPUT> Insert all BFM config parameters here
    -- Example:
    -- max_wait_cycles          : integer;
    -- max_wait_cycles_severity : t_alert_level;
    id_for_bfm               : t_msg_id;
    -- id_for_bfm_wait          : t_msg_id;
    -- id_for_bfm_poll          : t_msg_id;
    clock_period             : time;  -- Needed in the VVC
  end record;

  -- Define the default value for the BFM config
  constant C_COUNTER_BFM_CONFIG_DEFAULT : t_counter_bfm_config := (
    --<USER_INPUT> Insert defaults for all BFM config parameters here
    -- Example:
    -- max_wait_cycles          => 10,
    -- max_wait_cycles_severity => failure,
    id_for_bfm               => ID_BFM,
    -- id_for_bfm_wait          => ID_BFM_WAIT,
    -- id_for_bfm_poll          => ID_BFM_POLL,
    clock_period             => 5 ns
  );


  --========================================================================================================================
  -- BFM procedures 
  --========================================================================================================================


 --<USER_INPUT> Insert BFM procedure declarations here, e.g. read and write operations
 -- It is recommended to also have an init function which sets the BFM signals to their default state

  ------------------------------------------
  -- init_counter_if_signals
  ------------------------------------------
  -- - This function returns an SBI interface with initialized signals.
  -- - All counter input signals are initialized to 0
  -- - All counter outut signals are initialized to Z
  function init_counter_if_signals(
    data_width : natural
    ) return t_counter_if;


  ------------------------------------------
  -- counter_reset
  ------------------------------------------
  -- - This procedure resets the counter DUT 
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_reset (
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : out    std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );

  procedure counter_reset (
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );

  ------------------------------------------
  -- counter_check
  ------------------------------------------
  -- - This procedure checks the counter DUT Q output 
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_check (
    constant Q_exp         : in     std_logic_vector;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : out    std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant alert_level   : in     t_alert_level     := error;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );

  procedure counter_check (
    constant Q_exp         : in     std_logic_vector;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant alert_level   : in     t_alert_level     := error;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );
    
  ------------------------------------------
  -- counter_load
  ------------------------------------------
  -- - This procedure loads the counter DUT 
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_load (
    constant data_value    : in     std_logic_vector;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : inout  std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );

  procedure counter_load (
    constant data_value    : in     std_logic_vector;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );

  ------------------------------------------
  -- counter_count_up
  ------------------------------------------
  -- - This procedure makes the counter DUT count up
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_count_up (
    constant cycles        : in     natural;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : out    std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );

  procedure counter_count_up (
    constant cycles        : in     natural;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );

  -- IYHT: check counting down

  ------------------------------------------
  -- counter_hold
  ------------------------------------------
  -- - This procedure makes the counter DUT hold
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_hold (
    constant cycles        : in     natural;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : out    std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );

  procedure counter_hold (
    constant cycles        : in     natural;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    );

end package counter_bfm_pkg;


--========================================================================================================================
--========================================================================================================================

package body counter_bfm_pkg is


  --<USER_INPUT> Insert BFM procedure implementation here.
  ------------------------------------------
  -- init_counter_if_signals
  ------------------------------------------
  -- - This function returns an SBI interface with initialized signals.
  -- - All counter input signals are initialized to 0
  -- - All counter outut signals are initialized to Z
  function init_counter_if_signals(
    data_width : natural
    ) return t_counter_if is
    variable result : t_counter_if( data(data_width - 1 downto 0), 
                                       Q(data_width - 1 downto 0));
  begin
    result.Reset   := '0';
    result.Enable  := '0';
    result.Load    := '0';
    result.UpDn    := '0';
    result.Data    := (result.Data'range => '0');
    result.Q       := (result.Q'range => 'Z');
    return result;
  end function;


  ------------------------------------------
  -- counter_reset
  ------------------------------------------
  -- - This procedure resets the counter DUT 
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_reset (
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : out    std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
    constant proc_name  : string :=  "counter_reset";
    constant proc_call  : string :=  "counter_reset()";
  begin
    wait_num_rising_edge(clk, 1);
    Reset <= '1';
    wait_num_rising_edge(clk, 1);
    Reset <= '0';
    log(config.id_for_bfm, proc_call & " completed. " & add_msg_delimiter(msg), scope, msg_id_panel);
  end procedure;
  
  procedure counter_reset (
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
  begin
    counter_reset ( msg,          
                    clk,          
                    counter_if.Reset,        
                    counter_if.Enable,       
                    counter_if.Load,         
                    counter_if.UpDn,         
                    counter_if.Data,         
                    counter_if.Q,            
                    scope,        
                    msg_id_panel, 
                    config);
  end procedure;
  
  ------------------------------------------
  -- counter_check
  ------------------------------------------
  -- - This procedure checks the counter DUT Q output 
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_check (
    constant Q_exp         : in     std_logic_vector;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : out    std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant alert_level   : in     t_alert_level     := error;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
    constant proc_name  : string :=  "counter_check";
    constant proc_call  : string :=  "counter_check(Q_exp:" & to_string(Q_exp, HEX, AS_IS, INCL_RADIX) & ")";
    variable v_check_ok           : boolean;
    -- Normalise to the DUT Q width
    variable v_normalised_Q : std_logic_vector(Q'length-1 downto 0) :=
        normalize_and_check(Q_exp, Q, ALLOW_EXACT_ONLY, "Q_exp", "counter_core_in.Q", msg);
 begin
    v_check_ok := check_value(Q, Q_exp, alert_level, msg, scope, HEX_BIN_IF_INVALID, SKIP_LEADING_0, ID_NEVER, msg_id_panel, proc_call);
    if v_check_ok then
      log(config.id_for_bfm, proc_call & "=> OK, Q = " & to_string(Q_exp, HEX, SKIP_LEADING_0, INCL_RADIX) & ". " & add_msg_delimiter(msg), scope, msg_id_panel);
    end if;
  end procedure;

  procedure counter_check (
    constant Q_exp         : in     std_logic_vector;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant alert_level   : in     t_alert_level     := error;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
  begin
    counter_check ( Q_exp,
                    msg,          
                    clk,          
                    counter_if.Reset,        
                    counter_if.Enable,       
                    counter_if.Load,         
                    counter_if.UpDn,         
                    counter_if.Data,         
                    counter_if.Q,            
                    alert_level,
                    scope,
                    msg_id_panel, 
                    config);
  end procedure;

  ------------------------------------------
  -- counter_load
  ------------------------------------------
  -- - This procedure loads the counter DUT 
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_load (
    constant data_value    : in     std_logic_vector;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : inout  std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
    constant proc_name  : string :=  "counter_load";
    constant proc_call  : string :=  "counter_load(data_value:" & to_string(data_value, HEX, AS_IS, INCL_RADIX) & ")";
    -- Normalise to the DUT data_value width
    variable v_normalised_data : std_logic_vector(Data'length-1 downto 0) :=
        normalize_and_check(data_value, Data, ALLOW_EXACT_ONLY, "data_value", "counter_core_in.Data", msg);
 begin
    wait_num_rising_edge(clk, 1);
    Enable <= '1';
    Load   <= '1';
    Data   <= v_normalised_data;
    wait_num_rising_edge(clk, 1);
    Load   <= '0';
    log(config.id_for_bfm, proc_call & " completed. " & add_msg_delimiter(msg), scope, msg_id_panel);
  end procedure;

  procedure counter_load (
    constant data_value    : in     std_logic_vector;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
  begin
    counter_load (  data_value,
                    msg,          
                    clk,          
                    counter_if.Reset,        
                    counter_if.Enable,       
                    counter_if.Load,         
                    counter_if.UpDn,         
                    counter_if.Data,         
                    counter_if.Q,            
                    scope,        
                    msg_id_panel, 
                    config);
  end procedure;

  ------------------------------------------
  -- counter_count_up
  ------------------------------------------
  -- - This procedure makes the counter DUT count up
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_count_up (
    constant cycles        : in     natural;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : out    std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
    use std.textio.side;
    constant proc_name  : string :=  "counter_count_up";
    constant proc_call  : string :=  "counter_count_up(cycles:" & integer'image(cycles) & ")";
    -- Normalise to the DUT data_value width
 begin
    Enable <= '1';
    UpDn   <= '1';
    Load   <= '0';
    wait_num_rising_edge(clk, cycles);
    log(config.id_for_bfm, proc_call & " completed. " & add_msg_delimiter(msg), scope, msg_id_panel);
  end procedure;

  procedure counter_count_up (
    constant cycles        : in     natural;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
  begin
    counter_count_up (  cycles,
                        msg,          
                        clk,          
                        counter_if.Reset,        
                        counter_if.Enable,       
                        counter_if.Load,         
                        counter_if.UpDn,         
                        counter_if.Data,         
                        counter_if.Q,            
                        scope,        
                        msg_id_panel, 
                        config);
  end procedure;

  -- IYHT: check counting down

  ------------------------------------------
  -- counter_hold
  ------------------------------------------
  -- - This procedure makes the counter DUT hold
  -- - The counter interface in this procedure is given as individual signals
  procedure counter_hold (
    constant cycles        : in     natural;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   Reset         : out    std_logic;
    signal   Enable        : out    std_logic;
    signal   Load          : out    std_logic;
    signal   UpDn          : out    std_logic;
    signal   Data          : out    std_logic_vector;
    signal   Q             : inout  std_logic_vector;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
    use std.textio.side;
    constant proc_name  : string :=  "counter_hold";
    constant proc_call  : string :=  "counter_hold(cycles:" & integer'image(cycles) & ")";
    -- Normalise to the DUT data_value width
 begin
    Enable <= '0';
    wait_num_rising_edge(clk, cycles);
    log(config.id_for_bfm, proc_call & " completed. " & add_msg_delimiter(msg), scope, msg_id_panel);
  end procedure;

  procedure counter_hold (
    constant cycles        : in     natural;
    constant msg           : in     string;
    signal   clk           : in     std_logic;
    signal   counter_if    : inout  t_counter_if;
    constant scope         : in     string            := C_SCOPE;
    constant msg_id_panel  : in     t_msg_id_panel    := shared_msg_id_panel;
    constant config        : in     t_counter_bfm_config  := C_COUNTER_BFM_CONFIG_DEFAULT
    ) is
  begin
    counter_hold (  cycles,
                    msg,          
                    clk,          
                    counter_if.Reset,        
                    counter_if.Enable,       
                    counter_if.Load,         
                    counter_if.UpDn,         
                    counter_if.Data,         
                    counter_if.Q,            
                    scope,        
                    msg_id_panel, 
                    config);
  end procedure;


end package body counter_bfm_pkg;

