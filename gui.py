import PySimpleGUI as sg

# from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

matplotlib.use("TkAgg")
import datetime
from viperboxcontrol import ViperBoxControl
from parameters import (
    ConfigurationParameters,
    PulseShapeParameters,
    PulseTrainParameters,
    ViperBoxConfiguration,
    StimulationSweepParameters,
    verify_int_params,
)
import logging
import logging.handlers
import os
from os.path import basename
import json
from pathlib import Path
import requests
import threading
import sys
import time
import socket
import subprocess

no_box, emulated = False, False

batch_script_path = os.getcwd() + "\\update.bat"
print(batch_script_path)

recording_folder_path = os.getcwd() + "\\Recordings"
settings_folder_path = os.getcwd() + "\\Settings"

settings_list = []

LOG_FILENAME = "ViperBoxInterface.log"
open(LOG_FILENAME, "w").close()
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.INFO,
    # stream=sys.stdout,
    format="%(levelname)-8s - %(asctime)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

# # Create a logger
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# # Create a rotating file handler that logs debug and higher level messages
# file_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1e6, backupCount=10)
# file_handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(levelname)-8s %(asctime)s - %(name)s - %(message)s', '%H:%M:%S')
# file_handler.setFormatter(formatter)
# # Add the file handler to the logger
# logger.addHandler(file_handler)
logging.getLogger("matplotlib.font_manager").setLevel(logging.CRITICAL)

sg.theme("SystemDefaultForReal")

toggle_btn_off = b"iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeT\
    AAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRx\
    Aor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA1\
    4GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8\
    PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yM\
    p/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8Pt\
    kSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59Ri\
    CEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9c\
    uiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8\
    hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdG\
    RpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt\
    631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcm\
    rKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFU\
    rXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9e\
    u39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQm\
    ARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlg\
    yg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljc\
    sm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5\
    ErkJggg=="
toggle_btn_on = b"iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTA\
    AAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP\
    4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQ\
    gZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSS\
    kyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pq\
    cKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLIC\
    yBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3N\
    jEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9k\
    K5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6T\
    YMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNEx\
    WWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3\
    V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo\
    2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPD\
    VYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX7\
    2TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5\
    p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1An\
    YoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7z\
    nZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC"


def start_eo_acquire(start_oe=False):
    try:
        r = requests.get("http://localhost:37497/api/status")
        if r.json()["mode"] != "ACQUIRE":
            r = requests.put(
                "http://localhost:37497/api/status", json={"mode": "ACQUIRE"}
            )
    except Exception as e:
        if start_oe:
            os.startfile("C:\Program Files\Open Ephys\open-ephys.exe")
        else:
            logger.warning(
                "Failed to set up Open Ephys correctly, trying to start it now"
            )


def empty_socket():
    serverAddressPort = ("127.0.0.1", 9001)
    MULTICAST_TTL = 2
    UDPClientSocket: socket.socket = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
    )

    UDPClientSocket.setsockopt(
        socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL
    )
    databuffer = np.ones((30, 500), dtype="uint16")

    while True:
        global stop_threads
        UDPClientSocket.sendto(databuffer, serverAddressPort)
        time.sleep(0.1)
        if stop_threads:
            break


stop_threads = False
threading.Thread(target=empty_socket).start()
threading.Thread(target=start_eo_acquire, args=(True,)).start()
print("EO started")


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


# ------------------------------------------------------------------
# CF STIMULATION PULSE FRAME


def generate_plot(
    biphasic: int = 1,
    pulse_delay: int = 0,
    first_pulse_phase_width: int = 170,
    pulse_interphase_interval: int = 60,
    second_pulse_phase_width: int = 170,
    discharge_time: int = 200,
    pulse_amplitude_anode: int = 1,
    pulse_amplitude_cathode: int = 1,
    pulse_amplitude_equal: int = 0,
    pulse_duration: int = 600,
):
    if bool(pulse_amplitude_equal):
        pulse_amplitude_cathode = pulse_amplitude_anode
    if not bool(biphasic):
        pulse_amplitude_cathode = 0
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
    expand_x=True,
    visible=False,
)

# ------------------------------------------------------------------
# CF: VIPERBOX CONTROL FRAME

