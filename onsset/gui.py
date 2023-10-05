import tkinter

import runner
# import sys
# sys.path.append('gui')
from visualization import init_vis_charts, init_vis_map
from scenario import init_scenario
from config import init_config

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, PhotoImage

# https://m2.material.io/design/color/the-color-system.html#tools-for-picking-colors
# Main = "#0277BD"

import pandas as pd

primary_color = "#0288D1"
secondary_color = "white"

# Define basic parameters of the interface
root = tk.Tk()
root.geometry("900x700")
root.pack_propagate(False)

root.iconphoto(False, PhotoImage(file=r'C:\GitHub\ResourceMatters\onsset\resources\onsset_logo_3.png'))
root.resizable(True, True)
root.minsize(900, 700)
root.title('OnSSET - The Open Source Spatial Electrification Tool')
#root['bg'] = primary_color  # "#4a98ff"  # Background color

my_notebook = ttk.Notebook(root)
my_notebook.pack(fill="both", expand=1)

# The tabs of the interface
info_tab = tk.Frame(my_notebook, width=900, height=700, bg=primary_color)
#info_tab.pack(fill="both", expand=1)

config_tab = tk.Frame(my_notebook, width=900, height=700, bg=primary_color)
config_tab.pack(fill="both", expand=1)
init_config(config_tab, primary_color, secondary_color)

scenario = tk.Frame(my_notebook, width=900, height=700, bg=primary_color)
# vsb = tk.Scrollbar(scenario, orient="vertical", command=scenario.yview())
# vsb.pack(side="right", fill="y")
# scenario.configure(yscrollcommand=vsb.set)

# myscrollbar = tk.Scrollbar(scenario, orient="vertical")
# myscrollbar.pack(side="right", fill="y")
# scenario.configure(scrollregion=scenario.bbox("all"))
init_scenario(scenario, runner, primary_color, secondary_color)

results_map = tk.Frame(my_notebook, width=900, height=700, bg=primary_color)
init_vis_map(results_map)

results_tables = tk.Frame(my_notebook, width=900, height=700, bg=primary_color)
init_vis_charts(results_tables)

gis_extraction = tk.Frame(my_notebook, width=900, height=700, bg=primary_color)

#my_notebook.add(info_tab, text='Info')
my_notebook.add(config_tab, text='Calibration')
my_notebook.add(scenario, text='Run scenario')
# my_notebook.add(results_map, text='Visualize results')
# my_notebook.add(results_tables, text='Visualize summary charts')
#my_notebook.add(gis_extraction, text='GIS data extraction')

root.mainloop()

