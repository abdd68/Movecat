import tkinter as tk
import customtkinter as ctk

def render_markdown_to_textbox(textbox, markdown_text):
    lines = markdown_text.split('\n')
    for line in lines:
        if line.startswith('# '):
            textbox.insert(tk.END, line[2:] + '\n', 'h1')
        elif line.startswith('## '):
            textbox.insert(tk.END, line[3:] + '\n', 'h2')
        elif '**' in line:
            parts = line.split('**')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    textbox.insert(tk.END, part)
                else:
                    textbox.insert(tk.END, part, 'bold')
            textbox.insert(tk.END, '\n')
        elif '*' in line:
            parts = line.split('*')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    textbox.insert(tk.END, part)
                else:
                    textbox.insert(tk.END, part, 'italic')
            textbox.insert(tk.END, '\n')
        else:
            textbox.insert(tk.END, line + '\n')

# 创建主窗口
root = ctk.CTk()

# 创建Text控件
textbox = tk.Text(root, width=40, height=10, wrap='word')
textbox.pack(pady=20, padx=20)

# 配置文本样式
textbox.tag_configure('bold', font=('Helvetica', 12, 'bold'))
textbox.tag_configure('italic', font=('Helvetica', 12, 'italic'))
textbox.tag_configure('h1', font=('Helvetica', 16, 'bold'))
textbox.tag_configure('h2', font=('Helvetica', 14, 'bold'))

# 定义一些Markdown文本
markdown_text = """
# Heading 1
## Heading 2
This is a **bold** text and this is an *italic* text.
"""

# 渲染Markdown到文本框
render_markdown_to_textbox(textbox, markdown_text)

# 设置文本框为只读模式
textbox.configure(state="disabled")

# 运行主循环
root.mainloop()
