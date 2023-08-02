from lib.curve import *
from dataclasses import dataclass

@dataclass
class Proof:
    Message_1: [G1Point] * 3
    Message_2: G1Point
    Message_3: [G1Point] * 3
    Message_4: [Scalar] * 6
    Message_5: [G1Point] * 2

    # This shouldn't be passed to verifier in practical protocols
    # I added it to proof content since I didn't find a suitable lib to compute it
    scripts: [Scalar] * 6