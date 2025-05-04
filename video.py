import cv2
import numpy as np
import serial
import time

def video_to_serial(input_path, serial_port, baudrate=115200, 
                   oled_size=(128, 64), target_fps=10, threshold=168):
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
            
            # 二值化
            _, binary = cv2.threshold(resized, threshold, 255, cv2.THRESH_BINARY)
            
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
                time.sleep(0.01) #0.01s已经是极限了！！！再慢的延时一定会显示障碍
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
    input_video = "luckyStar.mp4"
    serial_port = "COM3"  # 根据实际情况修改
    baudrate = 1000000
    
    video_to_serial(input_video, serial_port, baudrate)