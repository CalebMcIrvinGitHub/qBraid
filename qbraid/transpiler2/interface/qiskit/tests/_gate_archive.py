from qiskit.circuit.library import standard_gates as sg
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit.measure import Measure
from qiskit.extensions.unitary import UnitaryGate

qiskit_gates = {
    "H": sg.h.HGate,
    "X": sg.x.XGate,
    "Y": sg.y.YGate,
    "Z": sg.z.ZGate,
    "S": sg.s.SGate,
    "Sdg": sg.s.SdgGate,
    "T": sg.t.TGate,
    "Tdg": sg.t.TdgGate,
    "I": sg.i.IGate,
    "SX": sg.sx.SXGate,
    "SXdg": sg.sx.SXdgGate,
    "Phase": sg.p.PhaseGate,
    "RX": sg.rx.RXGate,
    "RY": sg.ry.RYGate,
    "RZ": sg.rz.RZGate,
    "U1": sg.U1Gate,
    "R": sg.r.RGate,
    "U2": sg.u2.U2Gate,
    "U": sg.u.UGate,
    "U3": sg.u3.U3Gate,
    "CH": sg.h.CHGate,
    "CX": sg.x.CXGate,
    "Swap": sg.swap.SwapGate,
    "iSwap": sg.iswap.iSwapGate,
    "CSX": sg.sx.CSXGate,
    "DCX": sg.dcx.DCXGate,
    "CY": sg.y.CYGate,
    "CZ": sg.z.CZGate,
    "CPhase": sg.p.CPhaseGate,
    "CRX": sg.rx.CRXGate,
    "RXX": sg.rxx.RXXGate,
    "CRY": sg.ry.CRYGate,
    "RYY": sg.ryy.RYYGate,
    "CRZ": sg.rz.CRZGate,
    "RZX": sg.rzx.RZXGate,
    "RZZ": sg.rzz.RZZGate,
    "CU1": sg.u1.CU1Gate,
    "RCCX": sg.x.RCCXGate,
    "RC3X": sg.x.RC3XGate,
    "CCX": sg.x.CCXGate,
    "Unitary": UnitaryGate,
    "MEASURE": Measure,
}