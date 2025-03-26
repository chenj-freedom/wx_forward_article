import ddddocr

class DdddOcrHelper:
    # OCR 识别器
    def __init__(self):
        self.ocr = ddddocr.DdddOcr(beta=True)

    def recognize(self, image_path):
        try:
            image = open(image_path, "rb").read()
            return self.ocr.classification(image)
        except Exception as e:
            print(f"OCR 识别失败: {e}")
            return ""

# debug
if __name__ == "__main__":
    # 实例化 OCR 识别工具
    ocr_helper = DdddOcrHelper()

    # 识别本地图片
    image_path = "/Users/rcadmin/Downloads/1-0.png"
    result = ocr_helper.recognize(image_path)

    if result:
        print(f"OCR 识别结果: {result}")