import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.filedialog import asksaveasfile
from visualization import vis_map, vis_charts

import pandas as pd

def init_scenario(scenario, runner, primary_color, secondary_color):

    canvas = tk.Canvas(scenario, bg='red')
    canvas.pack(side='left', fill='both', expand=1)

    scrollbar = ttk.Scrollbar(scenario, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas_frame = tk.Frame(canvas, background=primary_color)
    canvas_f = canvas.create_window((0, 0), window=canvas_frame, anchor='nw')

    def FrameWidth(event):
        canvas_width = event.width
        canvas.itemconfig(canvas_f, width=canvas_width)

    def OnFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas_frame.bind("<Configure>", OnFrameConfigure)
    canvas.bind('<Configure>', FrameWidth)

    top_frame = tk.Frame(canvas_frame, height=20, bg=primary_color)
    top_frame.pack(fill='x')

    # Frame for TreeView
    frame1 = tk.LabelFrame(canvas_frame, height=200, text='Calibrated CSV data', bg=secondary_color)
    # Treeview widget
    tv1 = ttk.Treeview(frame1)
    treescrolly = tk.Scrollbar(frame1, orient="vertical", command=tv1.yview)
    treescrollx = tk.Scrollbar(frame1, orient="horizontal", command=tv1.xview)
    tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side="bottom", fill="x")
    treescrolly.pack(side="right", fill="y")
    tv1.pack(fill='both', expand=1)

    frame1.pack(pady=10, padx=40, fill='x')

    # Frame for selecting csv file
    file_frame = tk.LabelFrame(canvas_frame, text="Select the calibrated csv file", bg=secondary_color, height=75)
    file_frame.pack(pady=10, padx=40, fill='x')

    label_file = ttk.Label(file_frame, text="No file selected, click the browse button!")
    label_file.place(rely=0, relx=0)

    # csv file buttons
    button1 = tk.Button(file_frame, text="Browse a file", command=lambda: csv_File_dialog())
    button1.place(rely=0.4, relx=0.2)

    button2 = tk.Button(file_frame, text="Load File", command=lambda: load_csv_data())
    button2.place(rely=0.4, relx=0.6)


    # Frame for general parameters
    general_frame = tk.LabelFrame(canvas_frame, text="Enter general parameters", bg=secondary_color)
    general_frame.pack(pady=10, padx=40, fill='x')

    l1 = tk.Label(general_frame, text="Start year", bg=secondary_color)
    l1.grid(row=0, column=0, sticky='w')
    e1 = tk.Entry(general_frame)
    e1.grid(row=0, column=1, sticky='w')
    e1.insert(10, 2020)

    l2 = tk.Label(general_frame, text="End year", bg=secondary_color)
    l2.grid(row=1, column=0, sticky='w')
    e2 = tk.Entry(general_frame)
    e2.grid(row=1, column=1, sticky='w')
    e2.insert(10, 2030)

    l3 = tk.Label(general_frame, text="Intermediate year", bg=secondary_color)
    l3.grid(row=2, column=0, sticky='w')
    e3 = tk.Entry(general_frame)
    e3.grid(row=2, column=1, sticky='w')
    e3.insert(10, 2025)

    l4 = tk.Label(general_frame, text="Electrification rate target", bg=secondary_color)
    l4.grid(row=3, column=0, sticky='w')
    e4 = tk.Entry(general_frame)
    e4.grid(row=3, column=1, sticky='w')
    e4.insert(10, 1)

    l5 = tk.Label(general_frame, text="Electrification rate target (Intermediate year)", bg=secondary_color)
    l5.grid(row=4, column=0, sticky='w')
    e5 = tk.Entry(general_frame)
    e5.grid(row=4, column=1, sticky='w')
    e5.insert(10, 0.8)

    l6 = tk.Label(general_frame, text="End year population", bg=secondary_color)
    l6.grid(row=5, column=0, sticky='w')
    e6 = tk.Entry(general_frame)
    e6.grid(row=5, column=1, sticky='w')
    e6.insert(10, "")

    l7 = tk.Label(general_frame, text="Urban ratio (end year)", bg=secondary_color)
    l7.grid(row=6, column=0, sticky='w')
    e7 = tk.Entry(general_frame)
    e7.grid(row=6, column=1, sticky='w')
    e7.insert(10, "")

    l8 = tk.Label(general_frame, text="Discount rate", bg=secondary_color)
    l8.grid(row=7, column=0, sticky='w')
    e8 = tk.Entry(general_frame)
    e8.grid(row=7, column=1, sticky='w')
    e8.insert(10, "0.08")

    # Frame for off-grid technology costs
    off_grid_frame = tk.LabelFrame(canvas_frame, text="Enter off-grid technology parameters", bg=secondary_color)
    off_grid_frame.pack(pady=10, padx=40, fill='x')

    l11 = tk.Label(off_grid_frame, text="Diesel techs", bg=secondary_color)
    l11.grid(row=0, column=0, sticky='w')
    e11 = tk.Entry(off_grid_frame)
    e11.grid(row=0, column=1, sticky='w')
    e11.insert(10, 0)

    l12 = tk.Label(off_grid_frame, text="Diesel price", bg=secondary_color)
    l12.grid(row=1, column=0, sticky='w')
    e12 = tk.Entry(off_grid_frame)
    e12.grid(row=1, column=1, sticky='w')
    e12.insert(10, 0.5)

    l13 = tk.Label(off_grid_frame, text="Grid generation cost", bg=secondary_color)
    l13.grid(row=2, column=0, sticky='w')
    e13 = tk.Entry(off_grid_frame)
    e13.grid(row=2, column=1, sticky='w')
    e13.insert(10, 0.05)

    l14 = tk.Label(off_grid_frame, text="SA Diesel capital cost", bg=secondary_color)
    l14.grid(row=3, column=0, sticky='w')
    e14 = tk.Entry(off_grid_frame)
    e14.grid(row=3, column=1, sticky='w')
    e14.insert(10, 938)

    l15 = tk.Label(off_grid_frame, text="MG Diesel capital cost", bg=secondary_color)
    l15.grid(row=4, column=0, sticky='w')
    e15 = tk.Entry(off_grid_frame)
    e15.grid(row=4, column=1, sticky='w')
    e15.insert(10, 721)

    l16 = tk.Label(off_grid_frame, text="MG PV capital cost", bg=secondary_color)
    l16.grid(row=5, column=0, sticky='w')
    e16 = tk.Entry(off_grid_frame)
    e16.grid(row=5, column=1, sticky='w')
    e16.insert(10, "2950")

    l17 = tk.Label(off_grid_frame, text="MG Wind capital cost", bg=secondary_color)
    l17.grid(row=6, column=0, sticky='w')
    e17 = tk.Entry(off_grid_frame)
    e17.grid(row=6, column=1, sticky='w')
    e17.insert(10, "3750")

    l18 = tk.Label(off_grid_frame, text="MG Hydro capital cost", bg=secondary_color)
    l18.grid(row=7, column=0, sticky='w')
    e18 = tk.Entry(off_grid_frame)
    e18.grid(row=7, column=1, sticky='w')
    e18.insert(10, "3000")

    l19 = tk.Label(off_grid_frame, text="SA PV cost (<20 W)", bg=secondary_color)
    l19.grid(row=8, column=0, sticky='w')
    e19 = tk.Entry(off_grid_frame)
    e19.grid(row=8, column=1, sticky='w')
    e19.insert(10, "9620")

    l20 = tk.Label(off_grid_frame, text="SA PV cost (21-50 W)", bg=secondary_color)
    l20.grid(row=9, column=0, sticky='w')
    e20 = tk.Entry(off_grid_frame)
    e20.grid(row=9, column=1, sticky='w')
    e20.insert(10, "8780")

    l21 = tk.Label(off_grid_frame, text="SA PV cost (51-100 W)", bg=secondary_color)
    l21.grid(row=10, column=0, sticky='w')
    e21 = tk.Entry(off_grid_frame)
    e21.grid(row=10, column=1, sticky='w')
    e21.insert(10, "6380")

    l22 = tk.Label(off_grid_frame, text="SA PV cost (101-1000 W)", bg=secondary_color)
    l22.grid(row=11, column=0, sticky='w')
    e22 = tk.Entry(off_grid_frame)
    e22.grid(row=11, column=1, sticky='w')
    e22.insert(10, "4470")

    l23 = tk.Label(off_grid_frame, text="SA PV cost (>1000 W)                                      ", bg=secondary_color)
    l23.grid(row=12, column=0, sticky='w')
    e23 = tk.Entry(off_grid_frame)
    e23.grid(row=12, column=1, sticky='w')
    e23.insert(10, "6950")

    # Frame for T&D costs
    td_frame = tk.LabelFrame(canvas_frame, text="Enter T&D parameters", bg=secondary_color)
    td_frame.pack(pady=10, padx=40, fill='x')

    l24 = tk.Label(td_frame, text="HV line cost", bg=secondary_color)
    l24.grid(row=0, column=0, sticky='w')
    e24 = tk.Entry(td_frame)
    e24.grid(row=0, column=1, sticky='w')
    e24.insert(10, "53000")

    l25 = tk.Label(td_frame, text="MV line cost                                                     ", bg=secondary_color)
    l25.grid(row=1, column=0, sticky='w')
    e25 = tk.Entry(td_frame)
    e25.grid(row=1, column=1, sticky='w')
    e25.insert(10, "7000")

    l26 = tk.Label(td_frame, text="LV line cost", bg=secondary_color)
    l26.grid(row=3, column=0, sticky='w')
    e26 = tk.Entry(td_frame)
    e26.grid(row=3, column=1, sticky='w')
    e26.insert(10, "4250")

    # Bottom Frame for running and saving scenario
    bottom_frame = tk.Frame(canvas_frame, height=20, bg=primary_color)
    bottom_frame.pack(fill='x', pady=20)

    # Run scenario button
    run_button = tk.Button(bottom_frame, text="Run scenario", command=lambda: run_scenarios())
    run_button.place(relwidth=0.2, relx=0.2)

    # Save results button
    button_save_calib = tk.Button(bottom_frame, text="Save result files", command=lambda: save_results(), state='disabled')
    button_save_calib.place(relwidth=0.2, relx=0.6)

    bottom_frame_2 = tk.Frame(canvas_frame, height=20, bg=primary_color)
    bottom_frame_2.pack(fill='x', pady=20)

    def map_popup():
        top = tk.Toplevel(scenario)
        top.geometry("500x500")
        top.title("Least-cost technology map")

    def charts_popup():
        top = tk.Toplevel(scenario)
        top.geometry("500x500")
        top.title("Results charts")

    map_results_button = tk.Button(bottom_frame_2, text="Show results map", command=lambda: map_popup(), state='active')
    map_results_button.place(relwidth=0.2, relx=0.2)

    charts_results_button = tk.Button(bottom_frame_2, text="Show result charts", command=lambda: charts_popup(), state='active')
    charts_results_button.place(relwidth=0.2, relx=0.6)

    def save_results():
        file = asksaveasfile(filetypes=[("csv file", ".csv")], defaultextension=".csv")
        #calib_df.to_csv(file, index=False) # ToDo update to save scenarios and additional files
        messagebox.showinfo('OnSSET', 'Result files saved successfully!')

    def csv_File_dialog():
        filename = filedialog.askopenfilename(title="Select the calibrated csv file with GIS data")
        label_file["text"] = filename
        return None

    def excel_File_dialog():
        filename = filedialog.askopenfilename(title="Select the specs file")
        label_file2["text"] = filename
        return None

    def load_csv_data():
        file_path = label_file["text"]
        try:
            csv_filename = r"{}".format(file_path)
            df = pd.read_csv(csv_filename)
            # label_file["text"] = file_path + " opened!"
        except ValueError:
            tk.messagebox.showerror("Could not load file")
            return None
        except FileNotFoundError:
            tk.messagebox.showerror(f"Could not find the file {file_path}")
            return None

        clear_data()
        tv1["column"] = list(df.columns)
        tv1["show"] = "headings"
        for column in tv1["columns"]:
            tv1.heading(column, text=column)

        df_rows = df.to_numpy().tolist()
        for row in df_rows:
            tv1.insert("", "end", values=row)

    def clear_data():
        tv1.delete(*tv1.get_children())

    def run_scenarios():

        gis_cost_folder = False
        save_shapefiles = False
        gis_grid_extension = False
        short_results = False

        messagebox.showinfo('OnSSET', 'Browse to RESULTS folder to save outputs')
        results_folder = filedialog.askdirectory()
        messagebox.showinfo('OnSSET', 'Browse to SUMMARIES folder and name the scenario to save outputs')
        summary_folder = filedialog.askdirectory()

        label_file3["text"] = "Running, please wait"

        runner.scenario(label_file2["text"], label_file["text"], results_folder, summary_folder, gis_cost_folder,
                        save_shapefiles, gis_grid_extension, short_results)
        messagebox.showinfo('OnSSET', 'Finished! Check your results folder')
        label_file3["text"] = "Finished, go again?"





