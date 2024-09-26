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
  input  logic                      i_tra,
  input  logic                [7:0] i_byte_1,
  input  logic                [7:0] i_byte_2,

  output logic                [6:0] o_slvaddr,
  output logic                      o_tba,
  output logic                      o_rec,
  output logic                [7:0] o_byte_1,
  output logic                [7:0] o_byte_2
);

  // Register definitions
  struct packed {
    logic [6:0] SLVADDR;  //Slave address
    logic [23:0] reserved;  //
    logic       TBA;  //Type of address
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

  struct packed {
    logic [7:0] BYTE_0;  //Byte received
    logic [7:0] BYTE_1;  //Byte received
    logic [7:0] BYTE_2;  //Byte received
  } r_dt_rcv;

  struct packed {
    logic [7:0] BYTE_0;  //Byte to be transmitted
    logic [7:0] BYTE_1;  //Byte to be transmitted
    logic [7:0] BYTE_2;  //Byte to be transmitted
  } r_dt_tra;

  struct packed {
    logic [7:0] BYTE_0;  //Byte read
    logic [7:0] BYTE_1;  //Byte write
  } r_dt_mx;


  // Write FlipFlop
  always_ff @(posedge HCLK, negedge HRESETn) begin
    if(!HRESETn) begin
      r_addr <= 'h0;
      r_status <= 'h0;
      r_mask <= 'h0;
      r_dt_rcv <= 'h0;
      r_dt_tra <= 'h0;
      r_dt_mx <= 'h0;
    end
    else begin
      r_status.TRA <= i_tra;
      r_dt_tra.BYTE_1 <= i_byte_1;
      r_dt_tra.BYTE_2 <= i_byte_2;

      if (i_PSEL && i_PENABLE && i_PWRITE) begin
        case (i_PADDR)
          `ADDRESS_ADDR: begin
            r_addr.SLVADDR <= i_PWDATA[6:0];
            r_addr.TBA <= i_PWDATA[31];
          end
          `ADDRESS_STATUS: begin
            r_status.NAK <= i_PWDATA[0] ? 1'b0:r_status.NAK;
            r_status.TRA <= i_PWDATA[1] ? 1'b0:r_status.TRA;
          end
          `ADDRESS_MASK: begin
            r_mask.NAKE <= i_PWDATA[0];
            r_mask.TRAE <= i_PWDATA[1];
            r_mask.RECE <= i_PWDATA[2];
          end
          `ADDRESS_DT_RCV:
            r_dt_rcv <= i_PWDATA;
          `ADDRESS_DT_MX: begin
            r_dt_mx.BYTE_1 <= i_PWDATA[15:8];
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
      `ADDRESS_DT_TRA:
        o_PRDATA = r_dt_tra;
      `ADDRESS_DT_MX: begin
        o_PRDATA = 'h0;
        o_PRDATA[7:0] = r_dt_mx.BYTE_0;
      end
      default:
        o_PRDATA = 'h0;
    endcase
  end

  // To controller
  assign o_slvaddr = r_addr.SLVADDR;
  assign o_tba = r_addr.TBA;
  assign o_rec = r_status.REC;
  assign o_byte_1 = r_dt_rcv.BYTE_1;
  assign o_byte_2 = r_dt_rcv.BYTE_2;

  // To APB
  assign PREADY  = 1'b1;
  assign PSLVERR = 1'b0;

endmodule