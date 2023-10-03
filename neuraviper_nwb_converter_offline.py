"""******************  JA Westerberg 2023  ************************************
* NeuraViPeR NWB Converter (Offline)                                          *
*******************************************************************************
* Source filename :     neuraviper_nwb_converter_offline.py
*
*
* History :
* ~~~~~~~
* Version   Date        Authors   Comments
* v0.1      28/09/2023  JAW       Preliminary version
* v0.2      02/10/2023  JAW       Added metadata input and initialization tweak
*
* Feature requests:
* -buffer for systems with lower memory
****************************************************************************"""

import numpy as np
import PySimpleGUI as sg
import os.path

from datetime import datetime
from dateutil.tz import tzlocal
from uuid import uuid4
from NeuraviperPy import streamOpenFile, streamReadData
from pynwb import NWBHDF5IO, NWBFile
from pynwb.ecephys import ElectricalSeries

# init defaults

toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=='
toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6TYMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNExWWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPDVYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX72TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1AnYoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7znZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC'

# init the GUI
NAME_SIZE = 23
def name(name):
    dots = NAME_SIZE-len(name)-2
    return sg.Text(name + ' ' + '•'*dots, size=(NAME_SIZE,1), justification='r',pad=(0,0), font='Courier 10')

layout = [
    [sg.Text("Automatic NWB file generation for ViperBox recording", font = 18)],
    [
    sg.Text("ViperBox Recording Directory"),
    sg.In(size=(36, 1), enable_events=True, key="-FOLDER-"),
    sg.FolderBrowse(),
    ],
    [sg.Listbox(
        values=[], enable_events=True, size=(70, 10), key="-FILE LIST-"
    )],
    [sg.Text('Probe 0 State:'), sg.Text('Off'), sg.Button( 
        image_data=toggle_btn_off, 
        key='-TOGGLE PROBE 0-', 
        button_color=(sg.theme_background_color(), sg.theme_background_color()),  
        border_width=0, 
        metadata=False
    ), sg.Text('On')],
    [sg.Text('Probe 1 State:'), sg.Text('Off'), sg.Button( 
        image_data=toggle_btn_off, 
        key='-TOGGLE PROBE 1-', 
        button_color=(sg.theme_background_color(), sg.theme_background_color()), 
        border_width=0, 
        metadata=False
    ), sg.Text('On')],
    [sg.Text('Probe 2 State:'), sg.Text('Off'), sg.Button( 
        image_data=toggle_btn_off, 
        key='-TOGGLE PROBE 2-', 
        button_color=(sg.theme_background_color(), sg.theme_background_color()), 
        border_width=0, 
        metadata=False
    ), sg.Text('On')],
    [sg.Text('Probe 3 State:'), sg.Text('Off'), sg.Button( 
        image_data=toggle_btn_off, 
        key='-TOGGLE PROBE 3-', 
        button_color=(sg.theme_background_color(), sg.theme_background_color()), 
        border_width=0, 
        metadata=False
    ), sg.Text('On')],
    [sg.Text('NWB METADATA', font = 18)],
    [name('DATE'), sg.Input(default_text='20231002', key='-DATE-', s=45)],
    [name('INSTITUTION'), sg.Input(default_text='Netherlands Institute for Neuroscience', key='-INSTITUTION-',s=45)],
    [name('LAB'), sg.Input(default_text='Vision and Cognition Group', key='-LAB-',s=45)],
    [name('EXPERIMENTER'), sg.Input(default_text='JA Westerberg', key='-EXPERIMENTER-',s=45)],
    [name('SUBJECT'), sg.Input(default_text='toucan', key='-SUBJECT-',s=45)],
    [name('SESSION ID'), sg.Input(default_text='000', key='-SESSION ID-',s=45)],
    [name('EXPERIMENT'), sg.Input(default_text='conversion_demo', key='-EXPERIMENT-', s=45)],
    [sg.Button("RUN", size=(63, 1), key='-RECORD-', metadata=False)]
]

window = sg.Window(
    title = "ViperBox NWB Stream Converter", 
    layout = layout
)

