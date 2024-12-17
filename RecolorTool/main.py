import os
import webbrowser
import PySimpleGUI as sg
import colormap_gen
import colorswap_util
import pandas as pd


SUMMARY = f"""The purpose of this tool is to create recolored versions of a 
user-provided PNG image, based on a CSV Color Map file.

The CSV Color Map can be provided in two ways: 
1. Create your own mapping CSV file (see structure example in 'examples' folder)
2. Create the Color Map Input PNG image (see example in documentation)
- every time a color_map.csv is created the tool checks for previous versions
and archives them in the archive_color_map folder as backup

The recolor files will be generated and placed in a subfolder called 'recolors' 
The tool will generate the following output:
- a new PNG file for each color palette provided in the color map
- an all-in-one png file that stitches all the recolors into a single file
- a copy of the all-in-one file with a timestamp suffix in the archive folder

IMPORTANT: Recolors cannot be generated without a CSV Map file.
If you want to make adjustments you can either adjust the Color Map Input PNG 
and regenerate the CSV, or change the hex codes in the CSV directly.

IMPORTANT: a timestamped copy of each color map version, as well as each
all-in-one file containing stitched recolors is saved in the respective
archive folders at re-creation as backup

Progress messages and errors will appear in the OUTPUT LOG section.
Please report any issues or bugs on the GitHub issue tracker.
"""
INSTRUCTION = f"""1. OUTPUT: choose a folder where you want the tool to save all your files
2. COLOR MAP: 
    2.1 EITHER browse and select your Color Map Input PNG (if using)
    IMPORTANT: make sure to click the 'Generate Color Map' button!
    2.2 OR provide your own csv file called color_map.csv in the output folder
3. Browse and select your Base PNG File for the recolors 
4. Click the  'Generate Recolors' button
"""

def open_readme():
    """Opens the user documentation link in a web browser."""
    webbrowser.open("https://github.com/Teaiscoldagain/StardewUtilities/blob/main/README.md")



# UI layout 

frame_layout_summary = [
    [sg.Text(SUMMARY)]
],

frame_layout_documentation = [
    [sg.Text("Click the below button to open the user guide on GitHub:")],
    [sg.Button("Open Documentation Link in Browser", size=(None, 1), expand_x=True)]
]

frame_layout_instructions = [
    sg.Text(INSTRUCTION)
],

frame_layout1 = [
    [sg.Text("Select Folder:", size=(10, 1)), sg.Input(key="output_folder"), sg.FolderBrowse()]
],

frame_layout2 = [
    [sg.Text("Select File:", size=(10, 1)), sg.Input(key="map_input_path"), sg.FileBrowse()],
    [sg.Button("Generate Color Map CSV", size=(None, 1), expand_x=True)]  # Apply expand_x directly to the button, d'oh..
],

frame_layout3 = [
    [sg.Text("Select File:", size=(10, 1)), sg.Input(key="recolor_base_file"), sg.FileBrowse()],
    [sg.Button("Generate Recolors", size=(None, 1), expand_x=True)]
],

frame_layout4 = [
    [sg.Output(size=(50, 10), expand_x=True)],
    [sg.Column([[sg.Button("Open Output Folder", key="open_output_folder", expand_x=True, size=(None, 1))]], expand_x=True, pad=0),
                    sg.Column([[sg.Button("Exit", expand_x=True, size=(None, 1))]], expand_x=True,pad=0)]
]

layout = [
    [
        sg.Column([
            [sg.Frame('SUMMARY', frame_layout_summary, expand_y=True)],
            [sg.Frame('DOCUMENTATION', frame_layout_documentation, expand_x=True)],
        ], vertical_alignment='top', expand_y=True),  # vertical_alignment='top' goes here, come on remember that
        sg.Column([
            [sg.Frame('INSTRUCTIONS', frame_layout_instructions, expand_y=True,expand_x=True)],
            [sg.Frame('OUTPUT FOLDER', frame_layout1, expand_x=True)],
            [sg.Frame('OPTIONAL: COLOR MAP INPUT PNG', frame_layout2, expand_x=True)],
            [sg.Frame('BASE RECOLOR PNG', frame_layout3, expand_x=True)],
            [sg.Frame('OUTPUT LOG', frame_layout4, expand_x=True)],
        ],vertical_alignment='top')
    ]
]



def select_error_handler(missing_value):
    """Handles errors caused my missing selections (e.g. output folder, etc)

    Args:
        missing_value (string): passes which value is missing and should be alerted
    """
    
    error_message = f"Please select {missing_value} and try again."
    print(error_message)
    sg.popup(error_message, title="Error", button_color=('white', 'firebrick3'))
    return
    

def handle_generate_color_map(values, window):
    """Handles the 'Generate Color Map CSV' button."""
    map_input_path = values["map_input_path"]
    output_folder = values["output_folder"]
    colormap_filename = "color_map.csv"
    
    if not output_folder:
        select_error_handler("an Output Folder")
        return
    
    if not map_input_path:
        select_error_handler("a Color Map Input File")
        return

    color_map_output_path = os.path.join(output_folder, colormap_filename)
    try:
        colormap_gen.create_color_map(map_input_path, color_map_output_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        sg.popup_error(f"An error occurred: {e}", title="Error") #popup added

def handle_generate_recolors(values, window):
    """Handles the 'Generate Recolors' button."""
    recolor_base_file = values["recolor_base_file"]
    output_folder = values["output_folder"]
    colormap_filename = "color_map.csv"

    if not output_folder:
        select_error_handler("an Output Folder")
        return
    
    if not recolor_base_file:
        select_error_handler("a Recolor Base File")
        return

    color_map_path = os.path.join(output_folder, colormap_filename)

    if not os.path.exists(color_map_path):
        print(f"Warning: {colormap_filename} not found in the output folder.")
        sg.popup_error(f"{colormap_filename} not found in the output folder.", title="File Not Found") #popup added
        return

    try:
        df = pd.read_csv(color_map_path)
        if df.empty:
            print(f"Warning: {colormap_filename} is empty.")
            sg.popup_error(f"{colormap_filename} is empty.", title="Data Error") #popup added
            return
    except Exception as e:
        print(f"An error occurred while reading {colormap_filename}: {e}")
        sg.popup_error(f"An error occurred while reading {colormap_filename}: {e}", title="File Error") #popup added
        return

    try:
        colorswap_util.swap_colors(color_map_path, recolor_base_file, output_folder)
    except Exception as e:
        print(f"An error occurred: {e}")
        sg.popup_error(f"An error occurred: {e}", title="Error") #popup added

def handle_open_output_folder(values):
    """Handles the 'Open Output Folder' button."""
    output_folder = values["output_folder"]
    if output_folder:
        try:
            os.startfile(output_folder)
        except FileNotFoundError:
            print(f"Error: Output folder not found: {output_folder}")
            sg.popup_error(f"Output folder not found: {output_folder}", title="Folder Error") #popup added
        except Exception as e:
            print(f"An error occurred while opening the folder: {e}")
            sg.popup_error(f"An error occurred while opening the folder: {e}", title="Error") #popup added

# Create the window
window = sg.Window("Image Recolor Tool", layout)

# Main event loop
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break
    elif event == "Generate Color Map CSV":
        handle_generate_color_map(values, window)
    elif event == "Generate Recolors":
        handle_generate_recolors(values, window)
    elif event == "open_output_folder":
        handle_open_output_folder(values)
    elif event == "Open Documentation Link in Browser":
        open_readme()

# Close the window
window.close()