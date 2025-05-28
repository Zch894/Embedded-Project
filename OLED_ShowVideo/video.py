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
    input_video = "video\luckyStar.mp4" #自适应阈值，可原帧率
    origin_fps = 30
    input_video1 = "video\\aot_op_1.mp4" #自适应阈值，实测原帧率0.5MHz可达视频原长，波特率越大处理越快时长越短
    origin_fps1 = 25
    input_video2 = "video\\aot_end_1.mp4" #自适应阈值，可原帧率
    origin_fps2 = 24
    input_video3 = "video\\badApple.mp4" #最简单的二值化即可，实测帧率15最佳
    origin_fps3 = 60
    input_video4 = ".\\video\\aot_end_4.mp4"
    origin_fps4 = 0
    input_video5 = ".\\video\\aot_manga.mp4"
    origin_fps5 = 0
    serial_port = "COM3"  # 根据实际情况修改
    input_video_net = "https://upos-sz-mirror08c.bilivideo.com/upgcxcode/69/12/48361269/48361269_da3-1-100024.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&platform=pc&trid=65da6914fdfb4389966e3de102bdcc4u&deadline=1746380615&gen=playurlv3&os=08cbv&og=hw&uipk=5&nbs=1&mid=3546719776147818&tag=&oi=620283507&upsig=7c3bc48d6ac9377f63381ec19dba01c4&uparams=e,platform,trid,deadline,gen,os,og,uipk,nbs,mid,tag,oi&bvc=vod&nettype=0&bw=909878&dl=0&f=u_0_0&agrr=0&buvid=49D0C9F3-69E6-AA02-5515-864F083B253072865infoc&build=0&orderid=0,3"
    baudrate = 500000
    
    video_to_serial(input_video1, serial_port, baudrate, target_fps=origin_fps1)