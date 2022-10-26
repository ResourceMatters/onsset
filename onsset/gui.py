from runner import *

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd

root = tk.Tk()
root.geometry("500x700")
root.pack_propagate(False)
root.resizable(0, 0)
root.title('OnSSET - The Open Source Spatial Electrification Tool')
root['bg'] = "#4a98ff"


# Frame for TreeView
frame1 = tk.LabelFrame(root, text='Calibrated CSV data')
frame1.place(height=250, width=500)
frame1['bg'] = '#4a98ff'

# Frame for csv file
file_frame = tk.LabelFrame(root, text="Open csv file")
file_frame.place(height=100, width=400, rely=0.4, relx=0.1)
file_frame['bg'] = "white"

# Frame for specs file
file_frame2 = tk.LabelFrame(root, text="Open specs file")
file_frame2.place(height=100, width=400, rely=0.6, relx=0.1)
file_frame2['bg'] = "white"

# Frame for running OnSSET
file_frame3 = tk.LabelFrame(root, text="Run a scenario")
file_frame3.place(height=100, width=400, rely=0.8, relx=0.1)
file_frame3['bg'] = "white"

# Buttons
# csv file buttons
button1 = tk.Button(file_frame, text="Browse a file", command=lambda: csv_File_dialog())
button1.place(rely=0.4, relx=0.2)

button2 = tk.Button(file_frame, text="Load File", command=lambda: load_csv_data())
button2.place(rely=0.4, relx=0.6)

label_file = ttk.Label(file_frame, text="No file selected, click the browse button!")
label_file.place(rely=0, relx=0)

# specs file buttons
button3 = tk.Button(file_frame2, text="Browse a file", command=lambda: excel_File_dialog())
button3.place(rely=0.4, relx=0.4)

label_file2 = ttk.Label(file_frame2, text="No file selected, click the browse button!")
label_file2.place(rely=0, relx=0)

# Run scenario button
button4 = tk.Button(file_frame3, text="Run scenarios", command=lambda: run_scenarios())
button4.place(rely=0.4, relx=0.4)

label_file3 = ttk.Label(file_frame3, text="Start a run!")
label_file3.place(rely=0, relx=0)

# Treeview widget
tv1 = ttk.Treeview(frame1)
tv1.place(relheight=1, relwidth=1)

treescrolly = tk.Scrollbar(frame1, orient="vertical", command=tv1.yview)
treescrollx = tk.Scrollbar(frame1, orient="horizontal", command=tv1.xview)
tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
treescrollx.pack(side="bottom", fill="x")
treescrolly.pack(side="right", fill="y")


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
        label_file["text"] = file_path + " opened!"
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

    messagebox.showinfo('OnSSET', 'Browse to RESULTS folder to save outputs')
    results_folder = filedialog.askdirectory()
    messagebox.showinfo('OnSSET', 'Browse to SUMMARIES folder and name the scenario to save outputs')
    summary_folder = filedialog.askdirectory()

    short_results = messagebox.askyesno(title='OnSSET', message='Do you wish to save the result files with fewer output columns (else all columns will be saved)?')
    try:
        label_file3["text"] = "Running, please wait"

        scenario(label_file2["text"], label_file["text"], results_folder, summary_folder, gis_cost_folder, save_shapefiles, gis_grid_extension, short_results)
        messagebox.showinfo('OnSSET', 'Finished! Check your results folder')
        label_file3["text"] = "Finished, go again?"
    except FileNotFoundError:
        tk.messagebox.showerror('OnSSET', "Missing a file, did you select (browse) both the csv and specs file?")
        label_file3["text"] = "Start a run!"

root.mainloop()