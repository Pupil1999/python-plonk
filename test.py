from compiler.program import Program
from polycom import SRS
import py_ecc.bn128 as b
from lib.poly import *
from prover import Prover

def test1():
    SRS(16)

def test2():
    roots = xs = Scalar.roots_of_unity(8)
    print(roots[1]**9 == roots[1]**1)
    print([(i, val) for (i, val) in enumerate(roots)])

def test3():
    #poly = 1 + x^2 + x^3
    poly = Polynomial([Scalar(1), Scalar(2), Scalar(3)], Basis.MONOMIAL)
    print(poly.coeff_eval(3))
    print(poly.values)

def test4():
    poly = Polynomial([Scalar(i) for i in [1, 2, 3, 4]], Basis.LAGRANGE)
    ifft_poly = poly.ifft()
    xs = Scalar.roots_of_unity(4)
    print(ifft_poly.coeff_eval(xs[1]))
    #should output 3

def test5():
    program = Program(["e public", "c <== a * b", "e <== c * d"], 8)
    assignments = {"a": 3, "b": 4, "c": 12, "d": 5, "e": 60}
    srs = SRS(16)
    prover_ins = Prover(srs, program)
    proof = prover_ins.prove(assignments)

if __name__ == '__main__':
    test5()