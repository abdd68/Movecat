import customtkinter as ctk
import tkinter as tk
import numpy as np
from collections import OrderedDict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.pylab import mpl
from PIL import Image, ImageTk
import sys
import os
import pickle
import math
import json

def load_translations(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_translation(translations, lang, key):
    return translations.get(lang, {}).get(key, key)

def str2strint(str_):
    if str_ == "None":
        return '0'
    elif str_ == "A little":
        return '1'
    elif str_ == "Somewhat":
        return '2'
    elif str_ == 'Quite a bit':
        return '3'
    elif str_ == 'Severe':
        return '4'
    else:
        return str_

class CreateToolTip:
    def __init__(self, widget, text, delay=420):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.delay = delay
        self._after_id = None
        self.widget.bind("<Enter>", self.schedule_show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Motion>", self.move_tooltip)

    def schedule_show_tooltip(self, event):
        self._after_id = self.widget.after(self.delay, self.show_tooltip, event)

    def show_tooltip(self, event):
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(self.tooltip, text=self.text, corner_radius=5)
        label.pack()

    def hide_tooltip(self, event):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def move_tooltip(self, event):
        if self.tooltip:
            x = event.x_root + 10
            y = event.y_root + 10
            self.tooltip.wm_geometry(f"+{x}+{y}")

class MyScrollableCheckboxFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, title, labels, instructions, num_columns, font, get_text):
        super().__init__(master, width=660, height=270, label_text=get_text(title))
        self.title = title
        self.labels = labels
        self.instructions = instructions
        self.label_handles = []
        self.tooltip_handles = []
        self.output_labels = None
        self.split = 4
        self.entries = []
        self.options = ["None", "A little", "Somewhat", "Quite a bit", "Severe"]
        self.font = font
        self.get_text = get_text
        self.lrow = 1
        for i, (label_text, suggestion) in enumerate(self.labels.items()):
            row, column = i // num_columns, i % num_columns
            label = ctk.CTkLabel(self, text=get_text(label_text), font=self.font)
            self.label_handles.append(label)
            label.grid(row=row+1, column=column*2, padx=5, pady=5, sticky='w')
            tooltip_text = self.instructions[i]
            tooltip = CreateToolTip(label, tooltip_text)
            self.tooltip_handles.append(tooltip)
            entry_var = ctk.StringVar(value=suggestion)
            if i < self.split:
                entry = ctk.CTkEntry(self, textvariable=entry_var)
            else:
                entry = ctk.CTkOptionMenu(self, variable=None, values=self.options)
            entry.grid(row=row+1, column=column*2+1, padx=5, pady=5, sticky='w')

            self.entries.append(entry)
            self.lrow += 1
            self.grid_rowconfigure(row+1, weight=1)
            if row == 0:
                self.grid_columnconfigure(column*2, weight=1)
                self.grid_columnconfigure(column*2+1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def get(self):
        for i, (key, value) in enumerate(self.labels.items()):
            self.labels[key] = str2strint(self.entries[i].get())
        return self.labels
    
    def update_texts(self):
        self.configure(label_text=self.get_text(self.title))
        for i, (label_text, suggestion) in enumerate(self.labels.items()):
            self.label_handles[i].configure(text=self.get_text(label_text))
        for i in range(len(self.instructions)):
            self.tooltip_handles[i].text = self.get_text(self.instructions[i])
            if i >= self.split:
                self.entries[i].configure(values=[self.get_text(option) for option in self.options])
    

class PLOTFrame(ctk.CTkScrollableFrame):
    def __init__(self, master=None, title=None, font=None, get_text=None):
        super().__init__(master, width=720, height=330, label_text=get_text(title))
        self.master = master
        self.create_matplotlib()
        self.createWidget(self.figure)
        self.font = font

    def createWidget(self, figure):
        self.canvas = FigureCanvasTkAgg(figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_matplotlib(self):
        mpl.rcParams['font.sans-serif'] = ['SimHei']
        mpl.rcParams['axes.unicode_minus'] = False
        self.figure = plt.figure(num=2, figsize=(7, 9), dpi=80, facecolor="white", edgecolor='Teal', frameon=True)
        font = {'family': 'serif', 'serif': 'Times New Roman', 'weight': 'normal', 'size': 20}
        plt.rc('font', **font)
        plt.title('GBT weight', fontdict={'family': 'Times New Roman', 'weight': 'normal', 'size': 28}, pad=12)
        plt.yscale('symlog', linthresh=0.00005)
        plt.tick_params(axis='x', labelsize=18, rotation=60)
        plt.tick_params(axis='y', labelsize=18)
        data = [('ArmSwelling', 0.5666504441537034), ('SYM_COUNT', 0.32829106757634513), ('BreastSwelling', 0.05866949630997336), ('TIME_LAPSE', 0.0270874570016606), ('BMI', 0.0048442873079247665), ('FHT', 0.003799860520333767), ('Age', 0.0036176355797100405), ('Number_nodes', 0.0027917973843724414), ('Skin', 0.0018357913101027619), ('DISCOMFORT', 0.0009075648872365948), ('PAS', 0.0007936402703285446), ('Hormonal', 0.00019944254371048652), ('Radiation', 0.00017741997766747576), ('Mobility', 0.000173412474200293), ('ChestWallSwelling', 0.0001060488637141992), ('Lumpectomy', 2.9960955692536147e-05), ('Chemotherapy', 1.3416562172188665e-05), ('Mastectomy', 1.1256321151464536e-05)]
        x = [item[0] for item in data]
        y = [item[1] for item in data]
        loc = zip(x, y)
        plt.ylim(0, 1)
        plt.bar(x, y, facecolor='Teal', edgecolor='black')
        for x, y in loc:
            plt.text(x, y, '%.1g' % y, ha='center', va='bottom')
        plt.tight_layout(rect=[0, 0, 1, 0.95])

    def destroy(self):
        self.figure.clf()

class Page1(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.font = ("Helvetica", 16)
        self.create_widgets()

    def create_widgets(self):
        self.page_label = ctk.CTkLabel(self, text=self.parent.get_text("title"), font=self.font)
        self.page_label.grid(row=0, column=0, pady=50)

        self.button_begin = ctk.CTkButton(self, text=self.parent.get_text("begin_detection"), command=lambda: self.parent.show_frame("Page2"), font=self.font)
        self.button_begin.grid(row=1, column=0, pady=10)
        self.button_about = ctk.CTkButton(self, text=self.parent.get_text("about"), command=lambda: self.parent.show_frame("Pageabout"), font=self.font)
        self.button_about.grid(row=2, column=0, pady=10)

    def configure_grid(self):
        for row in range(3):
            self.grid_rowconfigure(row, weight=0)
        self.grid_columnconfigure(0, weight=1)

    def update_texts(self):
        self.page_label.configure(text=self.parent.get_text("title"))
        self.button_begin.configure(text=self.parent.get_text("begin_detection"))
        self.button_about.configure(text=self.parent.get_text("about"))

class Pageabout(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.font = ("Helvetica", 16)
        self.create_widgets()

    def create_widgets(self):
        self.about_label = ctk.CTkLabel(self, text=self.parent.get_text("about"), font=self.font)
        self.about_label.grid(row=0, column=0, pady=25, columnspan=3, sticky="ew")

        self.about_text = ctk.CTkLabel(self, text=self.parent.get_text("about_text"), font=self.font, wraplength=700)
        self.about_text.grid(row=1, column=0, padx=25, columnspan=3, pady=10)

        image = Image.open(os.path.join(basepath, "image\\UMKC.png")).resize((300, 300))
        tk_image = ImageTk.PhotoImage(image)
        self.image_label = ctk.CTkLabel(self, image=tk_image, text='')
        self.image_label.image = tk_image
        self.image_label.grid(row=2, column=0, padx=25, pady=10)

        image2 = Image.open(os.path.join(basepath, "image\\UMD.jpg")).resize((225, 225))
        tk_image2 = ImageTk.PhotoImage(image2)
        self.image_label2 = ctk.CTkLabel(self, image=tk_image2, text='')
        self.image_label2.image = tk_image2
        self.image_label2.grid(row=2, column=1, padx=25, pady=10)

        image3 = Image.open(os.path.join(basepath, "image\\NYU.png")).resize((300, 300))
        tk_image3 = ImageTk.PhotoImage(image3)
        self.image_label3 = ctk.CTkLabel(self, image=tk_image3, text='')
        self.image_label3.image = tk_image3
        self.image_label3.grid(row=2, column=2, padx=25, pady=10)

        self.return_button = ctk.CTkButton(self, text=self.parent.get_text("return_main_menu"), command=lambda: self.parent.show_frame("Page1"), font=self.font)
        self.return_button.grid(row=3, column=1, padx=25, pady=10)

    def configure_grid(self):
        for row in range(3):
            self.grid_rowconfigure(row, weight=0)
        for col in range(3):
            self.grid_columnconfigure(col, weight=1)

    def update_texts(self):
        self.about_label.configure(text=self.parent.get_text("about"))
        self.about_text.configure(text=self.parent.get_text("about_text"))
        self.return_button.configure(text=self.parent.get_text("return_main_menu"))

class Page2(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.font = ("Helvetica", 16)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        self.page_label = ctk.CTkLabel(self, text=self.parent.get_text("detection_page"), font=self.font)
        self.page_label.grid(row=0, column=0, pady=25, sticky="ew", columnspan=2)

        self.scrollable_checkbox_frame = MyScrollableCheckboxFrame(self, title="reported_symptoms", labels=self.parent.labels, instructions=self.parent.instructions, num_columns=2, font=self.font, get_text=self.parent.get_text)
        self.scrollable_checkbox_frame.grid(row=1, column=0, padx=10, columnspan=2, pady=0, sticky="nsew")

        def on_button():
            self.parent.labels = self.scrollable_checkbox_frame.get()
            self.parent.output_labels = self.label_processing(self.parent.labels)
            self.parent.show_frame("Page3")

        self.submit_button = ctk.CTkButton(self, text=self.parent.get_text("submit"), command=on_button, font=self.font)
        self.back_button = ctk.CTkButton(self, text=self.parent.get_text("return"), command=lambda: self.parent.show_frame("Page1"), font=self.font)
        self.submit_button.grid(row=2, column=0, pady=20, sticky="ew")
        self.back_button.grid(row=2, column=1, pady=20, sticky="ew")

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=0)
        for row in range(1, 3):
            self.grid_rowconfigure(row, weight=1)
        for col in range(2):
            self.grid_columnconfigure(col, weight=1)

    def update_texts(self):
        self.page_label.configure(text=self.parent.get_text("detection_page"))
        self.submit_button.configure(text=self.parent.get_text("submit"))
        self.back_button.configure(text=self.parent.get_text("return"))
        self.scrollable_checkbox_frame.update_texts()

    def label_processing(self, labels):
        def str2b(str_):
            return 0 if str_ == '0' else 1
        output_labels = OrderedDict({'BMI': "22.1", 'Age': "40", 'TIME_LAPSE': "1", 'Mobility': "1", 'ArmSwelling': "0", 'BreastSwelling': "0", 'Skin': "0", 'PAS': "0", 'FHT': "1", 'DISCOMFORT': "0", 'SYM_COUNT': "2", 'ChestWallSwelling': "0", 'Chemotherapy': "1", 'Radiation': "0", 'Number_nodes': "1", 'Mastectomy': "1", 'Lumpectomy': "0", 'Hormonal': "0"})
        output_labels['BMI'] = float(labels['Weight (Kg)']) / (float(labels['Height (cm)'])**2)
        output_labels['Age'] = labels['Age (years)']
        output_labels['TIME_LAPSE'] = math.log(float(labels['Time Lapse (years)']))
        output_labels['Mobility'] = max(int(labels['Limited shoulder movement']), int(labels['Limited elbow movement']), int(labels['Limited wrist movement']), int(labels['Limited fingers movement']), int(labels['Limited arm movement']))
        output_labels['Armswelling'] = labels['Arm or hand swelling']
        output_labels['BreastSwelling'] = labels['Breast swelling']
        output_labels['Skin'] = labels['Toughness or thickness of skin']
        output_labels['PAS'] = labels['Pain, aching, soreness']
        output_labels['FHT'] = max(int(labels['Firmness']), int(labels['Heaviness']), int(labels['Tightness']))
        output_labels['DISCOMFORT'] = labels['Pain, aching, soreness']
        output_labels['SYM_COUNT'] = sum(str2b(labels[k]) for k in ['Limited shoulder movement', 'Limited elbow movement', 'Limited wrist movement', 'Limited fingers movement', 'Limited arm movement', 'Arm or hand swelling', 'Breast swelling', 'Chest swelling', 'Toughness or thickness of skin', 'Pain, aching, soreness', 'Tightness', 'Firmness', 'Heaviness', 'Numbness', 'Burning', 'Stabbing', 'Tingling', 'Fatigue', 'Weakness', 'Redness', 'Hotness', 'Stiffness', 'Tenderness', 'Blister'])
        output_labels['ChestWallSwelling'] = labels['Chest swelling']
        output_labels['Chemotherapy'] = labels['Chemotherapy']
        output_labels['Radiation'] = labels['Radiation']
        output_labels['Number_nodes'] = int(labels['SLNB_Removed_LN'])+ int(labels['ALND_Removed_LN'])
        output_labels['Mastectomy'] = labels['Mastectomy']
        output_labels['Lumpectomy'] = labels['Lumpectomy']
        output_labels['Hormonal'] = labels['Hormonal therapy']
        return output_labels

class Page3(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.font = ("Helvetica", 16)
        self.parent = parent
        self.constructed = False

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=0)
        for row in range(1, 3):
            self.grid_rowconfigure(row, weight=1)
        for col in range(2):
            self.grid_columnconfigure(col, weight=1)

    def construct(self):
        if not self.constructed:
            self.constructed = True
        num_columns = 1
        self.page_label = ctk.CTkLabel(self, text=self.parent.get_text("detection_result"), font=self.font)
        self.page_label.grid(row=0, column=0, columnspan=num_columns*2, pady=25, sticky="nsew")

        select_mask = ['ArmSwelling', 'BreastSwelling', 'Skin', 'DISCOMFORT', 'SYM_COUNT', 'ChestWallSwelling', 'Age', 'Mastectomy', 'Hormonal', 'TIME_LAPSE']
        data_select = np.array([[self.parent.output_labels[item] for item in select_mask]], dtype=float)
        model_path = os.path.join(basepath, 'models\\GBT.pkl')

        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        y_pred = model.predict(data_select)
        re_dict = {0: self.parent.get_text("low_risk"), 1: self.parent.get_text("mild"), 2: self.parent.get_text("moderate_severe")}

        self.text_result = self.parent.get_text("your_predicted_lymphedema_risk").format(risk=re_dict[y_pred.item()])
        self.gbt_result = ctk.CTkLabel(self, text=self.text_result, font=self.font) # text_result -> gbt_result
        self.gbt_result.grid(row=1, columnspan=2)

        self.plot_button = ctk.CTkButton(self, text=self.parent.get_text("plot_bar_chart"), command=lambda: self.parent.show_frame("Pagechart"), font=self.font)
        self.plot_button.grid(row=2, column=0, pady=20, sticky="ew")
        self.back_button = ctk.CTkButton(self, text=self.parent.get_text("return"), command=lambda: self.parent.show_frame("Page2"), font=self.font)
        self.back_button.grid(row=2, column=1, pady=20, sticky="ew")

        self.update_texts()

    def remove(self):
        for widget in self.winfo_children():
            widget.destroy()

    def update_texts(self):
        self.page_label.configure(text=self.parent.get_text("detection_result"))
        self.gbt_result.configure(text=self.parent.get_text(self.text_result))
        self.plot_button.configure(text=self.parent.get_text("plot_bar_chart"))
        self.back_button.configure(text=self.parent.get_text("return"))

class Pagechart(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.font = ("Helvetica", 16)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        self.page_label = ctk.CTkLabel(self, text=self.parent.get_text("plot_bar_chart"), font=self.font)
        self.page_label.grid(row=0, column=0, pady=20, sticky="nsew")
        self.plot_frame = PLOTFrame(master=self, font=self.font, title="plot_bar_chart", get_text=self.parent.get_text)
        self.plot_frame.grid(row=1, column=0, padx=10, columnspan=2, pady=(10, 0), sticky="nsew")
        self.back_button = ctk.CTkButton(self, text=self.parent.get_text("return"), command=lambda: self.parent.show_frame("Page3"), font=self.font)
        self.back_button.grid(row=2, column=0, padx=10, columnspan=2, pady=(10, 0), sticky="ew")

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=0)
        for row in range(1, 3):
            self.grid_rowconfigure(row, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def update_texts(self):
        self.page_label.configure(text=self.parent.get_text("plot_bar_chart"))
        self.back_button.configure(text=self.parent.get_text("return"))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.translations = load_translations(os.path.join(basepath, "translations.json"))
        self.font = ("Helvetica", 16)
        self.lang = 'English'
        self.labels = OrderedDict({ 'Age (years)': '40', 'Time Lapse (years)': '1', 'Weight (Kg)': '60', 'Height (cm)': '170', 'Limited shoulder movement': "0",\
                                    'Limited elbow movement': "0", 'Limited wrist movement': "0", 'Limited fingers movement': "0", 'Limited arm movement': "0", 'Arm or hand swelling': "0",\
                                    'Breast swelling': "0", 'Chest swelling': "0", 'Toughness or thickness of skin': "0", 'Pain, aching, soreness': "0", 'Tightness': "0", 'Firmness': "0",\
                                    'Heaviness': "1", 'Numbness': "0", 'Burning': "0", 'Stabbing': "0", 'Tingling': "0", 'Fatigue': "0", 'Weakness': "0", 'Redness': "0", 'Hotness': "0",\
                                    'Stiffness': "0", 'Tenderness': "0", 'Blister': "0", 'Chemotherapy': '0', 'Radiation': '0', 'SLNB_Removed_LN': '0', 'ALND_Removed_LN': '0',\
                                    'Mastectomy': '0', 'Lumpectomy': '0', 'Hormonal therapy': '0'})  # key: default value
        self.instructions = ['Your age (years)', 'Time lapse since your recent breast cancer surgery (years)', 'Body weight (Kg)', 'Height (cm)', 'How much do you feel your shoulder movement is limited?', 'How much do you feel your elbow movement is limited?', 'How much do you feel your wrist movement is limited?', 'How much do you feel your fingers movement is limited?', 'How much do you feel your arm movement is limited?', 'How much do your arm or hand swell: if both, select the most intense feelings.', 'How much does your breast swell?', 'How much does your chest swell?', 'Toughness or thickness of skin', 'Do you feel pain, aching, or soreness: if more than one feeling, select the most intense one.', 'Tightness of your affected arm.', 'Firmness of your affected arm.', 'Heaviness of your affected arm.', 'Numbness of your affected arm.', 'The feeling of burning of your affected arm.', 'The feeling of stabbing of your affected arm.', 'The feeling of tingling, or feeling of needles of your affected arm.', 'The feeling of fatigue of your affected arm.', 'The feeling of weakness of your affected arm.', 'How much does your affected arm looks red?', 'How much does your affected arm feel hot?', 'How much does your affected arm feel stiff?', 'How much does your affected arm feel sensitive or tender when touching things?', 'Does you affected arm blisters?', 'Whether the patient had chemotherapy.', 'Whether the patient had radiation.', 'The number of removed sentinel lymph nodes.', 'The number of removed axillary lymph nodes', 'Whether the patient had Mastectomy.', 'Whether the patient had Lumpectomy.', 'Whether the patient had hormonal therapy.']
        self.output_labels = OrderedDict({'BMI': "22.1", 'Age': "40", 'TIME_LAPSE': "1", 'Mobility': "1", 'ArmSwelling': "0", 'BreastSwelling': "0", 'Skin': "0", 'PAS': "0", 'FHT': "1", 'DISCOMFORT': "0", 'SYM_COUNT': "2", 'ChestWallSwelling': "0", 'Chemotherapy': "1", 'Radiation': "0", 'Number_nodes': "1", 'Mastectomy': "1", 'Lumpectomy': "0", 'Hormonal': "0"})
        ctk.set_appearance_mode("light")
        self.title(self.get_text("title"))
        self.geometry("800x600")
        self.menu_bar = tk.Menu(self, font=self.font)
        self.config(menu=self.menu_bar)
        self.language_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.font)
        self.menu_bar.add_cascade(label="Language", menu=self.language_menu)
        # 添加语言选项
        languages = ["English (English)", "Chinese (简体中文)", "Spanish (Español)"]
        for language in languages:
            self.language_menu.add_command(label=language, command=lambda lang=language: self.set_language(lang))

        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.font)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Instructions", command=self.show_instructions)
        self.help_menu.add_command(label="About", command=lambda: self.show_frame("Pageabout"))

        self.frames = {}
        self.create_frames()
        self.show_frame("Page1")

    def create_frames(self):
        self.frames["Page1"] = Page1(self)
        self.frames["Page2"] = Page2(self)
        self.frames["Page3"] = Page3(self)
        self.frames["Pageabout"] = Pageabout(self)
        self.frames["Pagechart"] = Pagechart(self)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "remove") and callable(getattr(frame, "remove")):
            self.frames[page_name].remove()
            self.frames[page_name].construct()
        frame.tkraise()
        frame.configure_grid()

    def get_text(self, key):
        return get_translation(self.translations, self.lang, key)

    def set_language(self, lang):
        self.lang = lang.split(' ')[0]
        self.update_texts()

    def update_texts(self):
        for key, frame in self.frames.items():
            if key == 'Page3' and not self.frames["Page3"].constructed: # This page should not be updated initially, since it can not be initially constructed.
                continue
            if hasattr(frame, "update_texts") and callable(getattr(frame, "update_texts")):
                frame.update_texts()

    def show_instructions(self):
        # Function to display instructions
        tk.messagebox.showinfo("Instructions", self.get_text("In the detection page, detailed instructions are shown when you move the cursor🖱️ close to the words (for example, Your age (years)...)."))

if __name__ == '__main__':
    global basepath
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        basepath = sys._MEIPASS
    else:
        basepath = ""
    app = App()
    app.protocol("WM_DELETE_WINDOW", sys.exit)
    app.mainloop()
