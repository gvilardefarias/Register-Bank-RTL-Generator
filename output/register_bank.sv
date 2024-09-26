module register_bank #(
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
  output logic                      o_PREADY,
  output logic                      o_PSLVERR

  // Controller IO
  input  logic                     i_tra,

  output  logic                [6:0]o_slvaddr,
  output  logic                     o_tba,
  output  logic                     o_rec
);

  // Register definitions
  struct packed {
    logic [6:0] SLVADDR;  //Slave address
    logic [23:0] reserved;  //
    logic       TBA;  //Type of adrress
  } r_addr;

  struct packed {
    logic       NAK;  //Nack response
    logic       TRA;  //Byte transmited
    logic       REC;  //Byte received
  } r_status;

  struct packed {
    logic       NAKE;  //Nack response Mask
    logic       TRAE;  //Byte transmited Mask
    logic       RECE;  //Byte received Mask
  } r_mask;


  // Write FlipFlop
  always_ff @(posedge HCLK, negedge HRESETn) begin
    if(!HRESETn) begin
      r_addr <= 'h0;
      r_status <= 'h0;
      r_mask <= 'h0;
    end
    else begin
      r_status.TRA <= i_tra;

      if (i_PSEL && i_PENABLE && i_PWRITE) begin
        case (i_PADDR)
          `ADDRESS_ADDR: begin
            r_addr[6:0] <= i_PWDATA[6:0];
            r_addr[31] <= i_PWDATA[31];
          end
          `ADDRESS_STATUS: begin
            r_status[0] <= i_PWDATA[0] ? 1'b0:r_status[0];
            r_status[1] <= i_PWDATA[1] ? 1'b0:r_status[1];
          end
          `ADDRESS_MASK: begin
            r_mask[0] <= i_PWDATA[0];
            r_mask[1] <= i_PWDATA[1];
            r_mask[2] <= i_PWDATA[2];
          end
        endcase
      end
    end
  end

  // Read logic
  always_comb begin
    case (s_apb_addr)
      `ADDRESS_ADDR:
        o_PRDATA = r_addr;
      `ADDRESS_STATUS:
        o_PRDATA = r_status;
      `ADDRESS_MASK:
        o_PRDATA = r_mask;
      default:
        o_PRDATA = 'h0;
    endcase
  end

  // To controller
  assign o_slvaddr = r_addr.SLVADDR;
  assign o_tba = r_addr.TBA;
  assign o_rec = r_status.REC;

  // To APB
  assign PREADY  = 1'b1;
  assign PSLVERR = 1'b0;

endmodule