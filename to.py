# 修改后的NFTMinter类（关键修正点）
import asyncio
import json
from web3 import Web3
from eth_account import Account

class NFTMinter:
    def __init__(self, provider_url, contract_address, private_key):
        # 使用HTTPProvider替代WebSocket
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        
        # 确保ABI文件存在且正确
        with open("./abi.json", 'r') as f:
            self.abi = json.load(f)
        
        # 校验合约地址格式
        self.contract_address = Web3.to_checksum_address(contract_address)
        
        # 创建合约实例
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )
        
        # 使用eth_account处理账户
        self.account = Account.from_key(private_key)
        print(f"已加载账户：{self.account.address}")

    async def mint_nft(self, ipfsCID: str, timestamp: int):
        # 获取链参数
        chain_id = self.w3.eth.chain_id
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = self.w3.eth.gas_price
        
        # 构建交易（推荐使用最新web3.py语法）
        transaction = self.contract.functions.mintDroneNFT(
            ipfsCID,
            timestamp
        ).build_transaction({
            'chainId': chain_id,
            'gas': 200000,  # 可替换为 estimate_gas()
            'gasPrice': gas_price,
            'nonce': nonce,
        })

        # 签名交易（使用eth_account方式）
        signed_txn = Account.sign_transaction(transaction, self.account.key)
        
        # 发送原始交易
        tx_hash = signed_txn.raw_transaction
        return tx_hash.hex()

# 使用示例
async def main():
    # anvil默认配置
    ANVIL_RPC = "http://127.0.0.1:8545"
    CONTRACT_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # anvil默认第一个部署合约地址
    PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # anvil第一个测试账户私钥

    minter = NFTMinter(
        provider_url=ANVIL_RPC,
        contract_address=CONTRACT_ADDRESS,
        private_key=PRIVATE_KEY
    )
    
    # 验证连接
    if not minter.w3.is_connected():
        raise ConnectionError("无法连接到anvil节点")

    # 铸造NFT（使用最新区块时间戳）
    latest_block = minter.w3.eth.get_block('latest')
    tx_hash = await minter.mint_nft("QmTestCID", latest_block.timestamp)
    print(f"交易已发送: {tx_hash}")

    # 等待交易确认（anvil默认自动挖矿）
    receipt = minter.w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"交易已确认，区块号：{receipt['blockNumber']}")

if __name__ == "__main__":
    asyncio.run(main())