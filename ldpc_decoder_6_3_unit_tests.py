from nmigen import Elaboratable, Module, Signal, Array, unsigned, Const
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner, main
from nmigen.back.pysim import Simulator, Delay
from nmigen.test import *
from src.ldpc_decoder import LDPC_Decoder
import unittest

def Positive_Test(output, input):
    def test(self):
        with Simulator(self.dut) as sim:
            def process():
                yield self.dut.data_input.eq(input)
                yield Delay(1e-6)
                yield self.dut.start.eq(1)
                yield Delay(1e-6)
                yield self.dut.start.eq(0)

                #Delay for 16 clock cycles
                for i in range(16):
                    yield Delay(1e-6)
                self.assertEqual((yield self.dut.done), 1)
                self.assertEqual((yield self.dut.success), 1)
                self.assertEqual((yield self.dut.data_output), output)
            sim.add_sync_process(process)
            sim.add_clock(1e-6)
            sim.run()
    return test


class LDPC_Decoder_Test(unittest.TestCase):
    def setUp(self):
        parityCheckMatrix = [[0b111100],
                            [0b001101],
                            [0b100110] ]
        self.dut = LDPC_Decoder(parityCheckMatrix,6,3)
    
    #Zero Bit Errors
    test_0 = Positive_Test(0b000,0b000000)
    test_1 = Positive_Test(0b011,0b011001)
    test_2 = Positive_Test(0b110,0b110010)
    test_3 = Positive_Test(0b101,0b101011)
    test_4 = Positive_Test(0b111,0b111100)
    test_5 = Positive_Test(0b100,0b100101)
    test_6 = Positive_Test(0b001,0b001110)
    test_7 = Positive_Test(0b010,0b010111)
    test_8 = Positive_Test(0b011,0b011001)

    
    #One Bit Errors
    test_9 = Positive_Test(0b000,0b000100)
    test_10 = Positive_Test(0b011,0b011101)
    test_11 = Positive_Test(0b110,0b110110)
    test_12 = Positive_Test(0b101,0b101001)
    test_13 = Positive_Test(0b111,0b111110)
    test_14 = Positive_Test(0b100,0b100111)
    test_15 = Positive_Test(0b001,0b001111)
    test_16 = Positive_Test(0b010,0b010011)
    test_17 = Positive_Test(0b011,0b011011)
    