from .wrapper import QbraidWrapper
from .outputs import instruction_outputs
from .utils import supported_packages
from qbraid.exceptions import PackageError

class InstructionWrapper(QbraidWrapper):
    def __init__(self):

        self.instruction = None
        self.qubits = []

        self.gate = None
        self.params = None

        self._outputs = {}


    def transpile(self, package: str, output_qubit_mapping: dict = None, output_param_mapping: dict = None):
        
        if package == self.package:
            return self.circuit
        elif package in self.supported_packages:
            return instruction_outputs[package](self, output_qubit_mapping, output_param_mapping)
        else:
            raise PackageError(f"This instruction cannot be transpiled from {self.package} to {package}.")
