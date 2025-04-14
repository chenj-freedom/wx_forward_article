'''
{
  "platformName": "Android",
  "deviceName": "RFCT20EGLNJ",
  "automationName": "UiAutomator2",
  "appPackage": "com.tencent.mm",
  "appActivity": "com.tencent.mm.ui.LauncherUI",
  "enforceXPath1": true,
  "noReset": true,
  "unicodeKeyboard": true,
  "resetKeyboard": true,
  "ensureWebviewsHavePages": true,
  "nativeWebScreenshot": true,
  "newCommandTimeout": 3600,
  "connectHardwareKeyboard": true
}

'''

SHORT_INTERVAL = 3  # 3s
LONG_INTERVAL = 5   # 5s

# Desired Capabilities 配置
desired_caps = dict(
    platformName="Android",
    deviceName="RFCT20EGLNJ",
    automationName="UiAutomator2",
    appPackage="com.tencent.mm",
    appActivity="com.tencent.mm.ui.LauncherUI",
    enforceXPath1=True,
    noReset=True,
    unicodeKeyboard=True,
    resetKeyboard=True,
    ensureWebviewsHavePages=True,
    nativeWebScreenshot=True,
    newCommandTimeout=3600,
    connectHardwareKeyboard=True
)