viperbox_control_frame = sg.Frame(
    "Viperbox control",
    [
        [
            sg.Text("Hardware connection", size=(15, 0)),
            LEDIndicator("led_connect_hardware"),
        ],
        [sg.Text("BS connection", size=(15, 0)), LEDIndicator("led_connect_BS")],
        [sg.Text("Probe connection", size=(15, 0)), LEDIndicator("led_connect_probe")],
        [
            sg.Button("Reconnect", key="button_connect"),
            sg.Button("Disconnect", key="button_disconnect"),
        ],
        [sg.HorizontalSeparator("light gray")],
        [sg.Text("Subject"), sg.Input("Recording", key="input_filename", size=(15, 1))],
        [
            sg.Text(
                f"Saving in {basename(recording_folder_path)}",
                key="current_folder",
                size=(25, 1),
            ),
            sg.Button("Change folder", key="button_select_recording_folder"),
        ],
        # [sg.HorizontalSeparator("light gray")],
        # [
        #     sg.Text("Manual stimulation"),
        #     sg.Button(
        #         image_data=toggle_btn_off,
        #         key="button_toggle_stim",
        #         button_color=(sg.theme_background_color(), sg.theme_background_color()),
        #         border_width=0,
        #         metadata=False,
        #     ),
        #     sg.Text("Current amplitude sweep"),
        # ],
        [
            sg.Button("Start", size=(10, 1), key="button_start"),
            sg.Button("Stop", size=(10, 1), key="button_stop"),
            sg.Checkbox(
                "Record without stimulation",
                key="checkbox_rec_wo_stim",
                default=True,
                visible=False,
            ),
        ],
        [
            sg.Text("Recording status:"),
            LEDIndicator("led_rec"),
        ],
    ],
    # size=(400, 170),
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
        key=(f"reference_{i+1}"),
        pad=(1, 1),
        button_color="light gray",
    )
    for i in range(ref_MAX_COL)
]
reference_button_matrix.append(
    sg.Button(
        "B",
        size=(10, 1),
        key=(f"reference_{9}"),
        pad=(1, 1),
        button_color="red",
    )
)
reference_button_matrix = [reference_button_matrix]

gain_MAX_COL = 4
gain_switch_matrix = ["off" for _ in range(gain_MAX_COL)]
gain_switch_matrix[0] = "on"
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
        )
        for i, j in gain_dict.items()
    ]
]

reference_frame = sg.Frame(
    "Reference selection", reference_button_matrix, expand_y=True
)
gain_frame = sg.Frame("Gain selection", gain_button_matrix, expand_x=True)
update_button = sg.Button("Update ViperBox", key="update_viperbox_settings")
recording_frame = sg.Frame(
    "Recording settings",
    [[reference_frame], [gain_frame], [update_button]],
    expand_x=True,
)


def toggle_1d_color(event, reference_switch_matrix):
    row = int(event[-1]) - 1

    if reference_switch_matrix[row] == "off":
        reference_switch_matrix[row] = "on"
        return "red"
    else:
        reference_switch_matrix[row] = "off"
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
    return int(bin_input_list, 2)


# ------------------------------------------------------------------
# CF: ELECTRODE SELECTION FRAME

MAX_ROWS = 15
MAX_COL = 4

electrode_switch_matrix = [["off" for i in range(MAX_COL)] for j in range(MAX_ROWS)]
electrode_button_matrix = [
    [
        sg.Button(
            f"{i*MAX_ROWS+j+1}",
            size=(2, 1),
            key=(f"el_button_{i*MAX_ROWS+j+1}"),
            pad=(10, 1),
            button_color="light gray",
        )
        for i in range(MAX_COL)
    ]
    for j in range(MAX_ROWS)
]
electrode_button_matrix = electrode_button_matrix[::-1]
electrode_frame = sg.Frame(
    "Stimulation electrode selection", electrode_button_matrix, expand_y=True
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
                font=("Cascadia Mono", 8),
                default_text="Initializing ViperBox...",
            )
        ],
    ],
    size=(400, 280),
    # expand_y=True,
    expand_x=True,
)

# ------------------------------------------------------------------
# CF: STIMULATION SETTINGS FRAME

unit_h, unit_w = (4, 1)
inpsize_w, inpsize_h = (10, 1)

