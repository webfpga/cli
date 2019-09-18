module fpga_top(input wire WF_BUTTON, output wire WF_LED);
    assign WF_LED = ~WF_BUTTON;
endmodule
