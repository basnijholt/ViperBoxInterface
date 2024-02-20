import json
import logging
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import PySimpleGUI as sg
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# matplotlib.use("TkAgg")

visibility_swap = True

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.FileHandler("logs/debug.log"), logging.StreamHandler()],
)
logging.getLogger("matplotlib.font_manager").disabled = True
# Create a file handler
# handler = logging.FileHandler("log.txt")


# stdout_handler = logging.StreamHandler(sys.stdout)
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# stdout_handler.setFormatter(formatter)
# stdout_handler.setLevel(logging.DEBUG)  # Set the level for stdout logging
# logger.addHandler(stdout_handler)


def collapse(layout, key):
    return sg.pin(
        sg.Column(
            layout,
            key=key,
            visible=manual_stim,
            element_justification="r",
            expand_x=True,
        )
    )


def LEDIndicator(key=None, radius=15):
    return sg.Graph(
        canvas_size=(radius, radius),
        graph_bottom_left=(-radius, -radius),
        graph_top_right=(radius, radius),
        pad=(0, 0),
        key=key,
    )


def SetLED(window, key, status):
    graph = window[key]
    graph.erase()
    if status is True:
        graph.draw_circle((0, 0), 12, fill_color="green", line_color="green")
    elif status is None:
        graph.draw_circle((0, 0), 12, fill_color="red", line_color="red")
    elif status is False:
        graph.draw_circle((0, 0), 12, fill_color="gray", line_color="gray")


sg.theme("SystemDefaultForReal")

# ------------------------------------------------------------------
# CF STIMULATION PULSE FRAME


def generate_plot(
    # biphasic: int = 1,
    pulse_delay: int = 0,
    first_pulse_phase_width: int = 170,
    pulse_interphase_interval: int = 60,
    second_pulse_phase_width: int = 170,
    discharge_time: int = 200,
    pulse_amplitude_anode: int = 1,
    pulse_amplitude_cathode: int = 1,
    # pulse_amplitude_equal: int = 0,
    pulse_duration: int = 600,
):
    # if bool(pulse_amplitude_equal):
    #     pulse_amplitude_cathode = pulse_amplitude_anode
    # if not bool(biphasic):
    #     pulse_amplitude_cathode = 0
    time = np.linspace(0, pulse_duration, pulse_duration)
    current = np.zeros_like(time)
    tp1 = pulse_delay
    tp2 = tp1 + first_pulse_phase_width
    tp3 = tp2 + pulse_interphase_interval
    tp4 = tp3 + second_pulse_phase_width
    tp5 = tp4 + discharge_time
    current[(time >= 0) & (time <= tp1)] = 0
    current[(time > tp1) & (time <= tp2)] = pulse_amplitude_anode
    current[(time > tp2) & (time <= tp3)] = 0
    current[(time > tp3) & (time <= tp4)] = -pulse_amplitude_cathode
    current[(time > tp4) & (time <= tp5)] = 0

    fig = matplotlib.figure.Figure(figsize=(4, 3), dpi=100)
    ax = fig.add_subplot(111)
    fig.get_axes()[0].set_xlabel("Time [μs]")
    fig.get_axes()[0].set_ylabel("Pulse amplitude [μA]")
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.plot(time, current)
    fig.tight_layout()
    return fig


def draw_figure(canvas, figure):
    if not hasattr(draw_figure, "canvas_packed"):
        draw_figure.canvas_packed = {}
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    widget = figure_canvas_agg.get_tk_widget()
    if widget not in draw_figure.canvas_packed:
        draw_figure.canvas_packed[widget] = figure
        widget.pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    try:
        draw_figure.canvas_packed.pop(figure_agg.get_tk_widget())
    except Exception as e:
        print(f"Error removing {figure_agg} from list", e)
    plt.close("all")


plot_frame = sg.Frame(
    "Pulse preview",
    [
        [sg.Canvas(key="-CANVAS-")],
        [sg.Button("Reload")],
    ],
    size=(420, 360),
    visible=visibility_swap,
)

# ------------------------------------------------------------------
# CF: VIPERBOX CONTROL FRAME

viperbox_control_frame = sg.Column(
    # "Viperbox connection",
    # [
    [
        [sg.VPush()],
        [
            sg.Push(),
            sg.Column(
                [
                    [
                        sg.Text("ViperBox connected", size=(20, 0)),
                        LEDIndicator("led_connect_probe"),
                    ],
                    [
                        sg.Button("Connect", key="button_connect"),
                        sg.Button("Disconnect", key="button_disconnect"),
                    ],
                ],
            ),
            sg.Push(),
        ],
        [sg.VPush()],
    ],
    # ],
    expand_y=True,
)

