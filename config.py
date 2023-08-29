from dataclasses import dataclass, field
from typing import List


@dataclass
class PulseShapeParameters:
    biphasic: bool = False
    pulse_duration: int = 100
    first_pulse_phase_width: int = 170
    pulse_interphase_interval: int = 60
    second_pulse_phase_width: int = 170
    discharge_time: int
    discharge_time_extra: int
    idle_time: int
    pulse_amplitude_anode: int
    pulse_amplitude_cathode: int
    pulse_amplitude_equal: bool

    def __post_init__(self):
        self._validate_int_param("pulse_duration", 50, 200, 1, 100)
        self._validate_int_param("first_pulse_phase_width", 50, 200, 1, 100)
        self._validate_int_param("pulse_interphase_interval", 1, 10, 1, 5)
        self._validate_int_param("second_pulse_phase_width", 50, 200, 1, 100)
        self._validate_int_param("discharge_time", 10, 50, 1, 20)
        self._validate_int_param("discharge_time_extra", 10, 50, 1, 20)
        self._validate_int_param("idle_time", 1000, 2000, 1, 1500)
        self._validate_int_param("pulse_amplitude_anode", 0, 1000, 1, 500)
        self._validate_int_param("pulse_amplitude_cathode", 0, 1000, 1, 500)

    def _validate_int_param(self, name, min_val, max_val, step_size, default):
        val = getattr(self, name)
        if not isinstance(val, int):
            raise TypeError(f"{name} must be an int.")
        if val < min_val or val > max_val:
            raise ValueError(f"{name} must be between {min_val} and {max_val}.")
        if (val - min_val) % step_size != 0:
            raise ValueError(f"{name} must be a multiple of {step_size}.")


@dataclass
class PulseTrainParameters:
    number_of_pulses: int
    frequency_of_pulses: int
    number_of_trains: int
    train_interval: int
    on_set_jitter: int

    def __post_init__(self):
        self._validate_int_param("number_of_pulses", 1, 1000, 1, 10)
        self._validate_int_param("frequency_of_pulses", 1, 100, 1, 10)
        self._validate_int_param("number_of_trains", 1, 10, 1, 2)
        self._validate_int_param("train_interval", 100, 1000, 10, 200)
        self._validate_int_param("on_set_jitter", 0, 100, 1, 0)

    def _validate_int_param(self, name, min_val, max_val, step_size, default):
        val = getattr(self, name)
        if not isinstance(val, int):
            raise TypeError(f"{name} must be an int.")
        if val < min_val or val > max_val:
            raise ValueError(f"{name} must be between {min_val} and {max_val}.")
        if (val - min_val) % step_size != 0:
            raise ValueError(f"{name} must be a multiple of {step_size}.")


@dataclass
class ViperBoxConfig:
    probe: int
    handle: int = field(default=None)

    def __post_init__(self):
        if not 0 <= self.probe <= 3:
            raise ValueError("Probe must be between 0 and 3.")


@dataclass
class StimulationConfiguration:
    pulse_shape: PulseShapeParameters
    pulse_train: PulseTrainParameters
    electrodes: List[int]
    viperbox: ViperBoxConfig

    def __post_init__(self):
        self._validate_electrodes()

    def _validate_electrodes(self):
        if len(self.electrodes) != len(set(self.electrodes)):
            raise ValueError("Electrodes list must have unique values.")

        for electrode in self.electrodes:
            if not 1 <= electrode <= 128:
                raise ValueError("Electrodes must have values between 1 and 128.")


if __name__ == "__main__":
    # Example usage:
    pulse_shape = PulseShapeParameters(
        True, False, 100, 100, 5, 100, 20, 20, 1500, 500, 500, True
    )
    pulse_train = PulseTrainParameters(10, 10, 2, 200, 0)
    electrodes = [1, 2, 3]
    viperbox = ViperBoxConfig(0)
    config = StimulationConfiguration(pulse_shape, pulse_train, electrodes, viperbox)
