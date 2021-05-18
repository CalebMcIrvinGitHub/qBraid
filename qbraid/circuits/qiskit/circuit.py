from ..circuit import AbstractCircuitWrapper
from ..qubitset import QiskitQubitSet
from ..clbitset import ClbitSet
from ..clbit import Clbit
from ..parameterset import QiskitParameterSet
from .instruction import QiskitInstructionWrapper

from qiskit.circuit import QuantumCircuit as QiskitCircuit

class QiskitCircuitWrapper(AbstractCircuitWrapper):
    
    def __init__(self, circuit: QiskitCircuit):
        
        super().__init__
        
        self.circuit = circuit
        self._outputs = {}
        
        self.qubitset = QiskitQubitSet(circuit.qubits)
        self.clbitset = ClbitSet(circuit.clbits)
        self.parameterset = QiskitParameterSet(circuit.parameters)
        print(list(type(i) for i in self.parameterset.parameters))
        
        self.instructions = []
        
        #create an Instruction object for each instruction in the circuit
        for instruction, qubit_list, clbit_list in circuit.data:
            
            qubits = self.qubitset.get_qubits(qubit_list)
            clbits = self.clbitset.get_clbits(clbit_list)
            params = self.parameterset.get_parameters(instruction.params)
            
            if len(clbits)>0:
                assert(isinstance(clbits[0], Clbit))

            self.instructions.append(QiskitInstructionWrapper(instruction,qubits,clbits,params))
    
    @property
    def num_qubits(self):    
        return self.circuit.num_qubits
    
    @property
    def num_clbits(self):
        return self.circuit.num_clbits
    
    @property
    def supported_packages(self):
        return ['qiskit','braket','cirq']
    
    def transpile(self,package:str):

        if package in self.supported_packages:
            if package == 'cirq':    
                return self._to_cirq()
            elif package == 'braket':
                return self._to_braket()
            elif package == 'qiskit':
                return self.circuit
        
        else:
            print("The transpiler does not support conversion from qiskit to {}.".format(package))
        