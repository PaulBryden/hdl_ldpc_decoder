from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.back.pysim import Simulator, Delay
from nmigen.asserts import Assert, Assume, Cover
from src.ldpc_decoder_validator import LDPC_Decoder_Validator

class LDPC_Decoder(Elaboratable):
    def __init__(self, ParityCheckMatrix, codeword_width, data_width):

        #[PARAMETER] - codeword_width: Width of the input Codeword
        self.codeword_width = int(codeword_width)

        #[PARAMETER] - ParityCheckMatrixPythonArray: Python Array representing the parity check matrix
        self.ParityCheckMatrixPythonArray = ParityCheckMatrix

        #[PARAMETER] - ParityCheckMatrixRows: Width of the data input
        self.ParityCheckMatrixRows = int(len(ParityCheckMatrix))

        #[INPUT] - start: The start signal to start the decoding process
        self.start = Signal(1, name="input_start")

        #[INPUT] - data_input: The codeword to be decoded
        self.data_input = Signal(codeword_width, name="input_data")
        
        #[PARAMETER] - data_output_width: The length of the output data
        self.data_output_width = data_width

        #[OUTPUT] - data_output: The encoded data (codeword)
        self.data_output = Signal(self.data_output_width, reset=0, name="output_data")

        #[OUTPUT] - success : Flag indicating whether decoding was successful or not
        self.success = Signal(1, reset=0, name="output_success")
 
        #[OUTPUT] - done: The done signal to indicate that the decoding process has stopped.
        self.done = Signal(1, reset=0, name="output_done")

    def ports(self):
        return [self.data_input, self.start, self.data_output, self.done, self.success]

    def elaborate(self, platform):
        #Instantiate the Module
        m = Module()

        #Instantiate a decoder/validator for each bit-flip combination of the input codeword
        for i in range(0,self.codeword_width+1):
            m.submodules["decoder"+str(i)] = LDPC_Decoder_Validator(self.ParityCheckMatrixPythonArray,self.codeword_width)

        #codeword_list - An array containing the input codeword and copies of the input codeword, each with a different bit flipped
        codeword_list = Array([Signal(unsigned(self.codeword_width), reset=0) for _ in range(self.codeword_width+1)])
        
        #decoder_output_list - An array containing the parity check status of each parity check row for an input codeword
        decoder_output_list = Array([Signal(unsigned(self.ParityCheckMatrixRows), reset=0) for _ in range(self.codeword_width+1)])

        #decoders_done - A signal which lets the top level know when the submodules have finished decoding/validating
        decoders_done = Signal(1)
        m.d.comb += decoders_done.eq(m.submodules["decoder"+str(self.codeword_width)].done)

        #counter - A timeout counter for catching when the decoder never finishes decoding
        counter = Signal(self.codeword_width)

        #pipeline_stage - A signal for keeping track of the pipeline stage
        pipeline_stage = Signal(3, reset=0)

        #pipeline_stage - A signal for starting the submodules
        start_submodules = Signal(1, reset=0)

        for i in range(0,self.codeword_width+1):              
            m.d.comb +=  m.submodules["decoder"+str(i)].start.eq(start_submodules)
            m.d.sync +=  m.submodules["decoder"+str(i)].data_input.eq(codeword_list[i])
            m.d.comb +=  decoder_output_list[i].eq(m.submodules["decoder"+str(i)].data_output)
    
        #Reset the relevant registers/wires and load the input codeword into a decoder input register
        with m.If(self.start==1):
            m.d.sync += [
                codeword_list[self.codeword_width].eq(self.data_input),
                self.data_output.eq(0),
                self.done.eq(0),
                self.success.eq(0),
                counter.eq(0),
                pipeline_stage.eq(1)
            ]
        #Load the input codeword into the codeword list
        with m.If(pipeline_stage==1 & (~self.done)):
            for i in range(0,self.codeword_width):
                m.d.sync += [
                    codeword_list[i].eq(codeword_list[self.codeword_width]),
                    pipeline_stage.eq(pipeline_stage+1)
                ]
        #Flip the relevant bit on the codewords in the codeword list
        with m.If(pipeline_stage==2 & (~self.done)):
            for i in range(0,self.codeword_width):
                m.d.sync += [
                    codeword_list[i][i].eq(~codeword_list[i][i]),
                    pipeline_stage.eq(pipeline_stage+1)
                ]
        #Start validating all the codeword variations (Set Start Bit to 1)
        with m.Elif(pipeline_stage==3 & (~self.done)):
            for i in range(0,self.codeword_width):
                m.d.sync += [
                    start_submodules.eq(1),
                    pipeline_stage.eq(pipeline_stage+1)
                ]
        #Start validating all the codeword variations (Set Start Bit to 0)
        with m.Elif(pipeline_stage==4 & (~self.done)):
            for i in range(0,self.codeword_width):
                m.d.sync += [
                    start_submodules.eq(0),
                    pipeline_stage.eq(pipeline_stage+1)
                ]
        #Start counting the timeout and validating if any of the submodules was successful in validating the codeword.
        #Finally, output success or failure along with output data and STOP.
        with m.Elif(pipeline_stage==5  & (~self.done)):
            for i in range(0,self.codeword_width+1):
                m.d.sync +=  counter.eq(counter+1)
            with m.If( (decoders_done) & (counter>(self.codeword_width+2))):
                m.d.sync+=[ self.done.eq(1), self.success.eq(0)]
            with m.Elif( (decoders_done)):
                for i in range(0,self.codeword_width+1):
                    with m.If(decoder_output_list[i]==0b000):
                        m.d.sync+=[self.data_output.eq(codeword_list[self.codeword_width][ self.codeword_width-self.data_output_width:]),
                                    self.done.eq(1), self.success.eq(1)]
        return m