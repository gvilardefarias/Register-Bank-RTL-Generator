module register_bank #(
  // APB params
  APB_ADDR_WIDTH = 12,
  APB_DATA_WIDTH = 32
)
(
  // APB IO
  input  logic                      HCLK,
  input  logic                      HRESETn,
  input  logic [APB_ADDR_WIDTH-1:0] i_PADDR,
  input  logic [APB_DATA_WIDTH-1:0] i_PWDATA,
  input  logic                      i_PWRITE,
  input  logic                      i_PSEL,
  input  logic                      i_PENABLE,
   
  output logic [APB_DATA_WIDTH-1:0] o_PRDATA,

  // Controller IO
  input  logic                      i_tra,

  output logic                      o_tba,
  output logic                [6:0] o_slvaddr
);

  // Register definitions
  struct packed {
    logic       TBA;  //Type of address
    logic [23:0] reserved;  //
    logic [6:0] SLVADDR;  //Slave address
  } r_addr;

  struct packed {
    logic       REC;  //Byte received
    logic       TRA;  //Byte transmited
    logic       NAK;  //Nack response
  } r_status;


  // Write FlipFlop
  always_ff @(posedge HCLK, negedge HRESETn) begin
    if(!HRESETn) begin
      r_addr.TBA <= 'h0;
      r_addr.reserved <= 'h0;
      r_addr.SLVADDR <= 'h0;

      r_status.REC <= 'h0;
      r_status.TRA <= 'h0;
      r_status.NAK <= 'h0;
    end
    else begin
      if (i_PSEL && i_PENABLE && i_PWRITE) begin
        case (i_PADDR)
          `ADDRESS_ADDR: begin
            r_addr.TBA <= i_PWDATA[31];
            r_addr.SLVADDR <= i_PWDATA[6:0];
          end
          `ADDRESS_STATUS: begin
            r_status.TRA <= i_PWDATA[1] ? 1'b0:r_status.TRA;
            r_status.NAK <= i_PWDATA[0] ? 1'b0:r_status.NAK;
          end
        endcase
      end

      if(i_tra)
        r_status.TRA <= i_tra;
    end
  end

  // Read logic
  always_comb begin
    o_PRDATA = 'h0;

    case (i_PADDR)
      `ADDRESS_ADDR:
        o_PRDATA[31:0] = r_addr;
      `ADDRESS_STATUS:
        o_PRDATA[2:0] = r_status;
      default:
        o_PRDATA = 'h0;
    endcase
  end

  // To controller
  assign o_tba = r_addr.TBA;
  assign o_slvaddr = r_addr.SLVADDR;

endmodule