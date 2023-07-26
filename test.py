from compiler.program import Program
from polycom import SRS
import py_ecc.bn128 as b



def test1():
    SRS(16)

def test2():
    program = Program(["e public", "c <== a * b", "e <== c * d"], 32)
    print(program.constraints)

if __name__ == '__main__':
    test2()