import py_ecc.bn128 as b
from polycom import *
from compiler.program import Program, CommonPreprocessedInput
from lib.curve import Scalar
from lib.utils import *
from proof import Proof
from dataclasses import dataclass

@dataclass
class Verifier:
    witness_len: int
    srs: SRS
    program: Program
    pk: CommonPreprocessedInput

    def __init__(self, srs: SRS, program: Program):
        self.srs = srs
        self.program = program

        # length of witness vectors a, b, c; supposed to be exponential size
        self.witness_len = program.group_order
        self.pk = program.common_preprocessed_input()
        #print(self.pk.S1.values)

    def verify(self, proof: Proof) -> bool:
        True