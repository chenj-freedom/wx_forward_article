from appium.webdriver.common.appiumby import AppiumBy

def print_children(parent_element):
    try:
        child_elements = parent_element.find_elements(AppiumBy.XPATH, ".//*")  # 获取所有子元素
        child_count = len(child_elements)
        print(f"第一层子元素个数: {child_count}")
        for index, child in enumerate(child_elements):
            print(f"子元素 {index + 1} 的类型: {child.get_attribute('className')}")
    except Exception as e:
        print(f"print_children 捕获到异常：{e}")

def print_attr(element):
    try:
    # 获取常见属性
        attributes = ["package", "class", "text", "content-desc",
                      "resource-id", "checkable", "checked", "clickable",
                      "enabled", "focusable", "focused", "long-clickable",
                      "password", "scrollable", "selected", "bounds",
                      "displayed", "selection-start", "selection-end", "hint",
                      "extras"]

        # 逐个打印属性值
        for attr in attributes:
            value = element.get_attribute(attr)
            print(f"{attr}: {value}")
    except Exception as e:
        print(f"print_attr 捕获到异常：{e}")