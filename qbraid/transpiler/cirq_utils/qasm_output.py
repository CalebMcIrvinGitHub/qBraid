# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# isort: skip_file
# pylint: skip-file
# fmt: off

"""
Module defining utility classes for representing QASM.

"""
# pylint: skip-file

import re
from typing import TYPE_CHECKING, Callable, Dict, Optional, Set, Tuple, Union

from cirq import ops, protocols
from cirq.circuits.qasm_output import QasmTwoQubitGate, QasmUGate

if TYPE_CHECKING:
    import cirq


class QasmOutput:
    """Representation of a circuit in QASM (quantum assembly) format.
    Please note that the QASM importer is in an experimental state and
    currently only supports a subset of the full OpenQASM spec.
    Amongst others, classical control, arbitrary gate definitions,
    and even some of the gates that don't have a one-to-one representation
    in Cirq, are not yet supported.
    QASM output can be saved to a file using the save method.
    """

    valid_id_re = re.compile(r'[a-z][a-zA-Z0-9_]*\Z')

    def __init__(
        self,
        operations: 'cirq.OP_TREE',
        qubits: Tuple['cirq.Qid', ...],
        header: str = '',
        precision: int = 10,
        version: str = '2.0',
    ) -> None:
        """Representation of a circuit in QASM format.

        Args:
            operations: Tree of operations to insert.
            qubits: The qubits used in the operations.
            header: A multi-line string that is placed in a comment at the top
                of the QASM.
            precision: The number of digits after the decimal to show for
                numbers in the QASM code.
            version: The QASM version to target. Objects may return different
                QASM depending on version.
        """
        self.operations = tuple(ops.flatten_to_ops(operations))
        self.qubits = qubits
        self.header = header
        self.measurements = tuple(
            op for op in self.operations if isinstance(op.gate, ops.MeasurementGate)
        )
        meas_key_id_map, meas_comments = self._generate_measurement_ids()
        self.meas_comments = meas_comments
        qubit_id_map = self._generate_qubit_ids()
        self.args = protocols.QasmArgs(
            precision=precision,
            version=version,
            qubit_id_map=qubit_id_map,
            meas_key_id_map=meas_key_id_map,
        )

    def _generate_measurement_ids(self) -> Tuple[Dict[str, str], Dict[str, Optional[str]]]:
        # Pick an id for the creg that will store each measurement
        meas_key_id_map: Dict[str, str] = {}
        meas_comments: Dict[str, Optional[str]] = {}
        meas_i = 0
        for meas in self.measurements:
            key = protocols.measurement_key_name(meas)
            if key in meas_key_id_map:
                continue
            meas_id = f'm_{key}'
            if self.is_valid_qasm_id(meas_id):
                meas_comments[key] = None
            else:
                meas_id = f'm{meas_i}'
                meas_i += 1
                meas_comments[key] = ' '.join(key.split('\n'))
            meas_key_id_map[key] = meas_id
        return meas_key_id_map, meas_comments

    def _generate_qubit_ids(self) -> Dict['cirq.Qid', str]:
        return {qubit: f'q[{i}]' for i, qubit in enumerate(self.qubits)}

    def is_valid_qasm_id(self, id_str: str) -> bool:
        """Test if id_str is a valid id in QASM grammar."""
        return self.valid_id_re.match(id_str) is not None

    def save(self, path: Union[str, bytes, int]) -> None:
        """Write QASM output to a file specified by path."""
        with open(path, 'w') as f:

            def write(s: str) -> None:
                f.write(s)

            self._write_qasm(write)

    def __str__(self) -> str:
        """Return QASM output as a string."""
        output = []
        self._write_qasm(lambda s: output.append(s))
        return ''.join(output)

    def _write_qasm(self, output_func: Callable[[str], None]) -> None:
        self.args.validate_version('2.0')

        # Generate nice line spacing
        line_gap = [0]

        def output_line_gap(n):
            line_gap[0] = max(line_gap[0], n)

        def output(text):
            if line_gap[0] > 0:
                output_func('\n' * line_gap[0])
                line_gap[0] = 0
            output_func(text)

        # Comment header
        if self.header:
            for line in self.header.split('\n'):
                output(('// ' + line).rstrip() + '\n')
            output('\n')

        # Version
        output('OPENQASM 2.0;\n')
        output('include "qelib1.inc";\n')
        output_line_gap(2)

        # Function definitions
        # None yet

        # Register definitions
        # Qubit registers
        output(f"// Qubits: [{', '.join(map(str, self.qubits))}]\n")
        if len(self.qubits) > 0:
            output(f'qreg q[{len(self.qubits)}];\n')
        # Classical registers
        # Pick an id for the creg that will store each measurement
        already_output_keys: Set[str] = set()
        for meas in self.measurements:
            key = protocols.measurement_key_name(meas)
            if key in already_output_keys:
                continue
            already_output_keys.add(key)
            meas_id = self.args.meas_key_id_map[key]
            comment = self.meas_comments[key]
            if comment is None:
                output(f'creg {meas_id}[{len(meas.qubits)}];\n')
            else:
                output(f'creg {meas_id}[{len(meas.qubits)}];  // Measurement: {comment}\n')
        output_line_gap(2)

        # Operations
        self._write_operations(self.operations, output, output_line_gap)

    def _write_operations(
        self,
        op_tree: 'cirq.OP_TREE',
        output: Callable[[str], None],
        output_line_gap: Callable[[int], None],
    ) -> None:
        def keep(op: 'cirq.Operation') -> bool:
            return protocols.qasm(op, args=self.args, default=None) is not None

        def fallback(op):
            if len(op.qubits) not in [1, 2]:
                return NotImplemented

            mat = protocols.unitary(op, None)
            if mat is None:
                return NotImplemented

            if len(op.qubits) == 1:
                return QasmUGate.from_matrix(mat).on(*op.qubits)
            return QasmTwoQubitGate.from_matrix(mat).on(*op.qubits)

        def on_stuck(bad_op):
            return ValueError(f'Cannot output operation as QASM: {bad_op!r}')

        for main_op in ops.flatten_op_tree(op_tree):
            decomposed = protocols.decompose(
                main_op, keep=keep, fallback_decomposer=fallback, on_stuck_raise=on_stuck
            )

            qasms = [protocols.qasm(op, args=self.args) for op in decomposed]

            should_annotate = decomposed != [main_op] or qasms[0].count('\n') > 1
            if should_annotate:
                output_line_gap(1)
                if isinstance(main_op, ops.GateOperation):
                    x = str(main_op.gate).replace('\n', '\n //')
                    output(f'// Gate: {x!s}\n')
                else:
                    x = str(main_op).replace('\n', '\n //')
                    output(f'// Operation: {x!s}\n')

            for qasm in qasms:
                output(qasm)

            if should_annotate:
                output_line_gap(1)
