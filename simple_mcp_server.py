#!/usr/bin/env python3
"""
Simple MidPay MCP Server Implementation

A lightweight Model Context Protocol server for the MidPay escrow payment system.
This implementation provides a simple JSON-RPC interface for AI models to interact
with the MidPay system.
"""

import json
import sys
import asyncio
from typing import Dict, Any, List
from midpay import MidPay
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class SimpleMidPayMCPServer:
    def __init__(self):
        self.midpay = MidPay()
        
        # MongoDB connection for API key validation (optional)
        self.mongodb_uri = os.getenv('MONGODB_URI')
        if self.mongodb_uri:
            try:
                self.mongo_client = MongoClient(self.mongodb_uri)
                self.db = self.mongo_client['Midpay']
                self.valid_keys_collection = self.db['validKeys']
            except Exception as e:
                print(f"Warning: Could not connect to MongoDB: {e}", file=sys.stderr)
                self.mongo_client = None
        else:
            self.mongo_client = None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return server capabilities"""
        return {
            "resources": {
                "subscribe": False,
                "listChanged": False
            },
            "tools": {
                "listChanged": False
            },
            "logging": {},
            "prompts": {
                "listChanged": False
            },
            "experimental": {}
        }
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        return [
            {
                "uri": "midpay://accounts",
                "name": "Account Balances",
                "description": "Current balances for all accounts (A, B, and escrow)",
                "mimeType": "application/json"
            },
            {
                "uri": "midpay://blockchain",
                "name": "Blockchain Status", 
                "description": "Current blockchain status and verification",
                "mimeType": "application/json"
            },
            {
                "uri": "midpay://transactions/history",
                "name": "Transaction History",
                "description": "Complete transaction history from the blockchain",
                "mimeType": "application/json"
            }
        ]
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource"""
        if not uri.startswith("midpay://"):
            raise ValueError(f"Unsupported URI scheme: {uri}")
        
        path = uri.replace("midpay://", "")
        
        if path == "accounts":
            a_balance = self.midpay.get_balance("A")
            b_balance = self.midpay.get_balance("B")
            content = {
                "A": a_balance,
                "B": b_balance,
                "escrow": self.midpay.escrow_account
            }
        elif path == "blockchain":
            content = self.midpay.verify_blockchain()
        elif path == "transactions/history":
            content = self.midpay.get_transaction_history()
        else:
            raise ValueError(f"Unknown resource path: {path}")
        
        return {
            "contents": [
                {
                    "type": "text",
                    "text": json.dumps(content, indent=2)
                }
            ]
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        return [
            {
                "name": "create_transaction",
                "description": "Create a new escrow transaction from user A to user B",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "Amount to transfer (must be positive)"
                        },
                        "description": {
                            "type": "string", 
                            "description": "Description of the service or transaction"
                        }
                    },
                    "required": ["amount", "description"]
                }
            },
            {
                "name": "get_transaction_status",
                "description": "Get the status and details of a specific transaction",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "string",
                            "description": "The ID of the transaction to check"
                        }
                    },
                    "required": ["transaction_id"]
                }
            },
            {
                "name": "mark_service_completed",
                "description": "Mark a service as completed (B marks the service as done)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "string",
                            "description": "The ID of the transaction to mark as completed"
                        }
                    },
                    "required": ["transaction_id"]
                }
            },
            {
                "name": "confirm_completion",
                "description": "Confirm service completion and release escrow funds (A confirms B's work)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "string",
                            "description": "The ID of the transaction to confirm"
                        }
                    },
                    "required": ["transaction_id"]
                }
            },
            {
                "name": "cancel_transaction",
                "description": "Cancel a transaction and return funds to A",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "string",
                            "description": "The ID of the transaction to cancel"
                        }
                    },
                    "required": ["transaction_id"]
                }
            },
            {
                "name": "get_balance",
                "description": "Get the current balance of a user account",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "string",
                            "enum": ["A", "B"],
                            "description": "The user whose balance to check (A or B)"
                        }
                    },
                    "required": ["user"]
                }
            },
            {
                "name": "verify_blockchain",
                "description": "Verify the integrity of the blockchain",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_transaction_history",
                "description": "Get filtered transaction history",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "string",
                            "description": "Filter by user (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status (optional)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date for filtering (optional)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date for filtering (optional)"
                        }
                    }
                }
            }
        ]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls"""
        try:
            if name == "create_transaction":
                result = self.midpay.create_transaction(
                    arguments["amount"], 
                    arguments["description"]
                )
            elif name == "get_transaction_status":
                result = self.midpay.get_transaction_status(arguments["transaction_id"])
            elif name == "mark_service_completed":
                result = self.midpay.mark_service_completed(arguments["transaction_id"])
            elif name == "confirm_completion":
                result = self.midpay.confirm_completion(arguments["transaction_id"])
            elif name == "cancel_transaction":
                result = self.midpay.cancel_transaction(arguments["transaction_id"])
            elif name == "get_balance":
                balance = self.midpay.get_balance(arguments["user"])
                result = {"user": arguments["user"], "balance": balance}
            elif name == "verify_blockchain":
                result = self.midpay.verify_blockchain()
            elif name == "get_transaction_history":
                result = self.midpay.get_transaction_history(
                    arguments.get("user"),
                    arguments.get("status"),
                    arguments.get("start_date"),
                    arguments.get("end_date")
                )
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "error": str(e),
                            "tool": name,
                            "arguments": arguments
                        }, indent=2)
                    }
                ],
                "isError": True
            }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP messages"""
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": self.get_capabilities(),
                    "serverInfo": {
                        "name": "midpay-mcp-server",
                        "version": "1.0.0"
                    }
                }
            elif method == "resources/list":
                result = {"resources": self.list_resources()}
            elif method == "resources/read":
                result = self.read_resource(params["uri"])
            elif method == "tools/list":
                result = {"tools": self.list_tools()}
            elif method == "tools/call":
                result = self.call_tool(params["name"], params.get("arguments", {}))
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """Run the MCP server"""
        # Send initial messages to stderr for debugging
        print("MidPay MCP Server starting...", file=sys.stderr)
        print(f"MongoDB connected: {self.mongo_client is not None}", file=sys.stderr)
        
        while True:
            try:
                # Read JSON-RPC message from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                message = json.loads(line.strip())
                response = await self.handle_message(message)
                
                # Send response to stdout
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                print(f"Server error: {e}", file=sys.stderr)
                break

async def main():
    """Main function"""
    server = SimpleMidPayMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
