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

        # Public processed input
        # Should get these values directly in pratical implementation
        self.com_qm = KZG.commit(srs, self.pk.QM.ifft())
        self.com_ql = KZG.commit(srs, self.pk.QL.ifft())
        self.com_qr = KZG.commit(srs, self.pk.QR.ifft())
        self.com_qo = KZG.commit(srs, self.pk.QO.ifft())
        self.com_qc = KZG.commit(srs, self.pk.QC.ifft())

        self.com_s1 = KZG.commit(srs, self.pk.S1.ifft())
        self.com_s2 = KZG.commit(srs, self.pk.S2.ifft())
        self.com_s3 = KZG.commit(srs, self.pk.S3.ifft())

    def verify(self, proof: Proof, publics=[]) -> bool:
        beta = proof.scripts[0]
        gamma = proof.scripts[1]
        alpha = proof.scripts[2]
        zeta = proof.scripts[3]
        v = proof.scripts[4]
        u = proof.scripts[5]

        # Get witness commitments in Round 1
        com_a: G1Point = proof.Message_1[0]
        com_b: G1Point = proof.Message_1[1]
        com_c: G1Point = proof.Message_1[2]

        # Get permutation product check commitment in Round 2
        com_z: G1Point = proof.Message_2[0]
        #print(type(com_z))

        # Get quotient polynomial commitment in Round 3
        com_t_low: G1Point = proof.Message_3[0]
        com_t_mid: G1Point = proof.Message_3[1]
        com_t_hi: G1Point = proof.Message_3[2]
        
        # Get 6 openings before computing linearisation polynomial in Round 4
        a_zeta = proof.Message_4[0]
        b_zeta = proof.Message_4[1]
        c_zeta = proof.Message_4[2]
        s1_zeta = proof.Message_4[3]
        s2_zeta = proof.Message_4[4]
        z_wzeta = proof.Message_4[5]

        # Get two opening proof
        com_w_x: G1Point = proof.Message_5[0]
        com_w_zx: G1Point = proof.Message_5[1]

        wtl = self.witness_len
        domain = Scalar.roots_of_unity(wtl)
        # Step 1-4 are omitted since those are trivial
        # Step 5
        ZH_zeta = zeta**wtl - 1
        #print(ZH_zeta)

        # Step 6
        # Compute Lagrange polynomial L1(zeta)
        l1_zeta = (zeta**wtl - 1) / (wtl*(zeta - 1))
        #print(l1_zeta)

        # Step 7
        # Compute public input polynomial evaluation
        PI = Polynomial(
            [-Scalar(v) for v in publics]
            + [Scalar(0) for _ in range(wtl - len(publics))],
            Basis.LAGRANGE,
        )
        PI_zeta = PI.barycentric_eval(zeta)
        #print(PI_zeta)

        # Step 8
        r_0 = (  PI_zeta 
               - l1_zeta*(alpha**2) 
               - alpha*(a_zeta + beta*s1_zeta + gamma)*(b_zeta + beta*s2_zeta + gamma)*(c_zeta + gamma)*z_wzeta
            )

        # Step 9 & 10
        # Compute batched polynomial commitment
        # Prepare scalar vectors and point vectors for MSM
        scalar_vec = [a_zeta*b_zeta, a_zeta, b_zeta, c_zeta, Scalar(1)]
        scalar_vec.append(
              (a_zeta + beta*zeta + gamma)
             *(b_zeta + beta*2*zeta + gamma)
             *(c_zeta + beta*3*zeta + gamma)
             *alpha 
            + 
             l1_zeta*(alpha**2)
            +
             u
        )
        scalar_vec.append(
            - (a_zeta + beta*s1_zeta + gamma)
             *(b_zeta + beta*s2_zeta + gamma)
             *alpha
             *beta
             *z_wzeta
        )
        scalar_vec.append(-ZH_zeta)
        scalar_vec.append(-ZH_zeta*(zeta**wtl))
        scalar_vec.append(-ZH_zeta*(zeta**(2*wtl)))
        scalar_vec += [v, v**2, v**3, v**4, v**5]

        group_vec = [self.com_qm, self.com_ql, self.com_qr, self.com_qo, self.com_qc,
                     com_z, self.com_s3, com_t_low, com_t_mid, com_t_hi, com_a, com_b, com_c, self.com_s1, self.com_s2]
        com_F = ec_lincomb([(pt, scar) for (pt, scar) in zip(group_vec, scalar_vec)])
        #print(com_F)
        
        # Step 11
        # Compute batch evaluation
        s_e = -r_0 + a_zeta*v + b_zeta*(v**2) + c_zeta*(v**3) + s1_zeta*(v**4) + s2_zeta*(v**5) + u*z_wzeta
        com_E = KZG.commit(self.srs, Polynomial([s_e], Basis.MONOMIAL))
        #print(com_E)

        # Step 12
        # Batch evaluation
        p_left = b.pairing(self.srs.G2s[1], b.add(b.multiply(com_w_zx, u.n), com_w_x))
        
        root = Scalar.root_of_unity(self.witness_len)
        right = ec_lincomb([
            (com_w_x, zeta),
            (com_w_zx, u*zeta*root),
            (com_F, Scalar(1)),
            (com_E, Scalar(-1))
        ])
        p_right = b.pairing(self.srs.G2s[0], right)

        return p_left == p_right