viperbox_recording_settings_frame = sg.Column(
    # "ViperBox control",
    [
        [
            sg.Text("Subject"),
            sg.Input("Recording", key="input_filename", size=(15, 1)),
            sg.Button("Change folder", key="button_select_recording_folder"),
        ],
        [
            sg.Button("Start rec", size=(10, 1), key="button_rec", disabled=False),
            sg.Button("Stop rec", size=(10, 1), key="button_stop"),
            sg.Button(
                "Stimulate",
                size=(10, 1),
                key="button_stim",
                disabled=True,
                tooltip="Start recording before stimulating",
            ),
        ],
        [
            sg.Column(
                [
                    [
                        sg.Text("Recording status:"),
                        LEDIndicator("led_rec"),
                    ],
                ]
            ),
        ],
    ],
    expand_x=True,
    element_justification="c",
)

open_ephys_frame = sg.Frame(
    "Open ephys data viewer",
    [[sg.Button("Start Open Ephys", key="button_start_oe")]],
    expand_x=True,
)

# ------------------------------------------------------------------
# CF: GAIN AND REFERENCE FRAME

ref_MAX_COL = 8
reference_switch_matrix = ["off" for _ in range(ref_MAX_COL + 1)]
reference_switch_matrix[8] = "on"
reference_button_matrix = [
    sg.Button(
        f"{i+1}",
        size=(2, 1),
        key=(f"reference_{i}"),
        pad=(1, 1),
        button_color="light gray",
        disabled=False,
    )
    for i in range(ref_MAX_COL)
]
reference_button_matrix.append(
    sg.Button(
        "B",
        size=(10, 1),
        key=(f"reference_{8}"),
        pad=(1, 1),
        button_color="red",
        disabled=False,
    )
)
reference_button_matrix = [reference_button_matrix]

gain_MAX_COL = 4
gain_switch_matrix = ["off" for _ in range(gain_MAX_COL)]
gain_switch_matrix[0] = "on"
gain = 0
gain_dict = {
    "x60": 0,
    "x16": 1,
    "x12": 2,
    "x0.16": 3,
}
gain_button_matrix = [
    [
        sg.Button(
            i,
            size=(8, 1),
            key=(f"gain_{j}"),
            pad=(1, 1),
            button_color="red" if i == "x60" else "light gray",
            disabled=False,
        )
        for i, j in gain_dict.items()
    ]
]

reference_frame = sg.Column(
    # "Reference selection",
    [[sg.Text("Ref. selection", size=(10, 0)), sg.Column(reference_button_matrix)]],
    expand_x=True,
)

gain_frame = sg.Column(
    # "Gain selection",
    [[sg.Text("Gain selection", size=(10, 0)), sg.Column(gain_button_matrix)]],
    expand_x=True,
    vertical_alignment="bottom",
)

upload_rec_button = sg.Button(
    "Recording settings", key="upload_recording_settings", disabled=False
)

upload_stim_button = sg.Button(
    "Stimulation settings", key="upload_stimulation_settings", disabled=False
)

recording_settings_frame = sg.Frame(
    "Recording settings",
    [
        [reference_frame],
        [gain_frame],
    ],
    expand_x=True,
    # expand_y=True,
)

upload_settings_frame = sg.Column(
    # "Upload settings to ViperBox",
    [[sg.Text("Upload settings to ViperBox")], [upload_rec_button, upload_stim_button]],
    expand_x=True,
    element_justification="c",
)


def toggle_1d_color(event, reference_switch_matrix):
    row = int(event[-1])
    # print(reference_switch_matrix)

    if reference_switch_matrix[row] == "off":
        reference_switch_matrix[row] = "on"
        return "red"
    else:
        reference_switch_matrix[row] = "off"
        # print(
        #     "reference_switch_matrix.count('off') :",
        #     reference_switch_matrix.count("off"),
        # )
        if reference_switch_matrix.count("off") == 9:
            logger.warning("At least one reference needs to be selected.")
            reference_switch_matrix[row] = "on"
            return "red"
        return "light gray"


def toggle_gain_color(event, gain_switch_matrix):
    row = int(event[-1])

    gain_switch_matrix = ["off"] * 4
    gain_switch_matrix[row] = "on"
    return "red"


