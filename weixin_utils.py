from appium.webdriver.common.appiumby import AppiumBy
from selenium.common import NoSuchElementException

import time
import re

from weixin_config import LONG_INTERVAL


def time_sleep(interval):
    print(f"开始延迟 {interval} s..")
    time.sleep(interval)
    print(f"延迟执行结束..")

'''向下滑动固定距离'''
def scroll_down(driver):
    size = driver.get_window_size()  # 获取屏幕尺寸
    width = size["width"]
    height = size["height"]

    start_x = width // 2  # 屏幕中央
    start_y = height // 2  # 滑动起点（屏幕底部）
    end_y = 0

    # 通过 `perform_touch` 实现滑动
    interval = 1000
    driver.swipe(start_x, start_y, start_x, end_y, interval)
    time_sleep(LONG_INTERVAL)
    print(f"滑动完毕..滑动距离 {end_y - start_y} 像素，耗时 {interval} ms..")

'''向下滑动num次固定距离'''
def scroll_down_by_count(driver, count):
    while count > 0:
        scroll_down(driver)
        count = count - 1

'''
获取群聊列表容器y轴上的偏移量
input params: 
driver: 驱动框架

return value: 
>=0的数值 或者 None就非法
'''
def get_chat_groups_offset_y(driver):
    try:
        print(f"get_chat_groups_offset_y - 寻找 群聊列表容器..")
        try:
            layer = driver.find_element(AppiumBy.ID, 'com.tencent.mm:id/gu0')
        except NoSuchElementException:
            raise ValueError("找不到<群聊列表>容器..")

        # 在容器内查找第一个子元素
        print(f"get_chat_groups_offset_y - 尝试在群聊列表容器内寻找第一个子元素..")
        try:
            first_item = layer.find_elements(AppiumBy.XPATH, './/android.widget.LinearLayout')[0]
        except NoSuchElementException:
            raise ValueError("群聊列表为空，未找到任何群聊项！")

        bounds_str = first_item.get_attribute("bounds")
        # print(f"找到的第一个群聊item：{bounds_str}")

        # 解析字符串 "[x1,y1][x2,y2]"
        match = re.findall(r"\d+", bounds_str)
        if match:
            first_item_x1, first_item_y1, first_item_x2, first_item_y2 = map(int, match)
            item_width = first_item_x2 - first_item_x1
            item_height = first_item_y2 - first_item_y1
            print(f"get_chat_groups_offset_y - 第一个群聊item的坐标: 左上角({first_item_x1}, {first_item_y1})"
                  f", 右下角({first_item_x2}, {first_item_y2})")
        else:
            raise ValueError(f"无法解析 first_item 的 bounds 数据..")

    except Exception as e:
        print(f"get_chat_groups_offset_y error: {e}")
        return None

    return (first_item_y2 - first_item_y1)