stimulation_settings = sg.Frame(
    "Pre-load settings",
    [
        [
            sg.Button(
                "Select settings folder",
                key="button_select_settings_folder",
                expand_x=True,
            )
        ],
        [
            sg.Text("Filter:"),
            sg.Input(
                "",
                size=(15, 1),
                key="input_filter_name",
                # enable_events=True,
                expand_x=True,
            ),
        ],
        [
            sg.Listbox(
                size=(10, 6),
                key="listbox_settings",
                expand_y=True,
                expand_x=True,
                values=settings_list,
                enable_events=True,
            ),
        ],
        [
            sg.Button("Save settings", size=(10, 1), key="button_save_set"),
            sg.Input("sett_name", size=(15, 1), key="input_set_name"),
        ],
        [
            sg.Button("Load", size=(10, 1), key="button_load_set"),
            sg.Button("Delete", size=(10, 1), key="button_del_set"),
        ],
    ],
    expand_x=True,
    # size=(185,60),
    expand_y=True,
    vertical_alignment="t",
    visible=False,
)


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
            "led_connect_hardware",
            "led_connect_BS",
            "led_connect_probe",
            "input_filename",
            "led_rec",
            "checkbox_rec_wo_stim",
            "input_filter_name",
            "listbox_settings",
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
    settings_list = load_settings_folder(settings_folder_path)
    window["listbox_settings"].update(settings_list)


# ------------------------------------------------------------------
# CF: PULSE SHAPE FRAME

manual_stim = True
pulse_shape_col1 = sg.Column(
    [
        [
            sg.Text("Biphasic / Monophasic"),
            sg.Drop(
                key="biphasic",
                size=(inpsize_w - 2, inpsize_h),
                values=("Biphasic", "Monophasic"),
                auto_size_text=True,
                default_value="Biphasic",
                # enable_events=True,
            ),
            sg.T(" ", size=(unit_h, unit_w)),
        ],
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
    ],
    element_justification="r",
    expand_x=True,
)
pulse_shape_col2 = [
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
    [
        sg.T("Pulse amplitude equal"),
        sg.Checkbox(
            "",
            key="pulse_amplitude_equal",
            size=(inpsize_w - 4, inpsize_h),
            enable_events=True,
        ),
        sg.T(
            " ",
            size=(unit_h, unit_w),
        ),
    ],
]

