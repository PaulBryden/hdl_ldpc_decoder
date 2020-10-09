from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.back.pysim import Simulator, Delay
from nmigen.asserts import Assert, Assume, Cover

class LDPC_Decoder_Validator(Elaboratable):
    def __init__(self, ParityCheckMatrix, codeword_width):

        #[PARAMETER] - codeword_width: Width of the output Codeword
        self.codeword_width = int(codeword_width)

        #[PARAMETER] - data_output_matrix_rows: Rows of the Generator Matrix
        self.data_output_matrix_rows = int(len(ParityCheckMatrix))

        #[CONSTANT] - parity_check_matrix: A parity check matrix constant
        self.parity_check_matrix =  Array([Const(ParityCheckMatrix[_][0],unsigned(self.codeword_width)) for _ in range(self.data_output_matrix_rows)])

        #[INPUT] - start: The start signal to start the decoding process(codeword)
        self.start = Signal(1)

        #[INPUT] - data_input: The data to be encoded
        self.data_input = Signal(codeword_width)
        
        #[OUTPUT] - data_output: The result of each row parity check
        self.data_output = Signal(self.data_output_matrix_rows, reset=0)
 
        #[OUTPUT] - done: The done signal to indicate that the decoding process has stopped.
        self.done = Signal(1, reset=0)

    
 
    def ports(self):
        return [self.data_input, self.data_output, self.start, self.done]

    def elaborate(self, platform):
        #Instantiate the Module
        m = Module()

        #[ARRAY[SIGNAL]] - stage_1_working_matrix - An array of signals which represents the parity matrix used to validate the input codeword
        stage_1_working_matrix = Array([Signal(unsigned(self.codeword_width), reset=0) for _ in range(self.data_output_matrix_rows)])

        #[ARRAY[SIGNAL]] - stage_2_adder_buffer - An array of signals which are used to calculate whether there are an even number of 1s in each parity check row
        stage_2_adder_buffer = Array([Signal(unsigned(self.codeword_width), reset=0, name="stage_2_adder_buffer") for _ in range(self.data_output_matrix_rows)])

        #[SIGNAL] - stage_2_counter - Counts the worst case scenario for the even 1s calculation
        stage_2_counter = Signal(self.codeword_width)

        #[SIGNAL] - pipeline_stage - Signal to indicate whether we are in pipeline stage 0 or 1
        pipeline_stage = Signal(1)
        #[SIGNAL] - running - Signal to indicate that we are currently running
        running = Signal(1, reset=0)

        #if start bit is asserted, reset the system
        with m.If(self.start):
            for i in range(0,self.data_output_matrix_rows):
                m.d.sync += [
                    running.eq(1),
                    stage_1_working_matrix[i].eq(0),
                    stage_2_adder_buffer[i].eq(0),
                    stage_2_counter.eq(0),
                    self.done.eq(0),
                    self.data_output.eq(0b000),
                    pipeline_stage.eq(0),
                ]
        #First Pipeline Stage (0)
        #Data_input ANDed with each row of the parity check matrix
        with m.If(running & (pipeline_stage==0)):
            for i in range(0,self.data_output_matrix_rows):
                m.d.sync += [
                stage_1_working_matrix[i].eq(self.data_input & self.parity_check_matrix[i])
                ]
            m.d.sync += [
                pipeline_stage.eq(1)
            ]
        
        #Second Pipeline Stage (1)
        #Accumulate the ANDed data to calculate if there are an even number of 1s.
        with m.If(running & (pipeline_stage==1)):
            m.d.sync += [
                stage_2_counter.eq(stage_2_counter+1)
            ]
            for i in range(0,self.data_output_matrix_rows):
                for n in range(1,self.codeword_width):
                    if(n==1):
                        m.d.sync += [
                        stage_2_adder_buffer[i][n].eq(stage_1_working_matrix[i][n]^stage_1_working_matrix[i][n-1])
                        ]
                    else:
                        m.d.sync += [
                        stage_2_adder_buffer[i][n].eq(stage_2_adder_buffer[i][n-1]^stage_1_working_matrix[i][n])
                        ]
        #Output the result of each parity check row comparison (1=Fail, 0=Pass)
            with m.If(stage_2_counter==(self.codeword_width)):
                for i in range(0,self.data_output_matrix_rows):
                    m.d.sync += [
                            self.data_output[(self.data_output_matrix_rows-1)-i].eq( stage_2_adder_buffer[i][self.codeword_width-1]),
                            running.eq(0),
                            self.done.eq(1)
                        ]

        return m
        