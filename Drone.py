import hashlib
import base64
import json
import re
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import ipfshttpclient
from web3 import Web3
import os
import asyncio
import aioipfs
import rlp
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_account.datastructures import SignedTransaction
from hexbytes import HexBytes
from web3.exceptions import ContractLogicError
from eth_abi import encode



class NFTMinter:
    def __init__(self, provider_url, contract_address, private_key):
        self.w3 = Web3(Web3.LegacyWebSocketProvider(provider_url))
        
        with open("./abi.json", 'r') as f:
            self.abi = json.load(f) #the JSON object must be str, bytes or bytearray, not NoneType

        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=self.abi
        )
        self.account = self.w3.eth.account.from_key(private_key)
        # self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract_address = contract_address

    async def check_connection(self):  # 新增连接检查
        if not self.w3.is_connected():
            await asyncio.sleep(1)  # 等待重连
            if not self.w3.is_connected():
                raise ConnectionError("无法连接到WebSocket节点")
    
    
    def print_abi(self):
        print(f"Loaded ABI: {str(self.abi)[:100]}...")
        

    async def mint_nft(self, ipfsCID: str, timestamp: int):
        await self.check_connection()
        
        try:
        # 预估 Gas 并构建交易
            estimated_gas = self.contract.functions.mintDroneNFT(
                ipfsCID, timestamp
            ).estimate_gas({'from': self.account.address})
        
            tx = self.contract.functions.mintDroneNFT(
                ipfsCID, timestamp
            ).build_transaction({
                'chainId': self.w3.eth.chain_id,
                'gas': int(estimated_gas * 1.2),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gasPrice': self.w3.eth.gas_price
            })
        
        # 发送并等待交易
            signed_txn = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
            if tx_receipt.status != 1:
            # 尝试获取跟踪日志
                try:
                    trace = self.w3.geth.debug.trace_transaction(tx_hash, {'tracer': 'callTracer'})
                    raise ValueError(f"交易失败，跟踪日志: {trace}")
                except:
                    raise ValueError(f"交易失败，无法获取调试日志。可能原因：Gas不足或合约无错误回滚")
        
            return tx_receipt
    
        except ContractLogicError as e:
        # 解码自定义错误（需合约 ABI 包含错误定义）
            if 'data' in e.args[0]:
                error_code = e.args[0]['data'][:10]
                error_msg = self.contract.decode_error(error_code)
                raise ValueError(f"合约逻辑错误: {error_msg}")
            else:
                raise ValueError(f"合约逻辑错误: {e}")
        
        
        
        
        
        # latest_block = self.w3.eth.get_block('latest')
        # nonce = self.w3.eth.get_transaction_count(self.account.address)
        
        # chain_id = self.w3.eth.chain_id
        # nonce = self.w3.eth.get_transaction_count(self.account.address)
        # gas_price = self.w3.eth.gas_price
        
        # tx = self.contract.functions.mintDroneNFT(#对应smart contract中的mintDroneNFT函数
        #     ipfsCID,
        #     timestamp
        # ).build_transaction({
            
        #     'chainId': chain_id,
        #     'nonce': nonce,
        #     'gasPrice': gas_price,
        #     'gas': 200000,
        #     'from': self.account.address
        # })
        
        # # 3. 签名交易
        # signed_txn = self.w3.eth.account.sign_transaction(tx, self.account.key)
    
        # # 4. 发送交易到网络
        # tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
        # # 5. 等待交易确认
        # tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # if tx_receipt.status != 1:
        #     tx = self.w3.eth.get_transaction(tx_hash)
        #     debug_output = self.w3.geth.debug.trace_transaction(tx_hash,{})
        #     raise ValueError(f"交易失败，原因: {debug_output}")
        
        # return tx_receipt
        


