import py_ecc.bn128 as b
from lib.curve import ec_lincomb, G1Point, G2Point
from lib.poly import Polynomial, Basis

class SRS:
    G1s: list[G1Point]
    G2s: list[G2Point]
    power: int

    # Generate the SRS public parameters
    def __init__(self, powers):
        self.G1s = []
        self.G2s = []
        self.power = powers
        tau = 1918273498723
        self.G1s.append(b.G1)
        for i in range(1, powers):
            self.G1s.append(b.multiply(self.G1s[-1], tau))
            #print(self.G1s[i])
        self.G2s.append(b.G2)
        self.G2s.append(b.multiply(b.G2, tau))

class KZG:
    # Commit a polynomial to group1 curve
    @classmethod
    def commit(self, srs: SRS, poly: Polynomial) -> G1Point:
        assert(poly.basis == Basis.MONOMIAL)
        lens = poly.values.__len__()
        if lens > srs.power:
            raise Exception("Longer poly than srs!")
        return ec_lincomb([(p, scalars) for (p, scalars) in zip(srs.G1s[:lens], poly.values)])
        