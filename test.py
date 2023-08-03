from compiler.program import Program
from polycom import SRS
import py_ecc.bn128 as b
from lib.poly import *
from prover import Prover
from verifier import Verifier

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
    program = Program(["e public", "c <== a * b", "e <== c + d"], 8)
    srs = SRS(16)

    prover = Prover(srs, program)
    assignments = {"a": 3, "b": 4, "c": 12, "d": 5, "e": 17}
    proof = prover.prove(assignments)
    x = [17]

    verifier = Verifier(srs, program)
    valid = verifier.verify(proof, x)
    if valid:
        print("Pass!")
    else:
        print("Shit, you need to debug now.")

def test6():
    program = Program.from_str(
        """n public
        pb0 === pb0 * pb0
        pb1 === pb1 * pb1
        pb2 === pb2 * pb2
        pb3 === pb3 * pb3
        qb0 === qb0 * qb0
        qb1 === qb1 * qb1
        qb2 === qb2 * qb2
        qb3 === qb3 * qb3
        pb01 <== pb0 + 2 * pb1
        pb012 <== pb01 + 4 * pb2
        p <== pb012 + 8 * pb3
        qb01 <== qb0 + 2 * qb1
        qb012 <== qb01 + 4 * qb2
        q <== qb012 + 8 * qb3
        n <== p * q""",
        16,
    )
    srs = SRS(64)

    prover = Prover(srs, program)
    assignments = program.fill_variable_assignments(
        {
            "pb3": 1,
            "pb2": 1,
            "pb1": 0,
            "pb0": 1,
            "qb3": 0,
            "qb2": 1,
            "qb1": 1,
            "qb0": 1,
        }
    )
    proof = prover.prove(assignments)
    x = [91]

    verifier = Verifier(srs, program)
    valid = verifier.verify(proof, x)
    if valid:
        print("Pass!")
    else:
        print("Shit, you need to debug now.")

if __name__ == '__main__':
    test5()