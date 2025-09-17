`timescale 1ns/1ns
// `include "./src/GamePackage.sv"
import GamePackage::NUM_ROWS;
import GamePackage::NUM_COLS;

class Transaction;
    rand int row;
    rand int col;
    rand int val;
    // The 'with' constraint for randomization ranges
    constraint c_random_values {
        row inside {[0:GamePackage::NUM_ROWS-1]};
        col inside {[0:GamePackage::NUM_COLS-1]};
        val inside {[1:2]};
    }
endclass