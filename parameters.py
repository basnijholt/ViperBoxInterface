from dataclasses import dataclass, asdict, field
from typing import Any, List, Tuple
import random
import logging

logger = logging.getLogger(__name__)

"""
This module contains classes and functions for defining and verifying parameters
for stimulation and recording.

Known limitation of implementation
- all intervals between stimulation pulses are discharge moments so no recording from 
    those electrodes is possible during that time
"""

# TODO:
# - implement onset_jitter in trigger probably

verify_int_params = {
    "pulse_duration": [100, 100, 25500],
    "pulse_delay": [100, 0, 25500],
    "first_pulse_phase_width": [10, 10, 2550],
    "pulse_interphase_interval": [10, 0, 2550],
    "second_pulse_phase_width": [10, 0, 2550],
    "discharge_time": [100, 0, 25500],
    "pulse_amplitude_anode": [1, 0, 255],
    "pulse_amplitude_cathode": [1, 0, 255],
    "number_of_pulses": [1, 0, 255],
    "number_of_trains": [1, 1, 50],
    "discharge_time_extra": [100, 0, 25500],
    "onset_jitter": [1000, 0, 2000000],
    "pulse_amplitude_min": [1, 0, 255],
    "pulse_amplitude_max": [1, 0, 255],
    "pulse_amplitude_step": [1, 0, 255],
    "repetitions": [1, 0, 50],
    "frequency_of_pulses": [1, 40, 10000],
}


def verify_step_min_max(name: str, value: int, step: int, min_val: int, max_val: int):
    """
    Verifies that a given value is within a specified range and is a multiple of a step
    value.

    :param str name: Name of the parameter to verify
    :param int value: The value of the parameter to verify
    :param int step: The step size for the parameter
    :param int min_val: The minimum allowed value for the parameter
    :param int max_val: The maximum allowed value for the parameter
    :raises ValueError: If the value is out of the specified range or not a multiple of
    step
    """
    if not min_val <= value <= max_val:
        logger.error(f"{name} must be between {min_val} and {max_val}.")
        raise ValueError(f"{name} must be between {min_val} and {max_val}.")
    if (value - min_val) % step != 0:
        logger.error(f"{name} must be a multiple of {step}.")
        raise ValueError(f"{name} must be a multiple of {step}.")


@dataclass
class PulseShapeParameters:
    """
    Class for holding pulse shape parameters.

    :param bool biphasic: Whether the pulse is biphasic or monophasic (default: True)
    :param int pulse_delay: Delay before first pulse starts (default: 0 us)
    :param int first_pulse_phase_width: Width of the first phase of the pulse (default:
    170 us)
    :param int pulse_interphase_interval: Interval between the two phases of the pulse
    (default: 60 us)
    :param int second_pulse_phase_width: Width of the second phase of the pulse
    (default: 170 us)
    :param int discharge_time: Discharge interval between pulses (default: 200 us)
    :param int pulse_amplitude_anode: Amplitude of the anode pulse (default: 1)
    :param int pulse_amplitude_cathode: Amplitude of the cathode pulse (default: 1)
    :param bool pulse_amplitude_equal: Whether the amplitude of anode and cathode pulses
    should be equal (default: False)
    :param int pulse_duration: Duration of entire pulse (default: 600)
    """

    biphasic: bool = True
    pulse_delay: int = 0
    first_pulse_phase_width: int = 170
    pulse_interphase_interval: int = 60
    second_pulse_phase_width: int = 170
    discharge_time: int = 200
    pulse_amplitude_anode: int = 1
    pulse_amplitude_cathode: int = 1
    pulse_amplitude_equal: bool = False

    pulse_duration: int = 1000

    # shape_step_size_dict = {
    #     pulse_delay: 100,
    #     first_pulse_phase_width: 10,
    #     pulse_interphase_interval: 10,
    #     second_pulse_phase_width: 10,
    #     discharge_time: 100,
    #     pulse_amplitude_anode: 1,
    #     pulse_amplitude_cathode: 1,
    #     pulse_duration: 100,
    # }

    def __post_init__(self) -> None:
        """Initialize values and verify them."""
        self.correct_values()
        self.verify_values()

    def __setattr__(self, __name: str, __value: Any) -> None:
        """Make sure that every time a attribute is changed, some checks will be
        done."""
        super().__setattr__(__name, __value)
        self.verify_values()

    def correct_values(self) -> None:
        """Set and correct values based on other attributes."""
        self.discharge_time_extra = 0
        if self.pulse_amplitude_equal:
            self.pulse_amplitude_cathode = self.pulse_amplitude_anode
            self.biphasic = True
        if self.biphasic is False:
            self.pulse_amplitude_cathode = 0

    def verify_values(self) -> None:
        """Verify the values against minimum, maximum and step size."""
        # List of parameters to verify
        verify_params = [
            ("pulse_delay", self.pulse_delay, 100, 0, 25500),
            ("first_pulse_phase_width", self.first_pulse_phase_width, 10, 10, 2550),
            ("pulse_interphase_interval", self.pulse_interphase_interval, 10, 0, 2550),
            ("second_pulse_phase_width", self.second_pulse_phase_width, 10, 0, 2550),
            ("discharge_time", self.discharge_time, 100, 0, 25500),
            ("pulse_amplitude_anode", self.pulse_amplitude_anode, 1, 0, 255),
            ("pulse_amplitude_cathode", self.pulse_amplitude_cathode, 1, 0, 255),
            ("pulse_duration", self.pulse_duration, 100, 100, 25500),
        ]

        # Loop through parameters to verify and call verify_step_min_max
        for param in verify_params:
            verify_step_min_max(*param)

        # Additional validation checks
        self._additional_checks()

    def _additional_checks(self) -> None:
        """Run additional checks to verify the values."""

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
                    "Expected pulse_amplitude_cathode to be 0 when biphasic is False "
                    + "(i.e. monophasic)"
                )

        sum_pulses = (
            self.pulse_delay
            + self.first_pulse_phase_width
            + self.pulse_interphase_interval
            + self.second_pulse_phase_width
            + self.discharge_time
        )
        if self.pulse_duration != sum_pulses:
            print(
                self.pulse_delay,
                self.first_pulse_phase_width,
                self.pulse_interphase_interval,
                self.second_pulse_phase_width,
                self.discharge_time,
            )
            raise ValueError(
                f"Expected pulse_duration ({self.pulse_duration} us) is not equal to "
                + f"the sum of independent pulse parts ({sum_pulses} us)."
            )


