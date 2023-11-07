import threading
import time
from tkinter import ttk
from tkinter.filedialog import asksaveasfile

import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
try:
    from onsset.runner_modern import * # WHEN running pyinstaller
except ModuleNotFoundError:
    from runner_modern import *
from customtkinter import *
from PIL import ImageTk
from CTkMessagebox import CTkMessagebox
from onsset import *
from tkintermapview import TkinterMapView
import pandas as pd
import contextily as cx
import pyproj

global df
global end_year

set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(CTk):
    def __init__(self):
        super().__init__()

        self.filename = ""

        # configure window
        self.title("OnSSET - The Open Source Spatial Electrification Tool")
        self.geometry(f"{1200}x{580}")
        self.minsize(1100, 580)
        #self.iconpath = ImageTk.PhotoImage(file='logo.png')
        #self.wm_iconbitmap()
        #self.iconphoto(False, self.iconpath)

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.df = pd.DataFrame()
        self.end_year = 2022

        self.progressbar = CTkProgressBar(self, height=20, determinate_speed=0.3)
        self.progressbar.grid(column=1, row=4, padx=20, pady=(0, 20), sticky="nsew")
        self.progressbar.start()
        self.progressbar.grid_forget()

        self.calib = CalibrationTab(self, self.progressbar)
        self.scenario = ScenarioTab(self, self.df, self.end_year, self.progressbar)
        self.result = ResultsTab(self)

        self.sidebar_frame = Menu(self, self.calib, self.scenario, self.result)


