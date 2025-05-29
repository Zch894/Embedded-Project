import cv2
import numpy as np
import serial
import time

def video_to_serial(input_path, serial_port, baudrate=115200, 
                   oled_size=(128, 64), target_fps=24, threshold=68):
    """
    将视频处理后通过串口发送
    :param input_path: 输入视频路径
    :param serial_port: 串口端口(如 'COM3' 或 '/dev/ttyUSB0')
    :param baudrate: 波特率
    :param oled_size: OLED分辨率 (width, height)
    :param target_fps: 目标帧率
    :param threshold: 二值化阈值
    """
    # 打开串口
    try:
        ser = serial.Serial(serial_port, baudrate, write_timeout=1)
        time.sleep(2)  # 等待串口初始化
    except Exception as e:
        print(f"无法打开串口: {e}")
        return
    
    # 打开视频
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("无法打开视频文件")
        ser.close()
        return
    
    # 获取视频信息
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    skip_interval = max(1, int(original_fps / target_fps))
    
    print(f"开始发送视频到 {serial_port}...")
    
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # 跳帧控制帧率
            frame_count += 1
            if frame_count % skip_interval != 0:
                continue
                
            # 转换为灰度并调整大小
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, oled_size, interpolation=cv2.INTER_AREA)
            
            # 二值化(适合两色素材)
            #_, binary = cv2.threshold(resized, threshold, 255, cv2.THRESH_BINARY)
            
            # 使用自适应阈值替换原二值化(推荐最先使用的算法,大多数情况最好。而且不需要在输入串口前延时，可能是处理的慢一点不会覆盖数据)
            #实现：通过计算像素周围区域的加权平均值动态确定阈值。
            binary = cv2.adaptiveThreshold(resized, 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11, 2)

            # 大津法(适合前后景对比度较大的黑白漫画)
            #_, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # 转换为OLED格式 (每8行像素打包为1字节)
            oled_data = []
            for page in range(8):  # 64/8=8页
                for col in range(128):
                    byte = 0
                    for bit in range(8):
                        if binary[page*8 + bit, col] > 0:
                            byte |= (1 << bit)
                    oled_data.append(byte)
            for i in range(0, 1024, 128):
                ser.write(oled_data[i:i + 128])
                #time.sleep(0.01) #0.01s已经是极限了！！！再慢的延时一定会显示障碍
            # 显示处理帧
            cv2.imshow('Sending Frame', binary)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("视频发送完成")

if __name__ == "__main__":
    # 配置参数
    input_video = "video\\aot_op_1.mp4" #自适应阈值，可原帧率
    origin_fps = 25
    serial_port = "COM5"  # 根据实际情况修改
    baudrate = 500000
    
    video_to_serial(input_video, serial_port, baudrate, target_fps=origin_fps)