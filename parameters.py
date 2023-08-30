from dataclasses import dataclass, field
from typing import Any, List

# TODO:
# - run verify_values whenever any setting is changed (lazy) OR only run
#   relevant checks if specific values are changed
# - adapt and include discharge times if necessary, if so, add logic
#   to make interpulse_interval the same as the sum of both discharge times


@dataclass
class PulseShapeParameters:
    biphasic: bool = True
    pulse_duration: int = field(init=False)
    pulse_delay: int = field(init=False)
    first_pulse_phase_width: int = 170
    pulse_interphase_interval: int = 60
    second_pulse_phase_width: int = 170
    discharge_time: int = field(init=False)
    discharge_time_extra: int = field(init=False)
    interpulse_interval: int = 200  # = discharge time
    pulse_amplitude_anode: int = 1
    pulse_amplitude_cathode: int = 1
    pulse_amplitude_equal: bool = False
    initialized: bool = field(init=False)

    def __post_init__(self):
        self.pulse_duration = (
            self.first_pulse_phase_width
            + self.pulse_interphase_interval
            + self.second_pulse_phase_width
            + self.interpulse_interval
        )
        self.pulse_delay = 0
        self.discharge_time = self.interpulse_interval
        self.discharge_time_extra = 0
        if self.pulse_amplitude_equal:
            self.pulse_amplitude_cathode = self.pulse_amplitude_anode
            self.biphasic = True
        if self.biphasic is False:
            self.pulse_amplitude_cathode = 0
        self.initialized = True
        self.verify_values()

        def __setattr__(self, __name: str, __value: Any) -> None:
            super().__setattr__(__name, __value)
            # if self.initialized:
            self.verify_values()

    def verify_values(self):
        # Verify the values against min, max, and step size
        self.verify_step_min_max("pulse_delay", self.pulse_delay, 0, 100, 25500)
        self.verify_step_min_max("pulse_duration", self.pulse_duration, 100, 100, 25500)
        self.verify_step_min_max(
            "first_pulse_phase_width", self.first_pulse_phase_width, 10, 10, 2550
        )
        self.verify_step_min_max(
            "pulse_interphase_interval", self.pulse_interphase_interval, 10, 10, 2550
        )
        self.verify_step_min_max(
            "second_pulse_phase_width", self.second_pulse_phase_width, 10, 10, 2550
        )
        self.verify_step_min_max(
            "interpulse_interval", self.interpulse_interval, 100, 100, 51000
        )
        self.verify_step_min_max(
            "pulse_amplitude_anode", self.pulse_amplitude_anode, 1, 0, 255
        )
        self.verify_step_min_max(
            "pulse_amplitude_cathode", self.pulse_amplitude_cathode, 1, 0, 255
        )

    @staticmethod
    def verify_step_min_max(
        name: str, value: int, step: int, min_val: int, max_val: int
    ):
        if not min_val <= value <= max_val or value % step != 0:
            raise ValueError(
                f"{name} should be within [{min_val}, {max_val}] and follow step "
                + f"size {step}."
            )


@dataclass
class PulseTrainParameters:
    number_of_pulses: int = 50
    frequency_of_pulses: int = 2500
    number_of_trains: int = 1
    train_interval: int = 1000
    onset_jitter: int = 1000
    initialized: bool = field(init=False)

    def __post_init__(self):
        self.initialized = True
        self.verify_values()

    def verify_values(self):
        self.verify_step_min_max("number_of_pulses", self.number_of_pulses, 1, 1, 255)
        self.verify_step_min_max("number_of_trains", self.number_of_trains, 1, 1, 20)
        self.verify_step_min_max(
            "train_interval", self.train_interval, 1000, 1000, 3000000
        )
        self.verify_step_min_max("onset_jitter", self.onset_jitter, 1000, 0, 2000000)
        # TODO: check if 1/frequency_of_pulses is the same as pulse_duration, this
        #       should probably be done on the level of

        def __setattr__(self, __name: str, __value: Any) -> None:
            super().__setattr__(__name, __value)
            # if self.initialized:
            self.verify_values()

    @staticmethod
    def verify_step_min_max(
        name: str, value: int, step: int, min_val: int, max_val: int
    ):
        if not min_val <= value <= max_val or value % step != 0:
            raise ValueError(
                f"{name} should be within [{min_val}, {max_val}] and follow step "
                + f"size {step}."
            )


@dataclass
class ViperBoxConfiguration:
    probe: int
    # handle: int = None

    def __post_init__(self):
        if not 0 <= self.probe <= 3:
            raise ValueError("Probe value should be between 0 and 3.")

    def __setattr__(self, __name: str, __value: Any) -> None:
        super().__setattr__(__name, __value)
        self.verify_values()

    def verify_values(self):
        if not 0 <= self.probe <= 3:
            raise ValueError("Probe value should be between 0 and 3.")


@dataclass
class ConfigurationParameters:
    pulse_shape_parameters: PulseShapeParameters
    pulse_train_parameters: PulseTrainParameters
    list_of_stimulation_electrodes: List[int]
    viperbox_configuration: ViperBoxConfiguration

    def __post_init__(self):
        self.verify_electrodes()

    def verify_electrodes(self):
        electrodes_set = set(self.list_of_stimulation_electrodes)
        if len(electrodes_set) != len(self.list_of_stimulation_electrodes):
            # log "You've supplied duplicate electrodes."
            # raise ValueError("Duplicate electrodes are not allowed.")
            pass

        for elec in electrodes_set:
            if not 1 <= elec <= 128:
                raise ValueError("Electrodes should have values between 1 and 128.")

    def SUConfig_pars(handle, probe, stimunit=0, polarity=0):
        return (
            handle,
            probe,
            stimunit,
            polarity,
            PulseTrainParameters.number_of_pulses,
            PulseShapeParameters.pulse_amplitude_anode,
            PulseShapeParameters.pulse_amplitude_cathode,
            PulseShapeParameters.pulse_duration,
            PulseShapeParameters.pulse_delay,
            PulseShapeParameters.first_pulse_phase_width,
            PulseShapeParameters.pulse_interphase_interval,
            PulseShapeParameters.second_pulse_phase_width,
            PulseShapeParameters.discharge_time,
            PulseShapeParameters.discharge_time_extra,
        )


if __name__ == "__main__":
    # Example usage:
    pulse_shape = PulseShapeParameters()
    pulse_train = PulseTrainParameters()
    electrodes = [1, 2, 3]
    viperbox = ViperBoxConfiguration(0)
    config = ConfigurationParameters(pulse_shape, pulse_train, electrodes, viperbox)
    print(config.pulse_shape_parameters)
