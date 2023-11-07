from tkinter import ttk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from runner_modern import *
from tkinter.filedialog import asksaveasfile
from tkinter import *
from customtkinter import *
from PIL import ImageTk
from CTkMessagebox import CTkMessagebox

set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(CTk):
    def __init__(self):
        super().__init__()

        self.filename = ""

        # configure window
        self.title("OnSSET - The Open Source Spatial Electrification Tool")
        self.geometry(f"{1100}x{580}")
        self.minsize(1100, 580)
        self.iconpath = ImageTk.PhotoImage(file=r'C:\GitHub\ResourceMatters\onsset\resources\onsset_logo_3.png')
        self.wm_iconbitmap()
        self.iconphoto(False, self.iconpath)

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.tab_1 = CTkFrame(self)
        self.tab_1.configure(width=250)
        self.tab_1.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")
        # self.tab_1_ctk = CTkFrame(self.tab_1)
        # self.tab_1_ctk.pack(expand=1, fill='both')
        self.label_1 = CTkLabel(self.tab_1, text='TAB 1')
        self.label_1.pack(expand=1, fill='both')

        self.tab_2 = CTkFrame(self)
        self.tab_2.configure(width=250)
        self.tab_2.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")
        self.label_2 = CTkLabel(self.tab_2, text='TAB 2')
        self.label_2.pack(expand=1, fill='both')

        self.sidebar_frame = Menu(self, self.tab_1, self.tab_2)


class Menu(CTkFrame):
    def __init__(self, parent, tab_1, tab_2):
        super().__init__(parent)
        self.configure(width=140)
        self.configure(corner_radius=0)
        self.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)

        self.tab_1 = tab_1
        self.tab_2 = tab_2

        self.create_widgets()

    def create_widgets(self):
        self.logo_label = CTkLabel(self, text="Settings", font=CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = CTkButton(self, text='Calibration', command=self.display_calibration)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = CTkButton(self, text='Run scenario', command=self.display_scenario)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = CTkButton(self, text='Visualize results', command=self.display_results)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        self.appearance_mode_label = CTkLabel(self, text="Appearance Mode", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = CTkOptionMenu(self, values=["Light", "Dark"],command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        self.scaling_label = CTkLabel(self, text="Zoom", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = CTkOptionMenu(self, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        self.language_label = CTkLabel(self, text="Language", anchor="w")
        self.language_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.language_optionmenu = CTkOptionMenu(self, values=["English", "French"])
        self.language_optionmenu.grid(row=10, column=0, padx=20, pady=(10, 20))

        # set default values
        # self.sidebar_button_3.configure(state="disabled")
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

    def display_scenario(self):
        self.tab_2.grid(row=0, column=1, rowspan=4, padx=20, pady=20, sticky="nsew")

    def display_calibration(self):
        self.tab_2.grid_forget()

    def display_results(self):
        pass

    def change_appearance_mode_event(self, new_appearance_mode: str):
        set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        set_widget_scaling(new_scaling_float)


if __name__ == "__main__":
    app = App()
    app.mainloop()