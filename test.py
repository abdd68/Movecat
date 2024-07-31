import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pickle
import os

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.construct()

    def construct(self):
        select_mask = ['Mobility', 'ArmSwelling', 'BreastSwelling', 'Skin', 'FHT', 'DISCOMFORT',
                       'SYM_COUNT', 'ChestWallSwelling', 'Mastectomy', 'Lumpectomy', 'TIME_LAPSE']
        data_select = np.array([[self.master.parent.output_labels[item] for item in select_mask]], dtype=float)
        basepath = os.getcwd()
        model_path = os.path.join(basepath, 'models' , 'GBT.pkl')
        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        self.y_pred = model.predict_proba(data_select).squeeze()

        self.create_figure1()
        self.createWidget()

    def create_figure1(self):
        fig, ax = plt.subplots()
        ax.plot(self.y_pred)  # 示例图，按需调整
        ax.set_title('预测结果')

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # 在图表下添加文字
        comments_label = ttk.Label(self, text="Your detection result shows low risk, keep on the good record!")
        comments_label.pack()

        suggestions_label = ttk.Label(self, text="Suggestions:\n\nFor individuals at low risk for lymphedema, it's essential to stay informed about the condition and its early symptoms, such as swelling or skin changes.\n\nMaintain a healthy weight through balanced diet and regular exercise, keep your skin moisturized and protected from injuries, and avoid heavy lifting or activities that strain your limbs. Use compression garments when recommended and be cautious with extreme temperatures. Regularly monitor for any changes and consult your healthcare provider promptly if symptoms develop.")
        suggestions_label.pack()

    def createWidget(self):
        pass  # 你的现有小部件创建代码

root = tk.Tk()
app = Application(master=root)
app.mainloop()
