class Board;

    // OYS: Use unpacked array because the data is all independent
    // Columns x Rows
    int board[7][6];

    string boardName;

    function new (string boardName = "Default Board");
        this.boardName = boardName;
        // no need to initialize board since its statically allocated
    endfunction

    function void PlaceInColumn(int column, int value);
        this.board[column][0] = value;
    endfunction

    function void PlaceAtPosition(int col, int row, int value);
        this.board[col][row] = value;
    endfunction

    function int NextEmptySpace(int column); 
    // this func returns the value of row

        foreach (this.board[column][row]) begin // row is the iterator
            if (row == 0) begin
                return row;
                // alternatively you can set the result to the function name
                // e.g., NextEmptySpace = row
                // you can also declare input/output directions in the function name
                // that would allow you to return multiple values
            end
        end

    endfunction

    function void ResetBoard();
        this.board = '{default: 0};
    endfunction

    function void Display();

        for(int row = 5; row > -1; row--) begin
            for(int col = 0; col < 7; col++) begin
                $write("%d",this.board[col][row]);
            end
            $display("");
        end
    endfunction


endclass