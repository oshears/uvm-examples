--========================================================================================================================
-- This VVC was generated with Bitvis VVC Generator
--========================================================================================================================


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library uvvm_util;
context uvvm_util.uvvm_util_context;

library uvvm_vvc_framework;
use uvvm_vvc_framework.ti_vvc_framework_support_pkg.all;

use work.counter_bfm_pkg.all;
use work.vvc_methods_pkg.all;
use work.vvc_cmd_pkg.all;
use work.td_target_support_pkg.all;
use work.td_vvc_entity_support_pkg.all;
use work.td_cmd_queue_pkg.all;
use work.td_result_queue_pkg.all;

--========================================================================================================================
entity counter_vvc is
  generic (
    --<USER_INPUT> Insert interface specific generic constants here
    GC_DATA_WIDTH                            : integer range 1 to C_VVC_CMD_DATA_MAX_LENGTH;
    GC_INSTANCE_IDX                          : natural;
    GC_COUNTER_BFM_CONFIG                    : t_counter_bfm_config      := C_COUNTER_BFM_CONFIG_DEFAULT;
    GC_CMD_QUEUE_COUNT_MAX                   : natural                   := 1000;
    GC_CMD_QUEUE_COUNT_THRESHOLD             : natural                   := 950;
    GC_CMD_QUEUE_COUNT_THRESHOLD_SEVERITY    : t_alert_level             := WARNING;
    GC_RESULT_QUEUE_COUNT_MAX                : natural                   := 1000;
    GC_RESULT_QUEUE_COUNT_THRESHOLD          : natural                   := 950;
    GC_RESULT_QUEUE_COUNT_THRESHOLD_SEVERITY : t_alert_level             := WARNING
  );
  port (
    --<USER_INPUT> Insert BFM interface signals here
    counter_vvc_if              : inout t_counter_if := init_counter_if_signals( GC_DATA_WIDTH); 
    -- VVC control signals: 
    -- rst                         : in std_logic; -- Optional VVC Reset
    clk                         : in std_logic
  );
end entity counter_vvc;

--========================================================================================================================
--========================================================================================================================
architecture behave of counter_vvc is

  constant C_SCOPE      : string        := C_VVC_NAME & "," & to_string(GC_INSTANCE_IDX);
  constant C_VVC_LABELS : t_vvc_labels  := assign_vvc_labels(C_SCOPE, C_VVC_NAME, GC_INSTANCE_IDX, NA);

  signal executor_is_busy       : boolean := false;
  signal queue_is_increasing    : boolean := false;
  signal last_cmd_idx_executed  : natural := 0;
  signal terminate_current_cmd  : t_flag_record;

  -- Instantiation of the element dedicated Queue
  shared variable command_queue : work.td_cmd_queue_pkg.t_generic_queue;
  shared variable result_queue  : work.td_result_queue_pkg.t_generic_queue;

  alias vvc_config : t_vvc_config is shared_counter_vvc_config(GC_INSTANCE_IDX);
  alias vvc_status : t_vvc_status is shared_counter_vvc_status(GC_INSTANCE_IDX);
  alias transaction_info : t_transaction_info is shared_counter_transaction_info(GC_INSTANCE_IDX);

begin


--========================================================================================================================
-- Constructor
-- - Set up the defaults and show constructor if enabled
--========================================================================================================================
  work.td_vvc_entity_support_pkg.vvc_constructor(C_SCOPE, GC_INSTANCE_IDX, vvc_config, command_queue, result_queue, GC_COUNTER_BFM_CONFIG,
                  GC_CMD_QUEUE_COUNT_MAX, GC_CMD_QUEUE_COUNT_THRESHOLD, GC_CMD_QUEUE_COUNT_THRESHOLD_SEVERITY,
                  GC_RESULT_QUEUE_COUNT_MAX, GC_RESULT_QUEUE_COUNT_THRESHOLD, GC_RESULT_QUEUE_COUNT_THRESHOLD_SEVERITY);
--========================================================================================================================


