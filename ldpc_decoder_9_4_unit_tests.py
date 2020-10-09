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
        parityCheckMatrix = [[0b000011100],
                            [0b110000010],
                            [0b001100001],
                            [0b100001010],
                            [0b001000101],
                            [0b010110000]]
        self.dut = LDPC_Decoder(parityCheckMatrix,9,4)

    #Zero Bit Errors
    test_0 = Positive_Test(0b0000,0b000000000)
    test_1 = Positive_Test(0b0001,0b000110101)
    test_2 = Positive_Test(0b0010,0b001000001)
    test_3 = Positive_Test(0b0011,0b001110100)
    test_4 = Positive_Test(0b0100,0b010011010)
    test_5 = Positive_Test(0b0101,0b010101111)
    test_6 = Positive_Test(0b0110,0b011011011)
    test_7 = Positive_Test(0b0111,0b011101110)
    test_8 = Positive_Test(0b1000,0b100000010)
    test_9 = Positive_Test(0b1001,0b100110111)
    test_10 = Positive_Test(0b1010,0b101000011)
    test_11 = Positive_Test(0b1011,0b101110110)
    test_12 = Positive_Test(0b1100,0b110011000)
    test_13 = Positive_Test(0b1101,0b110101101)
    test_14 = Positive_Test(0b1110,0b111011001)
    test_15 = Positive_Test(0b1111,0b111101100)
    
    #1 Bit Errors
    test_16 = Positive_Test(0b0000,0b000001000)
    test_17 = Positive_Test(0b0001,0b000111101)
    test_18 = Positive_Test(0b0010,0b001001001)
    test_19 = Positive_Test(0b0011,0b001111100)
    test_20 = Positive_Test(0b0100,0b010010010)
    test_21 = Positive_Test(0b0101,0b010100111)
    test_22 = Positive_Test(0b0110,0b011010011)
    test_23 = Positive_Test(0b0111,0b011100110)
    test_24 = Positive_Test(0b1000,0b100001010)
    test_25 = Positive_Test(0b1001,0b100111111)
    test_26 = Positive_Test(0b1010,0b101010011)
    test_27 = Positive_Test(0b1011,0b101100110)
    test_28 = Positive_Test(0b1100,0b110001000)
    test_29 = Positive_Test(0b1101,0b110111101)
    test_30 = Positive_Test(0b1110,0b111001001)
    test_31 = Positive_Test(0b1111,0b111111100)