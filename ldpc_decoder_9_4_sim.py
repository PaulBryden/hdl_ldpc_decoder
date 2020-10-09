from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.back.pysim import Simulator, Delay
from src.ldpc_decoder import LDPC_Decoder

def testbench_process():
    #Run simulation for input word '010101111' (0 bit error)
    yield data_input.eq(0b010101111)
    yield start.eq(1)
    yield Delay(1e-6)
    yield start.eq(0)

    #Delay for 25 clock cycles
    for i in range(25):
        yield Delay(1e-6)

    #Run simulation for input word '010111111' (1 bit error)
    yield data_input.eq(0b010111111)
    yield start.eq(1)
    yield Delay(1e-6)
    yield start.eq(0)

    #Delay for 25 clock cycles
    for i in range(25):
        yield Delay(1e-6)

    #Run simulation for input word '110111111' (2 bit error)
    yield data_input.eq(0b110111111)
    yield start.eq(1)
    yield Delay(1e-6)
    yield start.eq(0)

    #Delay for 25 clock cycles
    for i in range(25):
        yield Delay(1e-6)

if __name__ == "__main__":

    #Instantiate an nMigen Module
    m = Module()
    
    #Instantiate the Generator Matrix 'G' for generating ldpc Code Words
    #https://en.wikipedia.org/wiki/Low-density_parity-check_code#Example_Encoder

   
    parityCheckMatrix = [[0b000011100],
                         [0b110000010],
                         [0b001100001],
                         [0b100001010],
                         [0b001000101],
                         [0b010110000]]

    #Instantiate the LDPC_Encoder Module with the generator matrix and output codeword size as parameters
    m.submodules.LDPC_Decoder = LDPC_Decoder = LDPC_Decoder(parityCheckMatrix,9,4)

    #Simulation

    #[SIGNAL] - data_input - A top level signal which connects the 'data_input' signal on the LDPC Encoder
    data_input = Signal(9)

    #[SIGNAL] - start - A top level signal which connects the 'start' signal on the LDPC Encoder
    start = Signal(1)

    #Link the local data_input and start signals to the LDPC Input Ports
    m.d.comb += LDPC_Decoder.data_input.eq(data_input)
    m.d.comb += LDPC_Decoder.start.eq(start)

    #Create a simulator instance with the local nMigen module which contains the LDPC Encoder
    sim = Simulator(m)

    #Add a synchronous testbench process to the simulator
    sim.add_sync_process(testbench_process) 

    #Add a clock to the simulator
    sim.add_clock(1e-6)

    #Run the simulation with all input and output ports from the LDPC_Encoder and write out the results
    with sim.write_vcd("test_9_4.vcd", "test_9_4.gtkw", traces=[data_input,start] + LDPC_Decoder.ports()):
       sim.run()