--========================================================================================================================
-- Command interpreter
-- - Interpret, decode and acknowledge commands from the central sequencer
--========================================================================================================================
  cmd_interpreter : process
     variable v_cmd_has_been_acked : boolean; -- Indicates if acknowledge_cmd() has been called for the current shared_vvc_cmd
     variable v_local_vvc_cmd        : t_vvc_cmd_record := C_VVC_CMD_DEFAULT;
  begin

    -- 0. Initialize the process prior to first command
    work.td_vvc_entity_support_pkg.initialize_interpreter(terminate_current_cmd, global_awaiting_completion);
    -- initialise shared_vvc_last_received_cmd_idx for channel and instance
    shared_vvc_last_received_cmd_idx(NA, GC_INSTANCE_IDX) := 0;

    -- Then for every single command from the sequencer
    loop  -- basically as long as new commands are received

      -- 1. wait until command targeted at this VVC. Must match VVC name, instance and channel (if applicable)
      --    releases global semaphore
      -------------------------------------------------------------------------
      work.td_vvc_entity_support_pkg.await_cmd_from_sequencer(C_VVC_LABELS, vvc_config, THIS_VVCT, VVC_BROADCAST, global_vvc_busy, global_vvc_ack, shared_vvc_cmd, v_local_vvc_cmd);
      v_cmd_has_been_acked := false; -- Clear flag
      -- update shared_vvc_last_received_cmd_idx with received command index
      shared_vvc_last_received_cmd_idx(NA, GC_INSTANCE_IDX) := v_local_vvc_cmd.cmd_idx;

      -- 2a. Put command on the queue if intended for the executor
      -------------------------------------------------------------------------
      if v_local_vvc_cmd.command_type = QUEUED then
        work.td_vvc_entity_support_pkg.put_command_on_queue(v_local_vvc_cmd, command_queue, vvc_status, queue_is_increasing);

      -- 2b. Otherwise command is intended for immediate response
      -------------------------------------------------------------------------
      elsif v_local_vvc_cmd.command_type = IMMEDIATE then
        case v_local_vvc_cmd.operation is

          when AWAIT_COMPLETION =>
            -- Await completion of all commands in the cmd_executor queue
            work.td_vvc_entity_support_pkg.interpreter_await_completion(v_local_vvc_cmd, command_queue, vvc_config, executor_is_busy, C_VVC_LABELS, last_cmd_idx_executed);

          when AWAIT_ANY_COMPLETION =>
            if not v_local_vvc_cmd.gen_boolean then
              -- Called with lastness = NOT_LAST: Acknowledge immediately to let the sequencer continue
              work.td_target_support_pkg.acknowledge_cmd(global_vvc_ack,v_local_vvc_cmd.cmd_idx);
              v_cmd_has_been_acked := true;
            end if;
            work.td_vvc_entity_support_pkg.interpreter_await_any_completion(v_local_vvc_cmd, command_queue, vvc_config, executor_is_busy, C_VVC_LABELS, last_cmd_idx_executed, global_awaiting_completion);

          when DISABLE_LOG_MSG =>
            uvvm_util.methods_pkg.disable_log_msg(v_local_vvc_cmd.msg_id, vvc_config.msg_id_panel, to_string(v_local_vvc_cmd.msg) & format_command_idx(v_local_vvc_cmd), C_SCOPE, v_local_vvc_cmd.quietness);

          when ENABLE_LOG_MSG =>
            uvvm_util.methods_pkg.enable_log_msg(v_local_vvc_cmd.msg_id, vvc_config.msg_id_panel, to_string(v_local_vvc_cmd.msg) & format_command_idx(v_local_vvc_cmd), C_SCOPE, v_local_vvc_cmd.quietness);

          when FLUSH_COMMAND_QUEUE =>
            work.td_vvc_entity_support_pkg.interpreter_flush_command_queue(v_local_vvc_cmd, command_queue, vvc_config, vvc_status, C_VVC_LABELS);

          when TERMINATE_CURRENT_COMMAND =>
            work.td_vvc_entity_support_pkg.interpreter_terminate_current_command(v_local_vvc_cmd, vvc_config, C_VVC_LABELS, terminate_current_cmd);

          -- when FETCH_RESULT =>
            -- work.td_vvc_entity_support_pkg.interpreter_fetch_result(result_queue, v_local_vvc_cmd, vvc_config, C_VVC_LABELS, last_cmd_idx_executed, shared_vvc_response);

          when others =>
            tb_error("Unsupported command received for IMMEDIATE execution: '" & to_string(v_local_vvc_cmd.operation) & "'", C_SCOPE);

        end case;

      else
        tb_error("command_type is not IMMEDIATE or QUEUED", C_SCOPE);
      end if;

      -- 3. Acknowledge command after runing or queuing the command
      -------------------------------------------------------------------------
      if not v_cmd_has_been_acked then
        work.td_target_support_pkg.acknowledge_cmd(global_vvc_ack,v_local_vvc_cmd.cmd_idx);
      end if;

    end loop;
  end process;
