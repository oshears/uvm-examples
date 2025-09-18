module Testbench;
  bit a, b, c, d;
  bit clk;

  always #10 clk = ~clk;

  // This is just a stimulus to trigger assertions
  initial begin
    for (int i = 0; i < 20; i++) begin
      {a, b, c, d} = $random;
      $display("%0t a=%0d b=%0d c=%0d d=%0d", $time, a, b, c, d);
      @(posedge clk);
    end
    #10 $finish;
  end

  // Step 2. Create sequence (optional), else add
  // boolean expr directly inside a property
  sequence s_ab;
    // Step 1. Create a boolean expression
    a ##1 b;
  endsequence

  // Step 2. Create sequence (optional)
  sequence s_cd;
    // Step 1. Create a boolean expression
    c ##2 d;
  endsequence

  // Step 3. Create property
  property p_expr;
    @(posedge clk) s_ab ##1 s_cd;
  endproperty

  // Step 4. Assert property
  assert property (p_expr);
endmodule