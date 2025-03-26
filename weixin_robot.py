from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from PIL import Image
from weixin_utils import time_sleep, scroll_down_by_count, get_chat_groups_offset_y
from weixin_debug import print_children, print_attr
from weixin_config import desired_caps, SHORT_INTERVAL, LONG_INTERVAL
from ocr_manager.ocr_manager import OcrManager
from config_loader import get_tencent_config

import re
import time

def tap_return_btn():
    try:
        layer = driver.find_element(AppiumBy.ID, "com.tencent.mm:id/ei")
        bounds_str = layer.get_attribute("bounds")
        match = re.findall(r"\d+", bounds_str)
        if match:
            x1, y1, x2, y2 = map(int, match)
            btn_x = 10
            btn_y = (y1 + y2) // 2
            print(f"‘返回按钮的坐标是：({btn_x, btn_y})")
        else:
            raise ValueError(f"无法解析 bounds 数据")
        driver.tap([(btn_x, btn_y)])

    except Exception as e:
        print(f"捕获到异常：{e}")

    finally:
        time_sleep(SHORT_INTERVAL)

def send_message_to_group(comment_str):
    """实现消息转发逻辑"""
    print(f"点击‘导入’按钮..")
    button = driver.find_element(AppiumBy.ID, "com.tencent.mm:id/coz")
    bounds_str = button.get_attribute("bounds")
    match = re.findall(r"\d+", bounds_str)
    if match:
        x1, y1, x2, y2 = map(int, match)
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        print(f"‘导入’按钮的中心点坐标是：({center_x, center_y})")
    else:
        raise ValueError(f"无法解析 bounds 数据")
    driver.tap([(center_x, center_y)])

    time_sleep(SHORT_INTERVAL)

    print(f"点击‘完成’按钮..")
    driver.tap([(center_x, center_y)])

    time_sleep(SHORT_INTERVAL)

    print(f"点击‘发送’按钮..")
    driver.tap([(center_x, center_y)])

    time_sleep(LONG_INTERVAL)

    print(f"找到‘给朋友留言’文本框..")
    layer = driver.find_element(AppiumBy.ID, 'com.tencent.mm:id/ocm')
    children = layer.find_elements(AppiumBy.XPATH, './/*')
    print_children(layer)
    # edit_box = layer.find_element(AppiumBy.XPATH, './/android.widget.EditText')
    edit_box = [child for child in children if child.get_attribute("className") == "android.widget.EditText"][0]
    print_attr(edit_box)
    edit_box.click()    # 一定要先获取焦点
    time_sleep(SHORT_INTERVAL)

    # 将中文文本设置到剪贴板
    driver.set_clipboard_text(comment_str)

    # 假设 driver 是你的 WebDriver 实例
    print(f"开始执行长按..")
    bounds_str = edit_box.get_attribute("bounds")
    match = re.findall(r"\d+", bounds_str)
    if match:
        edit_box_x1, edit_box_y1, edit_box_x2, edit_box_y2 = map(int, match)
        print(f"edit_box 坐标是{({edit_box_x1, edit_box_y1}), (edit_box_x2, edit_box_y2)}")
    else:
        raise ValueError(f"无法解析 bounds 数据")

    # 创建ActionChains实例，并指定指针类型为触摸
    actions = ActionChains(driver)
    touch_input = PointerInput("touch", "touch")
    actions.w3c_actions = ActionBuilder(driver, mouse=touch_input)

    # 定义长按操作
    actions.w3c_actions.pointer_action.click_and_hold(edit_box)
    actions.w3c_actions.pointer_action.pause(5)  # 长按5秒
    actions.w3c_actions.pointer_action.release()

    # 执行操作
    actions.perform()
    print(f"长按执行完毕..")

    print(f"点击‘粘贴’按钮..")
    driver.tap([(edit_box_x1, edit_box_y1 - 10)])

    time_sleep(SHORT_INTERVAL)
    print(f"点击’发送”按钮..")
    layer = driver.find_element(AppiumBy.ID, 'com.tencent.mm:id/jl_')
    children = layer.find_elements(AppiumBy.XPATH, './/*')
    last_child = children[-1]
    last_child.click()

    time_sleep(LONG_INTERVAL)

