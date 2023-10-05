import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.filedialog import asksaveasfile
import pandas as pd
import onsset

def init_config(config_tab, primary_color, secondary_color):
    label_font = tk.font.Font(weight="bold")
    #calib_df = pd.DataFrame()

    top_frame = tk.Frame(config_tab, height=20, bg=primary_color)
    top_frame.pack(fill='x')

    # Frame for start year inputs
    file_frame = tk.LabelFrame(config_tab, text="Enter start year information", bg=secondary_color)
    file_frame.pack(pady=10, padx=40, fill='x')

    l1 = tk.Label(file_frame, text="Start year", bg=secondary_color)
    l1.grid(row=0, column=0)
    e1 = tk.Entry(file_frame)
    e1.grid(row=0, column=1)
    e1.insert(10, 2020)

    l2 = tk.Label(file_frame, text="Start year population", bg=secondary_color)
    l2.grid(row=1, column=0)
    e2 = tk.Entry(file_frame)
    e2.grid(row=1, column=1)
    e2.insert(10, "")

    l3 = tk.Label(file_frame, text="Urban ratio (start year)", bg=secondary_color)
    l3.grid(row=2, column=0)
    #e3 = tk.Spinbox(file_frame, from_=0, to=int(e2.get())-int(e1.get()))
    e3 = tk.Entry(file_frame)
    e3.grid(row=2, column=1)

    l4 = tk.Label(file_frame, text="National electrification rate (start year)", bg=secondary_color)
    l4.grid(row=3, column=0)
    e4 = tk.Entry(file_frame)
    e4.grid(row=3, column=1)

    l5 = tk.Label(file_frame, text="Urban electrification rate (start year)", bg=secondary_color)
    l5.grid(row=4, column=0)
    e5 = tk.Entry(file_frame)
    e5.grid(row=4, column=1)
    e5.insert(10, "")

    l6 = tk.Label(file_frame, text="Rural electrification rate (start year)", bg=secondary_color)
    l6.grid(row=5, column=0)
    e6 = tk.Entry(file_frame)
    e6.grid(row=5, column=1)
    e6.insert(10, "")

    l19 = tk.Label(file_frame, text="Urban household size", bg=secondary_color)
    l19.grid(row=6, column=0)
    e19 = tk.Entry(file_frame)
    e19.grid(row=6, column=1)
    e19.insert(10, "5")

    l20 = tk.Label(file_frame, text="Rural household size", bg=secondary_color)
    l20.grid(row=7, column=0)
    e20 = tk.Entry(file_frame)
    e20.grid(row=7, column=1)
    e20.insert(10, "5")

    calib_text_frame = tk.LabelFrame(config_tab, bg=secondary_color)
    calib_text_frame.pack(pady=10, padx=40, fill='x')

    l7 = tk.Label(calib_text_frame, text="Calibration of currently electrified settlements", bg=secondary_color, font=label_font)
    l7.grid(row=0, column=0, sticky='w')

    l8 = tk.Label(calib_text_frame, text="The model calibrates which settlements are likely to be electrified in the start year, to match the national statistical values defined above.", bg=secondary_color)
    l8.grid(row=1, column=0, sticky='w')

    l13 = tk.Label(calib_text_frame, text="A settlement is considered to be electrified if it meets all of the following conditions:", bg=secondary_color)
    l13.grid(row=2, column=0, sticky='w')

    l9 = tk.Label(calib_text_frame, text="   - Has more night-time lights than the defined threshold (this is set to 0 by default)", bg=secondary_color)
    l9.grid(row=3, column=0, sticky='w')

    l10 = tk.Label(calib_text_frame, text="   - Is closer to the existing grid network than the distance limit", bg=secondary_color)
    l10.grid(row=4, column=0, sticky='w')

    l11 = tk.Label(calib_text_frame, text="   - Has more population than the threshold", bg=secondary_color)
    l11.grid(row=5, column=0, sticky='w')

    l12 = tk.Label(calib_text_frame, text="First, define the threshold limits. Then run the calibration and check if the results seem okay. Else, redefine these thresholds and run again.", bg=secondary_color)
    l12.grid(row=6, column=0, sticky='w')


    calib_frame = tk.LabelFrame(config_tab, text="Enter calibration parameters", bg=secondary_color)
    calib_frame.pack(pady=10, padx=40, fill='x')

    l14 = tk.Label(calib_frame, text="Minimum night-time lights", bg=secondary_color)
    l14.grid(row=0, column=0)
    e14 = tk.Entry(calib_frame)
    e14.grid(row=0, column=1)
    e14.insert(10, "0")

    l15 = tk.Label(calib_frame, text="Minimum population", bg=secondary_color)
    l15.grid(row=1, column=0)
    e15 = tk.Entry(calib_frame)
    e15.grid(row=1, column=1)
    e15.insert(10, "100")

    l16 = tk.Label(calib_frame, text="Max distance to service transformer", bg=secondary_color)
    l16.grid(row=2, column=0)
    e16 = tk.Entry(calib_frame)
    e16.grid(row=2, column=1)
    e16.insert(10, "1")

    l17 = tk.Label(calib_frame, text="Max distance to MV lines", bg=secondary_color)
    l17.grid(row=3, column=0)
    e17 = tk.Entry(calib_frame)
    e17.grid(row=3, column=1)
    e17.insert(10, "2")

    l18 = tk.Label(calib_frame, text="Max distance to HV lines", bg=secondary_color)
    l18.grid(row=4, column=0)
    e18 = tk.Entry(calib_frame)
    e18.grid(row=4, column=1)
    e18.insert(10, "25")

    def csv_File_dialog():
        filename = filedialog.askopenfilename(title="Select the csv file with GIS data")
        return filename

    def load_csv_data():
        file_path = csv_File_dialog()
        try:
            csv_filename = r"{}".format(file_path)
            onsseter = onsset.SettlementProcessor(csv_filename)
            return onsseter
        except ValueError:
            tk.messagebox.showerror("Could not load file")
            return None
        except FileNotFoundError:
            tk.messagebox.showerror(f"Could not find the file {file_path}")
            return None

    def calibrate():
        global calib_df
        messagebox.showinfo('OnSSET', 'Open the file with extracted GIS data')
        onsseter = load_csv_data()

        start_year = int(e1.get())
        start_year_pop = float(e2.get())
        urban_ratio_start_year = float(e3.get())
        elec_rate = float(e4.get())
        elec_rate_urban = float(e5.get())
        elec_rate_rural = float(e6.get())
        min_night_light = float(e14.get())
        min_pop = float(e15.get())
        max_transformer_dist = float(e16.get())
        max_mv_dist = float(e17.get())
        max_hv_dist = float(e18.get())
        hh_size_urban = float(e19.get())
        hh_size_rural = float(e20.get())

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

        pop_modelled, urban_modelled = onsseter.calibrate_current_pop_and_urban(start_year_pop, urban_ratio_start_year)

        elec_modelled, rural_elec_ratio, urban_elec_ratio = \
            onsseter.elec_current_and_future(elec_rate, elec_rate_urban, elec_rate_rural, start_year,
                                             min_night_lights=min_night_light,
                                             min_pop=min_pop,
                                             max_transformer_dist=max_transformer_dist,
                                             max_mv_dist=max_mv_dist,
                                             max_hv_dist=max_hv_dist)
        button_save_calib.config(state='active')
        calib_df = onsseter.df

        messagebox.showinfo('OnSSET', 'Calibration completed! The calibrated electrification rate was {}'.format(round(elec_modelled, 2)))

    def save_calibrated():
        file = asksaveasfile(filetypes=[("csv file", ".csv")], defaultextension=".csv")
        calib_df.to_csv(file, index=False)
        messagebox.showinfo('OnSSET', 'Calibrated file saved successfully!')

    bottom_frame = tk.Frame(config_tab, height=20, bg=primary_color)
    bottom_frame.pack(fill='x', pady=20)

    button_calib = tk.Button(bottom_frame, text="Run calibration", command=calibrate)
    button_calib.place(relwidth=0.2, relx=0.2)

    button_save_calib = tk.Button(bottom_frame, text="Save calibrated file", command=save_calibrated, state='disabled')
    button_save_calib.place(relwidth=0.2, relx=0.6)