--========================================================================================================================



--========================================================================================================================
-- Command executor
-- - Fetch and execute the commands
--========================================================================================================================
  cmd_executor : process
    variable v_cmd                                    : t_vvc_cmd_record;
    --variable v_Q                                      : t_vvc_result; -- See vvc_cmd_pkg
    variable v_timestamp_start_of_current_bfm_access  : time := 0 ns;
    variable v_timestamp_start_of_last_bfm_access     : time := 0 ns;
    variable v_timestamp_end_of_last_bfm_access       : time := 0 ns;
    variable v_command_is_bfm_access                  : boolean;
    variable v_normalised_data    : std_logic_vector(GC_DATA_WIDTH-1 downto 0) := (others => '0');
    variable v_normalised_Q       : std_logic_vector(GC_DATA_WIDTH-1 downto 0) := (others => '0');
    variable v_normalised_cycles  : natural;
  begin

    -- 0. Initialize the process prior to first command
    -------------------------------------------------------------------------
    work.td_vvc_entity_support_pkg.initialize_executor(terminate_current_cmd);
    loop

      -- 1. Set defaults, fetch command and log
      -------------------------------------------------------------------------
      work.td_vvc_entity_support_pkg.fetch_command_and_prepare_executor(v_cmd, command_queue, vvc_config, vvc_status, queue_is_increasing, executor_is_busy, C_VVC_LABELS);

      -- Reset the transaction info for waveview
      transaction_info := C_TRANSACTION_INFO_DEFAULT;
      transaction_info.operation := v_cmd.operation;
      transaction_info.msg := pad_string(to_string(v_cmd.msg), ' ', transaction_info.msg'length);

      -- Check if command is a BFM access
      --<USER_INPUT> Replace this if statement with a check of the current v_cmd.operation, in order to set v_cmd_is_bfm_access to true if this is a BFM access command
      if v_cmd.operation = RESET or v_cmd.operation = LOAD or v_cmd.operation = CHECK or v_cmd.operation = COUNT_UP or v_cmd.operation = HOLD then 
        v_command_is_bfm_access := true;                                                                            -- IYHT: check counting down
      else
        v_command_is_bfm_access := false;
      end if;

      -- Insert delay if needed
      work.td_vvc_entity_support_pkg.insert_inter_bfm_delay_if_requested(vvc_config                         => vvc_config,
                                                                         command_is_bfm_access              => v_command_is_bfm_access,
                                                                         timestamp_start_of_last_bfm_access => v_timestamp_start_of_last_bfm_access,
                                                                         timestamp_end_of_last_bfm_access   => v_timestamp_end_of_last_bfm_access,
                                                                         scope                              => C_SCOPE);

      if v_command_is_bfm_access then
        v_timestamp_start_of_current_bfm_access := now;
      end if;

      -- 2. Execute the fetched command
      -------------------------------------------------------------------------
      case v_cmd.operation is  -- Only operations in the dedicated record are relevant

        -- VVC dedicated operations
        --===================================

        --<USER_INPUT>: Insert BFM procedure calls here          
          when RESET =>
         -- Call the corresponding procedure in the BFM package.
            counter_reset(msg       => format_msg(v_cmd),
                      clk           => clk,
                      counter_if    => counter_vvc_if,
                      scope         => C_SCOPE,
                      msg_id_panel  => vvc_config.msg_id_panel,
                      config        => vvc_config.bfm_config);
          -- Add info to the transaction_for_waveview_struct if needed
            --transaction_info.reset := true;

         -- If the result from the BFM call is to be stored, e.g. in a read call, use the additional procedure illustrated in this read example
          when CHECK =>
            v_normalised_Q := normalize_and_check(v_cmd.Q, v_normalised_Q, ALLOW_WIDER_NARROWER, "Q", "shared_vvc_cmd.Q", "counter_check() called with too wide Q. " & v_cmd.msg);
          -- Add info to the transaction_for_waveview_struct if needed
            transaction_info.Q(GC_DATA_WIDTH - 1 downto 0) := v_normalised_Q;
         -- Call the corresponding procedure in the BFM package.
            counter_check(Q_exp    => v_normalised_Q,
                     msg           => format_msg(v_cmd),
                     clk           => clk,
                     counter_if    => counter_vvc_if,
                     scope         => C_SCOPE,
                     msg_id_panel  => vvc_config.msg_id_panel,
                     config        => vvc_config.bfm_config);

         when LOAD =>
            v_normalised_data := normalize_and_check(v_cmd.data, v_normalised_data, ALLOW_WIDER_NARROWER, "data", "shared_vvc_cmd.data", "counter_load() called with too wide data. " & v_cmd.msg);
         -- Add info to the transaction_for_waveview_struct if needed
            transaction_info.data(GC_DATA_WIDTH - 1 downto 0) := v_normalised_data;
         -- Call the corresponding procedure in the BFM package.
            counter_load(data_value=> v_normalised_data,
                     msg           => format_msg(v_cmd),
                     clk           => clk,
                     counter_if    => counter_vvc_if,
                     scope         => C_SCOPE,
                     msg_id_panel  => vvc_config.msg_id_panel,
                     config        => vvc_config.bfm_config);
 
         when COUNT_UP =>
         -- Add info to the transaction_for_waveview_struct if needed
            transaction_info.cycles := v_cmd.cycles;
         -- Call the corresponding procedure in the BFM package.
            counter_count_up(
                     cycles        => v_cmd.cycles,
                     msg           => format_msg(v_cmd),
                     clk           => clk,
                     counter_if    => counter_vvc_if,
                     scope         => C_SCOPE,
                     msg_id_panel  => vvc_config.msg_id_panel,
                     config        => vvc_config.bfm_config);
 
         -- IYHT: check counting down

         when HOLD =>
         -- Add info to the transaction_for_waveview_struct if needed
            transaction_info.cycles := v_cmd.cycles;
         -- Call the corresponding procedure in the BFM package.
            counter_hold(
                     cycles        => v_cmd.cycles,
                     msg           => format_msg(v_cmd),
                     clk           => clk,
                     counter_if    => counter_vvc_if,
                     scope         => C_SCOPE,
                     msg_id_panel  => vvc_config.msg_id_panel,
                     config        => vvc_config.bfm_config);
 
  

        -- UVVM common operations
        --===================================
        when INSERT_DELAY =>
          log(ID_INSERTED_DELAY, "Running: " & to_string(v_cmd.proc_call) & " " & format_command_idx(v_cmd), C_SCOPE, vvc_config.msg_id_panel);
          if v_cmd.gen_integer_array(0) = -1 then
            -- Delay specified using time
            wait until terminate_current_cmd.is_active = '1' for v_cmd.delay;
          else
            -- Delay specified using integer
            wait until terminate_current_cmd.is_active = '1' for v_cmd.gen_integer_array(0) * vvc_config.bfm_config.clock_period;
          end if;

        when others =>
          tb_error("Unsupported local command received for execution: '" & to_string(v_cmd.operation) & "'", C_SCOPE);
      end case;

      if v_command_is_bfm_access then
        v_timestamp_end_of_last_bfm_access := now;
        v_timestamp_start_of_last_bfm_access := v_timestamp_start_of_current_bfm_access;
        if ((vvc_config.inter_bfm_delay.delay_type = TIME_START2START) and 
           ((now - v_timestamp_start_of_current_bfm_access) > vvc_config.inter_bfm_delay.delay_in_time)) then
          alert(vvc_config.inter_bfm_delay.inter_bfm_delay_violation_severity, "BFM access exceeded specified start-to-start inter-bfm delay, " & 
                to_string(vvc_config.inter_bfm_delay.delay_in_time) & ".", C_SCOPE);
        end if;
      end if;

      -- Reset terminate flag if any occurred
      if (terminate_current_cmd.is_active = '1') then
        log(ID_CMD_EXECUTOR, "Termination request received", C_SCOPE, vvc_config.msg_id_panel);
        uvvm_vvc_framework.ti_vvc_framework_support_pkg.reset_flag(terminate_current_cmd);
      end if;

      last_cmd_idx_executed <= v_cmd.cmd_idx;
      -- Reset the transaction info for waveview
      transaction_info   := C_TRANSACTION_INFO_DEFAULT;

    end loop;
  end process;
--========================================================================================================================



--========================================================================================================================
-- Command termination handler
-- - Handles the termination request record (sets and resets terminate flag on request)
--========================================================================================================================
  cmd_terminator : uvvm_vvc_framework.ti_vvc_framework_support_pkg.flag_handler(terminate_current_cmd);  -- flag: is_active, set, reset
--========================================================================================================================


end behave;