def get_references(reference_switch_matrix):
    bin_input_list = "".join(
        ["1" if item == "on" else "0" for item in reference_switch_matrix]
    )
    ref_integer = int(bin_input_list, 2)
    # if ref_integer == 0:
    #     logger.warning("At least one reference needs to be selected.")
    #     asdfasdf
    return ref_integer


# ------------------------------------------------------------------
# CF: ELECTRODE SELECTION FRAME

MAX_ROWS = 15
MAX_COL = 4

electrode_switch_matrix = [["on" for i in range(MAX_COL)] for j in range(MAX_ROWS)]
electrode_button_matrix = [
    [
        sg.Button(
            f"{i*MAX_ROWS+j+1}",
            size=(2, 1),
            key=(f"el_button_{i*MAX_ROWS+j+1}"),
            pad=(10, 1),
            button_color="red",
        )
        for i in range(MAX_COL)
    ]
    for j in range(MAX_ROWS)
]
electrode_button_matrix = electrode_button_matrix[::-1]
print(type(electrode_button_matrix))
electrode_frame = sg.Frame(
    "Stimulation electrode selection",
    [
        [sg.Column(electrode_button_matrix)],
        [
            sg.Column(
                [
                    [
                        sg.Button(
                            "All",
                            size=(4, 0),
                            expand_x=True,
                            key="button_all",
                            button_color="red",
                        ),
                        sg.Button(
                            "None", size=(4, 0), expand_x=True, key="button_none"
                        ),
                    ]
                ],
                expand_x=True,
            )
        ],
    ],
    expand_y=True,
)


def toggle_2d_color(event, electrode_switch_matrix):
    electrode = int(event[10:])
    row = (electrode - 1) % MAX_ROWS
    col = (electrode - 1) // MAX_ROWS

    if electrode_switch_matrix[row][col] == "off":
        electrode_switch_matrix[row][col] = "on"
        return "red"
    else:
        electrode_switch_matrix[row][col] = "off"
        return "light gray"


def get_electrodes(electrode_switch_matrix, save_purpose=False):
    rows, cols = np.where(np.asarray(electrode_switch_matrix) == "on")
    if save_purpose:
        electrode_list = [str(i * MAX_ROWS + j + 1) for i, j in zip(cols, rows)]
    else:
        electrode_list = [i * MAX_ROWS + j + 1 for i, j in zip(cols, rows)]
    electrode_list.sort()
    return electrode_list


def set_reference_matrix(electrode_list):
    electrode_switch_matrix = [["off" for i in range(MAX_COL)] for j in range(MAX_ROWS)]
    for electrode in electrode_list:
        row = (int(electrode) - 1) % MAX_ROWS
        col = (int(electrode) - 1) // MAX_ROWS
        electrode_switch_matrix[row][col] = "on"
    return electrode_switch_matrix


# ------------------------------------------------------------------
# CF: LOG FRAME

log_frame = sg.Frame(
    "Log",
    [
        [
            sg.Multiline(
                key="mul_log",
                expand_y=True,
                expand_x=True,
                autoscroll=True,
                horizontal_scroll=True,
                disabled=True,
                font=("Cascadia Mono", 8),
                default_text="Initializing ViperBox...",
            )
        ],
    ],
    size=(420, 200),
    expand_y=True,
    expand_x=True,
)

# ------------------------------------------------------------------
# CF: STIMULATION SETTINGS FRAME

unit_h, unit_w = (4, 1)
inpsize_w, inpsize_h = (10, 1)

# stimulation_settings = sg.Frame(
#     "Pre-load settings",
#     [
#         [
#             sg.Button(
#                 "Select settings folder",
#                 key="button_select_settings_folder",
#                 expand_x=True,
#             )
#         ],
#         [
#             sg.Text("Filter:"),
#             sg.Input(
#                 "",
#                 size=(15, 1),
#                 key="input_filter_name",
#                 # enable_events=True,
#                 expand_x=True,
#             ),
#         ],
#         [
#             sg.Listbox(
#                 size=(10, 6),
#                 key="listbox_settings",
#                 expand_y=True,
#                 expand_x=True,
#                 values=settings_list,
#                 enable_events=True,
#             ),
#         ],
#         [
#             sg.Button("Save settings", size=(10, 1), key="button_save_set"),
#             sg.Input("sett_name", size=(15, 1), key="input_set_name"),
#         ],
#         [
#             sg.Button("Load", size=(10, 1), key="button_load_set"),
#             sg.Button("Delete", size=(10, 1), key="button_del_set"),
#         ],
#     ],
#     expand_x=True,
#     expand_y=True,
#     vertical_alignment="t",
#     visible=False,
# )


