original_str = 'Python 编码测试'
encoded_bytes =original_str
print(encoded_bytes)

ascii_encoded = original_str.encode("ascii",errors='ignore')
print(ascii_encoded)

encoded_bytes =b'Python \xe7\xbc\x96\xe7\xa0\x81\xe6\xb5\x8b\xe8\xaf\x95'#byte形式
    # Python ：ASCII字符直接显示

    # \xe7\xbc\x96 -> "编"（UTF-8编码）

    # \xe7\xa0\x81 -> "码"
    
    # \xe6\xb5\x8b -> "测"

    # \xe8\xaf\x95 ->"试"utf-8 "编码测试"
decoded_str =encoded_bytes.decode("utf-8")
print(decoded_str)

wrong_decoded = encoded_bytes.decode("ascii",errors="replace")
print(wrong_decoded)

    # 大端：高位字节存储在低地址，低位字节存储在高地址。大端（网络字节序）是标准（如 !i 格式符）。
    # 示例：整数 0x12345678 存储为 12 34 56 78。

    # 小端：低位字节存储在低地址，高位字节存储在高地址。小端是 x86/x64 架构的默认顺序，符合内存布局。
    # 示例：整数 0x12345678 存储为 78 56 34 12。
    