class Menu(CTkFrame):
    def __init__(self, parent, calib, scenario, result):
        super().__init__(parent)
        self.configure(width=140)
        self.configure(corner_radius=0)
        self.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.grid_rowconfigure(5, weight=1)

        self.calib = calib
        self.scenario = scenario
        self.result = result

        self.create_widgets(parent.scenario.df)

        self.display_calibration() # Set this as the start tab

    def create_widgets(self, df):
        self.logo_label = CTkLabel(self, text="Menu", font=CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = CTkButton(self, text='Calibration', command=self.display_calibration)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = CTkButton(self, text='Run scenario', command=self.display_scenario)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = CTkButton(self, text='Visualize results', command=self.display_results)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        # self.sidebar_button_4 = CTkButton(self, text='Save results', command=lambda: self.save_results(df))
        # self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        self.appearance_mode_label = CTkLabel(self, text="Appearance Mode", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = CTkOptionMenu(self, values=["Light", "Dark"],command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 10))

        self.scaling_label = CTkLabel(self, text="Zoom", anchor="w")
        self.scaling_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = CTkOptionMenu(self, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        self.language_label = CTkLabel(self, text="Language", anchor="w")
        self.language_label.grid(row=10, column=0, padx=20, pady=(10, 0))
        self.language_optionmenu = CTkOptionMenu(self, values=["English", "French"])
        self.language_optionmenu.grid(row=11, column=0, padx=20, pady=(10, 20))

        # set default values
        #self.sidebar_button_3.configure(state="disabled")
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

    # def save_results(self, df):
    #     if df.size == 0:
    #         CTkMessagebox(title='OnSSET', message='No results to display, first run a scenario', icon='warning')
    #     else:
    #         file = asksaveasfile(filetypes=[("csv file", ".csv")], defaultextension=".csv")
    #         #df.to_csv(file, index=False)  # ToDo update to save scenarios and additional files
    #         CTkMessagebox(title='OnSSET', message='Result files saved successfully!')

    def display_scenario(self):
        self.calib.grid_forget()
        self.scenario.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")
        self.result.grid_forget()

    def display_calibration(self):
        self.calib.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")
        self.scenario.grid_forget()
        self.result.grid_forget()

    def display_results(self):
        self.calib.grid_forget()
        self.scenario.grid_forget()
        self.result.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        set_widget_scaling(new_scaling_float)


class CalibrationTab(CTkScrollableFrame):
    # Calibration frame
    def __init__(self, parent, progressbar):
        super().__init__(parent)
        self.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")
        self.progressbar = progressbar
        self.create_widgets()
    
    def create_widgets(self):

        self.start_year_frame = CTkFrame(self, border_width=5)
        self.start_year_frame.pack(pady=10, padx=40, fill='x')
    
        l1 = CTkLabel(self.start_year_frame, text="Start year")
        l1.grid(row=0, column=0, padx=10, pady=(10, 0))
        self.e1 = CTkEntry(self.start_year_frame)
        self.e1.grid(row=0, column=1, padx=10, pady=(10, 0))
        self.e1.insert(10, 2020)
    
        l2 = CTkLabel(self.start_year_frame, text="Start year population")
        l2.grid(row=1, column=0, padx=10)
        self.e2 = CTkEntry(self.start_year_frame)
        self.e2.grid(row=1, column=1, padx=10)
        self.e2.insert(10, "")
    
        l3 = CTkLabel(self.start_year_frame, text="Urban ratio (start year)")
        l3.grid(row=2, column=0, padx=10)
        self.e3 = CTkEntry(self.start_year_frame)
        self.e3.grid(row=2, column=1, padx=10)
    
        l4 = CTkLabel(self.start_year_frame, text="Total electrification rate (start year)")
        l4.grid(row=3, column=0, padx=10)
        self.e4 = CTkEntry(self.start_year_frame)
        self.e4.grid(row=3, column=1, padx=10)
    
        l5 = CTkLabel(self.start_year_frame, text="Urban electrification rate (start year)")
        l5.grid(row=4, column=0, padx=10)
        self.e5 = CTkEntry(self.start_year_frame)
        self.e5.grid(row=4, column=1, padx=10)
        self.e5.insert(10, "")
    
        l6 = CTkLabel(self.start_year_frame, text="Rural electrification rate (start year)")
        l6.grid(row=5, column=0, padx=10)
        self.e6 = CTkEntry(self.start_year_frame)
        self.e6.grid(row=5, column=1, padx=10)
        self.e6.insert(10, "")
    
        l19 = CTkLabel(self.start_year_frame, text="Urban household size")
        l19.grid(row=6, column=0, padx=10)
        self.e19 = CTkEntry(self.start_year_frame)
        self.e19.grid(row=6, column=1, padx=10)
        self.e19.insert(10, "5")
    
        l20 = CTkLabel(self.start_year_frame, text="Rural household size")
        l20.grid(row=7, column=0, padx=10)
        self.e20 = CTkEntry(self.start_year_frame)
        self.e20.grid(row=7, column=1, padx=10, pady=(0,10))
        self.e20.insert(10, "5")
    
        self.calib_text_frame = CTkFrame(self, border_width=5)
        self.calib_text_frame.pack(pady=10, padx=40, fill='x')
    
        l7 = CTkLabel(self.calib_text_frame, text="Calibration of currently electrified settlements")
        l7.grid(row=0, column=0, sticky='w', padx=10, pady=(10,0))
    
        l8 = CTkLabel(self.calib_text_frame,
                      text="The model calibrates which settlements are likely to be electrified in the start year, to match the national statistical values defined above.")
        l8.grid(row=1, column=0, sticky='w', padx=10)
    
        l13 = CTkLabel(self.calib_text_frame,
                       text="A settlement is considered to be electrified if it meets all of the following conditions:")
        l13.grid(row=2, column=0, sticky='w', padx=10)
    
        l9 = CTkLabel(self.calib_text_frame,
                      text="   - Has more night-time lights than the defined threshold (this is set to 0 by default)")
        l9.grid(row=3, column=0, sticky='w', padx=10)
    
        l10 = CTkLabel(self.calib_text_frame,
                       text="   - Is closer to the existing grid network than the distance limit")
        l10.grid(row=4, column=0, sticky='w', padx=10)
    
        l11 = CTkLabel(self.calib_text_frame, text="   - Has more population than the threshold")
        l11.grid(row=5, column=0, sticky='w', padx=10)
    
        l12 = CTkLabel(self.calib_text_frame,
                       text="First, define the threshold limits. Then run the calibration and check if the results seem okay. Else, redefine these thresholds and run again.")
        l12.grid(row=6, column=0, sticky='w', padx=10, pady=(0,10))
    
        self.calib_values_frame = CTkFrame(self, border_width=5)
        self.calib_values_frame.pack(pady=10, padx=40, fill='x')
    
        l14 = CTkLabel(self.calib_values_frame, text="Minimum night-time lights")
        l14.grid(row=0, column=0, padx=10, pady=(10,0))
        self.e14 = CTkEntry(self.calib_values_frame)
        self.e14.grid(row=0, column=1, padx=10, pady=(10,0))
        self.e14.insert(10, "0")
    
        l15 = CTkLabel(self.calib_values_frame, text="Minimum population")
        l15.grid(row=1, column=0, padx=10)
        self.e15 = CTkEntry(self.calib_values_frame)
        self.e15.grid(row=1, column=1, padx=10)
        self.e15.insert(10, "100")
    
        l16 = CTkLabel(self.calib_values_frame, text="Max distance to service transformer")
        l16.grid(row=2, column=0, padx=10)
        self.e16 = CTkEntry(self.calib_values_frame)
        self.e16.grid(row=2, column=1, padx=10)
        self.e16.insert(10, "1")
    
        l17 = CTkLabel(self.calib_values_frame, text="Max distance to MV lines")
        l17.grid(row=3, column=0, padx=10)
        self.e17 = CTkEntry(self.calib_values_frame)
        self.e17.grid(row=3, column=1, padx=10)
        self.e17.insert(10, "2")
    
        l18 = CTkLabel(self.calib_values_frame, text="Max distance to HV lines")
        l18.grid(row=4, column=0, padx=10)
        self.e18 = CTkEntry(self.calib_values_frame)
        self.e18.grid(row=4, column=1, padx=10, pady=(0,10))
        self.e18.insert(10, "25")
    
        self.bottom_frame = CTkFrame(self, height=75, border_width=5)
        self.bottom_frame.pack(fill='x', pady=10, padx=40)
    
        self.button_calib = CTkButton(self.bottom_frame, text="Run calibration", command=lambda: self.run_calibration())
        self.button_calib.place(relx=0.2, rely=0.3)
    
        self.button_save_calib = CTkButton(self.bottom_frame, text="Save calibrated file", command=self.save_calibrated,
                                           state='disabled')
        self.button_save_calib.place(relx=0.6, rely=0.3)

    def run_calibration(self):
        self.start_progress()
        try:
            #calibrate(self) # ToDo add in this file?
            threading.Thread(target=calibrate, args=(self,), daemon=True).start()
            #new_thread.start()
        except:
            self.stop_progress()


    def save_calibrated(self):
        def internal_save_calib():
            self.calib_df.to_csv(file, index=False)
            self.stop_progress()
            CTkMessagebox(title='OnSSET', message='Calibrated file saved successfully!')

        self.start_progress()
        file = asksaveasfile(filetypes=[("csv file", ".csv")], defaultextension=".csv")
        if file != None:
            threading.Thread(target=internal_save_calib, daemon=True).start()
        else:
            self.stop_progress()

    def start_progress(self):
        self.progressbar.grid(column=1, row=4, padx=20, pady=(0, 20), sticky="nsew")
        self.button_calib.configure(state='disabled')
        self.button_save_calib.configure(state='disabled')

    def stop_progress(self):
        self.progressbar.grid_forget()
        self.button_calib.configure(state='normal')
        self.button_calib.configure(state='normal')


class ScenarioTab(CTkScrollableFrame):
    # Scenario frame
    def __init__(self, parent, df, end_year, progressbar):
        super().__init__(parent)
        self.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")

        self.progressbar = progressbar
        self.df = df
        self.end_year = end_year
        self.create_widgets()

    def create_widgets(self):
        # Frame for TreeView
        treeview_label = CTkLabel(self, text='Calibrated CSV data')
        treeview_label.pack(padx=40, fill='x')
        frame1 = CTkFrame(self, height=200, border_width=5)
        # Treeview widget
        bg_color = '#7f7f7f'
        text_color = 'black'
        treestyle = ttk.Style()
        treestyle.theme_use('default')
        treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)

        self.tv1 = ttk.Treeview(frame1)
        treescrolly = CTkScrollbar(frame1, orientation="vertical", command=self.tv1.yview)
        treescrollx = CTkScrollbar(frame1, orientation="horizontal", command=self.tv1.xview)
        self.tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        treescrollx.pack(side="bottom", fill="x")
        treescrolly.pack(side="right", fill="y")
        self.tv1.pack(fill='both', expand=1)
        frame1.pack(pady=(0, 10), padx=40, fill='x')

        # Frame for selecting csv file
        select_csv_frame = CTkFrame(self, height=100, border_width=5)  # , text="Select the calibrated csv file")
        select_csv_frame.pack(pady=10, padx=40, fill='x')

        self.label_file = CTkLabel(select_csv_frame, text="No file selected, click the browse button!")
        self.label_file.place(rely=0.05, relx=0.05)

        # csv file buttons
        self.select_csv_button = CTkButton(select_csv_frame, text="Browse a file",
                                           command=lambda: self.csv_scenario_File_dialog())
        self.select_csv_button.place(rely=0.4, relx=0.2)

        self.dispaly_csv_button = CTkButton(select_csv_frame, text="Display File",
                                            command=lambda: self.load_scenario_csv_data())
        self.dispaly_csv_button.place(rely=0.4, relx=0.6)

        # Frame for general parameters
        general_param_label = CTkLabel(self, text="Enter general parameters")
        general_param_label.pack(padx=40, fill='x')

        general_frame = CTkFrame(self, border_width=5)
        general_frame.pack(pady=(0, 10), padx=40, fill='x')

        g_label_1 = CTkLabel(general_frame, text="Start year")
        g_label_1.grid(row=1, column=0, sticky='w', padx=10, pady=(10,0))
        self.start_year = CTkEntry(general_frame)
        self.start_year.grid(row=1, column=1, sticky='w', pady=(10,0))
        self.start_year.insert(10, 2020)

        g_label_2 = CTkLabel(general_frame, text="End year")
        g_label_2.grid(row=2, column=0, sticky='w', padx=10)
        self.end_year = CTkEntry(general_frame)
        self.end_year.grid(row=2, column=1, sticky='w')
        self.end_year.insert(10, 2030)

        g_label_3 = CTkLabel(general_frame, text="Intermediate year")
        g_label_3.grid(row=3, column=0, sticky='w', padx=10)
        self.intermediate_year = CTkEntry(general_frame)
        self.intermediate_year.grid(row=3, column=1, sticky='w')
        self.intermediate_year.insert(10, 2025)

        g_label_4 = CTkLabel(general_frame, text="Electrification rate target")
        g_label_4.grid(row=4, column=0, sticky='w', padx=10)
        self.elec_target = CTkEntry(general_frame)
        self.elec_target.grid(row=4, column=1, sticky='w')
        self.elec_target.insert(10, 1)

        g_label_5 = CTkLabel(general_frame, text="Electrification rate target (Intermediate year)")
        g_label_5.grid(row=5, column=0, sticky='w', padx=10)
        self.intermediate_elec_target = CTkEntry(general_frame)
        self.intermediate_elec_target.grid(row=5, column=1, sticky='w')
        self.intermediate_elec_target.insert(10, 0.8)

        g_label_6 = CTkLabel(general_frame, text="End year population")
        g_label_6.grid(row=6, column=0, sticky='w', padx=10)
        self.pop_end_year = CTkEntry(general_frame)
        self.pop_end_year.grid(row=6, column=1, sticky='w')
        self.pop_end_year.insert(10, "")

        g_label_7 = CTkLabel(general_frame, text="Urban ratio (end year)")
        g_label_7.grid(row=7, column=0, sticky='w', padx=10)
        self.urban_end_year = CTkEntry(general_frame)
        self.urban_end_year.grid(row=7, column=1, sticky='w')
        self.urban_end_year.insert(10, "")

        g_label_8 = CTkLabel(general_frame, text="Discount rate")
        g_label_8.grid(row=8, column=0, sticky='w', padx=10)
        self.discount_rate = CTkEntry(general_frame)
        self.discount_rate.grid(row=8, column=1, sticky='w')
        self.discount_rate.insert(10, "0.08")

        g_label_9 = CTkLabel(general_frame, text="Urban residential demand")
        g_label_9.grid(row=9, column=0, sticky='w', padx=10)
        self.urban_tier = CTkOptionMenu(general_frame, values=["Low", "Medium", "High", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"])
        self.urban_tier.grid(row=9, column=1, sticky='w')

        g_label_10 = CTkLabel(general_frame, text="Rural residential demand")
        g_label_10.grid(row=10, column=0, sticky='w', padx=10)
        self.rural_tier = CTkOptionMenu(general_frame, values=["Low", "Medium", "High", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"])
        self.rural_tier.grid(row=10, column=1, sticky='w')

        g_label_11 = CTkLabel(general_frame, text="Industrial demand")
        g_label_11.grid(row=11, column=0, sticky='w', padx=10)
        self.industrial_demand = CTkOptionMenu(general_frame, values=["Low", "Medium", "High"])
        self.industrial_demand.grid(row=11, column=1, sticky='w')

        g_label_12 = CTkLabel(general_frame, text="Other demand")
        g_label_12.grid(row=12, column=0, sticky='w', padx=10, pady=(0, 10))
        self.other_demand = CTkOptionMenu(general_frame, values=["Low", "Medium", "High"])
        self.other_demand.grid(row=12, column=1, sticky='w', pady=(0, 10))

        # Bottom Frame for running and saving scenario
        bottom_frame = CTkFrame(self, height=75, border_width=5)
        bottom_frame.pack(fill='x', pady=20, padx=40)

        # Run scenario button
        self.run_button = CTkButton(bottom_frame, text="Run scenario", command=lambda: self.run())
        self.run_button.place(relx=0.2, rely=0.3)

        # Save results button
        self.button_save_results = CTkButton(bottom_frame, text="Save result files", command=lambda: self.save_results(), state='disabled')
        self.button_save_results.place(relx=0.6, rely=0.3)

    def run(self):
        self.start_progress()
        try:
            new_thread = threading.Thread(target=run_scenario, args=(self, self.filename), daemon=True)
            new_thread.start()
        except FileNotFoundError:
            CTkMessagebox(title='OnSSET', message='No csv file selected, Browse a file', icon='warning')
            self.stop_progress()
        except AttributeError:
            CTkMessagebox(title='OnSSET', message='No csv file selected, Browse a file', icon='warning')
            self.stop_progress()
        except ValueError:
            CTkMessagebox(title='OnSSET', message='Something went wrong, check the input variables!', icon='warning')
            self.stop_progress()
        except:
            CTkMessagebox(title='OnSSET', message='Something went wrong check the error file (TO BE ADDED)', icon='warning')
            self.stop_progress()

    def save_results(self):
        def save_results_internal():
            file = asksaveasfile(filetypes=[("csv file", ".csv")], defaultextension=".csv")
            if file != None:
                self.start_progress()
                self.dispaly_csv_button.configure(state='disabled')
                self.df.to_csv(file, index=False)  # ToDo update to save scenarios and additional files
                CTkMessagebox(title='OnSSET', message='Result files saved successfully!')
                self.dispaly_csv_button.configure(state='normal')
            else:
                CTkMessagebox(title='OnSSET', message='No results saved')
            self.stop_progress()

        if self.df.size == 0:
            CTkMessagebox(title='OnSSET', message='No results to display, first run a scenario', icon='warning')
        else:
            threading.Thread(target=save_results_internal, args=(), daemon=True).start()

    def csv_scenario_File_dialog(self):
        self.filename = filedialog.askopenfilename(title="Select the calibrated csv file with GIS data")
        self.label_file.configure(text=self.filename)
        return None

    def load_scenario_csv_data(self):

        def internal_display_scenario():
            csv_filename = r"{}".format(self.filename)
            df = pd.read_csv(csv_filename)
            self.label_file.configure(text=self.filename + " opened!")
            self.clear_data()
            self.tv1["column"] = list(df.columns)
            self.tv1["show"] = "headings"
            for column in self.tv1["columns"]:
                self.tv1.heading(column, text=column)
            df_rows = df.to_numpy().tolist()
            for row in df_rows:
                self.tv1.insert("", "end", values=row)

        self.start_progress()
        prev_state = self.button_save_results.cget('state')
        self.button_save_results.configure(state='disabled')
        try:
            internal_display_scenario()
            #threading.Thread(target=internal_display_scenario, daemon=True).start()
        except ValueError:
            CTkMessagebox(title='Error', message="Could not load file", icon="warning")
        except FileNotFoundError:
            CTkMessagebox(title='Error', message=f"Could not find the file {self.filename}", icon="warning")
        except AttributeError:
            CTkMessagebox(title='Error', message="No CSV file selected", icon="warning")

        self.stop_progress()
        if prev_state == 'normal':
            self.button_save_results.configure(state='normal')


    def clear_data(self):
        self.tv1.delete(*self.tv1.get_children())

    def start_progress(self):
        self.progressbar.grid(column=1, row=4, padx=20, pady=(0, 20), sticky="nsew")
        self.button_save_results.configure(state='disabled')
        self.run_button.configure(state='disabled')
        self.dispaly_csv_button.configure(state='disabled')

    def stop_progress(self):
        self.progressbar.grid_forget()
        self.run_button.configure(state='normal')
        self.dispaly_csv_button.configure(state='normal')



class ResultsTab(CTkTabview):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")
        self.add('Map')
        self.add('Charts')

        #self.df = pd.read_csv(r'C:\DRC\gui_test\0_2_1_1_1_0\cd-0_2_1_1_1_0.csv')

        self.map_frame = CTkFrame(self.tab('Map'))
        self.map_frame.place(relheight=0.9, relwidth=1)
        self.load_map_button = CTkButton(self.tab('Map'), text='Load map', command=lambda: self.scatter_plot(self.map_frame, parent.scenario.df, parent.scenario.end_year.get()))
        #self.load_map_button = CTkButton(self.tab('Map'), text='Load map', command=lambda: self.scatter_plot(self.map_frame, self.df, 2030))
        self.load_map_button.place(rely=0.925, relwidth=0.2, relx=0.5)
        self.background = CTkOptionMenu(self.tab('Map'), values=["OpenStreetMap", "Light", "Dark", "Colorful"])
        self.background.place(rely=0.925, relwidth=0.2, relx=0.25)
        self.background_label = CTkLabel(self.tab('Map'), text='Background map:')
        self.background_label.place(rely=0.925, relwidth=0.1, relx=0.13)

        self.chart_frame = CTkFrame(self.tab('Charts'))
        self.chart_frame.place(relheight=0.9, relwidth=1)
        self.load_chart_button = CTkButton(self.tab('Charts'), text='Load charts', command=lambda: self.vis_charts(self.chart_frame, parent.scenario.df, parent.scenario.intermediate_year.get(), parent.scenario.end_year.get()))
        #self.load_chart_button = CTkButton(self.tab('Charts'), text='Load charts',command=lambda: self.vis_charts(self.chart_frame, self.df, 2025, 2030))
        self.load_chart_button.place(rely=0.925, relwidth=0.2, relx=0.4)


    def scatter_plot(self, map_frame, df, end_year):

        if df.size == 0:
            CTkMessagebox(title='OnSSET', message='No results to display, first run a scenario', icon='warning')
        else:
            if self.background.get() == "Colorful":
                background = cx.providers.CartoDB.Voyager
            elif self.background.get() == "Dark":
                background = cx.providers.CartoDB.DarkMatter
            elif self.background.get() == "OpenStreetMap":
                background = cx.providers.OpenStreetMap.Mapnik
            else:
                background = cx.providers.CartoDB.Positron

            # Define the EPSG:4326 and EPSG:3857 CRS
            crs_4326 = pyproj.CRS('EPSG:4326')
            crs_3857 = pyproj.CRS('EPSG:3857')

            # Create a transformer to convert coordinates
            transformer = pyproj.Transformer.from_crs(crs_4326, crs_3857, always_xy=True)

            # Apply the transformation and create new columns
            # Vectorized transformation using NumPy
            lon_lat = df[[SET_X_DEG, SET_Y_DEG]].to_numpy()
            x_3857, y_3857 = transformer.transform(lon_lat[:, 0], lon_lat[:, 1])

            # Add the new columns to the DataFrame
            df['x_3857'] = x_3857
            df['y_3857'] = y_3857

            fig, ax = plt.subplots()
            fig.set_facecolor("#7f7f7f")

            fig.set_size_inches(9,9)

            colors = {3: '#ffc700',
                      5: '#e628a0',
                      6: '#1b8f4d',
                      7: '#28e66d',
                      99: '#808080',
                      1: '#4e53de'}

            for key in colors.keys():
                ax.scatter(df.loc[df['FinalElecCode{}'.format(end_year)] == key, 'x_3857'],
                            df.loc[df['FinalElecCode{}'.format(end_year)] == key, 'y_3857'], color=colors[key],
                            marker='o',
                            s=(df.loc[df['FinalElecCode{}'.format(end_year)] == key, 'Pop2030'] / 100000 * 2))

            ax.axis('off')
            fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

            try:
                cx.add_basemap(plt, source=background)
            except:
                pass

            canvas = FigureCanvasTkAgg(fig, master=map_frame)
            canvas.draw()
            canvas.get_tk_widget().place(relx=0, relwidth=1, relheight=0.9)

            self.legend_frame = CTkFrame(map_frame, border_width=5, width=20, height=100, fg_color='#222021')
            self.legend_frame.place(rely=0.5, relx=1, anchor=E)
            self.label_1 = CTkLabel(self.legend_frame, text="Grid", font=CTkFont(size=14, weight='bold'), text_color='#4e53de')
            self.label_1.grid(row=0, column=0, padx=30, pady=10)
            self.label_3 = CTkLabel(self.legend_frame, text="Stand-alone PV", font=CTkFont(size=14, weight='bold'),
                                    text_color='#ffc700')
            self.label_3.grid(row=1, column=0, padx=30, pady=10)
            self.label_5 = CTkLabel(self.legend_frame, text="Mini-grid PV", font=CTkFont(size=14, weight='bold'), text_color='#e628a0')
            self.label_5.grid(row=2, column=0, padx=30, pady=10)
            self.label_6 = CTkLabel(self.legend_frame, text="Mini-grid Wind", font=CTkFont(size=14, weight='bold'),
                                    text_color='#1b8f4d')
            self.label_6.grid(row=3, column=0, padx=30, pady=10)
            self.label_6 = CTkLabel(self.legend_frame, text="Mini-grid Hydro", font=CTkFont(size=14, weight='bold'),
                                    text_color='#28e66d')
            self.label_6.grid(row=4, column=0, padx=30, pady=10)
            self.label_99 = CTkLabel(self.legend_frame, text="Unelectrified", font=CTkFont(size=14, weight='bold'),
                                     text_color='#808080')
            self.label_99.grid(row=5, column=0, padx=30, pady=10)

            try:
                self.toolbar.destroy()
            except AttributeError:
                pass
            self.toolbar = NavigationToolbar2Tk(canvas, map_frame)
            self.toolbar.place(rely=0.9, relheight=0.1, relwidth=1)

    def vis_charts(self, frame_charts, df, intermediate_year, end_year):

        if df.size == 0:
            CTkMessagebox(title='OnSSET', message='No results to display, first run a scenario', icon='warning')
        else:
            yearsofanalysis = [intermediate_year, end_year]

            techs = ["Grid", "SA_PV", "MG_PV", "MG_Wind", "MG_Hydro"]
            labels = ["Grid", "Stand-alone PV", "Mini-grid PV", "Mini-grid Wind", "Mini-grid Hydro"]
            colors = ['#4e53de', '#ffc700', '#e628a0', '#1b8f4d', '#28e66d']

            elements = []
            for year in yearsofanalysis:
                elements.append("Population{}".format(year))
                elements.append("NewConnections{}".format(year))
                elements.append("Capacity{}".format(year))
                elements.append("Investment{}".format(year))

            sumtechs = []
            for year in yearsofanalysis:
                sumtechs.extend(["Population{}".format(year) + t for t in techs])
                sumtechs.extend(["NewConnections{}".format(year) + t for t in techs])
                sumtechs.extend(["Capacity{}".format(year) + t for t in techs])
                sumtechs.extend(["Investment{}".format(year) + t for t in techs])

            summary = pd.Series(index=sumtechs, name='country')

            for year in yearsofanalysis:
                for t in techs:
                    summary.loc["Population{}".format(year) + t] = df.loc[
                        (df[SET_MIN_OVERALL + '{}'.format(year)] == t + '{}'.format(year)), SET_POP + '{}'.format(
                            year)].sum() / 1000000
                    summary.loc["NewConnections{}".format(year) + t] = df.loc[
                        (df[SET_MIN_OVERALL + '{}'.format(year)] == t + '{}'.format(year)) &
                        (df[SET_ELEC_FINAL_CODE + '{}'.format(year)] < 99), SET_NEW_CONNECTIONS + '{}'.format(year)].sum() / 1000000
                    summary.loc["Capacity{}".format(year) + t] = df.loc[(df[SET_MIN_OVERALL + '{}'.format
                    (year)] == t + '{}'.format(year)) &
                                                                        (df[SET_ELEC_FINAL_CODE + '{}'.format
                                                                        (year)] < 99), SET_NEW_CAPACITY + '{}'.format
                                                                        (year)].sum() / 1000
                    summary.loc["Investment{}".format(year) + t] = df.loc[
                        (df[SET_MIN_OVERALL + '{}'.format(year)] == t + '{}'.format(year)) & (
                                df[SET_ELEC_FINAL_CODE + '{}'.format
                                (year)] < 99), SET_INVESTMENT_COST + '{}'.format(year)].sum()

            index = techs + ['Total']
            columns = []
            for year in yearsofanalysis:
                columns.append("Population{}".format(year))
                columns.append("NewConnections{}".format(year))
                columns.append("Capacity{} (MW)".format(year))
                columns.append("Investment{} (million USD)".format(year))

            summary_table = pd.DataFrame(index=index, columns=columns)

            summary_table[columns[0]] = summary.iloc[0:5].astype(int).tolist() + [int(summary.iloc[0:5].sum())]
            summary_table[columns[1]] = summary.iloc[5:10].astype(int).tolist() + [int(summary.iloc[5:10].sum())]
            summary_table[columns[2]] = summary.iloc[10:15].astype(int).tolist() + [int(summary.iloc[10:15].sum())]
            summary_table[columns[3]] = [round(x / 1e4) / 1e2 for x in summary.iloc[15:20].astype(float).tolist()] + [
                round(summary.iloc[15:20].sum() / 1e4) / 1e2]
            summary_table[columns[4]] = summary.iloc[20:25].astype(int).tolist() + [int(summary.iloc[20:25].sum())]
            summary_table[columns[5]] = summary.iloc[25:30].astype(int).tolist() + [int(summary.iloc[25:30].sum())] + summary_table[columns[1]]
            summary_table[columns[6]] = summary.iloc[30:35].astype(int).tolist() + [int(summary.iloc[30:35].sum())] + summary_table[columns[2]]
            summary_table[columns[7]] = [round(x / 1e4) / 1e2 for x in summary.iloc[35:40].astype(float).tolist()] + [
                round(summary.iloc[35:40].sum() / 1e4) / 1e2] + summary_table[columns[3]]

            summary_plot = summary_table.drop(labels='Total', axis=0)
            fig_size = [10,8]
            plt.rcParams["figure.figsize"] = fig_size
            f, axarr = plt.subplots(2, 2)
            f.set_facecolor("#7f7f7f")
            f.subplots_adjust(wspace=0.35, hspace=0.35)

            font_size = 8
            plt.rcParams["figure.figsize"] = fig_size

            sns.barplot(x=summary_plot.index.tolist(), y=columns[4], data=summary_plot, ax=axarr[0, 0], palette=colors)
            axarr[0, 0].set_ylabel('Population (Million)', fontsize=9)
            axarr[0, 0].tick_params(labelsize=font_size)
            axarr[0, 0].set_facecolor('#7f7f7f')
            axarr[0, 0].set_xticklabels([])
            axarr[0, 0].yaxis.grid(True)
            axarr[0, 0].set_axisbelow(True)
            #axarr[0, 0].grid(True)
            sns.barplot(x=summary_plot.index.tolist(), y=columns[5], data=summary_plot, ax=axarr[0, 1], palette=colors)
            axarr[0, 1].set_ylabel('New Connections (Million)', fontsize=9)
            axarr[0, 1].tick_params(labelsize=font_size)
            axarr[0, 1].set_facecolor('#7f7f7f')
            axarr[0, 1].set_xticklabels([])
            axarr[0, 1].yaxis.grid(True)
            axarr[0, 1].set_axisbelow(True)
            sns.barplot(x=summary_plot.index.tolist(), y=columns[6], data=summary_plot, ax=axarr[1, 0], palette=colors)
            axarr[1, 0].set_ylabel('New capacity (MW)', fontsize=9)
            axarr[1, 0].tick_params(labelsize=font_size)
            axarr[1, 0].set_facecolor('#7f7f7f')
            axarr[1, 0].set_xticklabels([])
            axarr[1, 0].yaxis.grid(True)
            axarr[1, 0].set_axisbelow(True)
            sns.barplot(x=summary_plot.index.tolist(), y=columns[7], data=summary_plot, ax=axarr[1, 1], palette=colors)
            axarr[1, 1].set_ylabel('Investments (million USD)', fontsize=9)
            axarr[1, 1].tick_params(labelsize=font_size)
            axarr[1, 1].set_facecolor('#7f7f7f')
            axarr[1, 1].set_xticklabels([])
            axarr[1, 1].yaxis.grid(True)
            axarr[1, 1].set_axisbelow(True)

            canvas = FigureCanvasTkAgg(f, master=frame_charts)
            canvas.draw()
            canvas.get_tk_widget().place(relx=0.5, rely=0, relheight=0.9, relwidth=0.8, anchor=N)
            try:
                self.toolbar_2.destroy()
            except AttributeError:
                pass
            self.toolbar_2 = NavigationToolbar2Tk(canvas, frame_charts)
            self.toolbar_2.update()

            self.legend_frame = CTkFrame(frame_charts, border_width=5, width=20, height=100, fg_color='#222021')
            self.legend_frame.place(rely=0.5, relx=1, anchor=E)
            self.label_1 = CTkLabel(self.legend_frame, text="Grid", font=CTkFont(size=14, weight='bold'), text_color='#4e53de')
            self.label_1.grid(row=0, column=0, padx=30, pady=10)
            self.label_3 = CTkLabel(self.legend_frame, text="Stand-alone PV", font=CTkFont(size=14, weight='bold'), text_color='#ffc700')
            self.label_3.grid(row=1, column=0, padx=30, pady=10)
            self.label_5 = CTkLabel(self.legend_frame, text="Mini-grid PV", font=CTkFont(size=14, weight='bold'), text_color='#e628a0')
            self.label_5.grid(row=2, column=0, padx=30, pady=10)
            self.label_6 = CTkLabel(self.legend_frame, text="Mini-grid Wind", font=CTkFont(size=14, weight='bold'), text_color='#1b8f4d')
            self.label_6.grid(row=3, column=0, padx=30, pady=10)
            self.label_6 = CTkLabel(self.legend_frame, text="Mini-grid Hydro", font=CTkFont(size=14, weight='bold'), text_color='#28e66d')
            self.label_6.grid(row=4, column=0, padx=30, pady=10)
            # self.label_99 = CTkLabel(self.legend_frame, text="Unelectrified", font=CTkFont(size=14, weight='bold'), text_color='#808080')
            # self.label_99.grid(row=5, column=0, padx=30, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    app.quit()

# # Frame for off-grid technology costs
        # off_grid_frame = CTkFrame(self) #, text="Enter off-grid technology parameters")
        # off_grid_frame.pack(pady=10, padx=40, fill='x')
        #
        # l11 = CTkLabel(off_grid_frame, text="Diesel techs")
        # l11.grid(row=0, column=0, sticky='w')
        # e11 = CTkEntry(off_grid_frame)
        # e11.grid(row=0, column=1, sticky='w')
        # e11.insert(10, 0)
        #
        # l12 = CTkLabel(off_grid_frame, text="Diesel price")
        # l12.grid(row=1, column=0, sticky='w')
        # e12 = CTkEntry(off_grid_frame)
        # e12.grid(row=1, column=1, sticky='w')
        # e12.insert(10, 0.5)
        #
        # l13 = CTkLabel(off_grid_frame, text="Grid generation cost")
        # l13.grid(row=2, column=0, sticky='w')
        # e13 = CTkEntry(off_grid_frame)
        # e13.grid(row=2, column=1, sticky='w')
        # e13.insert(10, 0.05)
        #
        # l14 = CTkLabel(off_grid_frame, text="SA Diesel capital cost")
        # l14.grid(row=3, column=0, sticky='w')
        # e14 = CTkEntry(off_grid_frame)
        # e14.grid(row=3, column=1, sticky='w')
        # e14.insert(10, 938)
        #
        # l15 = CTkLabel(off_grid_frame, text="MG Diesel capital cost")
        # l15.grid(row=4, column=0, sticky='w')
        # e15 = CTkEntry(off_grid_frame)
        # e15.grid(row=4, column=1, sticky='w')
        # e15.insert(10, 721)
        #
        # l16 = CTkLabel(off_grid_frame, text="MG PV capital cost")
        # l16.grid(row=5, column=0, sticky='w')
        # e16 = CTkEntry(off_grid_frame)
        # e16.grid(row=5, column=1, sticky='w')
        # e16.insert(10, "2950")
        #
        # l17 = CTkLabel(off_grid_frame, text="MG Wind capital cost")
        # l17.grid(row=6, column=0, sticky='w')
        # e17 = CTkEntry(off_grid_frame)
        # e17.grid(row=6, column=1, sticky='w')
        # e17.insert(10, "3750")
        #
        # l18 = CTkLabel(off_grid_frame, text="MG Hydro capital cost")
        # l18.grid(row=7, column=0, sticky='w')
        # e18 = CTkEntry(off_grid_frame)
        # e18.grid(row=7, column=1, sticky='w')
        # e18.insert(10, "3000")
        #
        # l19 = CTkLabel(off_grid_frame, text="SA PV cost (<20 W)")
        # l19.grid(row=8, column=0, sticky='w')
        # e19 = CTkEntry(off_grid_frame)
        # e19.grid(row=8, column=1, sticky='w')
        # e19.insert(10, "9620")
        #
        # l20 = CTkLabel(off_grid_frame, text="SA PV cost (21-50 W)")
        # l20.grid(row=9, column=0, sticky='w')
        # e20 = CTkEntry(off_grid_frame)
        # e20.grid(row=9, column=1, sticky='w')
        # e20.insert(10, "8780")
        #
        # l21 = CTkLabel(off_grid_frame, text="SA PV cost (51-100 W)")
        # l21.grid(row=10, column=0, sticky='w')
        # e21 = CTkEntry(off_grid_frame)
        # e21.grid(row=10, column=1, sticky='w')
        # e21.insert(10, "6380")
        #
        # l22 = CTkLabel(off_grid_frame, text="SA PV cost (101-1000 W)")
        # l22.grid(row=11, column=0, sticky='w')
        # e22 = CTkEntry(off_grid_frame)
        # e22.grid(row=11, column=1, sticky='w')
        # e22.insert(10, "4470")
        #
        # l23 = CTkLabel(off_grid_frame, text="SA PV cost (>1000 W)                                      ",
        #                bg=secondary_color)
        # l23.grid(row=12, column=0, sticky='w')
        # e23 = CTkEntry(off_grid_frame)
        # e23.grid(row=12, column=1, sticky='w')
        # e23.insert(10, "6950")
        #
        # # Frame for T&D costs
        # td_frame = CTkLabelFrame(self, text="Enter T&D parameters")
        # td_frame.pack(pady=10, padx=40, fill='x')
        #
        # l24 = CTkLabel(td_frame, text="HV line cost")
        # l24.grid(row=0, column=0, sticky='w')
        # e24 = CTkEntry(td_frame)
        # e24.grid(row=0, column=1, sticky='w')
        # e24.insert(10, "53000")
        #
        # l25 = CTkLabel(td_frame, text="MV line cost                                                     ",
        #                bg=secondary_color)
        # l25.grid(row=1, column=0, sticky='w')
        # e25 = CTkEntry(td_frame)
        # e25.grid(row=1, column=1, sticky='w')
        # e25.insert(10, "7000")
        #
        # l26 = CTkLabel(td_frame, text="LV line cost")
        # l26.grid(row=3, column=0, sticky='w')
        # e26 = CTkEntry(td_frame)
        # e26.grid(row=3, column=1, sticky='w')
        # e26.insert(10, "4250")
        #
        # # Bottom Frame for running and saving scenario
        # bottom_frame = tk.Frame(self, height=20, bg=primary_color)
        # bottom_frame.pack(fill='x', pady=20)
        #
        # # Run scenario button
        # run_button = tk.Button(bottom_frame, text="Run scenario", command=lambda: run_scenarios())
        # run_button.place(relwidth=0.2, relx=0.2)
        #
        # # Save results button
        # button_save_calib = tk.Button(bottom_frame, text="Save result files", command=lambda: save_results(),
        #                               state='disabled')
        # button_save_calib.place(relwidth=0.2, relx=0.6)
        #
        # bottom_frame_2 = tk.Frame(canvas_frame, height=20, bg=primary_color)
        # bottom_frame_2.pack(fill='x', pady=20)