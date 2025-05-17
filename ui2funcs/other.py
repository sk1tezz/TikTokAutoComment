import time
import random


def wait_for_element(d, element_list, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        for element in element_list:
            if d.xpath(element).exists:
                return element
        time.sleep(0.1)
    return None


def write(d, element, text, clear=True, delay=0.3, click=True, enter=False):
    if click:
        element.click()
    if clear:
        d.clear_text()
    time.sleep(0.5)
    for i in text:
        d.send_keys(text=i)
        sleepdelay = random.uniform(delay * 0.5, delay * 2)
        if sleepdelay < 0.3:
            sleepdelay = 0.3
        time.sleep(sleepdelay)
    if enter:
        d.sleep(1)
        d.press("enter")


def get_center_from_element(element):
    bounds = element.bounds
    x_left = bounds[0]
    y_top = bounds[1]
    x_right = bounds[2]
    y_bottom = bounds[3]
    x_center = (x_left + x_right) // 2
    y_center = (y_top + y_bottom) // 2
    return x_center, y_center


def restart_tiktok(d):
    d.press("home")
    d.sleep(3)
    d.press("home")
    d.sleep(2)
    d.app_stop("com.zhiliaoapp.musically")
    d.sleep(2)
    d.app_start("com.zhiliaoapp.musically")
    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(timeout=60)
