import hashlib
import json
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

class Block:
    def __init__(self, index, timestamp, transaction_data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transaction_data = transaction_data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
        
    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transaction_data": self.transaction_data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()
    
    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")
        return self.hash


class Blockchain:
    def __init__(self, difficulty=2):
        self.chain = [self._create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions = []
        
    def _create_genesis_block(self):
        return Block(0, time.time(), {"message": "Genesis Block"}, "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
        return self.get_latest_block().index + 1
    
    def mine_pending_transactions(self, miner_address):
        if not self.pending_transactions:
            return False
            
        block = Block(
            len(self.chain),
            time.time(),
            {
                "transactions": self.pending_transactions,
                "miner": miner_address
            },
            self.get_latest_block().hash
        )
        
        block.mine_block(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = []
        return block
    
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
                
            if current_block.previous_hash != previous_block.hash:
                return False
                
        return True
    
    def get_transaction_history(self, transaction_id=None):
        transactions = []
        for block in self.chain[1:]:
            if 'transactions' in block.transaction_data:
                block_transactions = block.transaction_data['transactions']
                
                if transaction_id:
                    matching = [t for t in block_transactions if t.get('transaction_id') == transaction_id]
                    transactions.extend(matching)
                else:
                    transactions.extend(block_transactions)
                    
        return transactions


class DigitalSignature:
    @staticmethod
    def generate_keys():
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        return private_key, public_key
    
    @staticmethod
    def sign_transaction(private_key, transaction_data):
        transaction_bytes = json.dumps(transaction_data, sort_keys=True).encode()
        signature = private_key.sign(
            transaction_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    @staticmethod
    def verify_signature(public_key, transaction_data, signature):
        transaction_bytes = json.dumps(transaction_data, sort_keys=True).encode()
        try:
            public_key.verify(
                signature,
                transaction_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