'''
功能：向下滑动N次屏幕之后，选择群聊
input params:
(container_x1, container_y1): 群聊列表容器的左上角坐标
container_width：群聊列表容器的宽度
(item_width, item_height): 群聊元素的宽和高
item_name_x_offset: 群聊名字对象的x轴偏移量
scroll_count: 在“选择群聊”页面，下滑了几次
max_elements_per_page: 一页最多群聊元素的数量

return value:
选中了几个群聊，并转发消息
'''
def select_group(container_x1, container_y1, container_width, container_height,
                   item_width, item_height, item_name_x_offset, scroll_count):
    global visited_groups
    global max_forward_groups_num_every_time
    global forward_msg

    # 一页最大容纳的群数量
    max_elements_per_page = container_height // item_height
    print(f"select_group - container_x1={container_x1}, container_y1={container_y1}"
          f", container_width={container_width}, container_height={container_height}"
          f", item_width={item_width}, item_height={item_height}"
          f", item_name_x_offset={item_name_x_offset}"
          f", scroll_count={scroll_count}"
          f", max_elements_per_page={max_elements_per_page}")

    # step1: 向下滑动N次
    print(f"select_group - 向下滑动 {scroll_count} 次..")
    scroll_down_by_count(driver, scroll_count)

    group_container_offset_y = get_chat_groups_offset_y(driver)
    if group_container_offset_y == item_height:
        group_container_offset_y = 0
    print(f"群聊列表容器整体y轴偏移量group_container_offset_y={group_container_offset_y}")

    # step2: 循环遍历群列表，点击未转发的群聊
    print(f"截屏中..")
    screenshot_path = "/Users/rcadmin/Downloads/1.png"
    driver.save_screenshot(screenshot_path)
    img = Image.open(screenshot_path)

    # 定义变量，表示本次选中的群聊个数
    selected_group_count = 0

    # step2: 遍历群聊列表
    for i in range(int(max_elements_per_page)):
        # 计算每个群的坐标
        y1 = container_y1 + group_container_offset_y + i * item_height
        y2 = y1 + item_height
        if y2 > container_y1 + container_height:
            continue

        # 截取群聊名字的图片
        print(f"i={i}, item_name_x_offset={item_name_x_offset}, y1={y1}"
              f", container_x1 + container_width={container_x1 + container_width}, y2={y2}")
        cropped_image = img.crop((item_name_x_offset, y1, container_x1 + container_width, y2))
        cropped_image_path = f"/Users/rcadmin/Downloads/1-{i}.png"
        cropped_image.save(cropped_image_path)

        # 识别群聊名字
        group_name = ocr_manager.recognize(cropped_image_path)
        print(f"[{i}] 识别出群名字：{group_name}")

        # 终止条件：如果识别结果为空，说明到了页面底部
        if not group_name:
            print(f"warning: 检测到空白群聊，结束遍历..")
            break

        # 判断是否已经转发过
        if group_name in visited_groups:
            print(f"warning: {group_name}, 该群聊已经转发过，故本次跳过..")
            continue  # 跳过已经转发的群聊

        # 记录新群聊并进行转发
        selected_group_count = selected_group_count + 1
        if selected_group_count > max_forward_groups_num_every_time:
            print(f"warning: 一次最多选中 {max_forward_groups_num_every_time} 个群聊..")
            selected_group_count = selected_group_count - 1
            break

        visited_groups.add(group_name)

        # 计算点击中心点
        group_center_x = container_x1 + item_width // 2
        group_center_y = container_y1 + group_container_offset_y + i * item_height + item_height // 2

        # 点击进入群聊
        driver.tap([(group_center_x, group_center_y)])

    # step3: 执行转发
    # 等待页面加载
    time_sleep(SHORT_INTERVAL)

    # 执行转发
    if selected_group_count != 0:
        send_message_to_group(forward_msg)
    else:
        tap_return_btn()
        tap_return_btn()
        tap_return_btn()

    return selected_group_count

