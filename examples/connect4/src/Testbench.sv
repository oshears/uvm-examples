// `include "./src/GamePackage.sv"
import GamePackage::NUM_ROWS;
import GamePackage::NUM_COLS;

module Testbench;
    Board board;


    initial begin

        // $urandom(0);

        board = new();



        // board.PlaceInColumn(1, 1);
        // board.PlaceInColumn(2, 2);
        // board.PlaceInColumn(3, 1);
        // board.PlaceInColumn(4, 2);

        for (int i = 0; i < 8; i++) begin
            // int row = $urandom % 6;
            // int col = $urandom % 6;
            // int val = ($urandom % 2) + 1;

            // int row = $urandom_range(5, 0);
            // int col = $urandom_range(6, 0);
            // int val = $urandom_range(2, 1);

            Transaction tr = new();
            tr.randomize();
            $display("col: %d, row: %d, val:%d", tr.col, tr.row, tr.val);
            board.PlaceAtPosition(tr.col, tr.row, tr.val);
        end

        board.Display();
    end

    // initial begin
    //     int val1, val2, val3;

    //     $display("Generating three random numbers in the range [10, 50]:");
    //     val1 = $urandom_range(50, 10);
    //     val2 = $urandom_range(50, 10);
    //     val3 = $urandom_range(50, 10);

    //     $display("Value 1: %0d", val1);
    //     $display("Value 2: %0d", val2);
    //     $display("Value 3: %0d", val3);

    //     // Verify that the values are different
    //     if (val1 != val2 && val2 != val3 && val1 != val3) begin
    //     $display("\nAs expected, each call generated a new, unique value within the specified range.");
    //     end
    // end
endmodule