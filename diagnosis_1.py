import customtkinter
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
    
# 工具提示类
class CreateToolTip:
    def __init__(self, widget, text, delay=420):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.delay = delay
        self._after_id = None
        self.widget.bind("<Enter>", self.schedule_show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Motion>", self.move_tooltip)  # 当鼠标在 widget 上移动时，更新工具提示的位置

    def schedule_show_tooltip(self, event):
        self._after_id = self.widget.after(self.delay, self.show_tooltip, event)

    def show_tooltip(self, event):
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip = customtkinter.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = customtkinter.CTkLabel(self.tooltip, text=self.text, corner_radius=5)
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

class MyScrollableCheckboxFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, labels, instructions, num_columns, font):
        super().__init__(master, width = 660, height = 270, label_text=title)
        self.labels = labels
        self.output_labels = None
        self.entries = []
        self.font = font
        self.lrow = 1
        for i, (label_text, suggestion) in enumerate(self.labels.items()):
            row, column = i // num_columns, i % num_columns
            label = customtkinter.CTkLabel(self, text=label_text, font=self.font)
            label.grid(row=row+1, column=column*2, padx=5, pady=5, sticky = 'w')
            tooltip_text = instructions[i]
            CreateToolTip(label, tooltip_text)
            entry_var = customtkinter.StringVar(value=suggestion)
            if i < 4:
                entry = customtkinter.CTkEntry(self, textvariable=entry_var)
            else:
                options = ["None", "A little", "Somewhat", "Quite a bit", "Severe"]
                entry = customtkinter.CTkOptionMenu(self, variable= None, values=options)
            entry.grid(row=row+1, column=column*2+1, padx=5, pady=5, sticky = 'w')

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
    
