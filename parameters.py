from dataclasses import dataclass, asdict
from typing import Any, List

# TODO:
# - run verify_values whenever any setting is changed (lazy) OR only run
#   relevant checks if specific values are changed
# - adapt and include discharge times if necessary, if so, add logic
#   to make interpulse_interval the same as the sum of both discharge times


def verify_step_min_max(name: str, value: int, step: int, min_val: int, max_val: int):
    if not min_val <= value <= max_val or value % step != 0:
        raise ValueError(
            f"{name} should be within [{min_val}, {max_val}] and follow step "
            + f"size {step}. It is currently {value}"
        )


@dataclass
class PulseShapeParameters:
    biphasic: bool = True
    first_pulse_phase_width: int = 170
    pulse_interphase_interval: int = 60
    second_pulse_phase_width: int = 170
    discharge_time: int = 200
    discharge_time_extra: int = 0
    interpulse_interval: int = 200  # = discharge time
    pulse_amplitude_anode: int = 1
    pulse_amplitude_cathode: int = 1
    pulse_amplitude_equal: bool = False

    def __post_init__(self) -> None:
        self.correct_values()
        self.verify_values()

    def __setattr__(self, __name: str, __value: Any) -> None:
        super().__setattr__(__name, __value)
        self.verify_values()

    def correct_values(self) -> None:
        self.discharge_time = self.interpulse_interval
        self.discharge_time_extra = 0
        if self.pulse_amplitude_equal:
            self.pulse_amplitude_cathode = self.pulse_amplitude_anode
            self.biphasic = True
        if self.biphasic is False:
            self.pulse_amplitude_cathode = 0

    def verify_values(self) -> None:
        # Verify the values against step size, min and max
        verify_step_min_max(
            "first_pulse_phase_width", self.first_pulse_phase_width, 10, 10, 2550
        )
        verify_step_min_max(
            "pulse_interphase_interval", self.pulse_interphase_interval, 10, 10, 2550
        )
        verify_step_min_max(
            "second_pulse_phase_width", self.second_pulse_phase_width, 10, 10, 2550
        )
        verify_step_min_max(
            "interpulse_interval", self.interpulse_interval, 100, 100, 51000
        )
        verify_step_min_max(
            "pulse_amplitude_anode", self.pulse_amplitude_anode, 1, 0, 255
        )
        verify_step_min_max(
            "pulse_amplitude_cathode", self.pulse_amplitude_cathode, 1, 0, 255
        )

        # some checks to see wheter values weren't changed manually
        expected_discharge_time = self.interpulse_interval
        if self.discharge_time != expected_discharge_time:
            raise ValueError(
                f"Expected discharge_time to be {expected_discharge_time}, but got "
                + f"{self.discharge_time}"
            )

        if self.discharge_time_extra != 0:
            raise ValueError("Expected discharge_time_extra to be 0")

        if self.pulse_amplitude_equal:
            if self.pulse_amplitude_cathode != self.pulse_amplitude_anode:
                raise ValueError(
                    "Expected pulse_amplitude_cathode to be equal to "
                    + "pulse_amplitude_anode when pulse_amplitude_equal is True"
                )

            if self.biphasic is False:
                raise ValueError(
                    "Expected biphasic to be True when pulse_amplitude_equal is True"
                )

        if self.biphasic is False:
            if self.pulse_amplitude_cathode != 0:
                raise ValueError(
                    "Expected pulse_amplitude_cathode to be 0 when biphasic is False"
                )


@dataclass
class PulseTrainParameters:
    number_of_pulses: int = 50
    frequency_of_pulses: int = 2500
    number_of_trains: int = 1
    train_interval: int = 1000
    onset_jitter: int = 1000

    def __post_init__(self) -> None:
        self.verify_values()

    def verify_values(self) -> None:
        verify_step_min_max("number_of_pulses", self.number_of_pulses, 1, 1, 255)
        verify_step_min_max("number_of_trains", self.number_of_trains, 1, 1, 20)
        verify_step_min_max("train_interval", self.train_interval, 1000, 1000, 3000000)
        verify_step_min_max("onset_jitter", self.onset_jitter, 1000, 0, 2000000)
        # TODO: check if 1/frequency_of_pulses is the same as pulse_duration, this
        #       should probably be done on the level of ConfigurationParameters

        def __setattr__(self, __name: str, __value: Any) -> None:
            super().__setattr__(__name, __value)
            self.verify_values()


@dataclass
class ViperBoxConfiguration:
    probe: int

    def __post_init__(self) -> None:
        if not 0 <= self.probe <= 3:
            raise ValueError("Probe value should be between 0 and 3.")

    def __setattr__(self, __name: str, __value: Any) -> None:
        super().__setattr__(__name, __value)
        self.verify_values()

    def verify_values(self) -> None:
        if not 0 <= self.probe <= 3:
            raise ValueError("Probe value should be between 0 and 3.")


@dataclass
class ConfigurationParameters:
    pulse_shape_parameters: PulseShapeParameters
    pulse_train_parameters: PulseTrainParameters
    list_of_stimulation_electrodes: List[int]
    viperbox_configuration: ViperBoxConfiguration

    def __post_init__(self) -> None:
        self.verify_electrodes()

    def verify_electrodes(self) -> None:
        electrodes_set = set(self.list_of_stimulation_electrodes)
        if len(electrodes_set) != len(self.list_of_stimulation_electrodes):
            # log "You've supplied duplicate electrodes."
            # raise ValueError("Duplicate electrodes are not allowed.")
            pass

        for elec in electrodes_set:
            if not 1 <= elec <= 128:
                raise ValueError("Electrodes should have values between 1 and 128.")

    def get_SUConfig_pars(self, handle=0, probe=0, stimunit=0, polarity=0) -> List[Any]:
        all_parameters = {
            **asdict(self.pulse_shape_parameters),
            **asdict(self.pulse_train_parameters),
        }
        return (
            handle,
            probe,
            stimunit,
            polarity,
            all_parameters.get("number_of_pulses", None),
            all_parameters.get("pulse_amplitude_anode", None),
            all_parameters.get("pulse_amplitude_cathode", None),
            all_parameters.get("pulse_duration", None),
            0,  # pulse_delay
            # all_parameters.get("pulse_delay", None),
            all_parameters.get("first_pulse_phase_width", None),
            all_parameters.get("pulse_interphase_interval", None),
            all_parameters.get("second_pulse_phase_width", None),
            all_parameters.get("discharge_time", None),
            all_parameters.get("discharge_time_extra", None),
        )


if __name__ == "__main__":
    # Example usage:
    pulse_shape = PulseShapeParameters()
    pulse_train = PulseTrainParameters()
    electrodes = [1, 2, 3]
    viperbox = ViperBoxConfiguration(0)
    config = ConfigurationParameters(pulse_shape, pulse_train, electrodes, viperbox)
    test = config.get_SUConfig_pars()
    print("SUConfig pars: ", test)
