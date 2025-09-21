Basic SystemVerilog and UVM test examples for interview preparation.


Load simulator:

```bash
# module load cadence/xcelium/21.03
module load synopsys/vcs/W-2024.09-SP2
export UVM_HOME=/nas/home/shears/Documents/uvm/uvm-examples/uvm-1.2
```


```bash
wget https://www.accellera.org/images/downloads/standards/uvm/uvm-1.2.tar.gz

export UVM_HOME=/nas/home/shears/Documents/uvm/uvm-examples/uvm-1.2

# Compile DPI Library for VCS
gcc -fPIC -shared -I${VCS_HOME}/include -DVCS \
    $UVM_HOME/src/dpi/uvm_dpi.cc \
    -o uvm_dpi.so
```