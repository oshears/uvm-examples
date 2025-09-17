--========================================================================================================================
-- Copyright (c) 2017 by Bitvis AS.  All rights reserved.
-- You should have received a copy of the license file containing the MIT License (see LICENSE.TXT), if not, 
-- contact Bitvis AS <support@bitvis.no>.
--
-- UVVM AND ANY PART THEREOF ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
-- WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
-- OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
-- OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH UVVM OR THE USE OR OTHER DEALINGS IN UVVM.
--========================================================================================================================

------------------------------------------------------------------------------------------
-- Description   : See library quick reference (under 'doc') and README-file(s)
------------------------------------------------------------------------------------------


library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;


library uvvm_util;
  context uvvm_util.uvvm_util_context;

library uvvm_vvc_framework;
use uvvm_vvc_framework.ti_vvc_framework_support_pkg.all;

--library vip_counter;
use work.vvc_methods_pkg.all;
use work.td_vvc_framework_common_methods_pkg.all;

use std.textio.all;

-- Test bench entity
entity counter_vvc_tb is
end entity;

-- Test bench architecture
architecture func of counter_vvc_tb is

  constant C_SCOPE              : string  := C_TB_SCOPE_DEFAULT;

  -- Clock and bit period settings
  constant C_CLK_PERIOD         : time := 10 ns;
  constant C_BIT_PERIOD         : time := 16 * C_CLK_PERIOD;
  
begin

  -----------------------------------------------------------------------------
  -- Instantiate test harness, containing DUT and Executors
  -----------------------------------------------------------------------------
  i_test_harness : entity work.counter_vvc_th;
 

  ------------------------------------------------
  -- PROCESS: p_main
  ------------------------------------------------
  p_main: process
    variable L : line;
  begin
  
    -- Wait for UVVM to finish initialization
    await_uvvm_initialization(VOID);
    
    -- TO DO: redirect all messages to a file and the screen

    
    -- TO DO: output the section headers, any message from here and messages related to sending commands to a VVC
    
    
    -- TO DO: output messages with ID ID_BFM and messages related to the testbench terminating (for whatever reason)
    
    -- IYHT: increase the ERROR stop limit

    -- TO DO: display which IDs are enabled or disabled

    -- IYHT: display the stop limits

    
    log(ID_LOG_HDR, "Starting simulation of TB for counter using VVCs", C_SCOPE);
    ------------------------------------------------------------

    log(ID_SEQUENCER, "Wait 10 clock period for reset to be turned off", C_SCOPE);
    wait for (10 * C_CLK_PERIOD); -- for reset to be turned off
    
    -- ANSWER: write your test case here

    

    -----------------------------------------------------------------------------
    -- Ending the simulation
    -----------------------------------------------------------------------------
    wait for 10 ns;             -- to allow some time for completion
    report_alert_counters(FINAL); -- Report final counters and print conclusion for simulation (Success/Fail)
    log(ID_LOG_HDR, "SIMULATION COMPLETED", C_SCOPE);

    -- Finish the simulation
    std.env.stop;
    wait;  -- to stop completely

  end process p_main;

end func;
