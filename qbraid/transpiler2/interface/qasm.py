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

from cirq import circuits

from qbraid.transpiler2.interface._parser import QasmParser


def circuit_from_qasm(qasm: str) -> circuits.Circuit:
    """Parses an OpenQASM string to `cirq.Circuit`.
    Args:
        qasm: The OpenQASM string
    Returns:
        The parsed circuit
    """

    return QasmParser().parse(qasm).circuit