'''
功能：转发公众号文章，并且指定了参数scroll_count
注意：在公众号文章这个页面。
input params:
scroll_count 在“选择群聊”页面，下滑了几次

return value: 
forward_num 转发了几个群
'''
def forward_article_by_scroll(scroll_count):
    try:
        print(f"寻找<转发>按钮-右上角三个点..")
        try:
            button = driver.find_element(AppiumBy.ID, 'com.tencent.mm:id/coy')
        except NoSuchElementException:
            raise ValueError("找不到<转发>按钮..")

        button.click()
        time_sleep(SHORT_INTERVAL)

        print(f"寻找<转发给朋友>按钮..")
        try:
            layer = driver.find_element(AppiumBy.ID, 'com.tencent.mm:id/avc')
            buttons = layer.find_elements(AppiumBy.ID, 'com.tencent.mm:id/m7g')
        except NoSuchElementException:
            raise ValueError("找不到<转发给朋友>-1按钮..")

        if buttons:
            first_button = buttons[0]
            first_button.click()
        else:
            raise ValueError("找不到<转发给朋友>-2按钮..")
        time_sleep(SHORT_INTERVAL)

        print(f"寻找<多选>按钮..")
        try:
            button = driver.find_element(AppiumBy.ID, 'com.tencent.mm:id/coz')
        except NoSuchElementException:
            raise ValueError("找不到<多选>按钮..")

        button.click()
        time_sleep(SHORT_INTERVAL)

        print(f"寻找<从通讯录选择>按钮..")
        try:
            button = driver.find_element(AppiumBy.ID, 'com.tencent.mm:id/chj')
        except NoSuchElementException:
            raise ValueError("找不到<从通讯录选择>按钮..")

        button.click()
        time_sleep(SHORT_INTERVAL)

        print(f"寻找<选择群聊>按钮..")
        try:
            layer = driver.find_element(AppiumBy.ID, 'com.tencent.mm:id/mim')
            button = layer.find_element(AppiumBy.CLASS_NAME, 'android.widget.LinearLayout')
        except NoSuchElementException:
            raise ValueError("找不到<选择群聊>按钮..")

        button.click()
        time_sleep(SHORT_INTERVAL)

        print(f"寻找 群聊列表容器..")
        try:
            layer = driver.find_element(AppiumBy.ID, 'com.tencent.mm:id/gu0')
        except NoSuchElementException:
            raise ValueError("找不到<群聊列表>容器..")

        # 获取 bounds 坐标信息
        bounds_str = layer.get_attribute("bounds")
        # print(f"原始 bounds 字符串: {bounds_str}")

        # 解析字符串 "[container_x1,container_y1][container_x2,container_y2]"
        match = re.findall(r"\d+", bounds_str)
        if match:
            container_x1, container_y1, container_x2, container_y2 = map(int, match)
            container_width = container_x2 - container_x1
            container_height = container_y2 - container_y1
            print(f"群聊列表容器坐标: 左上角({container_x1}, {container_y1}), 右下角({container_x2}, {container_y2})")
            print(f"群聊列表容器的宽度: {container_width}, 高度: {container_height}")
        else:
            raise ValueError(f"无法解析群聊列表容器的 bounds 数据..")

        # 在容器内查找第一个子元素
        print(f"尝试在群聊列表容器内寻找第一个子元素..")
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
            print(f"第一个群聊item的坐标: 左上角({first_item_x1}, {first_item_y1}), 右下角({first_item_x2}, {first_item_y2})")
            print(f"群聊item元素的宽度: {item_width}, 高度: {item_height}")
        else:
            raise ValueError(f"无法解析 first_item 的 bounds 数据..")

        # 计算群聊元素名字的x轴偏移量
        first_item_name_obj = first_item.find_elements(AppiumBy.XPATH, './/android.widget.LinearLayout')[1]
        bounds_str = first_item_name_obj.get_attribute("bounds")
        # print(f"第一个 群聊item名字对象 的bound：{bounds_str}")
        match = re.findall(r"\d+", bounds_str)
        if match:
            first_item_name_x1, first_item_name_y1, first_item_name_x2, first_item_name_y2 = map(int, match)
            item_name_x_offset = first_item_name_x1
            print(f"每一个 群聊item元素名字 x轴的偏移量是: {item_name_x_offset}")
        else:
            raise ValueError(f"无法解析 first_item_name_obj 的 bounds 数据..")

        # 校验
        if container_x1 != first_item_x1 or container_y1 != first_item_y1 or container_x2 != first_item_x2:
            raise ValueError(f"Error: 坐标不匹配..")

        print(f"开始 select_group..")
        return select_group(container_x1, container_y1, container_width, container_height,
                       item_width, item_height, item_name_x_offset, scroll_count)

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
# 每次最大转发的群数量
max_forward_groups_num_every_time = 9
# 转发附带的消息
forward_msg = "hello 世界，123你好啊！"


start_time = time.time()  # 记录起始时间

# 创建ocr

app_id, app_key = get_tencent_config()
print(f"App ID: {app_id}, App Key: {app_key}")

ocr_manager = OcrManager(provider="tencent",
                         app_id=app_id,
                         app_key=app_key)

# 连接 Appium Server
driver = webdriver.Remote("http://127.0.0.1:4723",
                          options = UiAutomator2Options().load_capabilities(desired_caps))

forward()

# 退出会话
driver.quit()
print("quit program!")

end_time = time.time()  # 记录结束时间
elapsed_time = end_time - start_time  # 计算耗时
hours, rem = divmod(elapsed_time, 3600)  # 计算小时
minutes, seconds = divmod(rem, 60)  # 计算分钟和秒
print(f"execution time: {int(hours)} h {int(minutes)} m {int(seconds)} s")