class PLOTFrame(customtkinter.CTkScrollableFrame):
    """一个经典的GUI写法"""
 
    def __init__(self, master=None, title = None, font = None):
        '''初始化方法'''
        super().__init__(master, width = 720, height = 330, label_text=title)  # 调用父类的初始化方法
        self.master = master
        self.create_matplotlib()
        self.createWidget(self.figure)
        self.font = font
            
    def createWidget(self, figure):
        """创建组件"""
        # 创建画布
        self.canvas = FigureCanvasTkAgg(figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
 
    def create_matplotlib(self):
        """创建绘图对象"""
        # 设置中文显示字体
        mpl.rcParams['font.sans-serif'] = ['SimHei']  # 中文显示
        mpl.rcParams['axes.unicode_minus'] = False  # 负号显示
        # 创建绘图对象f figsize的单位是英寸 像素 = 英寸*分辨率
        self.figure = plt.figure(num=2, figsize=(7, 9), dpi=80, facecolor="white", edgecolor='Teal', frameon=True)
        font = {'family': 'serif', 'serif': 'Times New Roman', 'weight': 'normal', 'size': 20}
        plt.rc('font', **font)
        plt.title('GBT weight', fontdict={'family': 'Times New Roman', 'weight': 'normal', 'size': 28},  pad = 12)
        plt.yscale('symlog', linthresh=0.00005)
        plt.tick_params(axis='x', labelsize=18, rotation = 60)
        plt.tick_params(axis='y', labelsize=18)
        data = [('ArmSwelling', 0.5666504441537034), ('SYM_COUNT', 0.32829106757634513), ('BreastSwelling', 0.05866949630997336), ('TIME_LAPSE', 0.0270874570016606), ('BMI', 0.0048442873079247665), ('FHT', 0.003799860520333767), ('Age', 0.0036176355797100405), ('Number_nodes', 0.0027917973843724414), ('Skin', 0.0018357913101027619), ('DISCOMFORT', 0.0009075648872365948), ('PAS', 0.0007936402703285446), ('Hormonal', 0.00019944254371048652), ('Radiation', 0.00017741997766747576), ('Mobility', 0.000173412474200293), ('ChestWallSwelling', 0.0001060488637141992), ('Lumpectomy', 2.9960955692536147e-05), ('Chemotherapy', 1.3416562172188665e-05), ('Mastectomy', 1.1256321151464536e-05)]
        x = [item[0] for item in data]
        y = [item[1] for item in data]
        loc = zip(x, y)  # 将x, y 两两配对
        plt.ylim(0, 1)  # 设置y轴的范围
        plt.bar(x, y, facecolor='Teal', edgecolor='black')  # 绘制柱状图(填充颜色绿色，边框黑色)
        for x, y in loc:
            plt.text(x, y, '%.1g' % y, ha='center', va='bottom')  # 保留小数点2位
        plt.tight_layout(rect=[0, 0, 1, 0.95])

    def destroy(self):
        """重写destroy方法"""
        self.figure.clf()

class Page1(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.font = ("Helvetica", 16)
        page_label = customtkinter.CTkLabel(self, text="Lymphedema Early Detection System", font=self.font)
        page_label.grid(row = 0, column = 0, pady=50)

        # 创建一个按钮
        button = customtkinter.CTkButton(self, text="Begin Detection", command=lambda: parent.show_frame("Page2"), font=self.font)
        button.grid(row=1, column = 0, pady=10)
        button = customtkinter.CTkButton(self, text="About", command=lambda: parent.show_frame("Pageabout"), font=self.font)
        button.grid(row=2, column = 0, pady=10)
    
    def configure_grid(self):
        # 配置 Page1 的行和列权重
        for row in range(3):  
            self.grid_rowconfigure(row, weight=0)
        for col in range(1):  
            self.grid_columnconfigure(col, weight=1)

class Pageabout(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.font = ("Helvetica", 16)
        about_label = customtkinter.CTkLabel(self, text="About", font=self.font)
        about_label.grid(row = 0, column = 0, pady = 25, columnspan = 3, sticky="ew")

        about_text = customtkinter.CTkLabel(self, text="This is the Lymphedema Early Detection System. "
                                                    "It is designed to detect early signs of lymphedema "
                                                    "using machine learning algorithms.", font=self.font, wraplength = 700)
        about_text.grid(row = 1, column = 0, padx = 25, columnspan = 3, pady = 10)

        # 打开图片文件
        image = Image.open(os.path.join(basepath, "image\\UMKC.png")).resize((300, 300))
        tk_image = ImageTk.PhotoImage(image)
        image_label = customtkinter.CTkLabel(self, image=tk_image, text='')
        image_label.image = tk_image  # 保持对图像对象的引用，避免被垃圾回收
        image_label.grid(row = 2, column = 0, padx = 25, pady = 10)

        # 打开图片文件
        image2 = Image.open(os.path.join(basepath, "image\\UMD.jpg")).resize((225, 225))
        tk_image2 = ImageTk.PhotoImage(image2)
        image_label2 = customtkinter.CTkLabel(self, image=tk_image2, text='')
        image_label2.image = tk_image2  # 保持对图像对象的引用，避免被垃圾回收
        image_label2.grid(row = 2, column =1, padx = 25, pady = 10)

        # 打开图片文件
        image3 = Image.open(os.path.join(basepath, "image\\NYU.png")).resize((300, 300))
        tk_image3 = ImageTk.PhotoImage(image3)
        image_label3 = customtkinter.CTkLabel(self, image=tk_image3, text='')
        image_label3.image = tk_image3  # 保持对图像对象的引用，避免被垃圾回收
        image_label3.grid(row = 2, column = 2, padx = 25, pady = 10)

        # 创建一个返回按钮
        return_button = customtkinter.CTkButton(self, text="Return to Main Menu", command=lambda: parent.show_frame("Page1"), font=self.font)
        return_button.grid(row = 3, column =1, padx = 25, pady = 10)

    def configure_grid(self):
        for row in range(3): 
            self.grid_rowconfigure(row, weight=0)
        for col in range(3):
            self.grid_columnconfigure(col, weight=1)

class Page2(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.font = ("Helvetica", 16)
        page_label = customtkinter.CTkLabel(self, text="Detection Page", font=self.font)
        page_label.grid(row=0, column=0, pady=25, sticky="ew", columnspan = 2)

        self.scrollable_checkbox_frame = MyScrollableCheckboxFrame(self, title="Reported symptoms", labels= parent.labels, instructions = parent.instructions, num_columns = 2, font = self.font)
        self.scrollable_checkbox_frame.grid(row=1, column=0, padx=10, columnspan = 2, pady=0, sticky="nsew")
        
        def on_button():
            parent.labels = self.scrollable_checkbox_frame.get()
            parent.output_labels = self.label_processing(parent.labels)
            parent.show_frame("Page3")
            
        submit_button = customtkinter.CTkButton(self, text="Submit", command=on_button, font=self.font)
        back_button = customtkinter.CTkButton(self, text="Return", command=lambda: parent.show_frame("Page1"), font=self.font)
        submit_button.grid(row=2, column=0, pady=20, sticky="ew")
        back_button.grid(row=2, column=1, pady=20, sticky="ew")
    
    def configure_grid(self):
        # 配置 Page1 的行和列权重
        self.grid_rowconfigure(0, weight=0)
        for row in range(1, 3):  # 假设 Page1 有 2 行
            self.grid_rowconfigure(row, weight=1)
        for col in range(2):  # Page1 有 1 列
            self.grid_columnconfigure(col, weight=1)

    def label_processing(self, labels):
        def str2b(str_):
            if str_ == '0':
                return 0
            else:
                return 1
        output_labels = OrderedDict({'BMI': "22.1", 'Age': "40", 'TIME_LAPSE': "1", 'Mobility': "1", 'ArmSwelling': "0", 'BreastSwelling': "0", 'Skin': "0", 'PAS': "0", \
                'FHT': "1", 'DISCOMFORT': "0", 'SYM_COUNT': "2", 'ChestWallSwelling': "0", 'Chemotherapy': "1", \
                'Radiation': "0", 'Number_nodes': "1", 'Mastectomy': "1", 'Lumpectomy': "0", \
                    'Hormonal': "0"})
        output_labels['BMI'] = float(labels['Weight (Kg)']) / (float(labels['Height (cm)'])*float(labels['Height (cm)']))
        output_labels['Age'] = labels['Age (years)']
        output_labels['TIME_LAPSE'] = math.log(float(labels['Time Lapse (years)']))
        output_labels['Mobility'] = max(int(labels['Limited shoulder movement']), int(labels['Limited elbow movement']), int(labels['Limited wrist movement']), int(labels['Limited fingers movement']), int(labels['Limited arm movement']))
        output_labels['Armswelling'] = labels['Arm or hand swelling']
        output_labels['BreastSwelling'] = labels['Breast swelling']
        output_labels['Skin'] = labels['Toughness or thickness of skin']
        output_labels['PAS'] = labels['Pain, aching, soreness']
        output_labels['FHT'] = max(int(labels['Firmness']), int(labels['Heaviness']), int(labels['Tightness']))
        output_labels['DISCOMFORT'] = labels['Pain, aching, soreness']
        output_labels['SYM_COUNT'] = str2b(labels['Limited shoulder movement'])+ str2b(labels['Limited elbow movement'])+str2b(labels['Limited wrist movement'])+str2b(labels['Limited fingers movement']) \
                +str2b(labels['Limited arm movement'])+str2b(labels['Arm or hand swelling'])+str2b(labels['Breast swelling'])+str2b(labels['Chest swelling'])+str2b(labels['Toughness or thickness of skin'])\
                +str2b(labels['Pain, aching, soreness'])+str2b(labels['Tightness'])+str2b(labels['Firmness'])+str2b(labels['Heaviness'])+str2b(labels['Numbness'])+str2b(labels['Burning'])\
                +str2b(labels['Stabbing'])+str2b(labels['Tingling'])+str2b(labels['Fatigue'])+str2b(labels['Weakness'])+str2b(labels['Redness'])+str2b(labels['Hotness'])+str2b(labels['Stiffness'])\
                +str2b(labels['Tenderness'])+str2b(labels['Blister'])
        output_labels['ChestWallSwelling'] = labels['Chest swelling']
        output_labels['Chemotherapy'] = labels['Chemotherapy']
        output_labels['Radiation'] = labels['Radiation']
        output_labels['Number_nodes'] = max(int(labels['SLNB_Removed_LN']), int(labels['ALND_Removed_LN']), int(labels['SLNB_ALND_Removed']))
        output_labels['Mastectomy'] = labels['Mastectomy']
        output_labels['Lumpectomy'] = labels['Lumpectomy']
        output_labels['Hormonal'] = labels['Hormonal therapy']
        return output_labels

class Page3(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.font = ("Helvetica", 16)
        self.parent = parent
        
    def configure_grid(self):
        # 配置 Page1 的行和列权重
        self.grid_rowconfigure(0, weight=0)
        for row in range(1, 3):  # 假设 Page1 有 2 行
            self.grid_rowconfigure(row, weight=1)
        for col in range(2):  # Page1 有 1 列
            self.grid_columnconfigure(col, weight=1)

    def construct(self):
        num_columns = 1
        page_label = customtkinter.CTkLabel(self, text="Detection Result", font=self.font)
        page_label.grid(row=0, column=0, columnspan=num_columns*2, pady=25, sticky="nsew")
        
        select_mask = ['ArmSwelling', 'BreastSwelling', 'Skin', 'DISCOMFORT', 'SYM_COUNT', 'ChestWallSwelling', 'Age', 'Mastectomy', 'Hormonal', 'TIME_LAPSE']
        data_select = np.array([[self.parent.output_labels[item] for item in select_mask]], dtype= float)
        model_path = os.path.join(basepath, 'models\\GBT.pkl')
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        y_pred = model.predict(data_select)
        # data_select_result = customtkinter.CTkLabel(root, text=f"y_pred: {y_pred}.", font=self.font)
        # data_select_result.grid(row = 2)
        re_dict = {0:"Low risk", 1:"Mild", 2: "Moderate/Severe"}
        gbt_result = customtkinter.CTkLabel(self, text=f"(GBT) Your predicted Lymphedema risk is: {re_dict[y_pred.item()]}.", font=self.font)
        gbt_result.grid(row = 1, columnspan = 2)
        plot_button = customtkinter.CTkButton(self, text="Plot Bar Chart", command=lambda: self.parent.show_frame("Pagechart"), font=self.font)
        plot_button.grid(row = 2, column=0, pady=20, sticky="ew")
        back_button = customtkinter.CTkButton(self, text="Return", command=lambda: self.parent.show_frame("Page2"), font=self.font)
        back_button.grid(row = 2, column=1, pady=20, sticky="ew")

    def remove(self):
        for widget in self.winfo_children():
            widget.destroy()

class Pagechart(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.font = ("Helvetica", 16)
        page_label = customtkinter.CTkLabel(self, text="Plot Bar Chart", font=self.font)
        page_label.grid(row=0, column=0, pady=20, sticky="nsew")
        self.plot_frame = PLOTFrame(master=self, font = self.font) # , title = 'Plot Bar Chart'
        self.plot_frame.grid(row=1, column=0, padx=10, columnspan = 2, pady=(10, 0), sticky="nsew")
        back_button = customtkinter.CTkButton(self, text="Return", command=lambda: parent.show_frame("Page3"), font=self.font)
        back_button.grid(row=2, column=0, padx=10, columnspan = 2, pady=(10, 0), sticky="ew")
    
    def configure_grid(self):
        # 配置 Page1 的行和列权重
        self.grid_rowconfigure(0, weight=0)
        for row in range(1,3):  # 假设 Page1 有 2 行
            self.grid_rowconfigure(row, weight=1)
        for col in range(1):  # Page1 有 1 列
            self.grid_columnconfigure(col, weight=1)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.labels = OrderedDict({'Age (years)': '40', 'Time Lapse (years)': '1', 'Weight (Kg)': '60', 'Height (cm)': '170', 'Limited shoulder movement': "0", 'Limited elbow movement': "0", \
                                   'Limited wrist movement': "0", 'Limited fingers movement': "0", 'Limited arm movement': "0", 'Arm or hand swelling': "0", 'Breast swelling': "0", 'Chest swelling': "0", \
                                    'Toughness or thickness of skin': "0", 'Pain, aching, soreness': "0", 'Tightness': "0", 'Firmness': "0", 'Heaviness': "1", \
                                    'Numbness': "0", 'Burning': "0", 'Stabbing': "0", 'Tingling': "0", 'Fatigue': "0",\
                                    'Weakness': "0", 'Redness': "0", 'Hotness': "0", 'Stiffness': "0", 'Tenderness': "0", 'Blister': "0", \
                                    'Chemotherapy': '0', 'Radiation' : '0', 'SLNB_Removed_LN': '0', 'ALND_Removed_LN': '0', 'SLNB_ALND_Removed': '0', \
                                    'Mastectomy': '0', 'Lumpectomy': '0', 'Hormonal therapy': '0'
                                 }) # key: default value
        self.instructions = ['Your age (years)', 'Time lapse since your recent breast cancer surgery (years)', 'Body weight (Kg)', 'Height (cm)', 'How much do you feel your shoulder movement is limited?', 'How much do you feel your elbow movement is limited?', \
                             'How much do you feel your wrist movement is limited?', 'How much do you feel your fingers movement is limited?', 'How much do you feel your arm movement is limited?', 'How much do your arm or hand swell: if both, select the most intense feelings.', 'How much does your breast swell?',\
                             'How much does your chest swell?', 'Toughness or thickness of skin', 'Do you feel pain, aching, or soreness: if more than one feeling, select the most intense one.', 'Tightness of your affected arm.', 'Firmness of your affected arm.', 'Heaviness of your affected arm.',\
                             'Numbness of your affected arm.', 'The feeling of burning of your affected arm.', 'The feeling of stabbing of your affected arm.', 'The feeling of tingling, or feeling of needles of your affected arm.', 'The feeling of fatigue of your affected arm.', 'The feeling of weakness of your affected arm.',\
                             'How much does your affected arm looks red?', 'How much does your affected arm feel hot?', 'How much does your affected arm feel stiff?', 'How much does your affected arm feel sensitive or tender when touching things?', 'Does you affected arm blisters?',\
                             'Whether the patient had chemotherapy.', 'Whether the patient had radiation.', 'The number of removed sentinel lymph nodes.', 'The number of removed axillary lymph nodes', 'The number of removed lymph nodes when the patient has both SLNB and ALND removed.',\
                             'Whether the patient had Mastectomy.', 'Whether the patient had Lumpectomy.', 'Whether the patient had hormonal therapy.' ]
        self.output_labels = OrderedDict({'BMI': "22.1", 'Age': "40", 'TIME_LAPSE': "1", 'Mobility': "1", 'ArmSwelling': "0", 'BreastSwelling': "0", 'Skin': "0", 'PAS': "0", \
                'FHT': "1", 'DISCOMFORT': "0", 'SYM_COUNT': "2", 'ChestWallSwelling': "0", 'Chemotherapy': "1", \
                'Radiation': "0", 'Number_nodes': "1", 'Mastectomy': "1", 'Lumpectomy': "0", \
                    'Hormonal': "0"})
        customtkinter.set_appearance_mode("light")
        self.title("Lymphedema Early Detection System")
        self.geometry("800x600")

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
        frame.configure_grid()  # 调用页面的 configure_grid 方法
    
if __name__ == '__main__':
    global basepath
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        basepath = sys._MEIPASS  # exe运行时临时文件夹路径(exe运行时使用绝对路径) C:\Users\linghky\AppData\Local\Temp\_MEI{6位数字}
    else:
        basepath = ""  # (python脚本运行时使用相对路径)
    app = App()
    app.protocol("WM_DELETE_WINDOW", sys.exit)
    app.mainloop()