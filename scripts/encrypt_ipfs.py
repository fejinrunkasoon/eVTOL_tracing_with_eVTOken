import hashlib
import base64
import json
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from web3 import Web3
import os
import asyncio
import aioipfs
from web3.exceptions import ContractLogicError


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
        self.contract_address = contract_address

    async def check_connection(self):  
        if not self.w3.is_connected():
            await asyncio.sleep(1)  
            if not self.w3.is_connected():
                raise ConnectionError("can't connect to WebSocket node")
            
    def print_abi(self):
        print(f"Loaded ABI: {str(self.abi)[:100]}...")
        

    async def mint_nft(self, ipfsCID: str, timestamp: int):
        await self.check_connection()
        
        try:
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
        
            signed_txn = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
            if tx_receipt.status != 1:
            
                try:
                    trace = self.w3.geth.debug.trace_transaction(tx_hash, {'tracer': 'callTracer'})
                    raise ValueError(f"Transaction failed ,try tracing: {trace}")
                except:
                    raise ValueError(f"Transaction failed cannot get the debug log. Possible reasons: insufficient gas or contract no error rollback.")
        
            return tx_receipt
    
        except ContractLogicError as e:
            if 'data' in e.args[0]:
                error_code = e.args[0]['data'][:10]
                error_msg = self.contract.decode_error(error_code)
                raise ValueError(f"Contract Logic Error: {error_msg}")
            else:
                raise ValueError(f"Contract Logic Error: {e}")
            
class DroneDataCrypto:
    def __init__(self, contract_address: str):
        self.contract_address = contract_address
       
    def _derive_aes_key(self, block_timestamp: int) -> bytes:
        h = hashlib.blake2b(digest_size=32)  
        contract_bytes = bytes.fromhex(self.contract_address.strip().lower()[2:])#
        h.update(contract_bytes) 
        h.update(block_timestamp.to_bytes(8, 'big'))
        return h.digest()  
        
    def _aes_encrypt(self, plaintext: str, timestamp: int) -> str:
        key = self._derive_aes_key(timestamp)  # AES-256 key derivation
        print(f"Encryption Key: {key.hex()}")
        nonce = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(key),  # AES-256
            modes.GCM(nonce),  # Galois/Counter Mode 
            backend=default_backend()  
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
            print(f"decrypt error: {str(e)}")
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
                raise ValueError(f"Field validation failed: {field}, Value: {value}")
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
        
        if metadata['encryption'] != 'AES-GCM-256':
            raise ValueError("the encryption algorithm is not supported")
        
        if 'block_timestamp' not in metadata:
            raise ValueError("lack of block timestamp parameter")
        
        try:
            decrypted = self._aes_decrypt(ciphertext, metadata['block_timestamp'])
            return json.loads(decrypted)
        except Exception as e:
            raise ValueError("Decrypt failed, possible reasons: key error, data tampering or timestamp mismatch") from e

async def upload_to_ipfs(data: dict) -> str:
    try:
        async with aioipfs.AsyncIPFS(host="127.0.0.1", port=5001) as client:
            json_data = json.dumps(data).encode()
            res = await client.add_bytes(json_data)
            return res['Hash']
    except aioipfs.APIError as e:
        raise ConnectionError(f"IPFS upload failed : {str(e)}")

async def get_token_cid(nft_minter: NFTMinter, token_id: int) -> str:
    
    cid,_= nft_minter.contract.functions.getDroneRecord(token_id).call(
        {'from': nft_minter.account.address}
    )
    return cid

async def download_from_ipfs(cid: str) -> dict:
    async with aioipfs.AsyncIPFS() as client:
        data_bytes = await client.cat(cid)
        return json.loads(data_bytes.decode())

async def main():
        try:
            nft_minter = NFTMinter(
            provider_url="ws://127.0.0.1:8545", #websocket defalt port is 8545 and open the anvil node
            contract_address = Web3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3"),
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            )#it can be changed freely according the real caller address(Deployed to: can be seen in README.txt) and private key of forge
            
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
            "height": "50",
            "altitude": "100",
            "VS": "10",
            "GS": "50",
            "course": "45"
            }
        
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
            
            tx_hash = await nft_minter.mint_nft(cid, latest_block.timestamp)
            print(f"Mint NFT transaction hash: {tx_hash}")
            
            token_id = 1 #it can be changed freely according the number of real token_id
        
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
          
