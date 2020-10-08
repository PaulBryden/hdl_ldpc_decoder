from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.back.pysim import Simulator, Delay
from nmigen.asserts import Assert, Assume, Cover

class LDPC_Decoder_Validator(Elaboratable):
    def __init__(self, GeneratorMatrix, codeword_width):

        #[PARAMETER] - codeword_width: Width of the output Codeword
        self.codeword_width = int(codeword_width)

        #[PARAMETER] - data_input_length: Width of the data input
        self.data_output_length = int(len(GeneratorMatrix))

        #[CONSTANT] - gen_matrix: A generator matrix constant
        self.gen_matrix =  Array([Const(GeneratorMatrix[_][0],unsigned(self.codeword_width)) for _ in range(self.data_output_length)])

        #[INPUT] - start: The start signal to start the decoding process(codeword)
        self.start = Signal(1)

        #[INPUT] - data_input: The data to be encoded
        self.data_input = Signal(codeword_width)
        
        #[OUTPUT] - data_output: The encoded data (codeword)
        self.data_output = Signal(self.data_output_length, reset=0)
 
        #[OUTPUT] - done: The done signal to indicate that the decoding process has stopped.
        self.done = Signal(1, reset=0)

        #[OUTPUT] - success: The success signal to indicate that decoding has completed successfully.
        self.success = Signal(1, reset=0)

    
 
    def ports(self):
        return [self.data_input, self.data_output, self.start, self.done]

    def elaborate(self, platform):
        #Instantiate the Module
        m = Module()

        #[ARRAY[SIGNAL]] - working_matrix - An array of signals which represents the matrix used to calculate the output codeword.
        stage_1_working_matrix = Array([Signal(unsigned(self.codeword_width), reset=0) for _ in range(self.data_output_length)])
        stage_2_adder_buffer = Array([Signal(unsigned(self.codeword_width), reset=0, name="stage_2_adder_buffer") for _ in range(self.data_output_length)])
        stage_2_counter = Signal(3)
        data_input_copy = Signal(unsigned(self.codeword_width))
        pipeline_stage = Signal(1)
        running = Signal(1, reset=0)
        with m.If(self.start):
            for i in range(0,self.data_output_length):
                m.d.sync += [
                    running.eq(1),
                    stage_1_working_matrix[i].eq(0),
                    stage_2_adder_buffer[i].eq(0),
                    stage_2_counter.eq(0),
                    self.done.eq(0),
                    self.data_output.eq(0b000),
                    pipeline_stage.eq(0),
                    data_input_copy.eq(self.data_input)
                ]
        #First Pipeline Stage (0)
        with m.If(running & (pipeline_stage==0)):
            for i in range(0,self.data_output_length):
                m.d.sync += [
                stage_1_working_matrix[i].eq(data_input_copy & self.gen_matrix[i]),
                    self.data_output.eq(0b000),
                ]
            m.d.sync += [
                pipeline_stage.eq(1)
            ]
        
        #Second Pipeline Stage (1)
        with m.If(running & (pipeline_stage==1)):
            m.d.sync += [
                stage_2_counter.eq(stage_2_counter+1)
            ]
            for i in range(0,self.data_output_length):
                for n in range(1,self.codeword_width):
                    if(n==1):
                        m.d.sync += [
                        stage_2_adder_buffer[i][n].eq(stage_1_working_matrix[i][n]^stage_1_working_matrix[i][n-1])
                        ]
                    else:
                        m.d.sync += [
                        stage_2_adder_buffer[i][n].eq(stage_2_adder_buffer[i][n-1]^stage_1_working_matrix[i][n])
                        ]
            with m.If(stage_2_counter==(self.codeword_width)):
                for i in range(0,self.data_output_length):
                    m.d.sync += [
                            self.data_output[(self.data_output_length-1)-i].eq( stage_2_adder_buffer[i][self.codeword_width-1]),
                            running.eq(0),
                            self.done.eq(1)
                        ]

        return m
        