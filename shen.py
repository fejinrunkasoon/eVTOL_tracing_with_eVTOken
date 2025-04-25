from web3 import Web3

# 连接 WebSocket
w3 = Web3(Web3.LegacyWebSocketProvider("ws://127.0.0.1:8545"))
assert w3.is_connected(), "连接失败！"

# 获取当前区块号
block_number = w3.eth.block_number
print(f"当前区块: {block_number}")

# 查询账户余额（Anvil 默认第一个账户）
balance = w3.eth.get_balance(w3.eth.accounts[0])
print(f"账户余额: {balance} wei (约 {w3.from_wei(balance, 'ether')} ETH)")