class DroneDataCrypto:
    def __init__(self, contract_address: str):
        self.contract_address = contract_address
       
    def _derive_aes_key(self, block_timestamp: int) -> bytes:
        h = hashlib.blake2b(digest_size=32)  # 使用blake2b哈希算法 
        contract_bytes = bytes.fromhex(self.contract_address.strip().lower()[2:])
        h.update(contract_bytes)  # h.update(contratc_address+block.timeatamp)->bytes格式
        h.update(block_timestamp.to_bytes(8, 'big'))
        return h.digest()  # 返回哈希值的bytes格式
        
    def _aes_encrypt(self, plaintext: str, timestamp: int) -> str:
        key = self._derive_aes_key(timestamp)  # 生成AES密钥，hash(contract_address+block.timestamp)
        print(f"Encryption Key: {key.hex()}")
        nonce = os.urandom(12)#随机数定义为12bytes
        cipher = Cipher(
            algorithms.AES(key),  # 256密钥
            modes.GCM(nonce),  # Galois/Counter Mode 
            backend=default_backend()  # 默认加密后端
        )     
        
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        
        return base64.b64encode(nonce + ciphertext + encryptor.tag).decode()
        
        
    def _aes_decrypt(self, ciphertext: str, block_timestamp: int) -> str:
        
        try:
            decoded = base64.b64decode(ciphertext)
            nonce = decoded[:12]
            tag = decoded[-16:]
            ciphertext_bytes = decoded[12:-16]
        
            key = self._derive_aes_key(block_timestamp)
        
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
        
            decryptor = cipher.decryptor()
        
            de=decryptor.update(ciphertext_bytes) + decryptor.finalize()
        
            return de.decode('utf-8')
        
        except Exception as e:
            print(f"解密失败细节: {str(e)}")
            raise
        
class DroneDataProcessor(DroneDataCrypto):
    def validate_inputs(self, data: dict) -> bool:
       
        validations = {
            'orderID': lambda x: re.match(r'^[A-Z0-9]{8}$', x),
            'flightStatus': lambda x: x in ['TakeOff', 'Inflight', 'Land'],
            'manufacturerID': lambda x: re.match(r'^[0-9A-Z]{18}$', x),
            'uasID': lambda x: len(x) == 11,
            'uasModel': lambda x: len(x) <= 50,
            'coordinate': lambda x: x in {'1', '2', '3'},
            'longitude': lambda x: -180 <= float(x) <= 180,
            'latitude': lambda x: -90 <= float(x) <= 90,
            'heightAltitype': lambda x: x in {'0', '1', '2', '3'},
            'height':lambda x: 0 <= float(x) <= 100,
            'altitude':lambda x: 0 <= float(x) <= 100,
            'VS': lambda x: 0 <= float(x) <= 100,
            'GS': lambda x: 0 <= float(x) <= 100,
            'course': lambda x: 0 <= float(x) < 360,
            'Duration': lambda x: float(x) > 10
        }
        
        for field, validator in validations.items():
            value = data.get(field, '')
            if not validator(value):
                raise ValueError(f"字段验证失败: {field}, 值: {value}")
        return True

    def encrypt_payload(self, data: dict, block_timestamp: int) -> tuple:
        plaintext = json.dumps(data, ensure_ascii=False)
        
        encrypted = self._aes_encrypt(plaintext, block_timestamp)
        metadata = {
            "encryption": "AES-GCM-256",
            "contract_address": self.contract_address,
            "block_timestamp": block_timestamp,
        }
        return encrypted, metadata

    def decrypt_payload(self, ciphertext: str, metadata: dict) -> dict:
        """解密数据"""
        if metadata['encryption'] != 'AES-GCM-256':
            raise ValueError("不支持的加密算法")
        
        if 'block_timestamp' not in metadata:
            raise ValueError("缺少区块链时间戳参数")
        
        try:
            decrypted = self._aes_decrypt(ciphertext, metadata['block_timestamp'])
            return json.loads(decrypted)
        except Exception as e:
            raise ValueError("解密失败，可能原因：密钥错误、数据篡改或时间戳不匹配") from e
        

# def interactive_input():
#     """增强型交互输入"""
#     print("无人机飞行数据录入系统")
#     print("="*40)
    
