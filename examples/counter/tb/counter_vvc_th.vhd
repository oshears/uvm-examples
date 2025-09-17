
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

-- IYHT: add the context clause to use the util clock generator

library uvvm_vvc_framework;
use uvvm_vvc_framework.ti_vvc_framework_support_pkg.all;

--library vip_counter;


-- Test harness entity
entity counter_vvc_th is
end entity;

-- Test harness architecture
architecture struct of counter_vvc_th is

  -- general control signals
  signal clk            : std_logic  := '0';
  
  -- counter VVC signals
  signal Reset, Enable, Load, UpDn: Std_logic;
  signal Data, Q: Std_logic_vector(7 downto 0);

  constant C_CLK_PERIOD : time := 5 ns; -- 200 MHz

begin

  -----------------------------------------------------------------------------
  -- Instantiate the concurrent procedure that initializes UVVM
  -----------------------------------------------------------------------------
  i_ti_uvvm_engine : entity uvvm_vvc_framework.ti_uvvm_engine;

  -----------------------------------------------------------------------------
  -- Instantiate DUT
  -----------------------------------------------------------------------------
  i_counter: entity work.counter
    port map (
      -- general control signals
      Clock           => clk,
      -- counter signals
      Reset           => Reset,
      Enable          => Enable,
      Load            => Load,
      UpDn            => UpDn,
      Data            => Data,
      Q               => Q
  );


  -----------------------------------------------------------------------------
  -- counter VVC
  -----------------------------------------------------------------------------
  i_counter_vvc: entity work.counter_vvc
  generic map(
    GC_DATA_WIDTH     => 8,
    GC_INSTANCE_IDX   => 1
  )
  port map(
    clk                   => clk,
    counter_vvc_if.Reset  => Reset,
    counter_vvc_if.Enable => Enable,
    counter_vvc_if.Load   => Load,
    counter_vvc_if.UpDn   => UpDn,
    counter_vvc_if.Data   => Data,
    counter_vvc_if.Q      => Q
  );

 
  -----------------------------------------------------------------------------
  -- Clock process
  -----------------------------------------------------------------------------  
  p_clk: process
  begin
    clk <= '0', '1' after C_CLK_PERIOD / 2;
    wait for C_CLK_PERIOD;
  end process;
  
  -- IYHT: use the util clock generator

end struct;
