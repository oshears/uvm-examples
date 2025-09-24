VCS_HOME=/nas/projects/edaTools/synopsys/vcs/W-2024.09-SP2/
UVM_HOME=/nas/home/shears/Documents/uvm/uvm-examples/uvm-1.2

build/vcs:
# 	vcs -ntb_opts uvm -debug_access+all -f filelist.f -o simv_executable
# 	vcs +ntb_opts uvm -cm_dir coverage_database -cm_hier Testbench -cm line+cond+fsm+tgl+assert -sverilog -full64 -kdb -debug_access+all -line -f filelist.f -top Testbench -o simv_executable
# 	+vcs+dumparrays 
# 	-ntb_opts tb_timescale=1ns/1ns
# 	+vcs+initmem+random 
	vcs -sv_lib /nas/home/shears/Documents/uvm/uvm-examples/uvm_dpi.so \
	+incdir+${UVM_HOME}/src \${UVM_HOME}/src/uvm.sv \
	+vcs+dumpvars+test.vcd \
	+vcs+initreg+random \
	-timescale=1ns/1ns \
	+define+LENGTH=4 -cm_dir coverage_database -cm_hier Testbench -cm line+cond+fsm+tgl+assert \
	-sverilog -full64 -kdb -debug_access+all -line -f filelist.f -top Testbench -o simv_executable

build/xcelium:
	
	xrun -sv -f files.f -access +rwc -cm_name coverage_test -cm_test coverage_test

waves:
	dve -vpd test.vcd
#   dve -full64 -toolexe simv -script cmd.tcl	
# -session <file>
.PHONY: build

build: build/vcs

run/vcs: build/vcs
# 	./simv -gui=DVE
# 	./simv_executable +ntb_random_seed=100
# 	./simv_executable +ntb_random_seed_automatic
	dve -full64 -script cmd.tcl -toolexe simv_executable +vcs+initreg+0

.PHONY: run

run: run/vcs

all: run

clean:
	rm xrun.history
	rm xrun.log
	rm xcelium.d