def save_settings(location, filename, settings):
    existing_settings = load_settings_folder(location)
    answer = "OK"
    if filename in existing_settings:
        answer = sg.popup_ok_cancel(
            f'Setting "{filename}" already exists, if you want to continue, press OK'
        )
    if answer == "OK":
        filename = filename + ".cfg"
        settings_save = settings.copy()
        delete = [
            # "led_connect_hardware",
            # "led_connect_BS",
            "led_connect_probe",
            "input_filename",
            "led_rec",
            "checkbox_rec_wo_stim",
            # "input_filter_name",
            # "listbox_settings",
            "input_set_name",
            "-CANVAS-",
            "mul_log",
        ]
        for key in delete:
            del settings_save[key]
        with open(location + "\\" + filename, "w") as f:
            json.dump(settings_save, f)


def read_saved_settings(location, filename):
    full_path = Path.joinpath(Path(location), filename + ".cfg")
    with open(full_path, "r") as f:
        return json.load(f)


def load_settings_folder(location):
    settings_list = [path.stem for path in Path(location).glob("*.cfg")]
    return settings_list


def update_settings_listbox(settings_folder_path):
    # settings_list = load_settings_folder(settings_folder_path)
    # window["listbox_settings"].update(settings_list)
    pass


# ------------------------------------------------------------------
# CF: PULSE SHAPE FRAME

