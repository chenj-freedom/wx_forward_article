from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from weixin_utils import time_sleep, scroll_down_by_count, post_process_ocrstr
from weixin_debug import print_children, print_attr
from weixin_config import desired_caps, SHORT_INTERVAL, LONG_INTERVAL
from ocr_manager.ocr_manager import OcrManager
from config_loader import get_tencent_config

import re
import time

def return_to_article():
    # 点击左上角 返回 按钮
    driver.tap([(55, 140)])
    time_sleep(SHORT_INTERVAL)
    driver.tap([(55, 140)])
    time_sleep(SHORT_INTERVAL)
    driver.tap([(55, 140)])
    time_sleep(SHORT_INTERVAL)
    driver.tap([(55, 140)])
    time_sleep(SHORT_INTERVAL)

def send_message_to_group():
    global forward_msg
    """实现消息转发逻辑"""
    print(f"找到<导入>按钮..点击之..")
    driver.tap([(970, 140)])
    time_sleep(SHORT_INTERVAL)
    
    print(f"找到<完成>按钮..点击之..")
    driver.tap([(945, 140)])
    time_sleep(SHORT_INTERVAL)

    print(f"找到<完成>按钮..点击之..")
    driver.tap([(945, 140)])
    time_sleep(SHORT_INTERVAL)

    print(f"找到<发消息>文本框..点击之..先获取焦点..")
    driver.tap([(486, 1775)])
    time_sleep(SHORT_INTERVAL)

    # 将中文文本设置到剪贴板
    driver.set_clipboard_text(forward_msg)

    print(f"开始执行长按..")
    # 创建ActionChains实例，并指定指针类型为触摸
    actions = ActionChains(driver)
    touch_input = PointerInput("touch", "touch")
    actions.w3c_actions = ActionBuilder(driver, mouse=touch_input)

    # 定义长按操作
    actions.w3c_actions.pointer_action.move_to_location(486, 1775)
    actions.w3c_actions.pointer_action.click_and_hold()
    actions.w3c_actions.pointer_action.pause(5)  # 长按5秒
    actions.w3c_actions.pointer_action.release()

    # 执行操作
    actions.perform()
    print(f"长按执行完毕..")

    print(f"找到<粘贴>按钮..点击之..")
    driver.tap([(96, 1708)])
    time_sleep(SHORT_INTERVAL)

    print(f"找到<发送>按钮..点击之..")
    driver.tap([(723, 1966)])
    time_sleep(LONG_INTERVAL)