pulse_shape_frame = sg.Frame(
    "Pulse shape parameters",
    [[pulse_shape_col1], [collapse(pulse_shape_col2, "pulse_shape_col2")]],
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
        [
            sg.Text("Frequency of pulses"),
            sg.Input(
                200,
                size=(inpsize_w, inpsize_h),
                key="frequency_of_pulses",
                # enable_events=True,
            ),
            sg.T("Hz", size=(unit_h, unit_w)),
        ],
        [
            sg.Text("Number of trains"),
            sg.Input(
                5,
                size=(inpsize_w, inpsize_h),
                key="number_of_trains",
                # enable_events=True,
            ),
            sg.T(" ", size=(unit_h, unit_w)),
        ],
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
        [
            sg.Text("On-set onset_jitter"),
            sg.Input(
                0,
                size=(inpsize_w, inpsize_h),
                key="onset_jitter",
                # enable_events=True
            ),
            sg.T("Sec", size=(unit_h, unit_w)),
        ],
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

# ------------------------------------------------------------------
# UPDATE

menu_def = [["&Application", ["&Update"]]]
layout = ([sg.Menu(menu_def, key="-MENU-", tearoff=False)],)

# ------------------------------------------------------------------
# INTEGRATION OF COMPONENTS

# sub_col1 = sg.Column([[stimulation_settings, ]], vertical_alignment='t')
col1 = sg.Column(
    [[viperbox_control_frame], [stimulation_settings], [recording_frame]],
    vertical_alignment="t",
)
col2 = sg.Column(
    [[electrode_frame]],
    vertical_alignment="t",
    visible=False,
)
col3 = sg.Column(
    [[pulse_shape_frame], [pulse_train_frame], [parameter_sweep]],
    vertical_alignment="t",
    visible=False,
)
col4 = sg.Column([[plot_frame], [log_frame]], vertical_alignment="t")


layout += ([[col1, col2, col3, col4]],)


window = sg.Window(
    "ViperBox Control",
    layout,
    #    size=(800, 800),
    finalize=True,
)
# ------------------------------------------------------------------
# HELPER FUNCTIONS


def get_last_timestamp(log_file_path):
    last_timestamp = ""
    with open(log_file_path, "rb") as f:
        for line in f:
            if line.decode()[:4] == str(datetime.datetime.now().year):
                last_timestamp = line.decode()
        if last_timestamp == "":
            return ""
        else:
            last_timestamp = last_timestamp.split(" - ")[0]
            return last_timestamp


def read_log_file(log_file_path):
    with open(log_file_path, "r") as f:
        return f.read()


def load_parameter_dicts(values):
    values = convert_biphasic(values)
    values["stim_sweep_electrode_list"] = get_electrodes(electrode_switch_matrix)
    pulse_shape_dct_from_gui = {
        k: int(values[k]) for k in PulseShapeParameters.__annotations__
    }
    pulse_shape = PulseShapeParameters(**pulse_shape_dct_from_gui)
    pulse_train_dct_from_gui = {
        k: int(values[k]) for k in PulseTrainParameters.__annotations__
    }
    pulse_train = PulseTrainParameters(**pulse_train_dct_from_gui)
    pulse_sweep_dct_from_gui = {
        k: values[k] for k in StimulationSweepParameters.__annotations__
    }
    pulse_sweep = StimulationSweepParameters(**pulse_sweep_dct_from_gui)
    return pulse_shape, pulse_train, pulse_sweep


def convert_biphasic(values):
    if values["biphasic"] == "Biphasic":
        values["biphasic"] = True
    else:
        values["biphasic"] = False
    return values


def verify_type_step_min_max(
    name: str, value: int, verify_int_params=verify_int_params
):
    """
    Verifies:
    - between min max
    - mod step = 0
    - is integer except for frequency of pulses
    """
    step = int(verify_int_params[name][0])
    min_val = int(verify_int_params[name][1])
    max_val = int(verify_int_params[name][2])
    color = "white"
    try:
        if name == "frequency_of_pulses":
            value = float(value)
        else:
            value = int(value)
    except:
        value = min_val
        logger.warning(f"parameter {name} was not a float or an integer.")
    if not min_val <= value <= max_val:
        logger.warning(
            f"Out of range. Parameter {name} should be between {min_val} and "
            + f"{max_val} with a step size of {step}."
        )
        color = "orange"
    elif (value - min_val) % step != 0:
        if name != "frequency_of_pulses":
            logger.warning(
                f"Wrong stepsize. Parameter {name} should be between {min_val} and "
                + f"{max_val} with a step size of {step}."
            )
            color = "orange"
    else:
        color = "white"
    return value, color


pulse_sum_list = [
    "pulse_delay",
    "first_pulse_phase_width",
    "pulse_interphase_interval",
    "second_pulse_phase_width",
    "discharge_time",
]


def verify_duration(values):
    sum_pulses = (
        int(values["pulse_delay"])
        + int(values["first_pulse_phase_width"])
        + int(values["pulse_interphase_interval"])
        + int(values["second_pulse_phase_width"])
        + int(values["discharge_time"])
    )
    if int(values["pulse_duration"]) < sum_pulses:
        logger.error(
            f"User input for pulse_duration ({values['pulse_duration']} us) is smaller than "
            + f"the sum of independent pulse parts ({sum_pulses} us)."
        )
        return False, sum_pulses
    else:
        return True, sum_pulses


def pulse2freq_conversion(pulse):
    freq = 1 / (int(pulse) / 1000000)
    return pulse, freq


def freq2pulse_conversion(freq):
    pulse = int(1 / float(freq) * 1000000 // 100 * 100)
    freq = 1 / (pulse / 1000000)
    return pulse, freq


def verify_pulse_min_max(amp_min, amp_max, step):
    return amp_min <= amp_max


# ------------------------------------------------------------------
# PREPARING

settings_list = load_settings_folder(settings_folder_path)

_, values = window.read(timeout=0)
SetLED(window, "led_rec", False)

print(f"Setting up with no_box = {no_box} and emulated = {emulated}")
VB = ViperBoxControl(no_box=no_box, emulated=emulated)

SetLED(window, "led_connect_hardware", VB._connected_handle)
SetLED(window, "led_connect_BS", VB._connected_BS)
SetLED(window, "led_connect_probe", VB._connected_probe)

fig = generate_plot()
figure_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
selected_user_setting = None
update_settings_listbox(settings_folder_path)

elements = [window[key] for key in verify_int_params.keys()]
for element in elements:
    element.bind("<FocusOut>", "+FOCUS OUT")

window["mul_log"].update(read_log_file(LOG_FILENAME))
last_event = ""
gain = None

# ------------------------------------------------------------------
# CF: MAIN

if __name__ == "__main__":
    while True:
        event, values = window.read()
        stop_threads = True
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        # viperbox control
        elif event == "button_connect":
            if VB._handle == "no_box":
                logger.info("VirtualBox initialized in testing mode")
            else:
                VB.connect_viperbox()
                SetLED(window, "led_connect_hardware", VB._connected_handle)
                SetLED(window, "led_connect_BS", VB._connected_BS)
                SetLED(window, "led_connect_probe", VB._connected_probe)
        elif event == "button_disconnect":
            VB.disconnect_viperbox()
            SetLED(window, "led_connect_hardware", VB._connected_handle)
            SetLED(window, "led_connect_BS", VB._connected_BS)
            SetLED(window, "led_connect_probe", VB._connected_probe)
        elif event[:3] == "el_":
            window[event].update(
                button_color=toggle_2d_color(event, electrode_switch_matrix)
            )
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
        elif event == "update_viperbox_settings":
            print("updating viperbox settings")
            reference_electrode = get_references(reference_switch_matrix)
            VB.update_channel_settings(reference_electrode, gain)
        elif event == "button_select_recording_folder":
            tmp_path = sg.popup_get_folder("Select recording folder")
            if tmp_path is not None:
                recording_folder_path = tmp_path
                window["current_folder"].update(
                    f"Saving in {basename(recording_folder_path)}"
                )
        elif event == "button_select_settings_folder":
            tmp_path = sg.popup_get_folder("Select settings folder")
            if tmp_path is not None:
                settings_folder_path = tmp_path
                settings_list = load_settings_folder(settings_folder_path)
                update_settings_listbox(settings_folder_path)
        elif event == "button_toggle_stim":
            window["button_toggle_stim"].metadata = not window[
                "button_toggle_stim"
            ].metadata
            window["button_toggle_stim"].update(
                image_data=toggle_btn_on
                if window["button_toggle_stim"].metadata
                else toggle_btn_off
            )
            manual_stim = not manual_stim
            window["key_parameter_sweep"].update(visible=not manual_stim)
            window["pulse_shape_col2"].update(visible=manual_stim)
        elif event == "button_start":
            SetLED(window, "led_rec", None)
            VB.set_file_path(recording_folder_path, values["input_filename"])
            VB.control_rec_setup()
            if values["checkbox_rec_wo_stim"]:
                VB.control_rec_start()
                start_eo_acquire()
            else:
                pulse_shape, pulse_train, pulse_sweep = load_parameter_dicts(values)
                electrode_list = get_electrodes(electrode_switch_matrix)
                viperbox = ViperBoxConfiguration(0)
                config = ConfigurationParameters(
                    pulse_shape, pulse_train, viperbox, pulse_sweep, electrode_list
                )
                VB.update_config(config)
                if manual_stim:
                    VB.control_send_parameters(electrode_list=electrode_list)
                    VB.stimulation_trigger()
                    start_eo_acquire()
                else:
                    VB.stim_sweep()
                    start_eo_acquire()
        elif event == "button_stop":
            SetLED(window, "led_rec", False)
            VB.control_rec_stop()
        # Edit user settings
        elif event == "button_save_set":
            electrode_list = get_electrodes(electrode_switch_matrix, True)
            values["electrode_list"] = get_electrodes(electrode_switch_matrix, True)
            save_settings(settings_folder_path, values["input_set_name"], values)
            update_settings_listbox(settings_folder_path)
        elif event == "button_load_set":
            if selected_user_setting:
                loaded_settings = read_saved_settings(
                    settings_folder_path, selected_user_setting
                )
                for setting in loaded_settings.keys():
                    if setting != "electrode_list":
                        window[setting].update(loaded_settings[setting])
                electrode_switch_matrix = set_reference_matrix(
                    loaded_settings["electrode_list"]
                )
                [
                    window[f"el_button_{button+1}"].update(button_color="light gray")
                    for button in range(MAX_ROWS * MAX_COL)
                ]
                [
                    window[f"el_button_{electrode}"].update(button_color="red")
                    for electrode in loaded_settings["electrode_list"]
                ]
        elif event == "button_del_set":
            answer = sg.popup_ok_cancel(
                "This action cannot be undone.\n\n If you want to delete multiple"
                + " settings, please do so through the file browser."
            )
            if answer == "OK":
                Path.unlink(
                    Path.joinpath(
                        Path(settings_folder_path), selected_user_setting + ".cfg"
                    )
                )
                update_settings_listbox(settings_folder_path)
        # Filter and select user settings
        elif event == "input_filter_name":
            if values["input_filter_name"] != "":
                search = values["input_filter_name"]
                new_values = [x for x in settings_list if search in x]
                window["listbox_settings"].update(new_values)
            else:
                window["listbox_settings"].update(settings_list)
        elif event == "listbox_settings":
            if values["listbox_settings"]:
                selected_user_setting = values["listbox_settings"][0]
        # make all values ints
        # check pulse parameters
        elif event == "pulse_amplitude_equal":
            if values["pulse_amplitude_equal"]:
                window["pulse_amplitude_cathode"].update(disabled=True)
                window["pulse_amplitude_cathode"].update(
                    value=values["pulse_amplitude_anode"]
                )
            else:
                window["pulse_amplitude_cathode"].update(disabled=False)

        # FOCUS
        elif event.endswith("+FOCUS OUT") and event != last_event:
            last_event = event
            event = event.split("+")[0]
            # print('event: ', event, window[event])
            next_element = window[event].get_next_focus()
            print("next event: ", next_element)
            # next_element = window[event].get_previous_focus()
            # next_element = next_element.get_next_focus()
            for key in verify_int_params.keys():
                checked_val, color = verify_type_step_min_max(key, values[key])
                if values[key] != checked_val:
                    # print(key, checked_val)
                    window[key].update(value=checked_val, background_color=color)
                # print("values['second_pulse_phase_width']: ", values['second_pulse_phase_width'])
            # window.finalize()
            if values["pulse_amplitude_equal"]:
                window["pulse_amplitude_cathode"].update(
                    value=values["pulse_amplitude_anode"]
                )
            elif event == "pulse_duration":
                _, frequency_of_pulses = pulse2freq_conversion(values["pulse_duration"])
                window["frequency_of_pulses"].update(value=frequency_of_pulses)
            elif event == "frequency_of_pulses":
                pulse_duration, frequency_of_pulses = freq2pulse_conversion(
                    values["frequency_of_pulses"]
                )
                window["frequency_of_pulses"].update(value=frequency_of_pulses)
                window["pulse_duration"].update(value=pulse_duration)
            elif event in pulse_sum_list:
                check, new_sum = verify_duration(values)
                if not check:
                    window["pulse_duration"].update(value=new_sum)
            # if figure_agg:
            #     delete_figure_agg(figure_agg)
            # values = convert_biphasic(values)
            # plot_vals = {k: int(values[k]) for k in generate_plot.__annotations__}
            # fig = generate_plot(**plot_vals)
            # figure_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
            # print('try to set focus after this')
            # elements = [window[key] for key in verify_int_params.keys()]
            # for element in elements:
            #     print(element)
            # next_element.set_focus()
            # print(event)
            # window[event].set_focus()
            # event, window = window.read()
            # print('event na figure hooplijk: ', event)

            # for key in verify_int_params.keys():
            #     checked_val = verify_type_step_min_max(key, values[key])
            #     if not key == 'frequency_of_pulses':
            #         if values[key] != checked_val:
            #             window[key].update(value=checked_val)

        # replot
        elif event == "Reload":
            # Implementation from https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib_Browser.py
            if figure_agg:
                delete_figure_agg(figure_agg)
            values = convert_biphasic(values)
            plot_vals = {k: int(values[k]) for k in generate_plot.__annotations__}
            fig = generate_plot(**plot_vals)
            figure_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
        elif event == "Update":
            if sg.popup_ok_cancel("Are you sure? This will close the application."):
                if not os.path.exists("update_blocker"):
                    subprocess.Popen(
                        batch_script_path,
                        shell=True,
                        stdin=None,
                        stdout=None,
                        stderr=None,
                        close_fds=True,
                        creationflags=subprocess.DETACHED_PROCESS,
                    )
                break
        window["mul_log"].update(read_log_file(LOG_FILENAME))

VB.disconnect_viperbox()
VB.free_library()

window.close()

# TODO with viperbox connected:
# - Test connect viperbox
# - add version of viperboxinterface to settings to see if they are compatible