@dataclass
class PulseTrainParameters:
    """
    Data class to store parameters of a pulse train.

    :param number_of_pulses: Number of pulses in the train.
    :param frequency_of_pulses: Frequency of pulses.
    :param number_of_trains: Number of pulse trains.
    :param train_interval: Interval between trains.
    :param onset_jitter: Jitter in onset timing.
    :param discharge_time_extra: Interpulse discharge interval.
    """

    number_of_pulses: int = 20
    frequency_of_pulses: float = 1000.0
    number_of_trains: int = 1
    # train_interval: int = 1000
    onset_jitter: int = 1000
    discharge_time_extra: int = 100

    train_step_size_dict = {number_of_pulses: 1, discharge_time_extra: 100}

    def __post_init__(self) -> None:
        """Verifies the values after initialization."""
        self.verify_values()

    def verify_values(self) -> None:
        """Verifies the constraints for all parameters."""
        verify_step_min_max("number_of_pulses", self.number_of_pulses, 1, 0, 255)
        verify_step_min_max("number_of_trains", self.number_of_trains, 1, 1, 20)
        # verify_step_min_max("train_interval", self.train_interval,
        # 1000, 1000, 3000000)
        verify_step_min_max("onset_jitter", self.onset_jitter, 1000, 0, 2000000)
        verify_step_min_max(
            "discharge_time_extra", self.discharge_time_extra, 100, 0, 25500
        ),
        # TODO: check if 1/frequency_of_pulses is the same as pulse_duration, this
        #       should probably be done on the level of ConfigurationParameters

    def __setattr__(self, __name: str, __value: Any) -> None:
        super().__setattr__(__name, __value)
        self.verify_values()


@dataclass
class ViperBoxConfiguration:
    """
    Data class to store the configuration parameters for a ViperBox.

    :param probe: Probe index to be used (should be between 0 and 3).
    """

    probe: int = 0

    def __post_init__(self) -> None:
        """Verifies the probe number is within bounds."""
        self.verify_values()

    def __setattr__(self, __name: str, __value: Any) -> None:
        super().__setattr__(__name, __value)
        self.verify_values()

    def verify_values(self) -> None:
        if not 0 <= self.probe <= 3:
            raise ValueError("Probe value should be between 0 and 3.")


