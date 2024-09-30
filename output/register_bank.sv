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
  output logic                      o_PSLVERR,

  // Controller IO
  input  logic                      i_tra,
  input  logic                [7:0] i_byte_2,
  input  logic                [7:0] i_byte_1,

  output logic                      o_tba,
  output logic                [6:0] o_slvaddr,
  output logic                      o_rec,
  output logic                [7:0] o_byte_2,
  output logic                [7:0] o_byte_1
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

  struct packed {
    logic       RECE;  //Byte received Mask
    logic       TRAE;  //Byte transmited Mask
    logic       NAKE;  //Nack response Mask
  } r_mask;

  struct packed {
    logic [7:0] BYTE_2;  //Byte received
    logic [7:0] BYTE_1;  //Byte received
    logic [7:0] BYTE_0;  //Byte received
  } r_dt_rcv;

  struct packed {
    logic [7:0] BYTE_2;  //Byte to be transmitted
    logic [7:0] BYTE_1;  //Byte to be transmitted
    logic [7:0] BYTE_0;  //Byte to be transmitted
  } r_dt_tra;

  struct packed {
    logic [7:0] BYTE_1;  //Byte write
    logic [7:0] BYTE_0;  //Byte read
  } r_dt_mx;

  struct packed {
    logic [31:0] data;  //Data
  } r_write_reg;

  struct packed {
    logic [31:0] data;  //Data
  } r_read_reg;


  // Write FlipFlop
  always_ff @(posedge HCLK, negedge HRESETn) begin
    if(!HRESETn) begin
      r_addr <= 'h0;
      r_status <= 'h0;
      r_mask <= 'h0;
      r_dt_rcv <= 'h0;
      r_dt_tra <= 'h0;
      r_dt_mx <= 'h0;
      r_write_reg <= 'h0;
      r_read_reg <= 'h0;
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
          `ADDRESS_MASK: begin
            r_mask.RECE <= i_PWDATA[2];
            r_mask.TRAE <= i_PWDATA[1];
            r_mask.NAKE <= i_PWDATA[0];
          end
          `ADDRESS_DT_RCV: begin
            r_dt_rcv.BYTE_2 <= i_PWDATA[23:16];
            r_dt_rcv.BYTE_1 <= i_PWDATA[15:8];
            r_dt_rcv.BYTE_0 <= i_PWDATA[7:0];
          end
          `ADDRESS_DT_MX: begin
            r_dt_mx.BYTE_1 <= i_PWDATA[15:8];
          end
          `ADDRESS_WRITE_REG:
            r_write_reg <= i_PWDATA;
        endcase
      end

      r_dt_tra.BYTE_2 <= i_byte_2;
      r_dt_tra.BYTE_1 <= i_byte_1;

      if(i_tra)
        r_status.TRA <= i_tra;

    end
  end

  // Read logic
  always_comb begin
    o_PRDATA = 'h0;

    case (i_PADDR)
      `ADDRESS_ADDR:
        o_PRDATA = r_addr;
      `ADDRESS_STATUS:
        o_PRDATA = r_status;
      `ADDRESS_MASK:
        o_PRDATA = r_mask;
      `ADDRESS_DT_TRA:
        o_PRDATA = r_dt_tra;
      `ADDRESS_DT_MX: begin
        o_PRDATA[7:0] = r_dt_mx.BYTE_0;
      end
      `ADDRESS_READ_REG:
        o_PRDATA = r_read_reg;
      default:
        o_PRDATA = 'h0;
    endcase
  end

  // To controller
  assign o_tba = r_addr.TBA;
  assign o_slvaddr = r_addr.SLVADDR;
  assign o_rec = r_status.REC;
  assign o_byte_2 = r_dt_rcv.BYTE_2;
  assign o_byte_1 = r_dt_rcv.BYTE_1;

  // To APB
  assign o_PREADY  = 1'b1;
  assign o_PSLVERR = 1'b0;

endmodule