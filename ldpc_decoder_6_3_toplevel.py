from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner
from src.ldpc_decoder import LDPC_Decoder

if __name__ == "__main__":
    #Instantiate a command line argument parser
    parser = main_parser()
    args = parser.parse_args()

    #Instantiate an nMigen Module
    m = Module()
    
    #Instantiate the Parity Check Matrix 'H' for generating ldpc Code Words
    #https://en.wikipedia.org/wiki/Low-density_parity-check_code

    parityCheckMatrix = [[0b111100],
                         [0b001101],
                         [0b100110] ]

    #Instantiate the LDPC_Decoder Module with the parity check matrix, input codeword size and output data size as parameters
    m.submodules.LDPC_Decoder = LDPC_Decoder = LDPC_Decoder(parityCheckMatrix,6,3)

    main_runner(parser, args, m, ports=[LDPC_Decoder.data_input, LDPC_Decoder.data_output, LDPC_Decoder.start, LDPC_Decoder.done, LDPC_Decoder.success])    
