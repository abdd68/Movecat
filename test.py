import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 检查 SimHei 字体是否在系统中
font_paths = fm.findSystemFonts()
simhei_font_path = None
for font_path in font_paths:
    if 'SimHei' in font_path:
        simhei_font_path = font_path
        break

if simhei_font_path:
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    print(f"SimHei font found at: {simhei_font_path}")
else:
    print("SimHei font not found. Please ensure it is installed on your system.")

# 创建示例图表
plt.title("示例标题", fontsize=20)
plt.xlabel("X轴标签")
plt.ylabel("Y轴标签")
plt.plot([1, 2, 3], [4, 5, 6])
plt.show()