@dataclass
class StimulationSweepParameters:
    """
    Data class for creating a stimulation list. If repetitions is larger than one and
    randomize is True, then a randomized list is concatenated repetition times.

    :param stim_sweep_electrode_list: List of stimulation electrodes.
    :param rec_electrodes_list: List of recording electrodes.
    :param pulse_amplitudes: Tuple of three ints for setting amplitude min, max and step
    :param randomize: Boolean flag to indicate if stim_list need to be randomized.
    :param repetitions: The number of times stim_list should be repeated and shuffled.
    """

    stim_sweep_electrode_list: List[int] = field(default_factory=list)
    # rec_electrodes_list: List[int] = field(default_factory=list)
    pulse_amplitude_min: int = 0
    pulse_amplitude_max: int = 1
    pulse_amplitude_step: int = 1
    randomize: bool = False
    repetitions: int = 1

    # amplitude_list: List[int] = field(init=False)
    # stim_list: List[Tuple[int, int]] = field(init=False)

    def __post_init__(self):
        # Check if pulse_amplitudes is a tuple of three ints
        self.pulse_amplitude_min = int(self.pulse_amplitude_min)
        self.pulse_amplitude_max = int(self.pulse_amplitude_max)
        self.pulse_amplitude_step = int(self.pulse_amplitude_step)
        self.repetitions = int(self.repetitions)
        self.verify_values()

        if self.pulse_amplitude_min >= self.pulse_amplitude_max:
            logger.error(
                "Pulse amplitude min should be smaller than Pulse amplitude max"
            )

        self.pulse_amplitudes: Tuple[int, int, int] = (
            self.pulse_amplitude_min,
            self.pulse_amplitude_max,
            self.pulse_amplitude_step,
        )

        if self.pulse_amplitudes == []:
            logger.error("Check your values for pulse amplitudes")

        # Check if repetitions is 1 or more
        if self.repetitions < 1:
            raise ValueError("repetitions must be 1 or more.")

        # Create amplitude_list
        self.amplitude_list = list(
            range(
                self.pulse_amplitudes[0],
                self.pulse_amplitudes[1],
                self.pulse_amplitudes[2],
            )
        )

        # Create stim_list
        self.stim_list = [
            (x, y) for x in self.stim_sweep_electrode_list for y in self.amplitude_list
        ]

        # If randomize is True, shuffle stim_list
        if self.randomize:
            random.shuffle(self.stim_list)

        # If repetitions is larger than one, repeat and shuffle stim_list
        if self.repetitions > 1:
            combined_list = self.stim_list.copy()
            for _ in range(self.repetitions - 1):
                temp_list = self.stim_list.copy()
                random.shuffle(temp_list)
                combined_list.extend(temp_list)
            self.stim_list = combined_list

    def verify_values(self) -> None:
        """Verifies the constraints for all parameters."""
        verify_step_min_max("pulse_amplitude_min", self.pulse_amplitude_min, 1, 0, 255)
        verify_step_min_max("pulse_amplitude_max", self.pulse_amplitude_max, 1, 0, 255)
        verify_step_min_max(
            "pulse_amplitude_step", self.pulse_amplitude_step, 1, 0, 255
        )
        verify_step_min_max("repetitions", self.repetitions, 1, 0, 50)


