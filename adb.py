import os
import subprocess
import time


def get_devices_list():
    result = subprocess.run(['adb.exe', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                            ).stdout.strip().split('\n')
    devices = result[1:]
    devices = [device.replace('\tdevice', '') for device in devices]
    return devices


def check_internet(device: str):
    result = subprocess.run(["adb.exe", "-s", device, "shell", "ping", "-c", "1", "8.8.8.8", "&&", "echo", "True",
                             "||", "echo", "False"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True).stdout.splitlines()[-1]
    if result == "True":
        return True
    return False


def restart_device(device: str):
    os.system(f"adb -s {device} reboot")
    time.sleep(10)

    while True:
        output = os.popen(f"adb -s {device} shell getprop sys.boot_completed").read().strip()
        if output == "1":
            break
        time.sleep(2)

    time.sleep(10)

    os.system(f"adb -s {device} shell input tap 500 1000")

    time.sleep(1)

    os.system(f"adb -s {device} shell input swipe 350 1300 350 150")
    time.sleep(3)


def reenable_mobile_internet(device: str):
    os.system(f"adb -s {device} shell svc data disable")
    time.sleep(10)
    os.system(f"adb -s {device} shell svc data enable")
