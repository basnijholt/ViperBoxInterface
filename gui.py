import PySimpleGUI as sg

from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import PySimpleGUI as sg
import matplotlib
matplotlib.use('TkAgg')

sg.theme("SystemDefaultForReal")


def LEDIndicator(key=None, radius=30):
    return sg.Graph(
        canvas_size=(radius, radius),
        graph_bottom_left=(-radius, -radius),
        graph_top_right=(radius, radius),
        pad=(0, 0),
        key=key,
    )


def SetLED(window, key, color):
    graph = window[key]
    graph.erase()
    graph.draw_circle((0, 0), 12, fill_color=color, line_color=color)

# Parameters for the biphasic pulse
amplitude = -1  # Amplitude of the first (cathodic) phase, in microAmps
duration = 0.2  # Duration of each phase, in milliseconds
inter_phase_interval = 0.05  # Time between the two phases, in milliseconds

# Generate the time and current arrays for the biphasic pulse
time = np.linspace(0, 2*duration + inter_phase_interval, 1000)
current = np.zeros_like(time)
current[(time>0)&(time<.1)] = 0
current[(time > .1) & (time <= duration)] = -amplitude
current[(time > duration + inter_phase_interval) & (time <= 2*duration + inter_phase_interval-0.1)] = amplitude
current[(time>2*duration + inter_phase_interval-0.1)&(time<2*duration + inter_phase_interval)] = 0

fig = matplotlib.figure.Figure(figsize=(4, 4), dpi=100)
# t = np.arange(0, 3, .01)
# fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
fig.add_subplot(111).plot(time, current)

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

control_frame = sg.Frame(
    "Viperbox control",
    [
        [
            sg.Text("Recording path:"),
            sg.Input(
                sg.user_settings_get_entry("-filename-", ""), size=(20, 10), key="-IN-"
            ),
            sg.FileSaveAs(),
        ],
        [sg.Text("Recording:")],
        [sg.Button("Rec", size=(10, 1)), LEDIndicator("rec")],
        [sg.Text("Stimulation:")],
        [
            sg.Button("Start", size=(10, 1)),
            sg.Button("Stop", size=(10, 1)),
            sg.Button("Single train", size=(10, 1)),
        ],
    ],
    size=(400, 180),
    expand_x=True,
)

log_frame = sg.Frame(
    "Log",
    [
        [
            sg.Multiline(
                size=(55, 150),
                key="-LOG-",
                expand_y=True,
            )
        ],
    ],
    size=(400, 200),
    # expand_y=True,
)

plot_frame = sg.Frame('Pulse preview',
                      [[sg.Canvas(key='-CANVAS-')]])

unit_h, unit_w = (4,1)
inp_w, inp_h = (10,1)

stim_par_frame = sg.Frame(
    "Stimulation parameters",
    [
        [
stimulation_settings = sg.Frame('Settings',
        [[sg.Button("Load settings"), sg.Button("Save settings"),
        sg.Button("Electrode selection")]],),],
        [sg.Frame("Pulse shape parameters",[
        [sg.Text("Biphasic/Monophasic"),sg.Drop(size=(inp_w-2, inp_h), values=("Biphasic", "Monophasic"),    auto_size_text=True,    default_value="Biphasic",), sg.T(' ', size=(unit_h, unit_w))],
        [sg.Text("Pulse duration", justification='l'), sg.Input(size=(inp_w, inp_h), key="Pulse duration"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Pulse delay"), sg.Input(size=(inp_w, inp_h), key="Pulse delay"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("1st pulse phase width"),sg.Input(size=(inp_w, inp_h), key="1st pulse phase width"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Pulse interphase interval"),sg.Input(size=(inp_w, inp_h), key="Pulse interphase interval"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("2nd pulse phase width"),sg.Input(size=(inp_w, inp_h), key="2nd pulse phase width"), sg.T('uSec', size=(unit_h, unit_w))],
        # [sg.Text("Discharge time"), sg.Input(size=(inp_w, inp_h), key="Discharge time"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Interpulse interval (discharge)"), sg.Input(size=(inp_w, inp_h), key="interpulse interval"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Pulse amplitude anode"), sg.Input(size=(inp_w, inp_h), key="Pulse amplitude anode"), sg.T('uA', size=(unit_h, unit_w))],
        [sg.Text("Pulse amplitude cathode"),sg.Input(size=(inp_w, inp_h), key="Pulse amplitude cathode"), sg.T('uA', size=(unit_h, unit_w))],
        [sg.T('Pulse amplitude equal'), sg.Checkbox(" ")],
        ], element_justification='r')],
        [sg.Frame("Pulse train parameters",[
        [sg.Text("Number of pulses"), sg.Input(size=(inp_w, inp_h), key="Number of pulses"), sg.T(' ', size=(unit_h, unit_w))],
        [sg.Text("Discharge time extra"), sg.Input(size=(inp_w, inp_h), key="Discharge time extra"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Frequency of pulses"), sg.Input(size=(inp_w, inp_h), key="Frequency of pulses"), sg.T('Hz', size=(unit_h, unit_w))],
        [sg.Text("Number of trains"), sg.Input(size=(inp_w, inp_h), key="Number of trains"), sg.T(' ', size=(unit_h, unit_w))],
        [sg.Text("Train interval"), sg.Input(size=(inp_w, inp_h), key="Train interval"), sg.T('Sec', size=(unit_h, unit_w))],
        [sg.Text("On-set jitter"), sg.Input(size=(inp_w, inp_h), key="On-set jitter"), sg.T('Sec', size=(unit_h, unit_w))],
        ], element_justification='r')],
        [sg.Frame("Parameter sweep", [
        [sg.Text("Pulse amplitude min"), sg.Input(size=(inp_w, inp_h), key="Pulse amplitude min"), sg.T('uA', size=(unit_h, unit_w))],
        [sg.Text("Pulse amplitude max"), sg.Input(size=(inp_w, inp_h), key="Pulse amplitude max"), sg.T('uA', size=(unit_h, unit_w))],
        [sg.Text("Pulse amplitude step"), sg.Input(size=(inp_w, inp_h), key="Pulse amplitude step"), sg.T('uA', size=(unit_h, unit_w))],
        [sg.Text("Repetitions"), sg.Input(size=(inp_w, inp_h), key="Repetitions"), sg.T(' ', size=(unit_h, unit_w))],
        [sg.Checkbox("Randomize")],
        ], element_justification='r')],
    ],
    element_justification="l",
)

col1 = sg.Column([[control_frame], [plot_frame], [log_frame]], vertical_alignment="t")
col2 = sg.Column([[stim_par_frame]])

layout = [[col1, col2]]

window = sg.Window(
    "ViperBox Control",
    layout,
    #    size=(800, 800),
    finalize=True
)

fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)

while True:
    event, values = window.read()
    SetLED(window, "rec", "gray")
    print(event, values)
    if event == sg.WIN_CLOSED:
        break

window.close()
