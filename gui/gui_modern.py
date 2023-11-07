from tkinter import ttk
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from runner_modern import *
from tkinter.filedialog import asksaveasfile
from customtkinter import *
from PIL import ImageTk
from CTkMessagebox import CTkMessagebox
import folium


global df
global end_year

techs = ["Grid", "SA_Diesel", "SA_PV", "MG_Diesel", "MG_PV", "MG_Wind", "MG_Hydro"]
colors = ['#73B2FF', '#EDD100', '#EDA800', '#1F6600', '#98E600', '#70A800', '#1FA800']

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
        self.iconpath = ImageTk.PhotoImage(file=r'C:\GitHub\ResourceMatters\onsset\resources\onsset_logo_3.png')
        self.wm_iconbitmap()
        self.iconphoto(False, self.iconpath)

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.df = pd.DataFrame()
        self.end_year = 2022

        self.calib = CalibrationTab(self)
        self.scenario = ScenarioTab(self, self.df, self.end_year)
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

    def save_results(self, df):
        if df.size == 0:
            CTkMessagebox(title='OnSSET', message='No results to display, first run a scenario', icon='warning')
        else:
            file = asksaveasfile(filetypes=[("csv file", ".csv")], defaultextension=".csv")
            #df.to_csv(file, index=False)  # ToDo update to save scenarios and additional files
            CTkMessagebox(title='OnSSET', message='Result files saved successfully!')

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
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")

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
    
        l4 = CTkLabel(self.start_year_frame, text="National electrification rate (start year)")
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
    
        self.button_calib = CTkButton(self.bottom_frame, text="Run calibration", command=lambda: calibrate(self))
        self.button_calib.place(relx=0.2, rely=0.3)
    
        self.button_save_calib = CTkButton(self.bottom_frame, text="Save calibrated file", command=self.save_calibrated,
                                           state='disabled')
        self.button_save_calib.place(relx=0.6, rely=0.3)

    def save_calibrated(self):
        file = asksaveasfile(filetypes=[("csv file", ".csv")], defaultextension=".csv")
        self.calib_df.to_csv(file, index=False)
        CTkMessagebox(title='OnSSET', message='Calibrated file saved successfully!')


class ScenarioTab(CTkScrollableFrame):
    # Scenario frame
    def __init__(self, parent, df, end_year):
        super().__init__(parent)
        self.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")

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

        g_label_9 = CTkLabel(general_frame, text="Urban demand")
        g_label_9.grid(row=9, column=0, sticky='w', padx=10)
        self.urban_tier = CTkOptionMenu(general_frame, values=["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Custom"])
        self.urban_tier.grid(row=9, column=1, sticky='w')

        g_label_10 = CTkLabel(general_frame, text="Rural demand")
        g_label_10.grid(row=10, column=0, sticky='w', padx=10, pady=(0,10))
        self.rural_tier = CTkOptionMenu(general_frame, values=["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Custom"])
        self.rural_tier.grid(row=10, column=1, sticky='w')

        # Bottom Frame for running and saving scenario
        bottom_frame = CTkFrame(self, height=75, border_width=5)
        bottom_frame.pack(fill='x', pady=20, padx=40)

        # Run scenario button
        run_button = CTkButton(bottom_frame, text="Run scenario", command=lambda: self.run())
        run_button.place(relx=0.2, rely=0.3)

        # Save results button
        self.button_save_results = CTkButton(bottom_frame, text="Save result files", command=lambda: self.save_results(), state='disabled')
        self.button_save_results.place(relx=0.6, rely=0.3)

    def run(self):
        try:
            run_scenario(self, self.filename)
            CTkMessagebox(title='OnSSET', message='Scenario run finished!')
            self.button_save_results.configure(state='normal')
            self.end_year = int(self.end_year.get())
            self.intermediate_year = int(self.intermediate_year.get())
            #self.parent.sidebar_frame.sidebar_button_3.configure(state="normal")
        except AttributeError:
            CTkMessagebox(title='OnSSET', message='No csv file selected, Browse a file', icon='warning')
        except ValueError:
            CTkMessagebox(title='OnSSET', message='Something went wrong, check the input variables!', icon='warning')

    def save_results(self, df):
        if df.size == 0:
            CTkMessagebox(title='OnSSET', message='No results to display, first run a scenario', icon='warning')
        else:
            file = asksaveasfile(filetypes=[("csv file", ".csv")], defaultextension=".csv")
            #df.to_csv(file, index=False)  # ToDo update to save scenarios and additional files
            CTkMessagebox(title='OnSSET', message='Result files saved successfully!')

    def csv_scenario_File_dialog(self):
        self.filename = filedialog.askopenfilename(title="Select the calibrated csv file with GIS data")
        self.label_file.configure(text=self.filename)
        return None

    def load_scenario_csv_data(self):
        try:
            csv_filename = r"{}".format(self.filename)
            df = pd.read_csv(csv_filename)
            self.label_file.configure(text=self.filename + " opened!")
        except ValueError:
            CTkMessagebox(title='Error', message="Could not load file", icon="warning")
            return None
        except FileNotFoundError:
            CTkMessagebox(title='Error', message=f"Could not find the file {self.filename}", icon="warning")
            return None

        self.clear_data()
        self.tv1["column"] = list(df.columns)
        self.tv1["show"] = "headings"
        for column in self.tv1["columns"]:
            self.tv1.heading(column, text=column)

        df_rows = df.to_numpy().tolist()
        for row in df_rows:
            self.tv1.insert("", "end", values=row)

    def clear_data(self):
        self.tv1.delete(*self.tv1.get_children())


