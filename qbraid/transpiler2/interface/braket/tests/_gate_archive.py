from braket.circuits.gates import (
    CY,
    CZ,
    XX,
    XY,
    YY,
    ZZ,
    CCNot,
    CNot,
    CPhaseShift,
    H,
    I,
    ISwap,
    PhaseShift,
    PSwap,
    Rx,
    Ry,
    Rz,
    S,
    Si,
    Swap,
    T,
    Ti,
    Unitary,
    V,
    Vi,
    X,
    Y,
    Z,
)

braket_gates = {
    # one-qubit, zero parameter
    "H": H,
    "X": X,
    "Y": Y,
    "Z": Z,
    "S": S,
    "Sdg": Si,
    "T": T,
    "Tdg": Ti,
    "I": I,
    "SX": V,
    "SXdg": Vi,
    # one-qubit, one parameter
    "Phase": PhaseShift,
    "RX": Rx,
    "RY": Ry,
    "RZ": Rz,
    "U1": PhaseShift,
    # two-qubit, zero parameter
    # 'CH':BraketGate.,
    "CX": CNot,
    "Swap": Swap,
    "iSwap": ISwap,
    # 'CSX':BraketGate.,
    # 'DCX': BraketGate.,
    "CY": CY,
    "CZ": CZ,
    # two-qubit, one parameter
    "RXX": XX,
    "RXY": XY,
    "RYY": YY,
    "RZZ": ZZ,
    "pSwap": PSwap,
    "CPhase": CPhaseShift,
    # multi-qubit
    "CCX": CCNot,
    # unitary
    "Unitary": Unitary,
}