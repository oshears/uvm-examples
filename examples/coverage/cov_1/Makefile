VCS_HOME=/nas/projects/edaTools/synopsys/vcs/W-2024.09-SP2/

build/vcs:
# 	vcs -ntb_opts uvm -debug_access+all -f filelist.f -o simv_executable
	vcs -cm_hier / -cm_create on -sverilog -full64 -kdb -debug_access+all -line -f filelist.f -top Testbench -o simv_executable

build/xcelium:
	
	xrun -sv -f files.f -access +rwc


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