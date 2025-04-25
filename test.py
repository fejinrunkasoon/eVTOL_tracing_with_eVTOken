from web3 import Web3
import json
import time
from eth_account import Account

# 配置Anvil本地节点
ANVIL_URL = "http://localhost:8545"
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # Anvil默认账户私钥
CONTRACT_ADDRESS = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"  # 替换为实际部署地址

# 初始化Web3
w3 = Web3(Web3.HTTPProvider(ANVIL_URL))
assert w3.is_connected(), "无法连接到节点"

# 加载合约ABI（需与最新部署合约匹配）
with open('./abi.json') as f:
    CONTRACT_ABI = json.load(f)

# 创建合约实例
contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=CONTRACT_ABI
)

def mint_test_nft(ipfs_cid="QmTestCID123"):
    try:
        # 设置发送账户
        account = w3.eth.account.from_key(PRIVATE_KEY)
        
        # 构建交易
        tx = contract.functions.mintDroneNFT(
            ipfs_cid,
            int(time.time())  # 使用当前时间戳
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_txn = Account.sign_transaction(tx, PRIVATE_KEY)
        
        # 发送交易
        tx_hash = signed_txn.raw_transaction
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # 解析事件日志获取tokenId
        mint_event = contract.events.DroneMinted().process_receipt(tx_receipt)[0]
        token_id = mint_event['args']['tokenId']
        
        print(f"铸造成功！Token ID: {token_id}")
        print(f"交易哈希: {tx_hash.hex()}")
        return token_id
        
    except Exception as e:
        print(f"铸造失败: {str(e)}")
        return None

def verify_token(token_id):
    try:
        # 验证代币存在性
        exists = contract.functions.ownerOf(token_id).call()
        print(f"代币 {token_id} 验证通过，所有者: {exists}")
        
        # 获取元数据
        uri = contract.functions.tokenURI(token_id).call()
        print(f"元数据URI: {uri}")
        
        # 获取飞行数据
        cid, timestamp = contract.functions.getDroneRecord(token_id).call()
        print(f"IPFS CID: {cid}")
        print(f"时间戳: {timestamp}")
        
        return True
        
    except Exception as e:
        print(f"验证失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 铸造测试代币
    new_token = mint_test_nft()
    
    if new_token:
        # 验证代币数据
        verify_token(new_token)