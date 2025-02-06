import base64

__all__ = ["encode_to_base64"]


def encode_to_base64(input_string: str) -> str:
    # 将字符串转换为字节
    input_bytes = input_string.encode("utf-8")

    # 将字节编码为Base64
    base64_bytes = base64.b64encode(input_bytes)

    # 将Base64字节转换为字符串
    base64_string = base64_bytes.decode("utf-8")

    return base64_string
