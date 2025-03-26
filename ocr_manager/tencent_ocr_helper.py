import json
import base64
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models

class TencentOcrHelper:
    def __init__(self, secret_id, secret_key):
        try:
            # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
            # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性
            # 以下代码示例仅供参考，建议采用更安全的方式来使用密钥
            # 请参见：https://cloud.tencent.com/document/product/1278/85305
            # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
            self.cred = credential.Credential(secret_id, secret_key)
            # 实例化一个http选项，可选的，没有特殊需求可以跳过
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"

            # 实例化一个client选项，可选的，没有特殊需求可以跳过
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象,clientProfile是可选的
            self.client = ocr_client.OcrClient(self.cred, "", clientProfile)
        except TencentCloudSDKException as err:
            print(err)
            self.client = None

    def recognize(self, image_path):
        if self.client is None:
            print("OCR 客户端未初始化，无法识别")
            return None

        try:
            # 读取本地图片并转换为 Base64 编码
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

            # 创建 OCR 请求对象
            req = models.GeneralBasicOCRRequest()
            params = {
                "ImageBase64": image_base64
            }
            req.from_json_string(json.dumps(params))

            # 发送请求并获取响应
            resp = self.client.GeneralBasicOCR(req)

            # 返回 JSON 格式的响应
            # return resp.to_json_string()
            return resp.TextDetections[0].DetectedText
        except TencentCloudSDKException as err:
            print(f"OCR 识别失败: {err}")
            return None
        except FileNotFoundError:
            print(f"文件未找到: {image_path}")
            return None
        except Exception as e:
            print(f"发生异常: {e}")
            return None


# debug
if __name__ == "__main__":
    # 用真实的 SecretId 和 SecretKey 替换
    secret_id = "xxx"
    secret_key = "xxx"

    # 实例化 OCR 识别工具
    ocr_helper = TencentOcrHelper(secret_id, secret_key)

    # 识别本地图片
    image_path = "/Users/rcadmin/Downloads/1-0.png"
    result = ocr_helper.recognize(image_path)

    if result:
        print(f"OCR 识别结果: {result}")