class ResultsTab(CTkTabview):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")
        self.add('Map')
        self.add('Charts')

        self.map_frame = CTkFrame(self.tab('Map'))
        self.map_frame.place(relheight=0.9, relwidth=1)
        self.load_map_button = CTkButton(self.tab('Map'), text='Load map', command=lambda: self.vis_map(self.map_frame, parent.scenario.df, parent.scenario.end_year))
        self.load_map_button.place(rely=0.925, relheight=0.05, relwidth=0.2, relx=0.4)

        self.chart_frame = CTkFrame(self.tab('Charts'))
        self.chart_frame.place(relheight=0.9, relwidth=1)
        self.load_chart_button = CTkButton(self.tab('Charts'), text='Load charts', command=lambda: self.vis_charts(self.chart_frame, parent.scenario.df, parent.scenario.intermediate_year, parent.scenario.end_year))
        self.load_chart_button.place(rely=0.925, relheight=0.05, relwidth=0.2, relx=0.4)

    def vis_charts(self, frame_charts, df, intermediate_year, end_year):

        if df.size == 0:
            CTkMessagebox(title='OnSSET', message='No results to display, first run a scenario', icon='warning')
        else:
            yearsofanalysis = [intermediate_year, end_year]

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
                            year)].sum()
                    summary.loc["NewConnections{}".format(year) + t] = df.loc[
                        (df[SET_MIN_OVERALL + '{}'.format(year)] == t + '{}'.format(year)) &
                        (df[SET_ELEC_FINAL_CODE + '{}'.format(year)] < 99), SET_NEW_CONNECTIONS + '{}'.format(year)].sum()
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

            summary_table[columns[0]] = summary.iloc[0:7].astype(int).tolist() + [int(summary.iloc[0:7].sum())]
            summary_table[columns[1]] = summary.iloc[7:14].astype(int).tolist() + [int(summary.iloc[7:14].sum())]
            summary_table[columns[2]] = summary.iloc[14:21].astype(int).tolist() + [int(summary.iloc[14:21].sum())]
            summary_table[columns[3]] = [round(x / 1e4) / 1e2 for x in summary.iloc[21:28].astype(float).tolist()] + [
                round(summary.iloc[21:28].sum() / 1e4) / 1e2]
            summary_table[columns[4]] = summary.iloc[28:35].astype(int).tolist() + [int(summary.iloc[28:35].sum())]
            summary_table[columns[5]] = summary.iloc[35:42].astype(int).tolist() + [int(summary.iloc[35:42].sum())]
            summary_table[columns[6]] = summary.iloc[42:49].astype(int).tolist() + [int(summary.iloc[42:49].sum())]
            summary_table[columns[7]] = [round(x / 1e4) / 1e2 for x in summary.iloc[49:56].astype(float).tolist()] + [
                round(summary.iloc[49:56].sum() / 1e4) / 1e2]

            techs_colors = dict(zip(techs, colors))

            # figure1 = plt.figure(figsize=(9, 9))

            summary_plot = summary_table.drop(labels='Total', axis=0)
            fig_size = [7, 7]
            plt.rcParams["figure.figsize"] = fig_size
            f, axarr = plt.subplots(2, 2)
            fig_size = [7, 7]
            font_size = 5
            plt.rcParams["figure.figsize"] = fig_size

            sns.barplot(x=summary_plot.index.tolist(), y=columns[4], data=summary_plot, ax=axarr[0, 0], palette=colors)
            axarr[0, 0].set_ylabel(columns[4], fontsize=2 * font_size)
            axarr[0, 0].tick_params(labelsize=font_size)
            sns.barplot(x=summary_plot.index.tolist(), y=columns[5], data=summary_plot, ax=axarr[0, 1], palette=colors)
            axarr[0, 1].set_ylabel(columns[5], fontsize=2 * font_size)
            axarr[0, 1].tick_params(labelsize=font_size)
            sns.barplot(x=summary_plot.index.tolist(), y=columns[6], data=summary_plot, ax=axarr[1, 0], palette=colors)
            axarr[1, 0].set_ylabel(columns[6], fontsize=2 * font_size)
            axarr[1, 0].tick_params(labelsize=font_size)
            sns.barplot(x=summary_plot.index.tolist(), y=columns[7], data=summary_plot, ax=axarr[1, 1], palette=colors)
            axarr[1, 1].set_ylabel(columns[7], fontsize=2 * font_size)
            axarr[1, 1].tick_params(labelsize=font_size)

            canvas = FigureCanvasTkAgg(f, master=frame_charts)
            canvas.get_tk_widget().pack()

    def folium_map(self, df, intermediate_year, end_year):
        m = self.least_cost_map(df, intermediate_year, end_year, population_threshold=100, result_year=2030)

        # display(Markdown('Colour coding for technology split:'))
        # display(HTML('<font color="{}">&bull;Grid</font>&nbsp;&nbsp;&nbsp;<font color="{}">&bull;Extended mini-grids</font>&nbsp;&nbsp;&nbsp;\
        #               <font color="{}">&bull;Hybrid mini-grid PV</font>&nbsp;&nbsp;&nbsp;\
        #               <font color="{}">&bull;Hybrid mini-grid wind</font>&nbsp;&nbsp;&nbsp;<font color="{}">&bull;Mini-grid hydro</font>&nbsp;&nbsp;&nbsp;\
        #               <font color="{}">&bull;Stand-alone PV</font>&nbsp;&nbsp;&nbsp;<font color="{}">&bull;Unelectrified</font>'.format(
        #     '#73B2FF', '#73B2FF', '#FE5931', '#A56A56', '#00518E', '#FFD38C', 'lightgray')))

        m

    def least_cost_map(self, df, intermediate_year, end_year, pop_threshold, result_year):
        results_df = df.loc[df[SET_POP_CALIB] > pop_threshold]
        x_ave = df[SET_X_DEG].mean()
        y_ave = df[SET_Y_DEG].mean()

        colors = ['#73B2FF', '#73B2FF', '#FFD38C', '#8FB722', '#8FB722', '#8FB722', '#00518E', '#FE5931', '#A56A56']
        m = folium.Map(location=[y_ave, x_ave], zoom_start=5)

        # Very light gray for unelectrified settlements, the rest get same colors as platform
        for index, row in results_df.iterrows():
            if row["FinalElecCode{}".format(result_year)] == 99:
                tech_color = 'lightgray'
            else:
                tech_color = colors[int((row["FinalElecCode{}".format(result_year)])) - 1]

            technologies_available = {1: 'Grid',
                                      2: 'Expanded mini-grid',
                                      4: 'Mini-grid Diesel',
                                      8: 'Hybrid mini-grid PV',
                                      9: 'Hybrid mini-grid wind',
                                      7: 'Mini-grid hydro',
                                      3: 'Stand-alone PV',
                                      99: 'Unelectrified'}

            # Data to show in popup, numbers have to transformed to strings first
            LineOne = "Technology choice: " + str(
                technologies_available.get(row["FinalElecCode{}".format(result_year)]))
            LineTwo = "Buildings: " + str(row['Buildings{}'.format(result_year)])
            LineThree = "Investment cost in first timestep: " + str(
                round(row['InvestmentCost{}'.format(intermediate_year)])) + " USD"
            LineFour = "Investment cost in second timestep: " + str(
                round(row['InvestmentCost{}'.format(end_year)])) + " USD"
            LineFive = "Total investment cost: " + str(round(row['InvestmentCost{}'.format(end_year)]) + round(
                row['InvestmentCost{}'.format(intermediate_year)])) + " USD"
            LineSix = "Added capacity in first timestep: " + str(
                round(row['NewCapacity{}'.format(intermediate_year)])) + " kW"
            LineSeven = "Added capacity in second timestep: " + str(
                round(row['NewCapacity{}'.format(end_year)])) + " kW"
            LineEight = "Total added capacity: " + str(round(row['NewCapacity{}'.format(end_year)]) + round(
                row['NewCapacity{}'.format(intermediate_year)])) + " kW"
            LineNine = "ID: " + str(row['id'])

            LineTot = LineOne + '<br>' + LineTwo + '<br>' + LineThree + '<br>' + LineFour + '<br>' + LineFive + '<br>' + LineSix + '<br>' + LineSeven + '<br>' + LineEight + '<br>' + LineNine

            iframe = folium.IFrame(LineTot,
                                   width=550,
                                   height=150)

            popup = folium.Popup(iframe,
                                 max_width=325)

            folium.Circle(
                location=[row[SET_Y_DEG], row[SET_X_DEG]],
                radius=np.sqrt(row[SET_GRID_CELL_AREA] / 3.14) * 1000,
                popup=popup,
                color=tech_color,
                fill_color=tech_color,
                fill=True
            ).add_to(m)

        return m

    def vis_map(self, frame_results, df, end_year):

        map_frame = frame_results

        if df.size == 0:
            CTkMessagebox(title='OnSSET', message='No results to display, first run a scenario', icon='warning')
        else:
            figure1 = plt.figure(figsize=(7, 7))
            figure1.add_subplot(111)
            # plt.figure(figsize=(9, 9))
            plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 3, SET_X_DEG],
                     df.loc[df['FinalElecCode{}'.format(end_year)] == 3, SET_Y_DEG], color='#EDA800',
                     marker=',', linestyle='none')
            plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 2, SET_X_DEG],
                     df.loc[df['FinalElecCode{}'.format(end_year)] == 2, SET_Y_DEG], color='#EDD100',
                     marker=',', linestyle='none')
            plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 4, SET_X_DEG],
                     df.loc[df['FinalElecCode{}'.format(end_year)] == 4, SET_Y_DEG], color='#1F6600',
                     marker=',', linestyle='none')
            plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 5, SET_X_DEG],
                     df.loc[df['FinalElecCode{}'.format(end_year)] == 5, SET_Y_DEG], color='#98E600',
                     marker=',', linestyle='none')
            plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 6, SET_X_DEG],
                     df.loc[df['FinalElecCode{}'.format(end_year)] == 6, SET_Y_DEG], color='#70A800',
                     marker=',', linestyle='none')
            plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 7, SET_X_DEG],
                     df.loc[df['FinalElecCode{}'.format(end_year)] == 7, SET_Y_DEG], color='#1FA800',
                     marker=',', linestyle='none')
            plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 1, SET_X_DEG],
                     df.loc[df['FinalElecCode{}'.format(end_year)] == 1, SET_Y_DEG], color='#73B2FF',
                     marker=',', linestyle='none')
            if df[SET_X_DEG].max() - df[SET_X_DEG].min() > df[SET_Y_DEG].max() - df[
                SET_Y_DEG].min():
                plt.xlim(df[SET_X_DEG].min() - 1, df[SET_X_DEG].max() + 1)
                plt.ylim((df[SET_Y_DEG].min() + df[SET_Y_DEG].max()) / 2 - 0.5 * abs(
                    df[SET_X_DEG].max() - df[SET_X_DEG].min()) - 1,
                         (df[SET_Y_DEG].min() + df[SET_Y_DEG].max()) / 2 + 0.5 * abs(
                             df[SET_X_DEG].max() - df[SET_X_DEG].min()) + 1)
            else:
                plt.xlim((df[SET_X_DEG].min() + df[SET_X_DEG].max()) / 2 - 0.5 * abs(
                    df[SET_Y_DEG].max() - df[SET_Y_DEG].min()) - 1,
                         (df[SET_X_DEG].min() + df[SET_X_DEG].max()) / 2 + 0.5 * abs(
                             df[SET_Y_DEG].max() - df[SET_Y_DEG].min()) + 1)
                plt.ylim(df[SET_Y_DEG].min() - 1, df[SET_Y_DEG].max() + 1)

            canvas = FigureCanvasTkAgg(figure1, master=map_frame)
            canvas.get_tk_widget().pack()


if __name__ == "__main__":
    app = App()
    app.mainloop()

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