manual_stim = True
pulse_shape_col_settings = sg.Column(
    [
        # [
        #     sg.Text("Biphasic / Monophasic"),
        #     sg.Drop(
        #         key="biphasic",
        #         size=(inpsize_w - 2, inpsize_h),
        #         values=("Biphasic", "Monophasic"),
        #         auto_size_text=True,
        #         default_value="Biphasic",
        #         # enable_events=True,
        #     ),
        #     sg.T(" ", size=(unit_h, unit_w)),
        # ],
        [
            sg.Text("Pulse duration"),
            sg.Input(
                600,
                size=(inpsize_w, inpsize_h),
                key="pulse_duration",
                # enable_events=True,
            ),
            sg.T("μSec", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("Pulse delay"),
            sg.Input(
                0,
                size=(inpsize_w, inpsize_h),
                key="pulse_delay",
                # enable_events=True
            ),
            sg.T("μSec", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("1st pulse phase width"),
            sg.Input(
                170,
                size=(inpsize_w, inpsize_h),
                key="first_pulse_phase_width",
                # enable_events=True,
            ),
            sg.T("μSec", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("Pulse interphase interval"),
            sg.Input(
                60,
                size=(inpsize_w, inpsize_h),
                key="pulse_interphase_interval",
                # enable_events=True,
            ),
            sg.T("μSec", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("2nd pulse phase width"),
            sg.Input(
                170,
                size=(inpsize_w, inpsize_h),
                key="second_pulse_phase_width",
                # enable_events=True,
            ),
            sg.T("μSec", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("Interpulse interval (discharge)"),
            sg.Input(
                200,
                size=(inpsize_w, inpsize_h),
                key="discharge_time",
                # enable_events=True,
            ),
            sg.T("μSec", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("Pulse amplitude anode"),
            sg.Input(
                5,
                size=(inpsize_w, inpsize_h),
                key="pulse_amplitude_anode",
                # enable_events=True,
            ),
            sg.T("μA", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("Pulse amplitude cathode"),
            sg.Input(
                5,
                size=(inpsize_w, inpsize_h),
                key="pulse_amplitude_cathode",
                # enable_events=True,
            ),
            sg.T("μA", size=(unit_h, unit_w)),
        ],
    ],
    element_justification="r",
    expand_x=True,
)
pulse_shape_col_el_frame = [
    [
        sg.Text("Pulse amplitude anode"),
        sg.Input(
            5,
            size=(inpsize_w, inpsize_h),
            key="pulse_amplitude_anode",
            # enable_events=True,
        ),
        sg.T("μA", size=(unit_h, unit_w)),
    ],
    [
        sg.Text("Pulse amplitude cathode"),
        sg.Input(
            5,
            size=(inpsize_w, inpsize_h),
            key="pulse_amplitude_cathode",
            # enable_events=True,
        ),
        sg.T("μA", size=(unit_h, unit_w)),
    ],
    # [
    #     sg.T("Pulse amplitude equal"),
    #     sg.Checkbox(
    #         "",
    #         key="pulse_amplitude_equal",
    #         size=(inpsize_w - 4, inpsize_h),
    #         enable_events=True,
    #     ),
    #     sg.T(
    #         " ",
    #         size=(unit_h, unit_w),
    #     ),
    # ],
]

pulse_shape_frame = sg.Frame(
    "Pulse shape parameters",
    [
        [pulse_shape_col_settings],
        # [collapse(pulse_shape_col_el_frame, "pulse_shape_col_el_frame")],
        # [pulse_shape_col_el_frame],
    ],
    element_justification="r",
    expand_x=True,
)

# ------------------------------------------------------------------
# CF: PULSE TRAIN FRAME

pulse_train_frame = sg.Frame(
    "Pulse train parameters",
    [
        [
            sg.Text("Number of pulses"),
            sg.Input(
                20,
                size=(inpsize_w, inpsize_h),
                key="number_of_pulses",
                # enable_events=True,
            ),
            sg.T(" ", size=(unit_h, unit_w)),
        ],
        # [
        #     sg.Text("Frequency of pulses"),
        #     sg.Input(
        #         200,
        #         size=(inpsize_w, inpsize_h),
        #         key="frequency_of_pulses",
        #         # enable_events=True,
        #     ),
        #     sg.T("Hz", size=(unit_h, unit_w)),
        # ],
        # [
        #     sg.Text("Number of trains"),
        #     sg.Input(
        #         5,
        #         size=(inpsize_w, inpsize_h),
        #         key="number_of_trains",
        #         # enable_events=True,
        #     ),
        #     sg.T(" ", size=(unit_h, unit_w)),
        # ],
        [
            sg.Text("Train interval (discharge)"),
            sg.Input(
                1000,
                size=(inpsize_w, inpsize_h),
                key="discharge_time_extra",
                # enable_events=True,
            ),
            sg.T("mSec", size=(unit_h, unit_w)),
        ],
        # [
        #     sg.Text("On-set onset_jitter"),
        #     sg.Input(
        #         0,
        #         size=(inpsize_w, inpsize_h),
        #         key="onset_jitter",
        #         # enable_events=True
        #     ),
        #     sg.T("Sec", size=(unit_h, unit_w)),
        # ],
    ],
    element_justification="r",
    expand_x=True,
)


# ------------------------------------------------------------------
# CF: PARAMETER SWEEP FRAME

parameter_sweep = sg.Frame(
    "Stimulation sweep parameters",
    [
        [
            sg.Text("Pulse amplitude min"),
            sg.Input(
                1,
                size=(inpsize_w, inpsize_h),
                key="pulse_amplitude_min",
                # enable_events=True,
            ),
            sg.T("μA", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("Pulse amplitude max"),
            sg.Input(
                20,
                size=(inpsize_w, inpsize_h),
                key="pulse_amplitude_max",
                # enable_events=True,
            ),
            sg.T("μA", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("Pulse amplitude step"),
            sg.Input(
                1,
                size=(inpsize_w, inpsize_h),
                key="pulse_amplitude_step",
                # enable_events=True,
            ),
            sg.T("μA", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("Repetitions"),
            sg.Input(
                1,
                size=(inpsize_w, inpsize_h),
                key="repetitions",
                # enable_events=True
            ),
            sg.T(" ", size=(unit_h, unit_w)),
        ],
        [sg.Checkbox("Randomize", key="randomize")],
    ],
    element_justification="r",
    expand_x=True,
    visible=not manual_stim,
    key="key_parameter_sweep",
)


menu_def = [["&Application"]]
layout = [[sg.Menu(menu_def, key="-MENU-", tearoff=False)]]

# ------------------------------------------------------------------
# INTEGRATION OF COMPONENTS

# col_settings = sg.Column(
#     [
#         [viperbox_control_frame],
#         [upload_settings_frame],
#         [viperbox_recording_settings_frame],
#         [recording_settings_frame],
#         [open_ephys_frame],
#     ],
#     k="col_settings",
#     vertical_alignment="t",
#     expand_y=True,
# )

col_el_frame = sg.Column(
    [[electrode_frame]],
    k="col_el_frame",
    expand_y=True,
    visible=visibility_swap,
)

col_params = sg.Column(
    [[pulse_shape_frame], [pulse_train_frame], [parameter_sweep]],
    k="col_params",
    vertical_alignment="t",
    visible=visibility_swap,
)
col_plot = sg.Column(
    [
        [plot_frame],
    ],
    k="col_plot",
    vertical_alignment="t",
)
col_log = sg.Column(
    [[log_frame]], k="col_log", vertical_alignment="t", expand_x=True, expand_y=True
)
for sublayout in [
    viperbox_control_frame,
    upload_settings_frame,
    viperbox_recording_settings_frame,
    col_el_frame,
    col_params,
    col_plot,
]:
    print(sublayout)
layout += [
    [
        sg.Column(
            [
                [
                    sg.Frame(
                        "ViperBox control",
                        [
                            [
                                viperbox_control_frame,
                                sg.VSeparator(),
                                viperbox_recording_settings_frame,
                                sg.VSeparator(),
                                upload_settings_frame,
                            ],
                        ],
                        expand_y=True,
                        expand_x=True,
                        element_justification="c",
                    )
                ],
                [
                    sg.Column(
                        # "Stimulation settings",
                        [
                            [
                                sg.Column([[recording_settings_frame], [col_plot]]),
                                col_params,
                                col_el_frame,
                            ]
                        ],
                    )
                ],
            ]
        )
    ]
]

window = sg.Window(
    "ViperBox Control",
    layout,
    finalize=False,
)

url = "http://127.0.0.1:8000/"
tmp_path = ""
_, values = window.read(timeout=0)
SetLED(window, "led_connect_probe", False)
SetLED(window, "led_rec", False)
fig = generate_plot()
figure_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)

if __name__ == "__main__":
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "button_connect":
            # window["led_connect_probe"].update("on")
            data = {"probe_list": "1", "emulation": "True", "boxless": "True"}
            response = requests.post(url + "connect", json=data)
            print(response.text)
        elif event == "button_disconnect":
            response = requests.post(url + "disconnect")
        elif event == "button_select_recording_folder":
            tmp_path = sg.popup_get_folder("Select recording folder")
            logger.info(f"Updated recordings file path to: {tmp_path}")
        elif event == "button_rec":
            if tmp_path:
                data = {"filename": f"{tmp_path}/{values['input_filename']}"}
            else:
                data = {"filename": f"{values['input_filename']}"}
            logger.info("Start recording button pressed")
            response = requests.post(url + "start_recording", json=data)
            response_dct = json.loads(response.text)
            print(response_dct)
            if response_dct["result"]:
                print("recording started")
                window["button_stim"].update(disabled=False)
            else:
                sg.popup_ok(f"{response_dct['feedback']}")
        elif event == "button_stop":
            logger.info("Stop recording button pressed")
            response = requests.post(url + "stop_recording")
            response_dct = json.loads(response.text)
            print(response_dct)
            if response_dct["result"]:
                print("recording stopped")
                window["button_stim"].update(disabled=True)
            else:
                sg.popup_ok(f"{response_dct['feedback']}")
        elif event[:3] == "el_":
            window[event].update(
                button_color=toggle_2d_color(event, electrode_switch_matrix)
            )
        elif event == "button_all":
            electrode_switch_matrix = [
                ["on" for i in range(MAX_COL)] for j in range(MAX_ROWS)
            ]
            for electrode in range(1, 61):
                window[f"el_button_{electrode}"].update(button_color="red")
        elif event == "button_none":
            electrode_switch_matrix = [
                ["off" for i in range(MAX_COL)] for j in range(MAX_ROWS)
            ]
            for electrode in range(1, 61):
                window[f"el_button_{electrode}"].update(button_color="light gray")
        elif event[:3] == "ref":
            window[event].update(
                button_color=toggle_1d_color(event, reference_switch_matrix)
            )
        elif event[:3] == "gai":
            window["gain_0"].update(button_color="light grey")
            window["gain_1"].update(button_color="light grey")
            window["gain_2"].update(button_color="light grey")
            window["gain_3"].update(button_color="light grey")
            window[event].update(
                button_color=toggle_gain_color(event, gain_switch_matrix)
            )
            gain = int(event[-1])
        elif event == "Reload":
            # Implementation from https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib_Browser.py
            if figure_agg:
                delete_figure_agg(figure_agg)
            plot_vals = {k: int(values[k]) for k in generate_plot.__annotations__}
            fig = generate_plot(**plot_vals)
            figure_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
