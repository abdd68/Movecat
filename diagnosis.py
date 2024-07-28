import customtkinter as ctk
import tkinter as tk
import numpy as np
from collections import OrderedDict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import sys
import os
import pickle
import math
import json
from tkinter import messagebox
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties

def load_translations(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def load_user_data(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_user_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def get_translation(translations, lang, key):
    return translations.get(lang, {}).get(key, key)



class CreateToolTip:
    def __init__(self, widget, text, font = None, delay=450):
        self.font = font
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
        label = ctk.CTkLabel(self.tooltip, text=self.text, corner_radius=5, font = self.font)
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
    def __init__(self, master, title, labels, suggestions, instructions, num_columns, font, get_text):
        super().__init__(master, width=660, height=350) # label_text=get_text(title)
        # self.title = title
        def on_mouse_wheel(event):
            self._parent_canvas.yview_scroll(-50 * int((event.delta / 120)), "units")
        if os.name == 'nt':
            self.bind_all("<MouseWheel>", on_mouse_wheel)
        elif os.name == 'posix':
            self.bind_all("<Button-4>", on_mouse_wheel)
            self.bind_all("<Button-5>", on_mouse_wheel)
        self.labels = labels
        self.suggestions = suggestions
        self.instructions = instructions
        self.label_handles = []
        self.tooltip_handles = []
        self.output_labels = None
        self.entries = []
        self.options = ["None", "A little", "Somewhat", "Quite a bit", "Severe"]
        self.font = font
        self.get_text = get_text
        self.lrow = 1
        bg_color = self.cget("fg_color")
        for i, (label_text) in enumerate(self.labels.keys()):
            if i < 30:
                row, column = i // num_columns, i % num_columns
            elif i == 30:
                row, column = i // num_columns + 2, 0
            elif i == 31:
                row, column = i // num_columns + 3, 0
            else:
                row, column = i // num_columns - 1, i % num_columns
                
            label_frame = ctk.CTkFrame(self, bg_color=bg_color, fg_color=bg_color)
            if i != 30 and i != 31:
                label_frame.grid(row=row+1, column=column*2, padx=5, pady=5, sticky='w')
            else:
                label_frame.grid(row=row+1, column=column*2, columnspan = 2, padx=5, pady=5, sticky='w')
            
            label = ctk.CTkLabel(label_frame, text=get_text(label_text), font=self.font, bg_color=bg_color, fg_color=bg_color)
            label.pack(side='left')
            self.label_handles.append(label)
            if i < 28:  # 前28项为必填
                asterisk = ctk.CTkLabel(label_frame, text="*", font=("Helvetica", 5*master.parent.fontsize/3), text_color="red", bg_color=bg_color, fg_color=bg_color)
                asterisk.pack(side='left')

            tooltip_text = self.get_text(self.instructions[i])
            tooltip = CreateToolTip(label, tooltip_text, font=self.font)
            self.tooltip_handles.append(tooltip)
            custom_font = ctk.CTkFont(family="Helvetica", size=master.parent.fontsize)
            if self.suggestions is None:
                entry_b = ctk.StringVar(value='')
                entry_var = ctk.StringVar(value='-')
            else:
                entry_b = ctk.StringVar(value=self.get_text(self.int2str(i, suggestions[label_text])))
                entry_var = ctk.StringVar(value=self.get_text(self.int2str(i, suggestions[label_text])))
            if i < 4:
                entry = ctk.CTkEntry(self, textvariable=entry_b, font = custom_font)
            elif i < 28:
                entry = ctk.CTkOptionMenu(self, variable=entry_var, values=self.options, font=custom_font)
                entry._dropdown_menu.configure(font=custom_font)
            elif i < 30:
                entry = ctk.CTkOptionMenu(self, variable=entry_var, values=['No', 'Yes'], font=custom_font)
                entry._dropdown_menu.configure(font=custom_font)
            elif i < 32:
                entry = ctk.CTkEntry(self, textvariable=entry_b, font = custom_font)
            else:
                entry = ctk.CTkOptionMenu(self, variable=entry_var, values=['No', 'Yes'], font=custom_font)
                entry._dropdown_menu.configure(font=custom_font)
                
            if i != 30 and i != 31:
                entry.grid(row=row+1, column=column*2+1, padx=5, pady=5, sticky='w')
            else:
                entry.grid(row=row+1, column=2, columnspan = 2, padx=5, pady=5, sticky='w')

            self.entries.append(entry)
            self.lrow += 1
            self.grid_rowconfigure(row+1, weight=1)
            if row == 0:
                self.grid_columnconfigure(column*2, weight=1)
                self.grid_columnconfigure(column*2+1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def get(self):
        admit_page3 = True
        for i, (key, value) in enumerate(self.labels.items()):
            self.labels[key] = self.str2int(i, self.entries[i].get())
            if self.labels[key].strip() != '' and self.labels[key].strip() != '-':
                continue
            else:
                if i < 28:
                    admit_page3 = False
                    break
                if i >= 28:
                    self.labels[key] = '-'
        return self.labels, admit_page3
    
    def update_texts(self):
        # self.configure(label_text=self.get_text(self.title))
        for i, (label_text, suggestion) in enumerate(self.labels.items()):
            self.label_handles[i].configure(text=self.get_text(label_text))
        for i in range(len(self.instructions)):
            self.tooltip_handles[i].text = self.get_text(self.instructions[i])
            if i >= 4 and i < 28:
                self.entries[i].configure(values=[self.get_text(option) for option in self.options])
            elif i >= 28 and i < 30 or i >= 32:
                self.entries[i].configure(values=[self.get_text(option) for option in ['No', 'Yes']])
    
    def str2int(self, i, str_):
        if str_ == "None" or str_ == "没有" or str_ == "Ninguno" :
            return '0'
        elif str_ == "A little" or str_ == "轻微" or str_ == "Un poco" :
            return '1'
        elif str_ == "Somewhat" or str_ == "有一些" or str_ == "Algo" :
            return '2'
        elif str_ == 'Quite a bit' or str_ == "较重" or str_ == "Relativamente grave" :
            return '3'
        elif str_ == 'Severe' or str_ == "严重" or str_ == "Severo" :
            return '4'
        elif str_ == "Yes" or str_ == "是" or str_ == "Sí":
            return '1'
        elif str_ == "No" or str_ == "否":
            return '0'
        else:
            return str_
        
    def int2str(self, i, int_):
        if int_ == "0" :
            if i >= 4 and i < 28:
                return "None"
            elif i >= 28 and i < 30 or i >= 32:
                return "No"
            else:
                return int_
        elif int_ == "1" :
            if i >= 4 and i < 28:
                return "A little"
            elif i >= 28 and i < 30 or i >= 32:
                return "Yes"
            else:
                return int_
        elif int_ == "2" :
            if i >= 4 and i < 28:
                return "Somewhat"
            else:
                return int_
        elif int_ == "3" :
            if i >= 4 and i < 28:
                return "Quite a bit"
            else:
                return int_
        elif int_ == "4" :
            if i >= 4 and i < 28:
                return "Severe"
            else:
                return int_
        else:
            return int_

class PLOTFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, title=None, font=None, get_text=None, fg_color = 'white', height=280):
        super().__init__(master, width=720, height=height, label_text=get_text(title), fg_color = fg_color)
        self.master = master
        self.get_text = get_text
        self.font = font
        def on_mouse_wheel(event):
            self._parent_canvas.yview_scroll(-50 * int((event.delta / 120)), "units")
        if os.name == 'nt':
            self.bind_all("<MouseWheel>", on_mouse_wheel)
        elif os.name == 'posix':
            self.bind_all("<MouseWheel>", on_mouse_wheel)

    def construct(self):
        self.create_figure1()
        self.create_figure2()
        self.create_figure3()
        self.createWidget()

    def createWidget(self):
        self.grid_columnconfigure(0, weight=1)

    def save_score(self):
        if self.master.parent.score_save_flag:
            with open(self.master.parent.record_data_path, 'r') as json_file:
                existing_data = json.load(json_file)
                user_dict = existing_data[self.master.parent.current_user]
                if 'score_list' not in user_dict:
                    user_dict['score_list'] = [self.overall_score]
                else: 
                    user_dict['score_list'].append(self.overall_score)
            with open(self.master.parent.record_data_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)
            self.master.parent.score_save_flag = False

    def cal_overall_score(self, y_pred):
        max_index = np.argsort(y_pred)[-1]
        submax_index = np.argsort(y_pred)[-2]
        if max_index == 2:
            base_score = 2 / 3 
            bias = (y_pred[max_index] - y_pred[submax_index]) / 3
            overall_score = base_score + bias
        elif max_index == 0:
            base_score = 0 / 3 
            bias = (y_pred[max_index] - y_pred[submax_index]) / 3
            overall_score = base_score + bias
        elif max_index == 1:
            base_score = 1 / 2 
            bias = (y_pred[max_index] - y_pred[submax_index]) / 6
            if submax_index == 2:
                overall_score = base_score + bias
            else:
                overall_score = base_score - bias
        overall_score *= 100
        return overall_score
        
    def create_figure1(self):
        y_pred = self.master.parent.y_pred.squeeze()
        overall_score = self.cal_overall_score(y_pred)
        self.overall_score = overall_score
        self.save_score()

        # 创建一个Figure
        plt.figure(num = 1, figsize=(8, 3), dpi=100)
        
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        if self.master.parent.lang == 'Chinese':
            font = {'family': 'SimHei', 'weight': 'normal', 'size': 22}
        else:
            font = {'family': 'serif', 'serif': 'Times New Roman', 'weight': 'normal', 'size': 22}
        plt.rc('font', **font)

        # 创建分段渐变条
        plt.title(self.get_text('Lymphedema risk score'), pad=50)
        gradient = np.linspace(0, 1, 1000).reshape(1, -1)
        plt.imshow(gradient, aspect='auto', cmap='RdYlGn_r', extent=[0, 100, 0, 1])

        # 绘制风险评分的指示线
        plt.axvline(overall_score, color='black', linewidth=2)
        plt.text(overall_score, 0.5, f'{overall_score:.1f}', color='black', va='center', ha='center', bbox=dict(facecolor='white',edgecolor='none', alpha=0.7))

        # 添加分界线
        threshold1 = 33.3
        threshold2 = 66.7
        plt.axvline(threshold1, color='blue', linestyle='--', linewidth=2)
        plt.axvline(threshold2, color='blue', linestyle='--', linewidth=2)

        # 添加箭头符号指示当前值，并将箭头放在图像上方
        re_dict = {0: "low_risk", 1: "mild", 2: "moderate_severe"}
        plt.gca().annotate(
            self.master.parent.get_text(re_dict[np.argsort(y_pred)[-1]]), xy=(overall_score, 1), xytext=(overall_score, 1.2),
            arrowprops=dict(facecolor='black', shrink=0.05, headwidth=10, width=2),
            ha='center', va='bottom', backgroundcolor='white'
        )

        # 设置图形标题和标签
        plt.gca().set_yticks([])
        plt.gca().set_xlim(0, 100)
        plt.tight_layout()

        self.canvas = FigureCanvasTkAgg(plt.figure(num=1), self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        
    def create_figure2(self):
        with open(self.master.parent.record_data_path, 'r') as json_file:
            existing_data = json.load(json_file)
            score_list = existing_data[self.master.parent.current_user]['score_list']

        plt.figure(num = 3, figsize=(8, 6.8), dpi=100)
        def plot_scores(scores):
            x = range(1, len(scores) + 1)
            plt.xticks(range(min(x) - 1, max(x) + 1, 1))
            plt.ylim(min(scores) - 5, max(scores) + 5)
            plt.plot(x, scores, marker='o', linestyle='-', color='b', linewidth=3, label='Scores')
            plt.title(self.get_text('Lymphedema Risk Score History'), pad = 20)
            plt.xlabel(self.get_text('Test Number'))
            plt.ylabel(self.get_text('Score'))
            plt.grid(True)
            for i in range(len(scores)):
                plt.text(x[i], scores[i] + 0.4, str(round(scores[i],1)), fontsize=24, ha='center', va='bottom')

        def create_buttons(self):
            button_frame = ctk.CTkFrame(self, fg_color='white', bg_color='white')
            button_frame.pack(fill='x', pady=(0, 0))
            button_frame.columnconfigure(0, weight=1)
            button_frame.columnconfigure(1, weight=1)
            button_frame.columnconfigure(2, weight=1)
            button_frame.columnconfigure(3, weight=1)
            
            custom_font = ctk.CTkFont(family="Helvetica", size=self.master.parent.fontsize)
            recent_5_button = ctk.CTkButton(button_frame, text=self.get_text("last 5 times"), command=show_recent_5, font=custom_font)
            recent_5_button.grid(row=0, column = 0, pady = 10)

            recent_10_button = ctk.CTkButton(button_frame, text=self.get_text("last 10 times"), command=show_recent_10, font=custom_font)
            recent_10_button.grid(row=0, column = 1, pady = 10)

            recent_20_button = ctk.CTkButton(button_frame, text=self.get_text("last 20 times"), command=show_recent_20, font=custom_font)
            recent_20_button.grid(row=0, column = 2, pady = 10)

            all_button = ctk.CTkButton(button_frame, text=self.get_text("Overall"), command=show_all, font=custom_font)
            all_button.grid(row=0, column = 3, pady = 10)
        
        def get_recent_data(data, num):
            return data[-num:]

        def show_recent_5():
            recent_5_data = get_recent_data(score_list, 5)
            update_plot(recent_5_data)
            
        def show_recent_10():
            recent_10_data = get_recent_data(score_list, 10)
            update_plot(recent_10_data)

        def show_recent_20():
            recent_20_data = get_recent_data(score_list, 20)
            update_plot(recent_20_data)
            
        def show_all():
            update_plot(score_list)

        def update_plot(data):
            plt.figure(num=3).clear()  # 清除之前的图表
            plot_scores(data)
            self.canvas_.draw()

        scores = score_list[-5:]
        plot_scores(scores)
        plt.tight_layout()

        self.canvas_ = FigureCanvasTkAgg(plt.figure(num=3), self)
        self.canvas_.draw()
        self.canvas_.get_tk_widget().pack(side='top', fill='both', expand=1)

        create_buttons(self)

    def create_figure3(self):
        
        plt.figure(num=4, figsize=(7, 12), dpi=80, facecolor="white", edgecolor='Teal', frameon=True)
        plt.title(self.get_text('Important factors contributing to Lymphedema'), pad=20, fontsize=36)
        plt.yscale('symlog', linthresh=0.00005)
        plt.tick_params(axis='x', labelsize=18, rotation=60)
        font_prop = FontProperties(family='Times New Roman')
        plt.tick_params(axis='y', labelsize=18)
        for label in plt.gca().get_yticklabels():
            label.set_fontproperties(font_prop)
        data = [('Arm or hand swelling', 0.5666504441537034), ('Symptom severity', 0.32829106757634513), ('Breast swelling', 0.05866949630997336), ('time lapse since last surgery', 0.0270874570016606), ('Height and weight (BMI)', 0.0048442873079247665), ('Tightness, firmness, and heaviness', 0.003799860520333767), ('Age', 0.0036176355797100405), ('Number of removed nodes', 0.0027917973843724414), ('Toughness of skin', 0.0018357913101027619), ('Discomfort', 0.0009075648872365948), ('Pain, aching and soreness', 0.0007936402703285446), ('Hormonal', 0.00019944254371048652), ('Radiation', 0.00017741997766747576), ('Limited Mobility', 0.000173412474200293), ('ChestWall swelling', 0.0001060488637141992), ('Lumpectomy', 2.9960955692536147e-05), ('Chemotherapy', 1.3416562172188665e-05), ('Mastectomy', 1.1256321151464536e-05)]
        data = [(self.get_text(value1),value2) for value1, value2 in data]
        x = [item[0] for item in data]
        y = [item[1] for item in data]
        loc = zip(x, y)
        plt.ylim(0, 1)
        plt.bar(x, y, facecolor='Teal')
        plt.xticks(fontsize = 24)
        plt.yticks(fontsize = 24)
        for x, y in loc:
            plt.text(x, y, '%.1g' % y, ha='center', va='bottom')
        plt.tight_layout()

        self.canvas = FigureCanvasTkAgg(plt.figure(num=4), self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1, pady = 30)

    def update_texts(self):
        self.remove()
        self.construct()

    def remove(self):
        plt.close('all')
        for widget in self.winfo_children():
            widget.destroy()


class Page1(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.font = self.parent.font_list[0]
        self.construct()

    def construct(self):
        self.page_label = ctk.CTkLabel(self, text=self.parent.get_text("title"), font=self.font)
        self.page_label.grid(row=0, column=0, pady=50)

        self.button_login, self.button_begin = None, None
        if self.parent.current_user is None:
            self.button_login = ctk.CTkButton(self, text=self.parent.get_text("Login/Register"), command=lambda: self.parent.show_frame("PageLogin"), font=self.font)
            self.button_login.grid(row=1, column=0, pady=10)
        else:
            self.button_begin = ctk.CTkButton(self, text=self.parent.get_text("begin_detection"), command=lambda: self.parent.show_frame("Page2"), font=self.font)
            self.button_begin.grid(row=2, column=0, pady=10)
        self.button_about = ctk.CTkButton(self, text=self.parent.get_text("about"), command=lambda: self.parent.show_frame("Pageabout"), font=self.font)
        self.button_about.grid(row=3, column=0, pady=10)

    def remove(self):
        for widget in self.winfo_children():
            widget.destroy()

    def configure_grid(self):
        for row in range(3):
            self.grid_rowconfigure(row, weight=0)
        self.grid_columnconfigure(0, weight=1)

    def update_texts(self):
        self.page_label.configure(text=self.parent.get_text("title"))
        if self.button_login is not None:
            self.button_login.configure(text=self.parent.get_text("Login/Register"))
        if self.button_begin is not None:
            self.button_begin.configure(text=self.parent.get_text("begin_detection"))
        self.button_about.configure(text=self.parent.get_text("about"))

class Pageabout(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.font = self.parent.font_list[0]
        self.create_widgets()

    def create_widgets(self):
        self.about_label = ctk.CTkLabel(self, text=self.parent.get_text("about"), font=self.font)
        self.about_label.grid(row=0, column=0, pady=25, columnspan=3, sticky="ew")

        self.about_text = ctk.CTkLabel(self, text=self.parent.get_text("about_text"), font=self.font, wraplength=700)
        self.about_text.grid(row=1, column=0, padx=25, columnspan=3, pady=10)

        image = Image.open(os.path.join(basepath, "data", "UMKC.png")).resize((300, 300))
        tk_image = ImageTk.PhotoImage(image)
        self.image_label = ctk.CTkLabel(self, image=tk_image, text='')
        self.image_label.image = tk_image
        self.image_label.grid(row=2, column=0, padx=25, pady=10)

        image2 = Image.open(os.path.join(basepath, "data", "UMD.jpg")).resize((225, 225))
        tk_image2 = ImageTk.PhotoImage(image2)
        self.image_label2 = ctk.CTkLabel(self, image=tk_image2, text='')
        self.image_label2.image = tk_image2
        self.image_label2.grid(row=2, column=1, padx=25, pady=10)

        image3 = Image.open(os.path.join(basepath, "data", "NYU.png")).resize((300, 300))
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
        self.parent = parent
        self.font = self.parent.font_list[0]
        self.reset_flag = False
        self.constructed = False

    def load_suggestions(self):
        if os.path.exists(self.parent.record_data_path):
            with open(self.parent.record_data_path, 'r') as json_file:
                json_data = json.load(json_file, object_pairs_hook=OrderedDict)
                if self.parent.current_user in json_data:
                    data = json_data[self.parent.current_user]['suggestions']
                else:
                    data = None
                return data
        else:
            return {}
        
    def save_suggestions(self, suggestions):
        existing_data = load_user_data(self.parent.record_data_path)
        try:
            existing_data[self.parent.current_user]['suggestions'] = suggestions
        except:
            existing_data[self.parent.current_user] = {}
            existing_data[self.parent.current_user]['suggestions'] = suggestions
        with open(self.parent.record_data_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)

    def construct(self):
        if not self.constructed:
            self.constructed = True
        if self.reset_flag:
            suggestions = None
        else:
            suggestions = self.load_suggestions()
        self.reset_flag = False

        self.page_label = ctk.CTkLabel(self, text=self.parent.get_text("detection_page"), font=self.font)
        self.page_label.grid(row=0, column=0, pady=25, sticky="ew", columnspan=4)

        self.scrollable_checkbox_frame = MyScrollableCheckboxFrame(self, title="reported_symptoms", labels=self.parent.labels, suggestions = suggestions, instructions=self.parent.instructions, num_columns=2, font=self.font, get_text=self.parent.get_text)
        self.scrollable_checkbox_frame.grid(row=1, column=0, padx=10, columnspan=4, pady=0, sticky="nsew")

        def on_button_submit():
            self.parent.labels, admit_page3 = self.scrollable_checkbox_frame.get()
            if not admit_page3:
                messagebox.showwarning(self.parent.get_text("Incomplete Data"), self.parent.get_text("Data not fully completed. Please fill in all required fields."))
                return
            suggestions = self.parent.labels
            self.save_suggestions(suggestions)
            self.parent.output_labels = self.label_processing(self.parent.labels)
            self.parent.score_save_flag = True
            self.parent.show_frame("Page3")

        def on_button_save():
            self.parent.labels, _ = self.scrollable_checkbox_frame.get()
            suggestions = self.parent.labels
            self.save_suggestions(suggestions)
            messagebox.showinfo(self.parent.get_text("Save"), self.parent.get_text("Data saved!"))
        
        def on_button_reset():
            response = messagebox.askyesno(self.parent.get_text("Confirmation"), self.parent.get_text("Are you sure you want to reset? This will clear your reported symptoms."))
            if not response:
                return
            self.reset_flag = True
            self.parent.show_frame("Page2")
            
        self.submit_button = ctk.CTkButton(self, text=self.parent.get_text("Reset"), command=on_button_reset, font=self.font)
        self.submit_button.grid(row=2, column=0, pady=20, sticky="ew")
        self.submit_button = ctk.CTkButton(self, text=self.parent.get_text("Save"), command=on_button_save, font=self.font)
        self.submit_button.grid(row=2, column=1, pady=20, sticky="ew")
        self.submit_button = ctk.CTkButton(self, text=self.parent.get_text("submit"), command=on_button_submit, font=self.font)
        self.submit_button.grid(row=2, column=2, pady=20, sticky="ew")
        self.back_button = ctk.CTkButton(self, text=self.parent.get_text("return"), command=lambda: self.parent.show_frame("Page1"), font=self.font)
        self.back_button.grid(row=2, column=3, pady=20, sticky="ew")

        self.update_texts()

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=0)
        for row in range(1, 2):
            self.grid_rowconfigure(row, weight=1)
        for col in range(4):
            self.grid_columnconfigure(col, weight=1)

    def update_texts(self):
        self.page_label.configure(text=self.parent.get_text("detection_page"))
        self.submit_button.configure(text=self.parent.get_text("submit"))
        self.back_button.configure(text=self.parent.get_text("return"))
        self.scrollable_checkbox_frame.update_texts()
    
    def remove(self):
        for widget in self.winfo_children():
            widget.destroy()
            
    def validate_str(self, _str):
        if _str == '-':
            return '0'
        else:
            return _str
        
    def label_processing(self, labels):
        def str2b(str_):
            return 0 if str_ == '0' else 1
        output_labels = OrderedDict({'BMI': "22.1", 'Age': "40", 'TIME_LAPSE': "1", 'Mobility': "1", 'ArmSwelling': "0", 'BreastSwelling': "0", 'Skin': "0", 'PAS': "0", 'FHT': "1", 'DISCOMFORT': "0", 'SYM_COUNT': "2", 'ChestWallSwelling': "0", 'Chemotherapy': "1", 'Radiation': "0", 'Number_nodes': "1", 'Mastectomy': "1", 'Lumpectomy': "0", 'Hormonal': "0"})
        output_labels['BMI'] = float(labels['Weight (Kg)']) / (float(labels['Height (cm)'])**2)
        output_labels['Age'] = labels['Age (years)']
        output_labels['TIME_LAPSE'] = math.log(float(labels['Time Lapse (years)']))
        output_labels['Mobility'] = max(int(labels['Limited shoulder movement']), int(labels['Limited elbow movement']), int(labels['Limited wrist movement']), int(labels['Limited fingers movement']), int(labels['Limited arm movement']))
        output_labels['ArmSwelling'] = labels['Arm or hand swelling']
        output_labels['BreastSwelling'] = labels['Breast swelling']
        output_labels['Skin'] = labels['Toughness or thickness of skin']
        output_labels['PAS'] = labels['Pain, aching, soreness']
        output_labels['FHT'] = max(int(labels['Firmness']), int(labels['Heaviness']), int(labels['Tightness']))
        output_labels['DISCOMFORT'] = labels['Pain, aching, soreness']
        output_labels['SYM_COUNT'] = sum(str2b(labels[k]) for k in ['Limited shoulder movement', 'Limited elbow movement', 'Limited wrist movement', 'Limited fingers movement', 'Limited arm movement', 'Arm or hand swelling', 'Breast swelling', 'Chest swelling', 'Toughness or thickness of skin', 'Pain, aching, soreness', 'Tightness', 'Firmness', 'Heaviness', 'Numbness', 'Burning', 'Stabbing', 'Tingling', 'Fatigue', 'Weakness', 'Redness', 'Hotness', 'Stiffness', 'Tenderness', 'Blister'])
        output_labels['ChestWallSwelling'] = labels['Chest swelling']
        output_labels['Chemotherapy'] = self.validate_str(labels['Chemotherapy'])
        output_labels['Radiation'] = self.validate_str(labels['Radiation'])
        output_labels['Number_nodes'] = int(self.validate_str(labels['SLNB_Removed_LN']))+ int(self.validate_str(labels['ALND_Removed_LN']))
        output_labels['Mastectomy'] = self.validate_str(labels['Mastectomy'])
        output_labels['Lumpectomy'] = self.validate_str(labels['Lumpectomy'])
        output_labels['Hormonal'] = self.validate_str(labels['Hormonal therapy'])
        return output_labels

class Page3(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.font = self.parent.font_list[0]
        self.constructed = False

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=0)
        for row in range(1, 4):
            self.grid_rowconfigure(row, weight=1)
        for col in range(2):
            self.grid_columnconfigure(col, weight=1)

    def construct(self):
        if not self.constructed:
            self.constructed = True
        num_columns = 1
        self.page_label = ctk.CTkLabel(self, text=self.parent.get_text("detection_result"), font=self.font)
        self.page_label.grid(row=0, column=0, columnspan=num_columns*2, pady=25, sticky="ew")

        select_mask = ['Mobility', 'ArmSwelling', 'BreastSwelling', 'Skin', 'FHT', 'DISCOMFORT'\
        , 'SYM_COUNT', 'ChestWallSwelling', 'Mastectomy', 'Lumpectomy', 'TIME_LAPSE']
        data_select = np.array([[self.parent.output_labels[item] for item in select_mask]], dtype=float)
        model_path = os.path.join(basepath, 'models' , 'GBT.pkl')

        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        y_pred = model.predict_proba(data_select)
        max_label = np.argmax(y_pred)
        self.parent.y_pred = y_pred
        re_dict = {0: "low_risk", 1: "mild", 2: "moderate_severe"}
        self.text_result = self.parent.get_text("your_predicted_lymphedema_risk").format(risk=self.parent.get_text(re_dict[max_label]))
        self.gbt_result = ctk.CTkLabel(self, text=self.text_result, font=self.font, height=170) # !!!!!
        self.gbt_result.grid(row=1, columnspan=2)
        weights = np.array([0, 50, 100])  # 权重
        with open(self.parent.record_data_path, 'r') as json_file:
            existing_data = json.load(json_file)
            try:
                score_list = existing_data[self.parent.current_user]['score_list']
            except:
                score_list = None
        overall_score = np.dot(y_pred.squeeze(), weights).item()
        self.comments = ctk.CTkTextbox(self, font=self.font, width=1500, height=280)

        if score_list is None:
            if max_label == 1 or max_label == 2:
                self.comments.insert('0.0', self.parent.get_text(f'This is your first time detecting Lymphedema. Keep on excercising and let us see your progress!'))
            elif max_label == 0:
                self.comments.insert('0.0', self.parent.get_text(f'This is your first time detecting Lymphedema. Keep on the good record!'))
        else:
            if not self.parent.score_save_flag: # not allowed to submit score. At this point the score must have been submitted
                if len(score_list) == 1:
                    last_time_score = score_list[0]
                else:
                    last_time_score = score_list[-2]
            else:
                last_time_score = score_list[-1]
            if max_label == 0:
                self.comments.insert('0.0', self.parent.get_text(f'Your detection result shows low risk, keep on the good record!'))
            elif overall_score > last_time_score and (max_label == 1 or max_label == 2):
                self.comments.insert('0.0', self.parent.get_text(f'Your detection result requires further inspection, please advice the doctors for further help. Keep on excercising and let us see your progress!'))
            elif overall_score == last_time_score and (max_label == 1 or max_label == 2):
                self.comments.insert('0.0', self.parent.get_text(f'Your detection result does not change since the last time. Keep on excercising and let us see your progress!'))
            elif overall_score < last_time_score - 3 and (max_label == 1 or max_label == 2):
                self.comments.insert('0.0', self.parent.get_text(f'Congratulations! Your detection result is much better than your last time. Keep on the good record!'))
            elif overall_score < last_time_score and (max_label == 1 or max_label == 2):
                self.comments.insert('0.0', self.parent.get_text(f'Congratulations! Your detection result is better than your last time. Keep on excercising and keep on the good record!'))
        self.comments.configure(state="disabled")
        self.comments.grid(row=2, columnspan=2, pady = 20)
        self.diagnosis = ctk.CTkTextbox(self, font=self.font, width=1500, height=400)
        self.diagnosis.insert('0.0', self.parent.get_text(f'diag_{re_dict[max_label]}') + self.parent.get_text("recommendation"))
        self.diagnosis.configure(state="disabled")
        self.diagnosis.grid(row=3, column = 0, columnspan=2, pady = 20)

        self.plot_button = ctk.CTkButton(self, text=self.parent.get_text("visualized diagnosis"), command=lambda: self.parent.show_frame("Pagechart"), font=self.font)
        self.plot_button.grid(row=4, column=0, pady=20, sticky="ew")
        self.back_button = ctk.CTkButton(self, text=self.parent.get_text("return"), command=lambda: self.parent.show_frame("Page2"), font=self.font)
        self.back_button.grid(row=4, column=1, pady=20, sticky="ew")

        self.update_texts()

    def remove(self):
        for widget in self.winfo_children():
            widget.destroy()

    def update_texts(self):
        self.page_label.configure(text=self.parent.get_text("detection_result"))
        self.gbt_result.configure(text=self.parent.get_text(self.text_result))
        self.plot_button.configure(text=self.parent.get_text("visualized diagnosis"))
        self.back_button.configure(text=self.parent.get_text("return"))


class Pagechart(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.font = self.parent.font_list[0]
        self.constructed = False

    def construct(self):
        if not self.constructed:
            self.constructed = True
        self.page_label = ctk.CTkLabel(self, text=self.parent.get_text("visualized diagnosis"), font=self.font)
        self.page_label.grid(row=0, column=0, pady=20, sticky="nsew")
        self.plot_frame = PLOTFrame(self, font=self.font, get_text=self.parent.get_text, fg_color = 'white', height=600)
        self.plot_frame.grid(row=1, column=0, padx=10, columnspan=2, pady=(10, 0), sticky="nsew")
        self.back_button = ctk.CTkButton(self, text=self.parent.get_text("return"), command=lambda: self.parent.show_frame("Page3"), font=self.font)
        self.back_button.grid(row=2, column=0, padx=10, columnspan=2, pady=(15, 20), sticky="ew")

        self.update_texts()

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=0)
        for row in range(1, 2):
            self.grid_rowconfigure(row, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def update_texts(self):
        self.page_label.configure(text=self.parent.get_text("visualized diagnosis"))
        self.back_button.configure(text=self.parent.get_text("return"))
        self.plot_frame.update_texts()

    def remove(self):
        for widget in self.winfo_children():
            widget.destroy()

class PageLogin(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.font = self.parent.font_list[0]
        self.construct()

    def construct(self):
        self.label_username = ctk.CTkLabel(self, text="Username:", font=self.font)
        self.label_username.grid(row=0, column=1, padx=10, pady=50, sticky="e")

        self.entry_username = ctk.CTkEntry(self, font=self.font)
        self.entry_username.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.label_password = ctk.CTkLabel(self, text="Password:", font=self.font)
        self.label_password.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        self.entry_password = ctk.CTkEntry(self, font=self.font)
        self.entry_password.grid(row=1, column=2, padx=10, pady=10, sticky="w")

        self.button_login = ctk.CTkButton(self, text="Login", command=self.login, font=self.font)
        self.button_login.grid(row=2, column=1, columnspan=2, padx=20, pady=10)

        self.button_register = ctk.CTkButton(self, text="Register", command=self.register, font=self.font)
        self.button_register.grid(row=3, column=1, columnspan=2, padx=10, pady=10)
        
        self.back_button = ctk.CTkButton(self, text="return", command=lambda: self.parent.show_frame("Page1"), font=self.font)
        self.back_button.grid(row=4, column=1, columnspan=2, pady=10)

        self.update_texts()

    def update_texts(self):
        self.label_username.configure(text=self.parent.get_text("Username:"))
        self.label_password.configure(text=self.parent.get_text("Password:"))
        self.button_login.configure(text=self.parent.get_text("Login"))
        self.button_register.configure(text=self.parent.get_text("Register"))
        self.back_button.configure(text=self.parent.get_text("return"))
    
    def configure_grid(self):
        for row in range(5):
            self.grid_rowconfigure(row, weight=0)
        for column in range(4):
            self.grid_columnconfigure(column, weight=1)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        userdata = load_user_data(self.parent.user_data_path)
        if username in userdata and userdata[username] == password:
            self.parent.current_user = username
            # messagebox.showinfo(self.parent.get_text("Login"), self.parent.get_text("Login successful")) # !!!
            self.parent.update_login_label()
            self.parent.show_frame("Page1")
        else:
            messagebox.showerror(self.parent.get_text("Login"), self.parent.get_text("Invalid username or password: your username or password is incorrect."))

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        userdata = load_user_data(self.parent.user_data_path)
        if username in userdata:
            messagebox.showerror(self.parent.get_text("Register"), self.parent.get_text("Username already exists"))
        elif username.strip() == '' or password.strip() == '':
            messagebox.showerror(self.parent.get_text("Register"), self.parent.get_text("Invalid username or password: can NOT be empty."))
        else:
            self.parent.user_data[username] = password
            save_user_data(self.parent.user_data_path, self.parent.user_data)
            messagebox.showinfo(self.parent.get_text("Register"), self.parent.get_text("Registration successful, please login next."))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.translations = load_translations(os.path.join(basepath, "data", "translations.json"))
        self.user_data_path = os.path.join(basepath, "data", "user_data.json")
        self.user_data = load_user_data(self.user_data_path)
        self.record_data_path = os.path.join(basepath, "data", "user_record.json")
        with open(os.path.join(basepath, "data", "default.json"), "r") as json_file:
            default = json.load(json_file)
            self.lang = default['lang']
            self.fontsize = default['fontsize']
        self.font_list = [("Helvetica", self.fontsize)]
        self.current_user = None
        self.y_pred = None
        self.score_save_flag = False
        self.labels = OrderedDict({ 'Age (years)': '', 'Time Lapse (years)': '', 'Weight (Kg)': '', 'Height (cm)': '', 'Limited shoulder movement': "",\
                                    'Limited elbow movement': "", 'Limited wrist movement': "", 'Limited fingers movement': "", 'Limited arm movement': "", 'Arm or hand swelling': "",\
                                    'Breast swelling': "", 'Chest swelling': "", 'Toughness or thickness of skin': "", 'Pain, aching, soreness': "", 'Tightness': "", 'Firmness': "",\
                                    'Heaviness': "", 'Numbness': "", 'Burning': "", 'Stabbing': "", 'Tingling': "", 'Fatigue': "", 'Weakness': "", 'Redness': "", 'Hotness': "",\
                                    'Stiffness': "", 'Tenderness': "", 'Blister': "", 'Chemotherapy': '', 'Radiation': '', 'SLNB_Removed_LN': '', 'ALND_Removed_LN': '',\
                                    'Mastectomy': '', 'Lumpectomy': '', 'Hormonal therapy': ''})  # the default value has been abandoned.
        self.instructions = ['Your age (years)', 'Time lapse since your recent breast cancer surgery (years)', 'Body weight (Kg)', 'Height (cm)', 'How much do you feel your shoulder movement is limited?', 'How much do you feel your elbow movement is limited?', 'How much do you feel your wrist movement is limited?', 'How much do you feel your fingers movement is limited?', 'How much do you feel your arm movement is limited?', 'How much do your arm or hand swell: if both, select the most intense feelings.', 'How much does your breast swell?', 'How much does your chest swell?', 'Toughness or thickness of skin', 'Do you feel pain, aching, or soreness: if more than one feeling, select the most intense one.', 'Tightness of your affected arm.', 'Firmness of your affected arm.', 'Heaviness of your affected arm.', 'Numbness of your affected arm.', 'The feeling of burning of your affected arm.', 'The feeling of stabbing of your affected arm.', 'The feeling of tingling, or feeling of needles of your affected arm.', 'The feeling of fatigue of your affected arm.', 'The feeling of weakness of your affected arm.', 'How much does your affected arm looks red?', 'How much does your affected arm feel hot?', 'How much does your affected arm feel stiff?', 'How much does your affected arm feel sensitive or tender when touching things?', 'Does you affected arm blisters?', 'Whether the patient had chemotherapy.', 'Whether the patient had radiation.', 'The number of removed sentinel lymph nodes.', 'The number of removed axillary lymph nodes', 'Whether the patient had Mastectomy.', 'Whether the patient had Lumpectomy.', 'Whether the patient had hormonal therapy.']
        self.output_labels = OrderedDict({'BMI': "22.1", 'Age': "40", 'TIME_LAPSE': "1", 'Mobility': "1", 'ArmSwelling': "0", 'BreastSwelling': "0", 'Skin': "0", 'PAS': "0", 'FHT': "1", 'DISCOMFORT': "0", 'SYM_COUNT': "2", 'ChestWallSwelling': "0", 'Chemotherapy': "1", 'Radiation': "0", 'Number_nodes': "1", 'Mastectomy': "1", 'Lumpectomy': "0", 'Hormonal': "0"})
        ctk.set_appearance_mode("light")
        self.title(self.get_text("title"))
        self.geometry("1000x700")
        self.menu_bar = tk.Menu(self, font=self.font_list[0])
        self.config(menu=self.menu_bar)
        # language_menu
        self.language_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.font_list[0])
        self.menu_bar.add_cascade(label=self.get_text("Language"), menu=self.language_menu)
        languages = ["English (English)", "Chinese (简体中文)", "Spanish (Español)"]
        for language in languages:
            self.language_menu.add_command(label=language, command=lambda lang=language: self.set_language(lang))

        self.fontsize_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.font_list[0])
        self.menu_bar.add_cascade(label=self.get_text("Fontsize"), menu=self.fontsize_menu)
        self.fontsize_menu.add_command(label = self.get_text("Small"), command=lambda: self.set_font(16))
        self.fontsize_menu.add_command(label = self.get_text("Medium"), command=lambda: self.set_font(24))
        self.fontsize_menu.add_command(label = self.get_text("Large"), command=lambda: self.set_font(32))
        self.fontsize_menu.add_command(label = self.get_text("Super Large"), command=lambda: self.set_font(40))

        # Account menu
        self.account_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.font_list[0])
        self.menu_bar.add_cascade(label=self.get_text("Account"), menu=self.account_menu)
        self.account_menu.add_command(label=self.get_text('Login/Register'), command=lambda: self.show_frame("PageLogin"))
        self.account_menu.add_command(label=self.get_text('Logout'), command=lambda: self.logout())
        self.account_menu.add_command(label=self.get_text('Delete Account'), command=lambda: self.delete_account())
        if self.current_user is not None:
            self.account_menu.add_command(label=self.get_text('Login as:') + self.current_user)
        else:
            self.account_menu.add_command(label=self.get_text('You are logged out'))

        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.font_list[0])
        self.menu_bar.add_cascade(label=self.get_text("Help"), menu=self.help_menu)
        self.help_menu.add_command(label=self.get_text("Instructions"), command=self.show_instructions)
        self.help_menu.add_command(label=self.get_text("About"), command=lambda: self.show_frame("Pageabout"))


        self.frames = {}
        self.create_frames()
        self.show_frame("Page1")

    def delete_account(self):
        if self.current_user == None:
            messagebox.showwarning(self.get_text('Not login'), self.get_text("You're logged out now. Please register or login first."))
            return
        dialog = PasswordDialog(self, font=self.font_list[0])
        self.wait_window(dialog)
        user_data = load_user_data(self.user_data_path)
        password = dialog.password
        if password == user_data[self.current_user]:
            answer = messagebox.askyesno(self.get_text('Confirmation'), self.get_text("Are you sure you want to delete this account? This operation can't be reversed."))
            if answer:
                self.logdel()
            else:
                return
        else:
            messagebox.showerror(self.get_text("Delete Account"), self.get_text("Invalid password: your password is incorrect."))

    def set_font(self, num):
        with open(os.path.join(basepath, "data", "default.json"), "r") as json_file:
            existing_data = json.load(json_file)
            existing_data['fontsize'] = num
        with open(os.path.join(basepath, "data", "default.json"), 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
        answer = messagebox.askyesno(self.get_text("Restart"), self.get_text("Changing the fontsize will restart the system. Make sure the data is saved."))
        if answer:
            # 使用os.execl重启程序
            python = sys.executable
            os.execl(python, python, *sys.argv)
        
    def create_frames(self):
        self.frames["PageLogin"] = PageLogin(self)
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
        if page_name == 'Page2':
            if self.current_user is None:
                messagebox.showinfo(self.get_text("Not login"), self.get_text("You're logged out now. Please register or login first."))
                return
        frame = self.frames[page_name]
        if hasattr(frame, "remove") and callable(getattr(frame, "remove")):
            self.frames[page_name].remove()
            self.frames[page_name].construct()
        frame.tkraise()
        frame.configure_grid()

    def update_login_label(self):
        # Clear the menu before updating
        self.account_menu.delete(3)
        # Add the updated command
        if self.current_user is not None:
            self.account_menu.add_command(label=self.get_text('Login as: ')+ self.current_user)
        else:
            self.account_menu.add_command(label=self.get_text('You are logged out'))

    def get_text(self, key):
        return get_translation(self.translations, self.lang, key)

    def set_language(self, lang):
        self.lang = lang.split(' ')[0]
        with open(os.path.join(basepath, "data", "default.json"), "r") as json_file:
            existing_data = json.load(json_file)
            existing_data['lang'] = self.lang
        with open(os.path.join(basepath, "data", "default.json"), 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
        self.update_texts()

    def update_texts(self):
        if os.name == 'nt':
            self.menu_bar.entryconfig(1, label=self.get_text("Language"))
            self.menu_bar.entryconfig(2, label=self.get_text("Fontsize"))
            self.menu_bar.entryconfig(3, label=self.get_text("Account"))
            self.menu_bar.entryconfig(4, label=self.get_text("Help"))
        elif os.name == 'posix':
            self.menu_bar.entryconfig(0, label=self.get_text("Language"))
            self.menu_bar.entryconfig(1, label=self.get_text("Fontsize"))
            self.menu_bar.entryconfig(2, label=self.get_text("Account"))
            self.menu_bar.entryconfig(3, label=self.get_text("Help"))
        self.help_menu.entryconfig(0, label=self.get_text("Instructions"))
        self.help_menu.entryconfig(1, label=self.get_text("About"))
        self.account_menu.entryconfig(0, label=self.get_text("Login/Register"))
        self.account_menu.entryconfig(1, label=self.get_text("Logout"))
        self.account_menu.entryconfig(2, label=self.get_text("Delete Account"))
        self.fontsize_menu.entryconfig(0, label=self.get_text("Small"))
        self.fontsize_menu.entryconfig(1, label=self.get_text("Medium"))
        self.fontsize_menu.entryconfig(2, label=self.get_text("Large"))
        self.fontsize_menu.entryconfig(3, label=self.get_text("Super Large"))
        if self.current_user is not None:
            self.account_menu.entryconfig(3, label=self.get_text("Login as: ") + self.current_user)
        else:
            self.account_menu.entryconfig(3, label=self.get_text("You are logged out"))
        for key, frame in self.frames.items():
            if hasattr(frame, "remove") and callable(getattr(frame, "remove")):
                if hasattr(frame, "constructed") and not frame.constructed:
                    continue
                frame.remove()
                frame.construct()
            if hasattr(frame, "update_texts") and callable(getattr(frame, "update_texts")):
                frame.update_texts()

    def show_instructions(self):
        # Function to display instructions
        tk.messagebox.showinfo(self.get_text("Instructions"), self.get_text("In the detection page, detailed instructions are shown when you move the cursor🖱️ close to the words (for example, Your age (years)...)."))

    def logout(self):
        messagebox.showinfo(self.get_text("Logout"), self.get_text("Logout sccessfully."))
        self.current_user = None
        self.update_login_label()
        self.show_frame("Page1")
        return
    
    def logdel(self):
        data = load_user_data(self.user_data_path)
        del data[self.current_user]
        save_user_data(self.user_data_path, data)
        data = load_user_data(self.record_data_path)
        try:
            del data[self.current_user]
        except:
            pass
        save_user_data(self.record_data_path, data)
        self.current_user = None
        self.update_login_label()
        self.show_frame("Page1")
        return
    
class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, font):
        super().__init__(parent)

        self.font = font
        self.title("Password Entry")
        self.geometry("350x250")
        self.transient(parent)  # 将对话框设置为父窗口的临时窗口
        self.grab_set()  # 使对话框成为模态

        self.label = ctk.CTkLabel(self, text=parent.get_text("Please enter your password:"), font = self.font)
        self.label.pack(pady=10)

        self.entry = ctk.CTkEntry(self, show='*', font = self.font)
        self.entry.pack(pady=10)

        self.button = ctk.CTkButton(self, text=parent.get_text("submit"), command=self.on_submit, font = self.font)
        self.button.pack(pady=10)

        self.password = None

    def on_submit(self):
        self.password = self.entry.get()
        self.destroy()
    
if __name__ == '__main__':
    global basepath
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        basepath = sys._MEIPASS
    else:
        basepath = os.path.abspath(".")
    font_path = os.path.join(basepath, 'data', 'SimHei.ttf') # 替换为SimHei.ttf的实际路径
    font_manager.fontManager.addfont(font_path)
    app = App()
    app.protocol("WM_DELETE_WINDOW", sys.exit)
    app.mainloop()