#     data = {
#         "orderID": str(input("产品序号（8位大写字母数字组合）: ").strip().upper()),
#         "flightStatus": str(_select_flight_status()),
#         "Duration":str(_input_flight_duration()),
#         "manufacturerID": str(input("统一社会信用代码（18位）: ").strip()),
#         "uasID": str(input("无人机登记号（11位）: ").strip()),
#         "uasModel": str(input("无人机型号: ").strip()),
#         "coordinate": str(_select_coordinate_system()),
#         "longitude": str(_input_coordinate("经度（-180~180）: ")),
#         "latitude": str(_input_coordinate("纬度（-90~90）: ")),
#         "heightAltitude": str(_select_height_mode()),
#         "VS": str(input("垂直速度（-100~100）: ").strip()),
#         "GS": str(_input_speed()),
#         "course": str(_input_course())
#     }
#     return data

async def upload_to_ipfs(data: dict) -> str:
    try:
        async with aioipfs.AsyncIPFS(host="127.0.0.1", port=5001) as client:
            json_data = json.dumps(data).encode()
            res = await client.add_bytes(json_data)
            return res['Hash']
    except aioipfs.APIError as e:
        raise ConnectionError(f"IPFS上传失败: {str(e)}")

async def get_token_cid(nft_minter: NFTMinter, token_id: int) -> str:
    
    cid,_= nft_minter.contract.functions.getDroneRecord(token_id).call(
        {'from': nft_minter.account.address}
    )
    return cid

async def download_from_ipfs(cid: str) -> dict:
    async with aioipfs.AsyncIPFS() as client:
        data_bytes = await client.cat(cid)
        return json.loads(data_bytes.decode())
 
# 辅助输入函数
# def _select_flight_status():
#     while True:
#         choice = input("飞行状态 [1]起飞 [2]飞行中 [3]降落: ").strip()
#         if choice == '1': return 'TakeOff'
#         if choice == '2': return 'Inflight'
#         if choice == '3': return 'Land'
#         print("无效输入，请重新选择")

# def _select_coordinate_system():
#     while True:
#         choice = input("坐标系 [1]WGS-84 [2]CGCS2000 [3]GLONASS-PZ90: ").strip()
#         if choice in {'1','2','3'}: return choice
#         print("请输入1-3")

# def _input_coordinate(prompt):
#     while True:
#         value = input(prompt).strip()
#         try:
#             if -180 <= float(value) <= 180:
#                 return value
#         except ValueError:
#             pass
#         print("请输入-180~180的数值")
        
# def _select_height_mode():
#     while True:
#         choice = input("高度模式 [0]GPS [1]Barometer [2]Radar [3]Lidar: ").strip()
#         if choice in {'0','1','2','3'}: return choice
#         print("请输入0-3")

# def _input_speed():
#     while True:
#         value = input("地速（0~100）: ").strip()
#         try:
#             if 0 <= float(value) <= 100:
#                 return value
#         except ValueError:
#             pass
#         print("请输入0~100的数值")
        
# def _input_course():
#     while True:
#         value = input("航向（0~360）: ").strip()
#         try:
#             if 0 <= float(value) < 360:
#                 return value
#         except ValueError:
#             pass
#         print("请输入0~360的数值")  
        
# def _input_flight_duration():
#     while True:
#         value = input("飞行时长（分钟）: ").strip()
#         try:
#             if 10 < float(value):
#                 return value
#         except ValueError:
#             pass
#         print("请输入满足大于10分钟的数值") 

def is_approved_manufacturer(self,contract, account):
    # 计算存储位置（_approvedManufacturers在slot 8）
    mapping_slot = 8
    
    # 编码键值对：address + slot
    key_data = encode(['address', 'uint256'], [account, mapping_slot])
    slot_hash = Web3.keccak(hexstr=Web3.to_hex(key_data)[2:])  # 去除0x前缀
    
    # 读取存储值
    value = self.w3.eth.get_storage_at(
        self.contract_address, 
        int.from_bytes(slot_hash, 'big')
    )
    return int.from_bytes(value, 'big') == 1

async def bypass_get_token_cid(nft_minter: NFTMinter, token_id: int) -> str:
    """绕过权限检查直接读取 IPFS CID"""
    # 计算存储插槽（_droneData 在 slot 13）
    slot = 13
    # 读取原始数据
    raw_data = nft_minter.w3.eth.get_storage_at(nft_minter.contract_address, slot)
    
    # 解码 bytes32 字符串
    return raw_data[64:].decode('utf-8').rstrip('\x00') 

