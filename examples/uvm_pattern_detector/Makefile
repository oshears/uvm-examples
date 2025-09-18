VCS_HOME=/nas/projects/edaTools/synopsys/vcs/W-2024.09-SP2/
UVM_HOME=/nas/home/shears/Documents/uvm/uvm-examples/uvm-1.2

build/vcs:
# 	vcs -ntb_opts uvm -debug_access+all -f filelist.f -o simv_executable
# 	vcs +ntb_opts uvm -cm_dir coverage_database -cm_hier Testbench -cm line+cond+fsm+tgl+assert -sverilog -full64 -kdb -debug_access+all -line -f filelist.f -top Testbench -o simv_executable
	vcs -sv_lib ./uvm_dpi.so +incdir+${UVM_HOME}/src ${UVM_HOME}/src/uvm.sv +define+LENGTH=4 -cm_dir coverage_database -cm_hier tb -cm line+cond+fsm+tgl+assert -sverilog -full64 -kdb -debug_access+all -line -f filelist.f -top tb -o simv_executable

build/xcelium:
	
	xrun -sv -f files.f -access +rwc -cm_name coverage_test -cm_test coverage_test


.PHONY: build

build: build/vcs

run/vcs: build/vcs
# 	./simv -gui=DVE
# 	./simv_executable +ntb_random_seed=100
	./simv_executable +ntb_random_seed_automatic

.PHONY: run

run: run/vcs

all: run

clean:
	rm xrun.history
	rm xrun.log
	rm xcelium.d