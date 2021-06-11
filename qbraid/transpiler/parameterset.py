import abc
from abc import ABC
from typing import Iterable
from sympy import Symbol
from qiskit.circuit.parameter import Parameter as QiskitParameter
from .parameter import QiskitParameterWrapper, CirqParameterWrapper, AbstractParameterWrapper
from qbraid.exceptions import PackageError


class AbstractParameterSet(ABC):
    def __init__(self):

        self.parameters = []
        self._outputs = {}

    def get_parameter(self, search_target_parameter):
        """Same as get_qubit but for parameters."""

        for param in self.parameters:
            if param.parameter == search_target_parameter:
                return param

    @abc.abstractmethod
    def get_parameters(self, search_target_parameters: Iterable):
        pass

    def _create_cirq(self):
        self._outputs["cirq"] = [p.transpile["cirq"] for p in self.parameters]

    def _create_qiskit(self):
        self._outputs["qiskit"] = [p.transpile["qiskit"] for p in self.parameters]

    def transpile(self, package: str):
        """Create transpiled object if it has not been created altready. Return"""

        if package not in self._outputs.keys():
            self._create_output(package)
        return self._outputs[package]

    def _create_output(self, package: str):

        if package == "cirq":
            self._create_cirq()
        elif package == "qiskit":
            self._create_qiskit()
        elif package == "braket":
            raise PackageError(package, "for transpiling parameterized circuits")
        else:
            raise PackageError(package)


class QiskitParameterSet(AbstractParameterSet):
    def __init__(self, parameters: Iterable[QiskitParameter]):

        super().__init__()
        self.parameters = [QiskitParameterWrapper(p) for p in parameters]

    def get_parameters(self, search_target_parameters: Iterable):

        output = []
        for param in search_target_parameters:
            if isinstance(param, QiskitParameter):
                output.append(self.get_parameter(param))
            else:
                output.append(param)

        for p in output:
            assert isinstance(
                p,
                (
                    float,
                    int,
                    QiskitParameter,
                    AbstractParameterWrapper,
                    Iterable[float],
                    Iterable[int],
                    Iterable[QiskitParameter],
                    Iterable[AbstractParameterWrapper],
                ),
            )

        return output


class CirqParameterSet(AbstractParameterSet):
    def __init__(self, parameters: Iterable[CirqParameterWrapper]):

        super().__init__()
        self.parameters = [CirqParameterWrapper(p) for p in parameters]

    def get_parameters(self, search_target_parameters: Iterable):

        output = []
        for param in search_target_parameters:
            if isinstance(param, Symbol):
                output.append(self.get_parameter(param))
            else:
                output.append(param)

        for p in output:
            assert isinstance(p, (float, int, AbstractParameterWrapper))

        return output