async def main():
        try:
        
            nft_minter = NFTMinter(
            provider_url="ws://127.0.0.1:8545",#websocket
            contract_address = Web3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3"),
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            )
            
            await nft_minter.check_connection()
            latest_block = nft_minter.w3.eth.get_block('latest')
        
            raw_data = {
            "orderID": "A1B2C3D4",
            "flightStatus": "TakeOff",
            "Duration": "20",
            "manufacturerID": "91350100M000100Y4A",
            "uasID": "UAV-DEFAULT",
            "uasModel": "DJI Mavic 3",
            "coordinate": "1",
            "longitude": "120.123456",
            "latitude": "30.123456",
            "heightAltitype": "0",
            "VS": "10",
            "GS": "50",
            "course": "45"
            }
        
            # print("\n自动生成的测试数据:")
            for key, value in raw_data.items():
                print(f"{key}: {value}")
        
      
            processor = DroneDataProcessor(nft_minter.contract.address)
            processor.validate_inputs(raw_data)
        
            encrypted, metadata = processor.encrypt_payload(raw_data, latest_block.timestamp)
        
            storage_payload = {
                "version": "2.1",
                "encrypted_data": encrypted,
                "metadata": metadata
            }
        
            nft_minter.print_abi()
        
            cid = await upload_to_ipfs(storage_payload)#cid 储存在链上
            print("\n Successfully uploaded data，IPFS CID:", cid)
            
            
            # is_approved = nft_minter.contract.functions.viewWhitelist(nft_minter.account.address).call()
            # print(f"白名单状态: {'已授权' if is_approved else '未授权'}")
    
            
            
            # # 在 Python 中添加检查
            # code = nft_minter.w3.eth.get_code(nft_minter.contract_address)
            # assert code != HexBytes('0x'), "合约未正确部署"
        
            tx_hash = await nft_minter.mint_nft(cid, latest_block.timestamp)
            print(f"Mint NFT transaction hash: {tx_hash}")
            
            # contract_owner = nft_minter.contract.functions.owner().call()
            # is_owner = (nft_minter.account.address.lower() == contract_owner.lower())
            # is_approved = is_approved_manufacturer(nft_minter, nft_minter.account.address,"0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
        
            # print(f"账户地址: {nft_minter.account.address}")
            # print(f"合约Owner: {contract_owner}")
            # print(f"授权制造商状态: {is_approved}")
            token_id = 1
            # if not is_owner and not is_approved:
            #     raise ValueError("无铸造权限，需添加至_approvedManufacturers")
            # nft_owner = nft_minter.contract.functions.ownerOf(token_id).call()
            # is_holder = (nft_owner.lower() == nft_minter.account.address.lower())
            # print(f"是否为代币持有者: {is_holder}")
            # contract_owner = nft_minter.contract.functions.owner().call()
            # print(f"合约所有者地址: {contract_owner}")
            # is_owner = (nft_minter.account.address.lower() == contract_owner.lower())
            # print(f"当前账户是否为合约所有者: {is_owner}")

       
            # is_whitelisted = nft_minter.contract.functions.viewWhitelist(nft_minter.account.address).call()
            # print(f"当前账户是否在白名单: {is_whitelisted}")

        
            # is_blacklisted = nft_minter.contract.functions.viewBlacklist(nft_minter.account.address).call()
            # print(f"当前账户是否被黑名单屏蔽: {is_blacklisted}")
            
         
            cid_on_chain = await get_token_cid(nft_minter, token_id)
            print(f"IPFS CID of tokenID=1: {cid_on_chain}")
            downloaded_payload = await download_from_ipfs(cid_on_chain)
            
            decrypted_data = processor.decrypt_payload(
                downloaded_payload['encrypted_data'],
                downloaded_payload['metadata'])

            print("\n Decrypted validation：")
            print(json.dumps(decrypted_data, indent=2, ensure_ascii=False))
        
        except Exception as e:
            print(f"error occurs: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
    
    