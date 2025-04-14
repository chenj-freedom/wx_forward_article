import sys
import os
import re

# 关键修正：添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用绝对路径导入
from ocr_manager.dddd_ocr_helper import DdddOcrHelper
from ocr_manager.tencent_ocr_helper import TencentOcrHelper
from ocr_manager.baidu_ocr_helper import BaiduOcrHelper

from config_loader import get_tencent_config

# OCR 管理器
class OcrManager:
    def __init__(self, provider="ddddocr", **kwargs):
        self.ocr = self._get_ocr_provider(provider, **kwargs)

    def _get_ocr_provider(self, provider, **kwargs):
        if provider == "ddddocr":
            return DdddOcrHelper()
        elif provider == "tencent":
            return TencentOcrHelper(kwargs.get("app_id", "default_app_id"), kwargs.get("app_key", "default_app_key"))
        elif provider == "baidu":
            return BaiduOcrHelper(kwargs.get("api_key", "default_api_key"),
                                  kwargs.get("secret_key", "default_secret_key"))
        else:
            raise ValueError("Unsupported OCR provider")

    def recognize(self, image_path):
        result = self.ocr.recognize(image_path)
        return result


# 使用示例
if __name__ == "__main__":
    image_path = "/Users/rcadmin/Downloads/1-0.png"

    # # 使用 ddddocr
    ocr_manager = OcrManager(provider="ddddocr")
    print(ocr_manager.recognize(image_path))

    app_id, app_key = get_tencent_config()
    # 使用腾讯 OCR
    ocr_manager = OcrManager(provider="tencent", app_id=app_id, app_key=app_key)
    print(ocr_manager.recognize(image_path))

    # 使用百度 OCR
    # ocr_manager = OcrManager(provider="baidu", api_key="your_api_key", secret_key="your_secret_key")
    # print(ocr_manager.recognize(image_data))
