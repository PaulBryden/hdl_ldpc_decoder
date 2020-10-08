from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.back.pysim import Simulator, Delay
from nmigen.asserts import Assert, Assume, Cover
from src.ldpc_decoder_validator import LDPC_Decoder_Validator

class LDPC_Decoder(Elaboratable):
    def __init__(self, GeneratorMatrix, codeword_width):

        #[PARAMETER] - codeword_width: Width of the output Codeword
        self.codeword_width = int(codeword_width)
        self.GeneratorMatrixPythonArray = GeneratorMatrix
        #[PARAMETER] - data_input_length: Width of the data input
        self.data_output_length = int(len(GeneratorMatrix))

        #[CONSTANT] - gen_matrix: A generator matrix constant
        self.gen_matrix =  Array([Const(GeneratorMatrix[_][0],unsigned(self.codeword_width)) for _ in range(self.data_output_length)])

        #[INPUT] - start: The start signal to start the decoding process(codeword)
        self.start = Signal(1)

        #[INPUT] - data_input: The data to be encoded
        self.data_input = Signal(codeword_width)
        
        #[OUTPUT] - data_output: The encoded data (codeword)
        self.data_output = Signal(self.data_output_length, reset=0, name="output_signal")

        #[OUTPUT] - success : The encoded data success (codeword)
        self.success = Signal(1, reset=0, name="success")
 
        #[OUTPUT] - done: The done signal to indicate that the decoding process has stopped.
        self.done = Signal(1, reset=0, name="Output_Done")

        #[OUTPUT] - success: The success signal to indicate that decoding has completed successfully.
        self.success = Signal(1, reset=0)

    
 
    def ports(self):
        return [self.data_input, self.data_output, self.start, self.done]

    def elaborate(self, platform):
        #Instantiate the Module
        m = Module()
        for i in range(0,self.codeword_width+1):
            m.submodules["decoder"+str(i)] = LDPC_Decoder_Validator(self.GeneratorMatrixPythonArray,self.codeword_width)

        codeword_working = Array([Signal(unsigned(self.codeword_width), reset=0) for _ in range(self.codeword_width+1)])
        output_ok = Array([Signal(unsigned(self.data_output_length), reset=0) for _ in range(self.codeword_width+1)])
        done_test = Signal(1)
        output_ready = Signal(1)
        m.d.comb += done_test.eq(m.submodules["decoder"+str(2)].done)
        counter = Signal(self.data_output_length)
        for i in range(0,self.codeword_width+1):              
            m.d.comb +=  m.submodules["decoder"+str(i)].start.eq(self.start)
            m.d.sync +=  m.submodules["decoder"+str(i)].data_input.eq(codeword_working[i])
            m.d.comb +=  output_ok[i].eq(m.submodules["decoder"+str(i)].data_output)
    
        with m.If(self.start==1):
            for i in range(0,self.codeword_width):
                m.d.sync += [
                    codeword_working[i].eq(self.data_input),
                    codeword_working[i][i].eq(~self.data_input[i]),
                ]
            m.d.sync += [
                codeword_working[self.codeword_width].eq(self.data_input),
                self.data_output.eq(0),
                self.done.eq(0),
                output_ready.eq(0),
                self.success.eq(0)
                
            ]
        with m.Elif((self.start==0)):
            for i in range(0,self.codeword_width+1):
                m.d.sync +=  counter.eq(counter+1)
        with m.If((self.start==0)&(done_test)):
            for i in range(0,self.codeword_width+1):
                with m.If(output_ok[i]==0b000):
                    m.d.sync+=[output_ready.eq(1),
                                self.data_output.eq(codeword_working[i][self.data_output_length:])]
        with m.If((self.start==0)& (done_test) & output_ready):
                    m.d.sync+=[ self.done.eq(1), self.success.eq(1)]
        with m.Elif((self.start==0)& (done_test) & counter==(self.codeword_width+1)):
            m.d.sync+=[ self.done.eq(1), self.success.eq(0)]
        return m