while True:
    
    event, values = window.read()
    
    if event == "EXIT" or event == sg.WIN_CLOSED:
        break
    
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            file_list = os.listdir(folder)
        except:
            file_list = []
    
        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".bin"))
        ]
        
        window["-FILE LIST-"].update(fnames)
    
    elif event == "-FILE LIST-":
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            initialize_nwb = True
            print("set folder")
        except:
            pass
        
    elif event == '-TOGGLE PROBE 0-':
        window['-TOGGLE PROBE 0-'].metadata = not window['-TOGGLE PROBE 0-'].metadata
        window['-TOGGLE PROBE 0-'].update(image_data=toggle_btn_on if window['-TOGGLE PROBE 0-'].metadata else toggle_btn_off)
            
    elif event == '-TOGGLE PROBE 1-':
        window['-TOGGLE PROBE 1-'].metadata = not window['-TOGGLE PROBE 1-'].metadata
        window['-TOGGLE PROBE 1-'].update(image_data=toggle_btn_on if window['-TOGGLE PROBE 1-'].metadata else toggle_btn_off)           
    
    elif event == '-TOGGLE PROBE 2-':
        window['-TOGGLE PROBE 2-'].metadata = not window['-TOGGLE PROBE 2-'].metadata
        window['-TOGGLE PROBE 2-'].update(image_data=toggle_btn_on if window['-TOGGLE PROBE 2-'].metadata else toggle_btn_off)
           
    elif event == '-TOGGLE PROBE 3-':
        window['-TOGGLE PROBE 3-'].metadata = not window['-TOGGLE PROBE 3-'].metadata
        window['-TOGGLE PROBE 3-'].update(image_data=toggle_btn_on if window['-TOGGLE PROBE 3-'].metadata else toggle_btn_off)
        
    elif event == '-RECORD-':
        window['-RECORD-'].metadata = not window['-RECORD-'].metadata         
    
    while window["-RECORD-"].metadata:
        
        if os.path.exists(os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0][:-3] + "nwb")):
            window['-RECORD-'].metadata = not window['-RECORD-'].metadata
            print("file already converted!")
            break
        
        if ~window['-TOGGLE PROBE 0-'].metadata & window['-TOGGLE PROBE 1-'].metadata & ~window['-TOGGLE PROBE 2-'].metadata & ~window['-TOGGLE PROBE 3-'].metadata:
            window['-RECORD-'].metadata = not window['-RECORD-'].metadata
            break
      
        print("nwb initializing...")
        
        filesize = os.path.getsize(filename)
        
        n_probes = 0        
        if window['-TOGGLE PROBE 0-'].metadata:
            probe0_Handle = streamOpenFile(filename, 0)
            n_probes +=1
            
        if window['-TOGGLE PROBE 1-'].metadata:
            probe1_Handle = streamOpenFile(filename, 1)
            n_probes +=1
        
        if window['-TOGGLE PROBE 2-'].metadata:
            probe2_Handle = streamOpenFile(filename, 2)
            n_probes +=1
        
        if window['-TOGGLE PROBE 3-'].metadata:
            probe3_Handle = streamOpenFile(filename, 3)
            n_probes +=1
            
        # make a reasonable attempt a determining the number of packets
        packet_estimate = int(filesize / n_probes / 400 * 1.1)
        
        # init the nwb file
        
        print("Probe0 active: " + str(window["-TOGGLE PROBE 0-"].metadata))
        print("Probe1 active: " + str(window["-TOGGLE PROBE 1-"].metadata))
        print("Probe2 active: " + str(window["-TOGGLE PROBE 2-"].metadata))
        print("Probe3 active: " + str(window["-TOGGLE PROBE 3-"].metadata))
        
        nwbfile = NWBFile(
            session_description = "auto-generated NWB for viperbox recording",
            identifier = str(uuid4()),
            session_start_time = datetime.now(tzlocal()),
            experimenter = values['-EXPERIMENTER-'],
            lab = values['-LAB-'],
            institution = values['-INSTITUTION-'],
            experiment_description = values['-EXPERIMENT-'],
            session_id = 
                "sub-" + values['-SUBJECT-'] + 
                "-ses-" + values['-DATE-'] + 
                "-exp-" + values['-EXPERIMENT-'] + 
                "-blk-" + values['-SESSION ID-']
        )
        
        # init the device information
        viperbox0_Device = nwbfile.create_device(
            name = "viperbox0_Device",
            description = "NeuraViper project, ViperBox data acquisition device",
            manufacturer = "IMEC"
        )
        
        # init the data electrode groupings
        viperbox0_ElectrodeColumn = nwbfile.add_electrode_column(
            name="label", 
            description="label of viperbox0 electrodes"
        )
        
        if window['-TOGGLE PROBE 0-'].metadata:
            probe0_ElectrodeGroup = nwbfile.create_electrode_group(
                name = "probe0_ElectrodeGroup",
                description = "electrode information for ViperBox probe 0",
                device = viperbox0_Device,
                location = "PLACEHOLDER",
            )
        
        if window['-TOGGLE PROBE 1-'].metadata:
            probe1_ElectrodeGroup = nwbfile.create_electrode_group(
                name = "probe1_ElectrodeGroup",
                description = "electrode information for ViperBox probe 0",
                device = viperbox0_Device,
                location = "PLACEHOLDER",
            )
        
        if window['-TOGGLE PROBE 2-'].metadata:
            probe2_ElectrodeGroup = nwbfile.create_electrode_group(
                name = "probe2_ElectrodeGroup",
                description = "electrode information for ViperBox probe 0",
                device = viperbox0_Device,
                location = "PLACEHOLDER",
            )
        
        if window['-TOGGLE PROBE 3-'].metadata:
            probe3_ElectrodeGroup = nwbfile.create_electrode_group(
                name = "probe3_ElectrodeGroup",
                description = "electrode information for ViperBox probe 0",
                device = viperbox0_Device,
                location = "PLACEHOLDER",
            )
        
        # init the electrodes themselves
        electrode_counter = 0
        
        if window['-TOGGLE PROBE 0-'].metadata:
            for ichannels in range(64):
                nwbfile.add_electrode(
                    group = probe0_ElectrodeGroup,
                    label = "probe0electrode{}".format(ichannels),
                    location = "PLACEHOLDER"
                )
                electrode_counter += 1
            
        if window['-TOGGLE PROBE 1-'].metadata:
            for ichannels in range(64):
                nwbfile.add_electrode(
                    group = probe1_ElectrodeGroup,
                    label = "probe1electrode{}".format(ichannels),
                    location = "PLACEHOLDER"
                )
                electrode_counter += 1
        
        if window['-TOGGLE PROBE 2-'].metadata:
            for ichannels in range(64):
                nwbfile.add_electrode(
                    group = probe2_ElectrodeGroup,
                    label = "probe2electrode{}".format(ichannels),
                    location = "PLACEHOLDER"
                )
                electrode_counter += 1
        
        if window['-TOGGLE PROBE 3-'].metadata:
            for ichannels in range(64):
                nwbfile.add_electrode(
                    group = probe3_ElectrodeGroup,
                    label = "probe3electrode{}".format(ichannels),
                    location = "PLACEHOLDER"
                )
                electrode_counter += 1
        
        # create the electrode table
        all_table_region = nwbfile.create_electrode_table_region(
            region = list(range(electrode_counter)),
            description = "all electrodes" 
        )
    
        print("nwb initialization complete!")
    
        if window['-TOGGLE PROBE 0-'].metadata:
            stream = streamReadData(probe0_Handle, packet_estimate)
            current_data = np.asarray(
                [stream[i].data for i in range(np.size(stream))], dtype="uint16"
                )
            current_time = np.asarray(
                [stream[i].timestamp for i in range(np.size(stream))], dtype="uint32")
            current_time = current_time / 1000.0
            
        if window['-TOGGLE PROBE 1-'].metadata:
            stream = streamReadData(probe1_Handle, packet_estimate)
            if not window['-TOGGLE PROBE 0-'].metadata:
                current_data = np.asarray(
                    [stream[i].data for i in range(np.size(stream))], dtype="uint16"
                    )
                current_time = np.asarray(
                    [stream[i].timestamp for i in range(np.size(stream))], dtype="uint32")
                current_time = current_time / 1000.0
                
            else:
                temp_current_data = np.asarray(
                    [stream[i].data for i in range(np.size(stream))], dtype="uint16"
                    )
                current_data = np.concatenate([current_data, temp_current_data], 1)
            
        if window['-TOGGLE PROBE 2-'].metadata:
            stream = streamReadData(probe2_Handle, packet_estimate)
            if not window['-TOGGLE PROBE 0-'].metadata and not window['-TOGGLE PROBE 1-'].metadata:
                current_data = np.asarray(
                    [stream[i].data for i in range(np.size(stream))], dtype="uint16"
                    )
                current_time = np.asarray(
                    [stream[i].timestamp for i in range(np.size(stream))], dtype="uint32")
                current_time = current_time / 1000.0
            
            else:
                temp_current_data = np.asarray(
                    [stream[i].data for i in range(np.size(stream))], dtype="uint16"
                    )
                current_data = np.concatenate([current_data, temp_current_data], 1)
            
        if window['-TOGGLE PROBE 3-'].metadata:
            stream = streamReadData(probe3_Handle, packet_estimate)
            if not window['-TOGGLE PROBE 0-'].metadata and not window['-TOGGLE PROBE 1-'].metadata and not window['-TOGGLE PROBE 2-'].metadata:
                current_data = np.asarray(
                    [stream[i].data for i in range(np.size(stream))], dtype="uint16"
                    )
                current_time = np.asarray(
                    [stream[i].timestamp for i in range(np.size(stream))], dtype="uint32")
                current_time = current_time / 1000.0
            else:
                temp_current_data = np.asarray(
                    [stream[i].data for i in range(np.size(stream))], dtype="uint16"
                    )
                current_data = np.concatenate([current_data, temp_current_data], 1)

        probes_ElectricalSeries = ElectricalSeries(
            name = "neuraviper",
            description = "probe data stream from ViperBox",
            data = current_data,
            electrodes = all_table_region,
            timestamps = current_time,
        )
        
        nwbfile.add_acquisition(probes_ElectricalSeries)
        
        # init file save
        print(os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0][:-3] + "nwb"))
        io = NWBHDF5IO(os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0][:-3] + "nwb"), mode="w")
        io.write(nwbfile)
        io.close(nwbfile)
        
        window['-RECORD-'].metadata = not window['-RECORD-'].metadata
                    
window.close()