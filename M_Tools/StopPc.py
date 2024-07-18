import os
import datetime
import time

def shutdown_at(year, month, day, hour, minute):
    shutdown_time = datetime.datetime(year, month, day, hour, minute)
    current_time = datetime.datetime.now()
    time_difference = (shutdown_time - current_time).total_seconds()

    if time_difference > 0:
        print(f"计划在 {shutdown_time} 关闭电脑.")
        time.sleep(time_difference)
        os.system("shutdown /s /t 1")  # 执行关机命令
    else:
        print("指定的时间已经过了，请重新设定时间.")

shutdown_at(2024, 7, 14, 15, 0)
