import ddddocr

class OcrHelper:
    # OCR 识别器
    ocr = ddddocr.DdddOcr(beta=True)

    @staticmethod
    def get_group_name_from_image(image):
        """使用 ddddocr 识别群聊名字"""
        try:
            return OcrHelper.ocr.classification(image)
        except Exception as e:
            print(f"OCR 识别失败: {e}")
            return ""
