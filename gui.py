import PySimpleGUI as sg

# from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

sg.theme("SystemDefaultForReal")

toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=='
toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6TYMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNExWWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPDVYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX72TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1AnYoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7znZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC'

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

# ------------------------------------------------------------------
# CF STIMULATION PULSE FRAME

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

fig = matplotlib.figure.Figure(figsize=(4, 3), dpi=100)
fig.add_subplot(111).plot(time, current)

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


plot_frame = sg.Frame('Pulse preview',
    [[sg.Canvas(key='-CANVAS-')]],
    expand_x=True,
)

# ------------------------------------------------------------------
# CF: VIPERBOX CONTROL FRAME

viperbox_control_frame = sg.Frame(
    "Viperbox control",
    [
        [
            sg.Text("Hardware connection"), 
            sg.Button('Connect', key='button_connect'), 
            LEDIndicator("led_connect")],
        [sg.HorizontalSeparator('light gray')],
        [sg.Text('Manual stimulation'),
            sg.Button(image_data=toggle_btn_off, key='button_toggle_stim', button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0, metadata=False),
            sg.Text('Current amplitude sweep')
        ],
        [
            # sg.Button("Rec", size=(10, 1)), 
            sg.Text('Rec'),
            LEDIndicator("led_rec"),
            sg.Input(
                sg.user_settings_get_entry("-filename-", ""), size=(20, 10), key="input_data_path"
            ),
            sg.FileSaveAs(),
        ],
        # [sg.HorizontalSeparator('light gray')],
        # [sg.Text("Stimulation:")],
        [
            sg.Button("Start", size=(10, 1), key='button_start'),
            sg.Button("Stop", size=(10, 1), key='button_stop'),
            sg.Checkbox("Record without stimulation", key='checkbox_rec_wo_stim')
        ],
    ],
    # size=(400, 170),
    expand_x=True,
)


# ------------------------------------------------------------------
# CF: ELECTRODE SELECTION FRAME

MAX_ROWS = 15
MAX_COL = 4

reference_matrix = [['off' for i in range(MAX_COL)] for j in range(MAX_ROWS)]
electrode_matrix = [[sg.Button(f'{i*MAX_ROWS+j+1}', size=(2, 1), 
                                key=(f'el_button_{i*MAX_ROWS+j+1}'), 
                                pad=(10,1), button_color='light gray') for i in range(MAX_COL)] for j in range(MAX_ROWS)]
electrode_matrix = electrode_matrix[::-1]
electrode_frame = sg.Frame('Stimulation electrode selection', electrode_matrix, expand_y=True)

def toggle_color(event, reference_matrix):
    electrode = int(event[10:])
    row = (electrode - 1) % MAX_ROWS
    col = (electrode - 1) // MAX_ROWS
        
    if reference_matrix[row][col] == 'off':
        reference_matrix[row][col] = 'on'
        return 'red'
    else:
        reference_matrix[row][col] = 'off'
        return 'light gray'

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
            )
        ],
    ],
    size=(400, 280),
    # expand_y=True,
    expand_x=True,
)

# ------------------------------------------------------------------
# CF: STIMULATION SETTINGS FRAME


unit_h, unit_w = (4,1)
inpsize_w, inpsize_h = (10,1)

stimulation_settings = sg.Frame('Pre-load settings',
        [
            [sg.Button("Load", size=(10,1), key='button_load_set')],
            [sg.Button('Delete', size=(10,1), key='button_del_set'),],
            [sg.Button("Save", size=(10,1), key='button_save_set'),],
            [sg.Input('', size=(15,1), key='input_set_name')],

[
            sg.Listbox(
                size=(10, 6),
                key="listbox_settings",
                values=['Corin_default', 'Cristina_default', 'mouse_jumpy'],
                expand_y=True,
                expand_x=True,
            )
        ]
    ], 
    expand_x=True,
    size=(185,60),
    expand_y=True,
    vertical_alignment='t',
)

# ------------------------------------------------------------------
# CF: PULSE SHAPE FRAME


