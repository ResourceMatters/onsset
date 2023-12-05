import threading
import time
import traceback
from tkinter import ttk
from tkinter.filedialog import asksaveasfile

import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# try:
#     from onsset.runner_modern import * # WHEN running pyinstaller
# except ModuleNotFoundError:
#     from runner_modern import run_scenario
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

    def csv_File_dialog(self):
        filename = filedialog.askopenfilename(title="Select the csv file with GIS data")
        return filename

    def load_csv_data(self):
        file_path = self.csv_File_dialog()

        if file_path[-3:] == 'csv':
            try:
                csv_filename = r"{}".format(file_path)
                onsseter = SettlementProcessor(csv_filename)
                return onsseter
            except ValueError:
                CTkMessagebox(title='Error', message="Could not load file", icon="warning")
                return None
            except FileNotFoundError:
                CTkMessagebox(title='Error', message=f"Could not find the file {file_path}", icon="warning")
                return None
        else:
            CTkMessagebox(title='Error', message=f"Only csv files can be used", icon="warning")
            return None

    def calibrate(self):
        # global calib_df
        CTkMessagebox(title='OnSSET', message='Open the CSV file with extracted GIS data')

        try:
            onsseter = self.load_csv_data()
            start_year = int(self.e1.get())
            start_year_pop = float(self.e2.get())
            urban_ratio_start_year = float(self.e3.get())
            elec_rate = float(self.e4.get())
            elec_rate_urban = float(self.e5.get())
            elec_rate_rural = float(self.e6.get())
            min_night_light = float(self.e14.get())
            min_pop = float(self.e15.get())
            max_transformer_dist = float(self.e16.get())
            max_mv_dist = float(self.e17.get())
            max_hv_dist = float(self.e18.get())
            hh_size_urban = float(self.e19.get())
            hh_size_rural = float(self.e20.get())

            # RUN_PARAM: these are the annual household electricity targets
            tier_1 = 38.7  # 38.7 refers to kWh/household/year. It is the mean value between Tier 1 and Tier 2
            tier_2 = 219
            tier_3 = 803
            tier_4 = 2117
            tier_5 = 2993

            onsseter.prepare_wtf_tier_columns(hh_size_rural, hh_size_urban,
                                              tier_1, tier_2, tier_3, tier_4, tier_5)

            onsseter.condition_df()

            onsseter.df['GridPenalty'] = onsseter.grid_penalties(onsseter.df)

            onsseter.df['WindCF'] = onsseter.calc_wind_cfs()

            onsseter.calibrate_current_pop_and_urban(start_year_pop, urban_ratio_start_year)

            elec_modelled, rural_elec_ratio, urban_elec_ratio = \
                onsseter.elec_current_and_future(elec_rate, elec_rate_urban, elec_rate_rural, start_year,
                                                 min_night_lights=min_night_light,
                                                 min_pop=min_pop,
                                                 max_transformer_dist=max_transformer_dist,
                                                 max_mv_dist=max_mv_dist,
                                                 max_hv_dist=max_hv_dist)
            self.button_save_calib.configure(state='normal')
            self.calib_df = onsseter.df

            urban_pop = onsseter.df.loc[onsseter.df[SET_URBAN] == 2, SET_POP_CALIB].sum()
            total_pop = onsseter.df[SET_POP_CALIB].sum()
            urban_pop_ratio = urban_pop / total_pop

            CTkMessagebox(title='OnSSET', width=600,
                          message='Calibration completed! \n'
                                  f'The calibrated total electrification rate was {round(elec_modelled, 2)} \n'
                                  f'The calibrated urban electrification rate was {round(urban_elec_ratio, 2)} \n'
                                  f'The calibrated rural electrification rate was {round(rural_elec_ratio, 2)} \n'
                                  f'The calibrated urban ratio was {round(urban_pop_ratio, 2)} \n')
            self.stop_progress()
            return onsseter.df
        # except ValueError:
        #     CTkMessagebox(title='OnSSET', message='Something went wrong, check the input variables!', icon='warning')
        except Exception as e:
            msg = CTkMessagebox(title='OnSSET', message='An error occured', option_1='Close',
                                option_2='Display error message', icon='warning')

            if msg.get() == 'Display error message':
                self.error_popup(e)
        self.stop_progress()

    def error_popup(self, error):
        def save_error(error):
            path = asksaveasfile(filetypes=[("txt file", ".txt")], defaultextension=".txt")

            # with open(path.name, "w") as f:
            #     traceback.TracebackException.from_exception(error).print(file=f)

            with open(path.name, 'a') as f:
                f.write(str(error))
                f.write(traceback.format_exc())

        popup = CTkToplevel()
        popup.geometry('600x300')
        popup.title('Error message')
        popup.attributes('-topmost', 'true')

        error_frame = CTkTextbox(popup, wrap='none')
        error_frame.insert("0.0", traceback.format_exc())
        error_frame.place(relwidth=1, relheight=1)

        save_button = CTkButton(popup, text='Save error message', command=lambda: save_error(error))
        save_button.place(relx=0.5, rely=0.9, anchor='s')

    def run_calibration(self):
        self.start_progress()
        try:
            threading.Thread(target=self.calibrate, daemon=True).start()
        except Exception as e:
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
        self.mg_inputs = None
        self.standalone_inputs = None
        self.south_grid_inputs = None
        self.general_inputs = None
        self.east_grid_inputs = None
        self.west_grid_inputs = None
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

        def create_entry_boxes(frame_label, info_dict, output_dict):
            # Frame for south grid parameters
            frame_label = CTkLabel(self, text=frame_label)
            frame_label.pack(padx=40, fill='x')

            frame = CTkFrame(self, border_width=5)
            frame.pack(pady=(0, 10), padx=40, fill='x')

            i = 0
            for key in list(info_dict):
                if i == 0:
                    y = (10, 0)
                elif i == len(info_dict) - 1:
                    y = (0, 10)
                else:
                    y = (0, 0)
                info = info_dict[key]
                label = CTkLabel(frame, text=info[0])
                label.grid(row=i, column=0, sticky='w', padx=10, pady=y)
                if type(info[1]) == list:
                    entry = CTkOptionMenu(frame, values=info[1])
                else:
                    entry = CTkEntry(frame)
                    entry.insert(10, str(info[1]))
                entry.grid(row=i, column=1, sticky='w', pady=y)
                output_dict[key] = entry

                try:
                    description = CTkLabel(frame, text=info[2])
                    description.grid(row=i, column=2, sticky='w', padx=10, pady=y)
                except:
                    pass

                i += 1

        # Define and create general parameters
        general_dict = {
            'start_year': ("Start year", 2020, 'Write the start year of the analysis'), 
            'end_year': ("End year", 2030, 'Write the end year of the analysis'),
            'intermediate_year': ('Intermediate year', 2025),
            'elec_target': ('Electrification rate target', 1, 'E.g. 1 for 100% electrification rate or 0.80 for 80% electrification rate'),
            'intermediate_elec_target': ('Electrification rate target (Intermediate year)', 0.75, 'E.g. for a target electrification rate of 75%, enter 0.75'),
            'end_year_pop': ('End year population', "", 'Write the population in the end year of the analysis (e.g. 2030)'),
            'end_year_urban': ("Urban ratio (end year)", "", 'Write the urban population population ratio in the end year (e.g. 2030)'),
            'hh_size_urban': ('Urban household size', 5, 'Write the number of people per household in urban areas'),
            'hh_size_rural': ('Rural household size', 5, 'Write the number of people per household in rural areas'),
            'discount_rate': ('Discount rate', 0.08, 'Write the discount rate'),
            'urban_tier': ("Urban residential demand", ["Low", "Medium", "High", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"]),
            'rural_tier': ("Rural residential demand", ["Low", "Medium", "High", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"]),
            'industrial_demand': ('Industrial demand', ["Low", "Medium", "High"]),
            'other_demand': ('Other demand', ["Low", "Medium", "High"])
        }

        self.general_inputs = {}

        create_entry_boxes("Enter general parameters", general_dict, self.general_inputs)

        # Define and create south grid parameters
        south_grid_dict = {
            'grid_generation_cost': ('Grid generation cost', 0.05, 'This is the grid electricity generation cost (USD/kWh)'),
            'grid_losses': (
            'Grid T&D losses', 0.05, 'The fraction of electricity lost in transmission and distribution (percentage)'),
            'grid_capacity_investment_cost': ('Grid capacity investment cost', 2000, 'The cost in USD/kW for generation capacity upgrades of the grid'),
            'max_connections': ('Max annual new grid-connections', 999999999, 'This is the maximum amount of new households that can be connected to the grid in one year (thousands)'),
            'max_capacity': ('Max annual new grid generation capacity (MW)', 999999999, 'This is the maximum generation capacity that can be added to the grid in one year (MW)')
                           }

        self.south_grid_inputs = {}

        create_entry_boxes('Enter parameters for the south grid', south_grid_dict, self.south_grid_inputs)

        # Define and create east grid parameters
        east_grid_dict = {
            'grid_generation_cost': ('Grid generation cost', 0.05, 'This is the grid electricity generation cost (USD/kWh)'),
            'grid_losses': (
            'Grid T&D losses', 0.05, 'The fraction of electricity lost in transmission and distribution (percentage)'),
            'grid_capacity_investment_cost': ('Grid capacity investment cost', 2000, 'The cost in USD/kW for generation capacity upgrades of the grid'),
            'max_connections': ('Max annual new grid-connections', 999999999, 'This is the maximum amount of new households that can be connected to the grid in one year (thousands)'),
            'max_capacity': ('Max annual new grid generation capacity (MW)', 999999999, 'This is the maximum generation capacity that can be added to the grid in one year (MW)')
                           }

        self.east_grid_inputs = {}

        create_entry_boxes('Enter parameters for the east grid', east_grid_dict, self.east_grid_inputs)

        # Define and create west grid parameters
        west_grid_dict = {
            'grid_generation_cost': ('Grid generation cost', 0.05, 'This is the grid electricity generation cost (USD/kWh)'),
            'grid_losses': (
            'Grid T&D losses', 0.05, 'The fraction of electricity lost in transmission and distribution (percentage)'),
            'grid_capacity_investment_cost': ('Grid capacity investment cost', 2000, 'The cost in USD/kW for generation capacity upgrades of the grid'),
            'max_connections': ('Max annual new grid-connections', 999999999, 'This is the maximum amount of new households that can be connected to the grid in one year (thousands)'),
            'max_capacity': ('Max annual new grid generation capacity (MW)', 999999999, 'This is the maximum generation capacity that can be added to the grid in one year (MW)'),
            'intensification_dist': ('Intensification', 0, 'Buffer distance (km) from the current grid network for automatic connection to the grid')
                           }

        self.west_grid_inputs = {}

        create_entry_boxes('Enter parameters for the west grid', west_grid_dict, self.west_grid_inputs)

        standalone_dict = {
            'sa_cost_1': ('Investment cost (1-20 W)', 9620, 'Stand-alone PV capital cost (USD/kW) for household systems under 20 W'),
            'sa_cost_2': ('Investment cost (21-50 W)', 8780, 'Stand-alone PV capital cost (USD/kW) for household systems between 21-50 W'),
            'sa_cost_3': ('Investment cost (51-100 W)', 6380, 'Stand-alone PV capital cost (USD/kW) for household systems between 51-100 W'),
            'sa_cost_4': ('Investment cost (101-1000 W)', 6380, 'Stand-alone PV capital cost (USD/kW) for household systems between 101-1000 W'),
            'sa_cost_5': ('Investment cost (>1 kW)', 6380, 'Stand-alone PV capital cost (USD/kW) for household systems over 1 kW')
        }

        self.standalone_inputs = {}

        create_entry_boxes('Enter parameters for stand-alone PV', standalone_dict, self.standalone_inputs)

        mini_grids_dict = {
            'mg_pv_capital_cost': ('PV mini-grid investment cost', 2950, 'PV mini-grid capital cost (USD/kW) as expected in the years of the analysis'),
            'mg_wind_capital_cost': ('Wind mini-grid investment cost', 3750, 'Wind mini-grid  capital cost (USD/kW) as expected in the years of the analysis'),
            'mg_hydro_capital_cost': ('Hydro mini-grid investment cost', 3000, 'Hydro mini-grid  capital cost (USD/kW) as expected in the years of the analysis')
        }

        self.mg_inputs = {}

        create_entry_boxes('Enter parameters for renewable mini-grids', mini_grids_dict, self.mg_inputs)

        # Bottom Frame for running and saving scenario
        bottom_frame = CTkFrame(self, height=75, border_width=5)
        bottom_frame.pack(fill='x', pady=20, padx=40)

        # Run scenario button
        self.run_button = CTkButton(bottom_frame, text="Run scenario", command=lambda: self.run())
        self.run_button.place(relx=0.2, rely=0.3)

        # Save results button
        self.button_save_results = CTkButton(bottom_frame, text="Save result files", command=lambda: self.save_results(), state='disabled')
        self.button_save_results.place(relx=0.6, rely=0.3)

    def retrieve_inputs(self):

        self.start_year = int(self.general_inputs['start_year'].get())
        self.intermediate_year = int(self.general_inputs['intermediate_year'].get())
        self.end_year = int(self.general_inputs['end_year'].get())
        self.intermediate_electrification_target = float(self.general_inputs['intermediate_elec_target'].get())
        self.end_year_electrification_rate_target = float(self.general_inputs['elec_target'].get())
        self.disc_rate = float(self.general_inputs['discount_rate'].get())
        self.pop_future = float(self.general_inputs['end_year_pop'].get())
        self.urban_future = float(self.general_inputs['end_year_urban'].get())
        self.urban_hh_size = float(self.general_inputs['hh_size_urban'].get())
        self.rural_hh_size = float(self.general_inputs['hh_size_rural'].get())

        self.grid_losses_ouest = float(self.west_grid_inputs['grid_losses'].get())
        self.grid_power_plants_capital_cost_ouest = float(self.west_grid_inputs['grid_capacity_investment_cost'].get())
        self.grid_generation_cost_ouest = float(self.west_grid_inputs['grid_generation_cost'].get())
        self.annual_new_grid_connections_limit_ouest = float(self.west_grid_inputs['max_connections'].get())
        self.annual_grid_cap_gen_limit_ouest = float(self.west_grid_inputs['max_capacity'].get())
        self.auto_intensification_ouest = float(self.west_grid_inputs['intensification_dist'].get())

        rural_tier_text = self.general_inputs['rural_tier'].get()
        urban_tier_text = self.general_inputs['urban_tier'].get()
        industrial_demand_text = self.general_inputs['industrial_demand'].get()
        other_demand_text = self.general_inputs['other_demand'].get()

        tier_dict = {'Tier 1': 1,
                     'Tier 2': 2,
                     'Tier 3': 3,
                     'Tier 4': 4,
                     'Tier 5': 5,
                     'Low': 6,
                     'Medium': 7,
                     'High': 8}

        other_demand_dict = {'Low': 0,
                             'Medium': 1,
                             'High': 2}

        self.rural_tier = tier_dict[rural_tier_text]
        self.urban_tier = tier_dict[urban_tier_text]
        self.industrial_demand = other_demand_dict[industrial_demand_text]
        self.social_productive_demand = other_demand_dict[other_demand_text]

    def error_popup(self, error):
        def save_error(error):
            path = asksaveasfile(filetypes=[("txt file", ".txt")], defaultextension=".txt")

            # with open(path.name, "w") as f:
            #     traceback.TracebackException.from_exception(error).print(file=f)

            with open(path.name, 'a') as f:
                f.write(str(error))
                f.write(traceback.format_exc())

        popup = CTkToplevel()
        popup.geometry('600x300')
        popup.title('Error message')
        popup.attributes('-topmost', 'true')

        error_frame = CTkTextbox(popup, wrap='none')
        error_frame.insert("0.0", traceback.format_exc())
        error_frame.place(relwidth=1, relheight=1)

        save_button = CTkButton(popup, text='Save error message', command=lambda: save_error(error))
        save_button.place(relx=0.5, rely=0.9, anchor='s')

    def run(self):
        self.start_progress()

        try:
            self.retrieve_inputs()
            new_thread = threading.Thread(target=self.run_scenario, daemon=True)
            new_thread.start()
        except FileNotFoundError:
            CTkMessagebox(title='OnSSET', message='No csv file selected, Browse a file', icon='warning')
            self.stop_progress()
        except AttributeError:
            CTkMessagebox(title='OnSSET', message='No csv file selected, Browse a file', icon='warning')
            self.stop_progress()
        # except ValueError:
        #     CTkMessagebox(title='OnSSET', message='Something went wrong, check the input variables!', icon='warning')
        #     self.stop_progress()
        # except:
        #     CTkMessagebox(title='OnSSET', message='Something went wrong check the error file (TO BE ADDED)', icon='warning')
        #     self.stop_progress()

    def run_scenario(self):
        try:
            settlements_in_csv = self.filename
            onsseter = SettlementProcessor(settlements_in_csv)

            onsseter.df['HealthDemand'] = 0
            onsseter.df['EducationDemand'] = 0
            onsseter.df['AgriDemand'] = 0
            onsseter.df['CommercialDemand'] = 0
            onsseter.df['HeavyIndustryDemand'] = 0

            start_year = self.start_year
            intermediate_year = self.intermediate_year
            end_year = self.end_year

            # ToDo
            gis_grid_extension = False
            max_grid_extension_dist = 50

            # South grid specifications
            auto_intensification_sud = 0
            annual_new_grid_connections_limit_sud = 999999999
            annual_grid_cap_gen_limit_sud = 999999999

            # East grid specifications
            auto_intensification_est = 0
            annual_new_grid_connections_limit_est = 999999999
            annual_grid_cap_gen_limit_est = 999999999
            grid_generation_cost_est = 0.07
            grid_power_plants_capital_cost_est = 2000
            grid_losses_est = 0.08

            # Here the scenario run starts

            if self.social_productive_demand == 1:
                onsseter.df['HealthDemand'] = onsseter.df['health_dem_low']
                onsseter.df['EducationDemand'] = onsseter.df['edu_dem_low']
                onsseter.df['AgriDemand'] = onsseter.df['agri_dem_low']
                onsseter.df['CommercialDemand'] = onsseter.df['prod_dem_low']
            elif self.social_productive_demand == 2:
                onsseter.df['HealthDemand'] = onsseter.df['health_dem_mid']
                onsseter.df['EducationDemand'] = onsseter.df['edu_dem_mid']
                onsseter.df['AgriDemand'] = onsseter.df['agri_dem_mid']
                onsseter.df['CommercialDemand'] = onsseter.df['prod_dem_mid']
            elif self.social_productive_demand == 3:
                onsseter.df['HealthDemand'] = onsseter.df['health_dem_high']
                onsseter.df['EducationDemand'] = onsseter.df['edu_dem_high']
                onsseter.df['AgriDemand'] = onsseter.df['agri_dem_high']
                onsseter.df['CommercialDemand'] = onsseter.df['prod_dem_high']

            if self.industrial_demand == 1:
                onsseter.df['HeavyIndustryDemand'] = onsseter.df['ind_dem_low']
            elif self.industrial_demand == 2:
                onsseter.df['HeavyIndustryDemand'] = onsseter.df['ind_dem_mid']
            elif self.industrial_demand == 3:
                onsseter.df['HeavyIndustryDemand'] = onsseter.df['ind_dem_high']

            if self.rural_tier == 6:
                onsseter.df['ResidentialDemandTierCustom'] = onsseter.df['hh_dem_low']
            elif self.rural_tier == 7:
                onsseter.df['ResidentialDemandTierCustom'] = onsseter.df['hh_dem_mid']
            elif self.rural_tier == 8:
                onsseter.df['ResidentialDemandTierCustom'] = onsseter.df['hh_dem_high']

            onsseter.df.drop(['hh_dem_low', 'hh_dem_mid', 'hh_dem_high', 'health_dem_low', 'health_dem_mid',
                              'health_dem_high', 'edu_dem_low', 'edu_dem_mid', 'edu_dem_high', 'agri_dem_low',
                              'agri_dem_mid', 'agri_dem_high', 'prod_dem_low', 'prod_dem_mid', 'prod_dem_high',
                              'ind_dem_low', 'ind_dem_mid', 'ind_dem_high'], axis=1, inplace=True)

            Technology.set_default_values(base_year=start_year,
                                          start_year=start_year,
                                          end_year=end_year,
                                          discount_rate=self.disc_rate)

            grid_calc_ouest = Technology(om_of_td_lines=0.1,
                                         distribution_losses=self.grid_losses_ouest,
                                         connection_cost_per_hh=150,
                                         base_to_peak_load_ratio=0.8,
                                         capacity_factor=1,
                                         tech_life=30,
                                         grid_capacity_investment=self.grid_power_plants_capital_cost_ouest,
                                         grid_price=self.grid_generation_cost_ouest)

            grid_calc_sud = Technology(om_of_td_lines=0.1,
                                       distribution_losses=float(self.south_grid_inputs['grid_losses'].get()),
                                       connection_cost_per_hh=150,
                                       base_to_peak_load_ratio=0.8,
                                       capacity_factor=1,
                                       tech_life=30,
                                       grid_capacity_investment=float(self.south_grid_inputs['grid_capacity_investment_cost'].get()),
                                       grid_price=float(self.south_grid_inputs['grid_generation_cost'].get()))

            grid_calc_est = Technology(om_of_td_lines=0.1,
                                       distribution_losses=grid_losses_est,
                                       connection_cost_per_hh=150,
                                       base_to_peak_load_ratio=0.8,
                                       capacity_factor=1,
                                       tech_life=30,
                                       grid_capacity_investment=grid_power_plants_capital_cost_est,
                                       grid_price=grid_generation_cost_est)

            mg_hydro_calc = Technology(om_of_td_lines=0.02,
                                       distribution_losses=0.05,
                                       connection_cost_per_hh=92,
                                       base_to_peak_load_ratio=0.85,
                                       capacity_factor=0.5,
                                       tech_life=35,
                                       capital_cost={float("inf"): 5000},
                                       om_costs=0.03,
                                       mini_grid=True)

            mg_wind_calc = Technology(om_of_td_lines=0.02,
                                      distribution_losses=0.05,
                                      connection_cost_per_hh=92,
                                      base_to_peak_load_ratio=0.85,
                                      capital_cost={float("inf"): 3750},
                                      om_costs=0.02,
                                      tech_life=20,
                                      mini_grid=True)

            mg_pv_calc = Technology(om_of_td_lines=0.02,
                                    distribution_losses=0.05,
                                    connection_cost_per_hh=92,
                                    base_to_peak_load_ratio=0.85,
                                    tech_life=25,
                                    om_costs=0.015,
                                    capital_cost={float("inf"): 2950},
                                    mini_grid=True)

            sa_pv_calc = Technology(base_to_peak_load_ratio=0.9,
                                    tech_life=25,
                                    om_costs=0.02,
                                    capital_cost={float("inf"): 6950,
                                                  1: 4470,
                                                  0.100: 6380,
                                                  0.050: 8780,
                                                  0.020: 9620
                                                  },
                                    standalone=True)

            mg_diesel_calc = Technology(om_of_td_lines=0.02,
                                        distribution_losses=0.05,
                                        connection_cost_per_hh=92,
                                        base_to_peak_load_ratio=0.85,
                                        capacity_factor=0.7,
                                        tech_life=20,
                                        om_costs=0.1,
                                        capital_cost={float("inf"): 672},
                                        mini_grid=True)

            sa_diesel_calc = Technology(base_to_peak_load_ratio=0.9,
                                        capacity_factor=0.5,
                                        tech_life=20,
                                        om_costs=0.1,
                                        capital_cost={float("inf"): 814},
                                        standalone=True)

            sa_diesel_cost = {'diesel_price': 0.8,
                              'efficiency': 0.28,
                              'diesel_truck_consumption': 14,
                              'diesel_truck_volume': 300}

            mg_diesel_cost = {'diesel_price': 0.8,
                              'efficiency': 0.33,
                              'diesel_truck_consumption': 33.7,
                              'diesel_truck_volume': 15000}

            annual_new_grid_connections_limit = {'Est': annual_new_grid_connections_limit_est,
                                                 'Sud': annual_new_grid_connections_limit_sud,
                                                 'Ouest': self.annual_new_grid_connections_limit_ouest}

            annual_grid_cap_gen_limit = {'Est': annual_grid_cap_gen_limit_est,
                                         'Sud': annual_grid_cap_gen_limit_sud,
                                         'Ouest': self.annual_grid_cap_gen_limit_ouest}

            grids = ['Est', 'Ouest', 'Sud']
            grid_calcs = [grid_calc_est, grid_calc_ouest, grid_calc_sud]
            auto_intensifications = [auto_intensification_est, self.auto_intensification_ouest, auto_intensification_sud]

            onsseter.df.loc[onsseter.df['Region'] == 'Haut-Katanga', 'ClosestGrid'] = 'Sud'
            onsseter.df.loc[onsseter.df['Region'] == 'Haut-Lomami', 'ClosestGrid'] = 'Sud'
            onsseter.df.loc[onsseter.df['Region'] == 'Lualaba', 'ClosestGrid'] = 'Sud'
            onsseter.df.loc[onsseter.df['Region'] == 'Tanganyka', 'ClosestGrid'] = 'Sud'
            onsseter.df.loc[onsseter.df['Region'] == 'Kasai-Central', 'ClosestGrid'] = 'Sud'
            onsseter.df.loc[onsseter.df['Region'] == 'Lomami', 'ClosestGrid'] = 'Sud'
            onsseter.df.loc[onsseter.df['Region'] == 'Kasai-Oriental', 'ClosestGrid'] = 'Sud'

            onsseter.df.loc[onsseter.df['Region'] == 'Kongo Central', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Kinshasa', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Kwango', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Kasai', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Kwilu', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Mai-Ndombe', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Tshuapa', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Equateur', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Mongala', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Sud-Ubangi', 'ClosestGrid'] = 'Ouest'
            onsseter.df.loc[onsseter.df['Region'] == 'Nord-Ubangi', 'ClosestGrid'] = 'Ouest'

            onsseter.df.loc[onsseter.df['Region'] == 'Sud-Kivu', 'ClosestGrid'] = 'Est'
            onsseter.df.loc[onsseter.df['Region'] == 'Nord-Kivu', 'ClosestGrid'] = 'Est'
            onsseter.df.loc[onsseter.df['Region'] == 'Maniema', 'ClosestGrid'] = 'Est'
            onsseter.df.loc[onsseter.df['Region'] == 'Sankuru', 'ClosestGrid'] = 'Est'
            onsseter.df.loc[onsseter.df['Region'] == 'Tshopo', 'ClosestGrid'] = 'Est'
            onsseter.df.loc[onsseter.df['Region'] == 'Ituri', 'ClosestGrid'] = 'Est'
            onsseter.df.loc[onsseter.df['Region'] == 'Bas-Uele', 'ClosestGrid'] = 'Est'
            onsseter.df.loc[onsseter.df['Region'] == 'Haut-Uele', 'ClosestGrid'] = 'Est'

            prioritization = 2

            # RUN_PARAM: One shall define here the years of analysis (excluding start year),
            # together with access targets per interval and timestep duration
            yearsofanalysis = [intermediate_year, end_year]
            eleclimits = {intermediate_year: self.intermediate_electrification_target,
                          end_year: self.end_year_electrification_rate_target}
            time_steps = {intermediate_year: intermediate_year - start_year, end_year: end_year - intermediate_year}

            onsseter.current_mv_line_dist()

            onsseter.project_pop_and_urban(self.pop_future, self.urban_future, start_year, end_year, intermediate_year)

            # if gis_grid_extension:
            #     onsseter.df = onsset_gis.create_geodataframe(onsseter.df)

            for year in yearsofanalysis:
                eleclimit = eleclimits[year]
                time_step = time_steps[year]

                onsseter.set_scenario_variables(year, self.rural_hh_size, self.urban_hh_size, time_step,
                                                start_year, self.urban_tier, self.rural_tier, 1)

                onsseter.diesel_cost_columns(sa_diesel_cost, mg_diesel_cost, year)

                sa_diesel_investment, sa_pv_investment, mg_diesel_investment, mg_pv_investment, mg_wind_investment, \
                    mg_hydro_investment = onsseter.calculate_off_grid_lcoes(mg_hydro_calc, mg_wind_calc, mg_pv_calc,
                                                                            sa_pv_calc, mg_diesel_calc,
                                                                            sa_diesel_calc, year, end_year, time_step)

                grid_investment = np.zeros(len(onsseter.df['X_deg']))
                grid_investment_combined = np.zeros(len(onsseter.df['X_deg']))
                onsseter.df[SET_LCOE_GRID + "{}".format(year)] = 99
                onsseter.df['grid_investment' + "{}".format(year)] = 0

                if gis_grid_extension:
                    print('')
                    onsseter.df['extension_distance_' + '{}'.format(year)] = 99

                    onsseter.pre_screening(eleclimit, year, time_step, prioritization, self.auto_intensification_ouest,
                                           auto_intensification_sud, auto_intensification_est)

                for grid, grid_calc, auto_intensification in zip(grids, grid_calcs, auto_intensifications):
                    grid_cap_gen_limit = time_step * annual_grid_cap_gen_limit[grid] * 1000
                    grid_connect_limit = time_step * annual_new_grid_connections_limit[grid] * 1000

                    grid_investment, grid_cap_gen_limit, grid_connect_limit = \
                        onsseter.pre_electrification(grid_calc.grid_price, year, time_step, end_year, grid_calc,
                                                     grid_cap_gen_limit, grid_connect_limit, grid_investment, grid)

                    if gis_grid_extension:
                        print('Running pathfinder for ' + grid + ' grid')

                        grid_investment = np.zeros(len(onsseter.df['X_deg']))
                        onsseter.max_extension_dist(year, time_step, end_year, start_year, grid_calc, grid)

                        # ToDo
                        # onsseter.df = onsset_gis.find_grid_path(onsseter.df, year, time_step, start_year, grid_connect_limit,
                        #                                         grid_cap_gen_limit, gis_cost_folder, grid,
                        #                                         max_grid_extension_dist,
                        #                                         out_folder, save_shapefiles)

                        onsseter.df[SET_LCOE_GRID + "{}".format(year)], onsseter.df[
                            SET_MIN_GRID_DIST + "{}".format(year)], \
                            onsseter.df[SET_ELEC_ORDER + "{}".format(year)], onsseter.df[
                            SET_MV_CONNECT_DIST], grid_investment = onsseter.elec_extension_gis(grid_calc,
                                                                                                max_grid_extension_dist,
                                                                                                year,
                                                                                                start_year,
                                                                                                end_year,
                                                                                                time_step,
                                                                                                new_investment=grid_investment,
                                                                                                grid_name=grid)
                        grid_investment_combined += np.nan_to_num(grid_investment[0])

                    else:
                        onsseter.df[SET_LCOE_GRID + "{}".format(year)], onsseter.df[
                            SET_MIN_GRID_DIST + "{}".format(year)], \
                            onsseter.df[SET_ELEC_ORDER + "{}".format(year)], onsseter.df[
                            SET_MV_CONNECT_DIST], grid_investment = onsseter.elec_extension(grid_calc,
                                                                                            max_grid_extension_dist,
                                                                                            year,
                                                                                            start_year, end_year,
                                                                                            time_step,
                                                                                            grid_cap_gen_limit,
                                                                                            grid_connect_limit,
                                                                                            grid_investment,
                                                                                            auto_intensification,
                                                                                            prioritization,
                                                                                            grid_name=grid)

                onsseter.df['grid_investment' + "{}".format(year)] = grid_investment_combined

                if gis_grid_extension:
                    grid_investment = grid_investment_combined

                onsseter.results_columns(year, time_step, prioritization, self.auto_intensification_ouest,
                                         auto_intensification_sud, auto_intensification_est)

                grid_investment = pd.DataFrame(grid_investment)

                onsseter.calculate_investments(sa_diesel_investment, sa_pv_investment, mg_diesel_investment,
                                               mg_pv_investment, mg_wind_investment,
                                               mg_hydro_investment, grid_investment, year)

                if gis_grid_extension:
                    print('')
                    onsseter.apply_limitations_gis(year, time_step)
                else:
                    onsseter.apply_limitations(eleclimit, year, time_step, prioritization, self.auto_intensification_ouest,
                                               auto_intensification_sud, auto_intensification_est)

                onsseter.calculate_new_capacity(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc,
                                                sa_diesel_calc, grid_calc_ouest, grid_calc_sud, grid_calc_est, year)

                onsseter.update_results_columns(year)

            for i in range(len(onsseter.df.columns)):
                if onsseter.df.iloc[:, i].dtype == 'float64':
                    onsseter.df.iloc[:, i] = pd.to_numeric(onsseter.df.iloc[:, i], downcast='float')
                elif onsseter.df.iloc[:, i].dtype == 'int64':
                    onsseter.df.iloc[:, i] = pd.to_numeric(onsseter.df.iloc[:, i], downcast='signed')

            self.df = onsseter.df
            CTkMessagebox(title='OnSSET', message='Scenario run finished!')
            self.button_save_results.configure(state='normal')
            self.run_button.configure(state='normal')
            self.dispaly_csv_button.configure(state='normal')
            self.progressbar.grid_forget()
        except FileNotFoundError:
            CTkMessagebox(title='OnSSET', message='No csv file selected, Browse a file', icon='warning')
            self.stop_progress()
        except AttributeError:
            CTkMessagebox(title='OnSSET', message='No csv file selected, Browse a file', icon='warning')
            self.stop_progress()
        # except ValueError:
        #     CTkMessagebox(title='OnSSET', message='Something went wrong, check the input variables!', icon='warning')
        #     self.stop_progress()
        except Exception as e:
            msg = CTkMessagebox(title='OnSSET', message='An error occured', option_1='Close',
                                option_2='Display error message', icon='warning')

            if msg.get() == 'Display error message':
                self.error_popup(e)
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
        self.load_map_button = CTkButton(self.tab('Map'), text='Load map', command=lambda: self.scatter_plot(self.map_frame, parent.scenario.df, parent.scenario.general_inputs['end_year'].get()))
        #self.load_map_button = CTkButton(self.tab('Map'), text='Load map', command=lambda: self.scatter_plot(self.map_frame, self.df, 2030))
        self.load_map_button.place(rely=0.925, relwidth=0.2, relx=0.5)
        self.background = CTkOptionMenu(self.tab('Map'), values=["OpenStreetMap", "Light", "Dark", "Colorful"])
        self.background.place(rely=0.925, relwidth=0.2, relx=0.25)
        self.background_label = CTkLabel(self.tab('Map'), text='Background map:')
        self.background_label.place(rely=0.925, relwidth=0.1, relx=0.13)

        self.chart_frame = CTkFrame(self.tab('Charts'))
        self.chart_frame.place(relheight=0.9, relwidth=1)
        self.load_chart_button = CTkButton(self.tab('Charts'), text='Load charts', command=lambda: self.vis_charts(self.chart_frame, parent.scenario.df, parent.scenario.general_inputs['intermediate_year'].get(), parent.scenario.general_inputs['end_year'].get()))
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