'''
功能：转发公众号文章，并且指定了参数scroll_count
注意：在公众号文章这个页面。
input params:
scroll_count 在“选择群聊”页面，下滑了几次

return value: 
forward_num 转发了几个群
'''
def forward_article_by_scroll(scroll_count):
    global visited_groups
    global ocr_call_count
    global max_forward_groups_num_every_time

    try:
        print(f"找到<转发>按钮-右上角三个点..点击之..")
        driver.tap([(1005, 140)])
        time_sleep(SHORT_INTERVAL)

        print(f"找到<转发给朋友>按钮..点击之..")
        driver.tap([(108, 1512)])
        time_sleep(SHORT_INTERVAL)

        print(f"找到<多选>按钮..点击之..")
        driver.tap([(993, 140)])
        time_sleep(SHORT_INTERVAL)

        print(f"找到<从通讯录选择>按钮..点击之..")
        driver.tap([(918, 900)])
        time_sleep(SHORT_INTERVAL)

        print(f"找到<选择群聊>按钮..点击之..")
        driver.tap([(530, 430)])
        time_sleep(SHORT_INTERVAL)

        print(f"寻找 群聊列表容器..")
        # 群聊列表容器坐标 (0, 204) (1080, 2205)
        container_x1 = 0
        container_y1 = 204
        container_x2 = 1080
        container_y2 = 2205
        container_width = container_x2 - container_x1
        container_height = container_y2 - container_y1

        # 群聊元素坐标 (324, 204) (1037, 355)
        item_name_x_offset = 324
        item_width = container_width
        item_height = 355 - 204 # 151

        # step1: 向下滑动N次
        print(f"select_group - 向下滑动 {scroll_count} 次..")
        scroll_down_by_count(driver, scroll_count)

        # 循环遍历群列表，点击未转发的群聊
        print(f"截屏中..")
        screenshot_path = "/Users/rcadmin/Downloads/1-fullscreen.png"
        driver.save_screenshot(screenshot_path)
        img = Image.open(screenshot_path)
        cropped_image = img.crop((item_name_x_offset, container_y1, container_x1 + container_x2, container_y2))
        cropped_image_path = "/Users/rcadmin/Downloads/1-grouplist.png"
        cropped_image.save(cropped_image_path)

        # 预处理
        ocr_call_count = ocr_call_count + 1
        group_list = ocr_manager.recognize(cropped_image_path)
        if scroll_count == 0:   # 没有偏移，不对group_list做处理
            print(f"type of group_list={type[group_list]}")
            pass
        else:   # 删除头尾元素
            if len(group_list) > 0:
                del group_list[0]
                if len(group_list) > 0:
                    del group_list[-1]

        # 定义变量，表示本次选中的群聊个数
        selected_group_count = 0
        for group in group_list:
            group_name = group.DetectedText
            print(f"*****ocr return group_name={group_name}")
            group_name = post_process_ocrstr(group_name)
            group_coordinate = (container_width // 2, container_y1 + group.ItemPolygon.Y)
            # 跳过空名称和已转发群聊
            if not group_name or group_name in visited_groups:
                continue

            # 数量限制检查
            if selected_group_count >= max_forward_groups_num_every_time:
                break

            print(f"检测到未转发群聊并点击之..group_name={group_name}, group_coordinate={group_coordinate}")
            selected_group_count = selected_group_count + 1
            visited_groups.add(group_name)
            driver.tap([group_coordinate])
            time_sleep(1)

        if selected_group_count > 0:
            send_message_to_group()
        else:
            print(f"没有找到未转发的群聊..返回到文章页..")
            return_to_article()
            
        return selected_group_count
    except Exception as e:
        print(f"捕获到异常：{e}")


'''
功能：转发文章
注意：在公众号文章这个页面。
'''
def forward():
    scroll_count = 0
    # 连续转发群聊为0的次数，到达3次，就说明全部转发完毕
    consecutive_zero_forward_count = 0

    while True:
        time_sleep(LONG_INTERVAL)
        time_sleep(LONG_INTERVAL)
        forward_num = forward_article_by_scroll(scroll_count)
        if forward_num == 0:
            scroll_count = scroll_count + 1
            consecutive_zero_forward_count = consecutive_zero_forward_count + 1

            if consecutive_zero_forward_count >= 3:
                print(f"全部群聊转发完毕..")
                break
        else:
            consecutive_zero_forward_count = 0

    # 打印出已经转发的群聊
    print(f"已经转发了 {len(visited_groups)} 个群，如下：")
    for group in visited_groups:
        print(group)


########################################################################################################################

# 全局变量
# 已转发的群聊集合
visited_groups = set()
# 一共调用了几次ocr接口
ocr_call_count = 0
# 每次最大转发的群数量
max_forward_groups_num_every_time = 9
# 转发附带的消息
forward_msg = "hello world 你好～～"

start_time = time.time()  # 记录起始时间

# 创建ocr

app_id, app_key = get_tencent_config()
print(f"App ID: {app_id}, App Key: {app_key}")

ocr_manager = OcrManager(provider="tencent",
                         app_id=app_id,
                         app_key=app_key)

# 连接 Appium Server
driver = webdriver.Remote("http://127.0.0.1:4723",
                          options=UiAutomator2Options().load_capabilities(desired_caps))

forward()

# 退出会话
driver.quit()
print("quit program!")

end_time = time.time()  # 记录结束时间
elapsed_time = end_time - start_time  # 计算耗时
hours, rem = divmod(elapsed_time, 3600)  # 计算小时
minutes, seconds = divmod(rem, 60)  # 计算分钟和秒
print(f"execution time: {int(hours)} h {int(minutes)} m {int(seconds)} s")
print(f"ocr_call_count: {ocr_call_count}")