"""QiskitBackendWrapper Class"""

from qiskit import IBMQ, Aer, execute, transpile as qiskit_transpile
from qiskit.providers.ibmq.managed import IBMQJobManager
from qiskit.providers.backend import Backend as QiskitBackend
from qiskit.providers.ibmq import IBMQProviderError
from qiskit.utils.quantum_instance import QuantumInstance

from qbraid.devices._utils import get_config, init_job
from qbraid.devices.device import DeviceLikeWrapper
from qbraid.devices.enums import DeviceStatus
from qbraid.devices.ibm.job import QiskitJobWrapper
from qbraid.devices.ibm.result import QiskitResultWrapper
from qbraid.devices.exceptions import DeviceError


class QiskitBackendWrapper(DeviceLikeWrapper):
    """Wrapper class for IBM Qiskit ``Backend`` objects."""

    def __init__(self, device_info, **kwargs):
        """Create a QiskitBackendWrapper."""

        super().__init__(device_info, **kwargs)

    def _get_device(self) -> QiskitBackend:
        """Initialize an IBM device."""
        if self._obj_ref == "IBMQ":
            if IBMQ.active_account() is None:
                IBMQ.load_account()
            group = get_config("group", "IBM")
            project = get_config("project", "IBM")
            try:
                provider = IBMQ.get_provider(hub="ibm-q", group=group, project=project)
            except IBMQProviderError:
                IBMQ.load_account()
                provider = IBMQ.get_provider(hub="ibm-q", group=group, project=project)
            return provider.get_backend(self._obj_arg)
        elif self._obj_ref == "Aer":
            return Aer.get_backend(self._obj_arg)
        else:
            raise DeviceError(f"obj_ref {self._obj_ref} not found.")

    @property
    def status(self):
        """Return the status of this Device.

        Returns:
            str: The status of this Device
        """
        backend_status = self.vendor_dlo.status()
        if not backend_status.operational:
            return DeviceStatus.OFFLINE
        return DeviceStatus.ONLINE

    def execute(self, run_input, *args, **kwargs):
        """Runs circuit(s) on qiskit backend via :meth:`~qiskit.utils.QuantumInstance.execute`.

        Creates a :class:`~qiskit.utils.QuantumInstance`, invokes its ``execute`` method,
        applies a QiskitResultWrapper, and returns the result.

        Args:
            run_input: An individual or a list of circuit objects to run on the wrapped device.
            kwargs: Any kwarg options to pass to the device for the run.

        Returns:
            qbraid.devices.ibm.QiskitResultWrapper: The result like object for the run.

        """
        run_input, _ = self._compat_run_input(run_input)
        quantum_instance = QuantumInstance(self.vendor_dlo, *args, **kwargs)
        qiskit_result = quantum_instance.execute(run_input)
        qbraid_result = QiskitResultWrapper(qiskit_result)
        return qbraid_result

    def run(self, run_input, *args, **kwargs):
        """Runs circuit(s) on qiskit backend via :meth:`~qiskit.execute`

        Uses the :meth:`~qiskit.execute` method to create a :class:`~qiskit.providers.Job` object,
        applies a :class:`~qbraid.devices.ibm.QiskitJobWrapper`, and return the result.

        Args:
            run_input: A circuit object to run on the wrapped device.

        Keyword Args:
            shots (int): The number of times to run the task on the device. Default is 1024.


        Returns:
            qbraid.devices.ibm.QiskitJobWrapper: The job like object for the run.

        """
        run_input, qbraid_circuit = self._compat_run_input(run_input)
        if "shots" in kwargs:
            shots = kwargs.pop("shots")
            self.vendor_dlo.set_options(shots=shots)
        else:
            shots = self.vendor_dlo.options.get("shots")
        compiled_circuit = qiskit_transpile(run_input, self.vendor_dlo)
        if self._obj_ref == "Aer":
            qiskit_job = execute(compiled_circuit, self.vendor_dlo, *args, **kwargs)
            qiskit_job_id = qiskit_job.job_id()
        else:
            job_manager = IBMQJobManager()
            job_set = job_manager.run([compiled_circuit], backend=self.vendor_dlo)
            qiskit_job = job_set.jobs()[0]
            qiskit_job_id = job_set.job_set_id()
        qbraid_job_id = init_job(qiskit_job_id, self, qbraid_circuit, shots)
        qbraid_job = QiskitJobWrapper(
            qbraid_job_id, vendor_job_id=qiskit_job_id, device=self, vendor_jlo=qiskit_job
        )
        return qbraid_job
