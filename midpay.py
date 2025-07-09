import json
import os
import time
from datetime import datetime, timedelta
from blockchain import Blockchain, DigitalSignature

class MidPay:
    def __init__(self):
        self.transactions = {}
        self.escrow_account = 0
        self.setup_bank_files()
        self.blockchain = Blockchain(difficulty=2)
        self.keys = {
            "A": DigitalSignature.generate_keys(),
            "B": DigitalSignature.generate_keys()
        }
        self.disputes = {}
        self.users = {"A": {}, "B": {}}
        
    def setup_bank_files(self):
        """Initialize bank account files if they don't exist"""
        # Create A's bank account if it doesn't exist
        if not os.path.exists("A_bank.json"):
            with open("A_bank.json", "w") as f:
                json.dump({"balance": 1000, "transactions": []}, f, indent=4)
        
        # Create B's bank account if it doesn't exist
        if not os.path.exists("B_bank.json"):
            with open("B_bank.json", "w") as f:
                json.dump({"balance": 500, "transactions": []}, f, indent=4)
    
    def get_balance(self, user):
        """Get the balance of a user's account"""
        with open(f"{user}_bank.json", "r") as f:
            data = json.load(f)
        return data["balance"]
        
    def create_transaction(self, amount, service_description):
        """A initiates a payment to MidPay"""
        # Check if A has sufficient balance
        a_balance = self.get_balance("A")
        if a_balance < amount:
            return {"status": "failed", "message": "Insufficient funds in A's account"}
        
        # Generate transaction ID
        transaction_id = str(int(time.time()))
        
        # Store transaction details
        self.transactions[transaction_id] = {
            "amount": amount,
            "service": service_description,
            "status": "pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None,
            "released_at": None
        }
        
        # Deduct from A's account and move to escrow
        self._update_balance("A", -amount, f"Payment to escrow for {service_description} [ID: {transaction_id}]")
        self.escrow_account += amount
        
        transaction_data = {
            "transaction_id": transaction_id,
            "amount": amount,
            "service": service_description,
            "status": "pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": "A",
            "to": "escrow"
        }
        signature = DigitalSignature.sign_transaction(self.keys["A"][0], transaction_data)
        transaction_data["signature"] = signature.hex()
        self.blockchain.add_transaction(transaction_data)
        self.blockchain.mine_pending_transactions("midpay-system")
        
        return {
            "status": "success", 
            "message": f"Payment of ${amount} moved to escrow. Transaction ID: {transaction_id}",
            "transaction_id": transaction_id
        }
    
    def mark_service_completed(self, transaction_id):
        """B marks the service as completed"""
        if transaction_id not in self.transactions:
            return {"status": "failed", "message": "Invalid transaction ID"}
        
        if self.transactions[transaction_id]["status"] != "pending":
            return {"status": "failed", "message": "Transaction is not in pending state"}
        
        # Mark service as completed
        self.transactions[transaction_id]["status"] = "completed"
        self.transactions[transaction_id]["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        transaction_data = {
            "transaction_id": transaction_id,
            "status": "completed",
            "completed_at": self.transactions[transaction_id]["completed_at"],
            "completed_by": "B",
            "action": "mark_completed"
        }
        signature = DigitalSignature.sign_transaction(self.keys["B"][0], transaction_data)
        transaction_data["signature"] = signature.hex()
        self.blockchain.add_transaction(transaction_data)
        self.blockchain.mine_pending_transactions("midpay-system")
        
        return {
            "status": "success", 
            "message": "Service marked as completed. Waiting for confirmation from A."
        }
    
    def confirm_completion(self, transaction_id):
        """A confirms that the service has been completed, releasing funds to B"""
        if transaction_id not in self.transactions:
            return {"status": "failed", "message": "Invalid transaction ID"}
        
        if self.transactions[transaction_id]["status"] != "completed":
            return {"status": "failed", "message": "Service not yet marked as completed by B"}
        
        # Release funds to B
        amount = self.transactions[transaction_id]["amount"]
        service = self.transactions[transaction_id]["service"]
        
        self._update_balance("B", amount, f"Payment received for {service} [ID: {transaction_id}]")
        self.escrow_account -= amount
        
        # Update transaction status
        self.transactions[transaction_id]["status"] = "released"
        self.transactions[transaction_id]["released_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        transaction_data = {
            "transaction_id": transaction_id,
            "status": "released",
            "released_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from": "escrow",
            "to": "B",
            "confirmed_by": "A",
            "action": "release_payment"
        }
        signature = DigitalSignature.sign_transaction(self.keys["A"][0], transaction_data)
        transaction_data["signature"] = signature.hex()
        self.blockchain.add_transaction(transaction_data)
        self.blockchain.mine_pending_transactions("midpay-system")
        
        return {
            "status": "success", 
            "message": f"Payment of ${amount} released to B."
        }
    
    def cancel_transaction(self, transaction_id):
        """A cancels the transaction, returning funds from escrow"""
        if transaction_id not in self.transactions:
            return {"status": "failed", "message": "Invalid transaction ID"}
        
        if self.transactions[transaction_id]["status"] == "released":
            return {"status": "failed", "message": "Cannot cancel - funds already released"}
        
        # Return funds to A
        amount = self.transactions[transaction_id]["amount"]
        service = self.transactions[transaction_id]["service"]
        
        self._update_balance("A", amount, f"Refund for cancelled service: {service} [ID: {transaction_id}]")
        self.escrow_account -= amount
        
        # Update transaction status
        self.transactions[transaction_id]["status"] = "cancelled"
        
        transaction_data = {
            "transaction_id": transaction_id,
            "status": "cancelled",
            "cancelled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from": "escrow",
            "to": "A",
            "cancelled_by": "A",
            "action": "cancel_transaction"
        }
        signature = DigitalSignature.sign_transaction(self.keys["A"][0], transaction_data)
        transaction_data["signature"] = signature.hex()
        self.blockchain.add_transaction(transaction_data)
        self.blockchain.mine_pending_transactions("midpay-system")
        
        return {
            "status": "success", 
            "message": f"Transaction cancelled. ${amount} returned to A."
        }
    
    def _update_balance(self, user, amount, description):
        """Update a user's balance and record the transaction"""
        with open(f"{user}_bank.json", "r") as f:
            data = json.load(f)
        
        data["balance"] += amount
        data["transactions"].append({
            "amount": amount,
            "description": description,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        with open(f"{user}_bank.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def get_transaction_status(self, transaction_id):
        """Get the status of a transaction"""
        if transaction_id not in self.transactions:
            return {"status": "failed", "message": "Invalid transaction ID"}
        
        blockchain_transactions = self.blockchain.get_transaction_history(transaction_id)
        blockchain_status = "verified" if blockchain_transactions else "not found in blockchain"
        transaction_info = self.transactions[transaction_id].copy()
        transaction_info["blockchain_status"] = blockchain_status
        transaction_info["blockchain_history"] = blockchain_transactions
        
        return {
            "status": "success",
            "transaction": transaction_info
        }
    
    def verify_blockchain(self):
        is_valid = self.blockchain.is_chain_valid()
        return {
            "status": "success" if is_valid else "failed",
            "message": "Blockchain is valid" if is_valid else "Blockchain has been tampered with"
        }
    
    def display_accounts(self):
        """Display current balances and escrow amount"""
        a_balance = self.get_balance("A")
        b_balance = self.get_balance("B")
        
        print("\n=== ACCOUNT SUMMARY ===")
        print(f"A's Balance: ${a_balance}")
        print(f"B's Balance: ${b_balance}")
        print(f"Escrow: ${self.escrow_account}")
        print("=======================\n")
    
    # New methods for enhanced features
    
    def get_transaction_history(self, user=None, status=None, start_date=None, end_date=None):
        """Get filtered transaction history"""
        filtered_transactions = {}
        
        for tx_id, tx in self.transactions.items():
            # Apply filters
            if user and user not in ["A", "B"]:
                continue
                
            if status and tx["status"] != status:
                continue
                
            if start_date:
                tx_date = datetime.strptime(tx["created_at"], "%Y-%m-%d %H:%M:%S")
                if tx_date < datetime.strptime(start_date, "%Y-%m-%d"):
                    continue
                    
            if end_date:
                tx_date = datetime.strptime(tx["created_at"], "%Y-%m-%d %H:%M:%S")
                if tx_date > datetime.strptime(end_date, "%Y-%m-%d"):
                    continue
            
            filtered_transactions[tx_id] = tx
            
        return {
            "status": "success",
            "transactions": filtered_transactions
        }
    
    def create_user(self, user_id, initial_balance):
        """Create a new user with initial balance"""
        if os.path.exists(f"{user_id}_bank.json"):
            return {"status": "failed", "message": f"User {user_id} already exists"}
            
        with open(f"{user_id}_bank.json", "w") as f:
            json.dump({"balance": initial_balance, "transactions": []}, f, indent=4)
            
        # Create keys for the new user
        self.keys[user_id] = DigitalSignature.generate_keys()
        self.users[user_id] = {"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        return {
            "status": "success",
            "message": f"User {user_id} created with initial balance of ${initial_balance}"
        }
    
    def get_user_details(self, user_id):
        """Get user details including balance and transaction count"""
        if not os.path.exists(f"{user_id}_bank.json"):
            return {"status": "failed", "message": f"User {user_id} does not exist"}
            
        with open(f"{user_id}_bank.json", "r") as f:
            bank_data = json.load(f)
        
        user_transactions = 0
        for tx_id, tx in self.transactions.items():
            if tx_id.startswith(user_id) or tx.get("from") == user_id or tx.get("to") == user_id:
                user_transactions += 1
        
        return {
            "status": "success",
            "user": {
                "user_id": user_id,
                "balance": bank_data["balance"],
                "transaction_count": user_transactions,
                "transaction_history": bank_data["transactions"]
            }
        }
    
    def create_dispute(self, transaction_id, reason):
        """Create a dispute for a transaction"""
        if transaction_id not in self.transactions:
            return {"status": "failed", "message": "Invalid transaction ID"}
            
        if self.transactions[transaction_id]["status"] not in ["pending", "completed"]:
            return {"status": "failed", "message": "Can only dispute pending or completed transactions"}
            
        # Generate dispute ID
        dispute_id = f"D-{transaction_id}-{int(time.time())}"
        
        # Store dispute details
        self.disputes[dispute_id] = {
            "transaction_id": transaction_id,
            "reason": reason,
            "status": "open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": None,
            "resolution": None
        }
        
        # Update transaction status
        self.transactions[transaction_id]["status"] = "disputed"
        self.transactions[transaction_id]["dispute_id"] = dispute_id
        
        transaction_data = {
            "transaction_id": transaction_id,
            "status": "disputed",
            "dispute_id": dispute_id,
            "reason": reason,
            "action": "create_dispute"
        }
        signature = DigitalSignature.sign_transaction(self.keys["A"][0], transaction_data)  # Assuming A can create disputes
        transaction_data["signature"] = signature.hex()
        self.blockchain.add_transaction(transaction_data)
        self.blockchain.mine_pending_transactions("midpay-system")
        
        return {
            "status": "success",
            "message": f"Dispute created with ID: {dispute_id}",
            "dispute_id": dispute_id
        }
    
    def resolve_dispute(self, dispute_id, resolution):
        """Resolve a dispute"""
        if dispute_id not in self.disputes:
            return {"status": "failed", "message": "Invalid dispute ID"}
            
        if self.disputes[dispute_id]["status"] != "open":
            return {"status": "failed", "message": "Dispute is not open"}
            
        if resolution not in ["refund", "release"]:
            return {"status": "failed", "message": "Resolution must be either 'refund' or 'release'"}
        
        transaction_id = self.disputes[dispute_id]["transaction_id"]
        transaction = self.transactions[transaction_id]
        amount = transaction["amount"]
        
        # Update dispute status
        self.disputes[dispute_id]["status"] = "resolved"
        self.disputes[dispute_id]["resolved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.disputes[dispute_id]["resolution"] = resolution
        
        if resolution == "refund":
            # Return money to A
            self._update_balance("A", amount, f"Refund from dispute resolution [Dispute: {dispute_id}]")
            self.escrow_account -= amount
            # Update transaction status
            self.transactions[transaction_id]["status"] = "refunded"
            action = "refund_to_A"
            to_user = "A"
        else:  # resolution == "release"
            # Release money to B
            self._update_balance("B", amount, f"Payment from dispute resolution [Dispute: {dispute_id}]")
            self.escrow_account -= amount
            # Update transaction status
            self.transactions[transaction_id]["status"] = "released"
            action = "release_to_B"
            to_user = "B"
        
        transaction_data = {
            "dispute_id": dispute_id,
            "transaction_id": transaction_id,
            "resolution": resolution,
            "resolved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from": "escrow",
            "to": to_user,
            "action": action
        }
        # Assuming admin resolves disputes (using A's key for simplicity)
        signature = DigitalSignature.sign_transaction(self.keys["A"][0], transaction_data)
        transaction_data["signature"] = signature.hex()
        self.blockchain.add_transaction(transaction_data)
        self.blockchain.mine_pending_transactions("midpay-system")
        
        return {
            "status": "success",
            "message": f"Dispute resolved with resolution: {resolution}"
        }
    
    def create_multi_party_transaction(self, parties, amount, description):
        """Create a transaction involving multiple parties"""
        if not all(party in self.keys for party in parties):
            return {"status": "failed", "message": "One or more invalid parties"}
            
        # Generate transaction ID
        transaction_id = f"MULTI-{int(time.time())}"
        
        # Store transaction details
        self.transactions[transaction_id] = {
            "amount": amount,
            "service": description,
            "status": "pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None,
            "released_at": None,
            "parties": parties
        }
        
        # Split amount equally for now (could be customized in the future)
        share_amount = amount / (len(parties) - 1)  # Excluding the receiver
        
        # Move funds to escrow
        for party in parties:
            if party != parties[-1]:  # Assuming last party is the receiver
                # Check if party has sufficient balance
                party_balance = self.get_balance(party)
                if party_balance < share_amount:
                    # Rollback any transactions already made
                    for p in parties:
                        if p != parties[-1] and p != party:
                            self._update_balance(p, share_amount, f"Refund for failed multi-party transaction [ID: {transaction_id}]")
                            self.escrow_account -= share_amount
                    
                    return {"status": "failed", "message": f"Insufficient funds in {party}'s account"}
                
                # Deduct from party's account
                self._update_balance(party, -share_amount, f"Multi-party payment to escrow [ID: {transaction_id}]")
                self.escrow_account += share_amount
                
                transaction_data = {
                    "transaction_id": transaction_id,
                    "amount": share_amount,
                    "service": description,
                    "status": "pending",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "from": party,
                    "to": "escrow",
                    "type": "multi-party"
                }
                signature = DigitalSignature.sign_transaction(self.keys[party][0], transaction_data)
                transaction_data["signature"] = signature.hex()
                self.blockchain.add_transaction(transaction_data)
        
        self.blockchain.mine_pending_transactions("midpay-system")
        
        return {
            "status": "success",
            "message": f"Multi-party payment of ${amount} moved to escrow. Transaction ID: {transaction_id}",
            "transaction_id": transaction_id
        }
    
    def get_api_keys(self):
        """Get list of valid API keys"""
        try:
            with open('validkeys.json', 'r') as file:
                keys = json.load(file)
                # Hide actual keys, just return number of keys
                return {
                    "count": len(keys),
                    "keys": ["****" + key[-6:] for key in keys]  # Only show last 6 chars
                }
        except:
            return {"count": 0, "keys": []}
    
    def revoke_api_key(self, key):
        """Revoke an API key"""
        try:
            with open('validkeys.json', 'r') as file:
                keys = json.load(file)
                
            if key not in keys:
                return {"status": "failed", "message": "API key not found"}
                
            keys.remove(key)
            
            with open('validkeys.json', 'w') as file:
                json.dump(keys, file, indent=4)
                
            return {"status": "success", "message": "API key revoked successfully"}
        except Exception as e:
            return {"status": "failed", "message": f"Error revoking API key: {str(e)}"}
    
    def schedule_transaction(self, amount, description, execute_at):
        """Schedule a transaction for future execution"""
        # In a real system, this would use something like a task queue (Celery, etc.)
        # For this demo, we'll just create a transaction with a scheduled status
        
        # Generate transaction ID
        transaction_id = f"SCHEDULED-{int(time.time())}"
        
        # Store transaction details
        self.transactions[transaction_id] = {
            "amount": amount,
            "service": description,
            "status": "scheduled",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execute_at": execute_at
        }
        
        transaction_data = {
            "transaction_id": transaction_id,
            "amount": amount,
            "service": description,
            "status": "scheduled",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execute_at": execute_at,
            "action": "schedule_transaction"
        }
        signature = DigitalSignature.sign_transaction(self.keys["A"][0], transaction_data)
        transaction_data["signature"] = signature.hex()
        self.blockchain.add_transaction(transaction_data)
        self.blockchain.mine_pending_transactions("midpay-system")
        
        return {
            "status": "success",
            "message": f"Transaction scheduled for {execute_at}. Transaction ID: {transaction_id}",
            "transaction_id": transaction_id
        }
    
    def get_transaction_volume(self, period="month"):
        """Get transaction volume analytics"""
        now = datetime.now()
        
        if period == "day":
            start_date = datetime(now.year, now.month, now.day, 0, 0, 0)
        elif period == "week":
            start_date = now - timedelta(days=now.weekday())
            start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        elif period == "month":
            start_date = datetime(now.year, now.month, 1, 0, 0, 0)
        elif period == "year":
            start_date = datetime(now.year, 1, 1, 0, 0, 0)
        else:
            return {"status": "failed", "message": "Invalid period. Use: day, week, month, or year"}
        
        total_volume = 0
        transaction_count = 0
        status_counts = {"pending": 0, "completed": 0, "released": 0, "cancelled": 0, "disputed": 0, "scheduled": 0}
        
        for tx_id, tx in self.transactions.items():
            tx_date = datetime.strptime(tx["created_at"], "%Y-%m-%d %H:%M:%S")
            if tx_date >= start_date:
                total_volume += tx["amount"]
                transaction_count += 1
                status_counts[tx["status"]] = status_counts.get(tx["status"], 0) + 1
        
        return {
            "status": "success",
            "period": period,
            "total_volume": total_volume,
            "transaction_count": transaction_count,
            "status_breakdown": status_counts
        }
    
    def get_user_analytics(self, user_id):
        """Get analytics for a specific user"""
        if not os.path.exists(f"{user_id}_bank.json"):
            return {"status": "failed", "message": f"User {user_id} does not exist"}
        
        with open(f"{user_id}_bank.json", "r") as f:
            bank_data = json.load(f)
        
        # Analyze transaction history
        total_in = 0
        total_out = 0
        for tx in bank_data["transactions"]:
            if tx["amount"] > 0:
                total_in += tx["amount"]
            else:
                total_out += abs(tx["amount"])
        
        # Count transactions in blockchain
        blockchain_txs = 0
        for tx in self.blockchain.chain:
            for trans in tx.transactions:
                if "from" in trans and trans["from"] == user_id:
                    blockchain_txs += 1
                if "to" in trans and trans["to"] == user_id:
                    blockchain_txs += 1
        
        return {
            "status": "success",
            "user_id": user_id,
            "current_balance": bank_data["balance"],
            "total_incoming": total_in,
            "total_outgoing": total_out,
            "transaction_count": len(bank_data["transactions"]),
            "blockchain_transaction_count": blockchain_txs
        }



if __name__ == "__main__":
    # This file is now used as a library for the MCP server
    # To run the MCP server, use: python simple_mcp_server.py
    print("MidPay Core Library")
    print("Use 'python simple_mcp_server.py' to start the MCP server")
    print("Use 'python test_mcp_server.py' to test the MCP server")