@dataclass
class ConfigurationParameters:
    """
    Data class to store all the configuration parameters:
    - pulse shape
    - pulse train
    - stimulation electrodes
    - ViperBox

    :param pulse_shape_parameters: Object of PulseShapeParameters class.
    :param pulse_train_parameters: Object of PulseTrainParameters class.
    :param stim_electrode_list: List of electrodes to be stimulated.
    :param viperbox_configuration: Object of ViperBoxConfiguration class.
    """

    pulse_shape_parameters: PulseShapeParameters = field(
        default_factory=PulseShapeParameters
    )
    pulse_train_parameters: PulseTrainParameters = field(
        default_factory=PulseTrainParameters
    )
    viperbox_configuration: ViperBoxConfiguration = field(
        default_factory=ViperBoxConfiguration
    )
    stim_configuration: StimulationSweepParameters = field(
        default_factory=StimulationSweepParameters
    )
    stim_electrode_list: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Verifies the electrodes after initialization."""
        self.verify_electrodes()

    def verify_electrodes(self, num_electrodes=64) -> None:
        """Verifies the constraints for the list of electrodes."""
        electrodes_set = set(self.stim_electrode_list)
        if len(electrodes_set) == 0:
            logger.info("No electrodes were selected")
            return None
            # raise ValueError("Electrode list can't be empty")

        for elec in electrodes_set:
            if not 1 <= elec <= num_electrodes:
                raise ValueError(
                    f"Electrodes should have values between 1 and {num_electrodes}."
                )

    def get_SUConfig_pars(
        self, handle=None, probe=0, stim_unit=0, polarity=0
    ) -> List[Any]:
        """
        Generate and return stimulation unit parameters from all the configured
        parameters.

        :param handle: Hardware handle (default is None).
        :param probe: Probe index (default is 0).
        :param stim_unit: Stimulation unit index (default is 0).
        :param polarity: Polarity of the pulse (default is 0).
        :return: A list containing the SUConfig parameters that can be fed directly into
        NVP.writeSUConfiguration.
        """
        all_parameters = {
            **asdict(self.pulse_shape_parameters),
            **asdict(self.pulse_train_parameters),
        }

        if not handle:
            raise ValueError("No handle was passed")

        SU_params = [
            "number_of_pulses",
            "pulse_amplitude_anode",
            "pulse_amplitude_cathode",
            "pulse_duration",
            "pulse_delay",
            "first_pulse_phase_width",
            "pulse_interphase_interval",
            "second_pulse_phase_width",
            "discharge_time",
            "discharge_time_extra",
        ]

        SU_converted_params = [
            all_parameters.get(param, None) // verify_int_params[param][0]
            for param in SU_params
        ]

        SU_all_params = [
            handle,
            probe,
            stim_unit,
            polarity,
        ] + SU_converted_params

        return SU_all_params
        # return (
        #     handle,
        #     probe,
        #     stim_unit,
        #     polarity,
        #     all_parameters.get(
        #         "number_of_pulses", None
        #     ) // verify_int_params['number_of_pulses'][0],
        #     # // etc. necessary to convert human readable values to machine values
        #     all_parameters.get(
        #         "pulse_amplitude_anode", None
        #     ) // self.pulse_shape_parameters.pulse_amplitude_anode,
        #     all_parameters.get(
        #         "pulse_amplitude_cathode", None
        #     ) // self.pulse_shape_parameters.pulse_amplitude_cathode,
        #     all_parameters.get(
        #         "pulse_duration", None
        #     ) // self.pulse_shape_parameters.pulse_duration,
        #     all_parameters.get(
        #         "pulse_delay", None
        #     ) // self.pulse_shape_parameters.pulse_delay,
        #     all_parameters.get(
        #         "first_pulse_phase_width", None
        #     ) // self.pulse_shape_parameters.first_pulse_phase_width,
        #     all_parameters.get(
        #         "pulse_interphase_interval", None
        #     ) // self.pulse_shape_parameters.pulse_interphase_interval,
        #     all_parameters.get(
        #         "second_pulse_phase_width", None
        #     ) // self.pulse_shape_parameters.second_pulse_phase_width,
        #     all_parameters.get(
        #         "discharge_time", None
        #     ) // self.pulse_shape_parameters.discharge_time,
        #     all_parameters.get(
        #         "discharge_time_extra", None
        #     ) // self.pulse_train_parameters.discharge_time_extra,
        # )

    @property
    def stim_time(self):
        """Returns total stimulation time of one train in seconds."""
        total_stim_time = (
            self.pulse_shape_parameters.pulse_duration
            * self.pulse_train_parameters.number_of_pulses
        ) + self.pulse_shape_parameters.discharge_time_extra
        if self.pulse_train_parameters.number_of_trains > 0:
            return total_stim_time * self.pulse_train_parameters.number_of_trains / 1e6
        else:
            return total_stim_time / 1e6


if __name__ == "__main__":
    # Example usage:
    pulse_shape = PulseShapeParameters()
    pulse_train = PulseTrainParameters()
    electrodes = [1, 2, 3]
    viperbox = ViperBoxConfiguration()
    stim_configuration = StimulationSweepParameters(
        # stim_sweep_electrode_list=[1, 2],
        # rec_electrodes_list=[3, 4],
        # pulse_amplitudes=(1, 10, 2),
        # randomize=True,
        # repetitions=2,
    )
    # config = ConfigurationParameters(
    #     pulse_shape, pulse_train, viperbox, stim_configuration, electrodes
    # )

    config = ConfigurationParameters()

    print("config: ", config)

    test = config.get_SUConfig_pars(handle="no_box")
    print("SUConfig pars: ", test)
    # print(
    #     "StimulationSweepParameters.amplitude_list: ",
    #     config.stim_configuration.amplitude_list,
    # )
    # print("StimulationSweepParameters.stim_list: ",
    #       config.stim_configuration.stim_list)
    # print("total train time: ", config.stim_time)
