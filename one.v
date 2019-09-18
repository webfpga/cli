module fpga_top(input wire WF_BUTTON, output wire WF_LED);
    reg a;
    wire b;
    two _two(a, b);
    assign WF_LED = WF_BUTTON;
endmodule
