import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


class MacularHoleAnalyzer:
    def __init__(self):
        self.fundus_image = None  # 原始超广角眼底图像
        self.display_image = None  # 显示使用的缩放图像
        self.fundus_points = []  # 选择的关键点坐标 [(x1, y1), (x2, y2)]
        self.scale_factor = 1.0  # 缩放比例

    def fundus_point_selection(self):
        """
        让用户选取超广角眼底图像的两个关键点，保持原始图像比例进行显示和点选。
        """
        # 弹出文件选择对话框
        root = tk.Tk()
        root.withdraw()
        image_path = filedialog.askopenfilename(
            title="选择超广角眼底图像",
            filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        root.destroy()

        if not image_path:
            print("未选择图像")
            return None

            # 读取原始图像
        self.fundus_image = cv2.imread(image_path)
        if self.fundus_image is None:
            print(f"无法加载图像 {image_path}")
            return None

            # 获取图像尺寸
        height, width = self.fundus_image.shape[:2]

        # 计算缩放比例（保持原始比例）
        screen = tk.Tk()
        screen_width = screen.winfo_screenwidth()
        screen_height = screen.winfo_screenheight()
        screen.destroy()

        # 计算缩放比例
        scale_width = screen_width * 0.8 / width
        scale_height = screen_height * 0.8 / height
        self.scale_factor = min(scale_width, scale_height)

        # 调整图像大小
        display_width = int(width * self.scale_factor)
        display_height = int(height * self.scale_factor)

        # 缩放图像
        self.display_image = cv2.resize(
            self.fundus_image.copy(),
            (display_width, display_height),
            interpolation=cv2.INTER_AREA
        )

        # 重置点列表
        self.fundus_points = []

        # 创建窗口并设置鼠标回调
        cv2.namedWindow("超广角眼底图像", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("超广角眼底图像", display_width, display_height)
        cv2.setMouseCallback("超广角眼底图像", self.mouse_callback)

        # 显示图像
        while True:
            # 创建显示图像的副本
            display = self.display_image.copy()

            # 绘制已选择的点
            for i, point in enumerate(self.fundus_points):
                # 将原始坐标转换为显示坐标
                x = int(point[0] * self.scale_factor)
                y = int(point[1] * self.scale_factor)

                # 绘制点
                cv2.circle(display, (x, y), 5, (0, 255, 0), -1)

                # 添加点的序号
                cv2.putText(display, f"Point {i + 1}", (x + 10, y + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # 如果有两个点，绘制连接线
            if len(self.fundus_points) == 2:
                pt1 = (int(self.fundus_points[0][0] * self.scale_factor),
                       int(self.fundus_points[0][1] * self.scale_factor))
                pt2 = (int(self.fundus_points[1][0] * self.scale_factor),
                       int(self.fundus_points[1][1] * self.scale_factor))
                cv2.line(display, pt1, pt2, (0, 255, 0), 2)

                # 显示图像
            cv2.imshow("超广角眼底图像", display)

            # 等待按键
            key = cv2.waitKey(1) & 0xFF

            # 如果选择了两个点或按下'q'键，退出
            if len(self.fundus_points) == 2 or key == ord('q'):
                break

                # 关闭窗口
        cv2.destroyAllWindows()

        return self.fundus_points

    def mouse_callback(self, event, x, y, flags, param):
        """
        鼠标回调函数，处理点的选择
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # 将显示坐标转换回原始图像坐标
            orig_x = int(x / self.scale_factor)
            orig_y = int(y / self.scale_factor)

            # 添加点
            self.fundus_points.append((orig_x, orig_y))

    def visualize_macular_hole(self, ratio):
        """
        可视化黄斑裂孔，绘制空心圆
        """
        if len(self.fundus_points) < 2:
            print("请先选择两个点")
            return

            # 计算距离和半径
        p1 = np.array(self.fundus_points[0])
        p2 = np.array(self.fundus_points[1])
        distance = np.linalg.norm(p1 - p2)
        radius = int(ratio * distance)

        # 创建显示图像副本
        display_image = self.display_image.copy()

        # 计算显示坐标
        center_x = int(self.fundus_points[0][0] * self.scale_factor)
        center_y = int(self.fundus_points[0][1] * self.scale_factor)
        display_radius = int(radius * self.scale_factor)

        # 绘制空心圆
        cv2.circle(display_image, (center_x, center_y), display_radius,
                   (255, 0, 0), 2)  # 蓝色空心圆

        # 添加文字说明
        cv2.putText(display_image, f"Ratio: {ratio:.4f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(display_image, f"Distance: {distance:.1f} pixels", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(display_image, f"Radius: {radius:.1f} pixels", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # 显示结果
        cv2.imshow("黄斑裂孔分析结果", display_image)

        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"macular_hole_analysis_{timestamp}.png"
        cv2.imwrite(filename, display_image)
        print(f"分析结果已保存到 {filename}")

        # 等待按键
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # 使用示例


if __name__ == "__main__":
    analyzer = MacularHoleAnalyzer()

    # 选择图像并标注点
    points = analyzer.fundus_point_selection()

    if points:
        # 生成示意图，ratio可以根据实际需求调整
        analyzer.visualize_macular_hole(ratio=0.5)