pulse_shape_frame = sg.Frame("Pulse shape parameters",[
        [sg.Text("Biphasic/Monophasic"),sg.Drop(key='drop_biphasic',  size=(inpsize_w-2, inpsize_h), values=("Biphasic", "Monophasic"), auto_size_text=True, default_value="Biphasic",), sg.T(' ', size=(unit_h, unit_w))],
        [sg.Text("Pulse duration", justification='l'), sg.Input(600, size=(inpsize_w, inpsize_h), key="input_pulse_duration"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Pulse delay"), sg.Input(0, size=(inpsize_w, inpsize_h), key="input_pulse_delay"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("1st pulse phase width"),sg.Input(170, size=(inpsize_w, inpsize_h), key="input_first_pulse_phase_width"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Pulse interphase interval"),sg.Input(60, size=(inpsize_w, inpsize_h), key="input_pulse_interphase_interval"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("2nd pulse phase width"),sg.Input(170, size=(inpsize_w, inpsize_h), key="input_second_pulse_phase_width"), sg.T('uSec', size=(unit_h, unit_w))],
        # [sg.Text("Discharge time"), sg.Input(, size=(inpsize_w, inpsize_h), key="Discharge time"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Interpulse interval (discharge)"), sg.Input(200, size=(inpsize_w, inpsize_h), key="input_discharge_time"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Pulse amplitude anode"), sg.Input(5, size=(inpsize_w, inpsize_h), key="input_pulse_amplitude_anode"), sg.T('uA', size=(unit_h, unit_w))],
        [sg.Text("Pulse amplitude cathode"),sg.Input(5, size=(inpsize_w, inpsize_h), key="input_pulse_amplitude_cathode"), sg.T('uA', size=(unit_h, unit_w))],
        [sg.T('Pulse amplitude equal'), sg.Checkbox("", key='checkbox_pulse_amplitude_equal')],
        ], 
        element_justification='r',
        expand_x=True)#],
        # [

            
# ------------------------------------------------------------------
# CF: PULSE TRAIN FRAME


pulse_train_frame = sg.Frame("Pulse train parameters",[
        [sg.Text("Number of pulses"), sg.Input(20, size=(inpsize_w, inpsize_h), key="input_number_of_pulses"), sg.T(' ', size=(unit_h, unit_w))],
        # [sg.Text("Discharge time extra"), sg.Input(200, size=(inpsize_w, inpsize_h), key="Discharge time extra"), sg.T('uSec', size=(unit_h, unit_w))],
        [sg.Text("Frequency of pulses"), sg.Input(200, size=(inpsize_w, inpsize_h), key="input_frequency_of_pulses"), sg.T('Hz', size=(unit_h, unit_w))],
        [sg.Text("Number of trains"), sg.Input(5, size=(inpsize_w, inpsize_h), key="input_number_of_trains"), sg.T(' ', size=(unit_h, unit_w))],
        [sg.Text("Train interval (discharge)"), sg.Input(2, size=(inpsize_w, inpsize_h), key="input_discharge_time_extra"), sg.T('Sec', size=(unit_h, unit_w))],
        [sg.Text("On-set jitter"), sg.Input(0, size=(inpsize_w, inpsize_h), key="input_jitter"), sg.T('Sec', size=(unit_h, unit_w))],
        ], 
        element_justification='r',
        expand_x=True)

# ------------------------------------------------------------------
# CF: PARAMETER SWEEP FRAME


ps_dis=False
parameter_sweep = sg.Frame("Stimulation sweep parameters", [
        [sg.Text("Pulse amplitude min"), sg.Input(1, size=(inpsize_w, inpsize_h), key="input_pulse_amplitude_min", disabled=ps_dis), sg.T('uA', size=(unit_h, unit_w))],
        [sg.Text("input_pulse_amplitude_max"), sg.Input(20, size=(inpsize_w, inpsize_h), key="input_pulse_amplitude_max", disabled=ps_dis), sg.T('uA', size=(unit_h, unit_w))],
        [sg.Text("Pulse amplitude step"), sg.Input(1, size=(inpsize_w, inpsize_h), key="input_pulse_amplitude_step", disabled=ps_dis), sg.T('uA', size=(unit_h, unit_w))],
        [sg.Text("Repetitions"), sg.Input(size=(3, inpsize_w, inpsize_h), key="input_repetitions", disabled=ps_dis), sg.T(' ', size=(unit_h, unit_w))],
        [sg.Checkbox("Randomize", key='checkbox_randomize')],
        ], element_justification='r',
        expand_x=True,
        )

# ------------------------------------------------------------------
# INTEGRATION OF COMPONENTS

sub_col1 = sg.Column([[stimulation_settings, electrode_frame]], vertical_alignment='t')
col1 = sg.Column([[viperbox_control_frame], [sub_col1]], vertical_alignment="t")
col2 = sg.Column([[pulse_shape_frame],[pulse_train_frame],[parameter_sweep]], vertical_alignment='t')
# col2 = sg.Column([[pulse_shape_frame],[pulse_train_frame]], vertical_alignment='t')
col3 = sg.Column([[plot_frame],[log_frame]], vertical_alignment='t')

layout = [[col1, col2, col3]],

window = sg.Window(
    "ViperBox Control",
    layout,
    #    size=(800, 800),
    finalize=True
)


fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
_, _ = window.read(timeout=0)
SetLED(window, "led_rec", "gray")
SetLED(window, "led_connect", "gray")


# ------------------------------------------------------------------
# CF: MAIN

if __name__ == "__main__":

    # import os
    # os.startfile("C:\Program Files\Open Ephys\open-ephys.exe")

    while True:
        try:
            event, values = window.read()
        #     print(event, values)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            print(event[10:])
            if event[:3] == 'el_':
                window[event].update(button_color=toggle_color(event, reference_matrix))
        except Exception as e:
            print(e)
            window.close()

window.close()
