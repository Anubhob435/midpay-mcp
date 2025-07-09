#!/usr/bin/env python3
"""
Test script for the MidPay MCP Server

This script tests the basic functionality of the MCP server by sending
JSON-RPC messages and verifying responses.
"""

import json
import subprocess
import asyncio
import sys
import os

class MCPServerTest:
    def __init__(self, server_script="simple_mcp_server.py"):
        self.server_script = server_script
        self.process = None
        self.message_id = 1
    
    def get_next_id(self):
        """Get next message ID"""
        current_id = self.message_id
        self.message_id += 1
        return current_id
    
    async def start_server(self):
        """Start the MCP server process"""
        self.process = subprocess.Popen(
            [sys.executable, self.server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Give the server a moment to start
        await asyncio.sleep(1)
    
    async def send_message(self, method, params=None):
        """Send a message to the MCP server"""
        message = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": method
        }
        
        if params:
            message["params"] = params
        
        # Send message
        message_line = json.dumps(message) + "\n"
        self.process.stdin.write(message_line)
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if response_line:
            return json.loads(response_line.strip())
        return None
    
    async def test_initialize(self):
        """Test server initialization"""
        print("Testing initialization...")
        response = await self.send_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        })
        
        if response and "result" in response:
            print("✓ Initialization successful")
            print(f"  Server: {response['result']['serverInfo']['name']}")
            print(f"  Version: {response['result']['serverInfo']['version']}")
            return True
        else:
            print("✗ Initialization failed")
            print(f"  Response: {response}")
            return False
    
    async def test_list_resources(self):
        """Test listing resources"""
        print("\nTesting resource listing...")
        response = await self.send_message("resources/list")
        
        if response and "result" in response and "resources" in response["result"]:
            resources = response["result"]["resources"]
            print(f"✓ Found {len(resources)} resources")
            for resource in resources:
                print(f"  - {resource['name']}: {resource['uri']}")
            return True
        else:
            print("✗ Resource listing failed")
            print(f"  Response: {response}")
            return False
    
    async def test_list_tools(self):
        """Test listing tools"""
        print("\nTesting tool listing...")
        response = await self.send_message("tools/list")
        
        if response and "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"✓ Found {len(tools)} tools")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            return True
        else:
            print("✗ Tool listing failed")
            print(f"  Response: {response}")
            return False
    
    async def test_read_resource(self):
        """Test reading a resource"""
        print("\nTesting resource reading...")
        response = await self.send_message("resources/read", {
            "uri": "midpay://accounts"
        })
        
        if response and "result" in response:
            print("✓ Resource reading successful")
            content = response["result"]["contents"][0]["text"]
            accounts = json.loads(content)
            print(f"  Account A: ${accounts['A']}")
            print(f"  Account B: ${accounts['B']}")
            print(f"  Escrow: ${accounts['escrow']}")
            return True
        else:
            print("✗ Resource reading failed")
            print(f"  Response: {response}")
            return False
    
    async def test_get_balance_tool(self):
        """Test the get_balance tool"""
        print("\nTesting get_balance tool...")
        response = await self.send_message("tools/call", {
            "name": "get_balance",
            "arguments": {"user": "A"}
        })
        
        if response and "result" in response:
            print("✓ get_balance tool successful")
            content = response["result"]["content"][0]["text"]
            result = json.loads(content)
            print(f"  User A balance: ${result['balance']}")
            return True
        else:
            print("✗ get_balance tool failed")
            print(f"  Response: {response}")
            return False
    
    async def test_create_transaction_tool(self):
        """Test the create_transaction tool"""
        print("\nTesting create_transaction tool...")
        response = await self.send_message("tools/call", {
            "name": "create_transaction",
            "arguments": {
                "amount": 100,
                "description": "Test transaction for MCP server"
            }
        })
        
        if response and "result" in response:
            print("✓ create_transaction tool successful")
            content = response["result"]["content"][0]["text"]
            result = json.loads(content)
            if "transaction_id" in result:
                print(f"  Transaction ID: {result['transaction_id']}")
                return result["transaction_id"]
            else:
                print(f"  Result: {result}")
                return None
        else:
            print("✗ create_transaction tool failed")
            print(f"  Response: {response}")
            return None
    
    async def test_verify_blockchain_tool(self):
        """Test the verify_blockchain tool"""
        print("\nTesting verify_blockchain tool...")
        response = await self.send_message("tools/call", {
            "name": "verify_blockchain",
            "arguments": {}
        })
        
        if response and "result" in response:
            print("✓ verify_blockchain tool successful")
            content = response["result"]["content"][0]["text"]
            result = json.loads(content)
            print(f"  Blockchain valid: {result.get('valid', 'Unknown')}")
            return True
        else:
            print("✗ verify_blockchain tool failed")
            print(f"  Response: {response}")
            return False
    
    async def cleanup(self):
        """Clean up the server process"""
        if self.process:
            self.process.terminate()
            await asyncio.sleep(1)
            if self.process.poll() is None:
                self.process.kill()
    
    async def run_all_tests(self):
        """Run all tests"""
        print("MidPay MCP Server Test Suite")
        print("=" * 40)
        
        try:
            await self.start_server()
            
            # Run tests in sequence
            tests = [
                self.test_initialize(),
                self.test_list_resources(),
                self.test_list_tools(),
                self.test_read_resource(),
                self.test_get_balance_tool(),
                self.test_create_transaction_tool(),
                self.test_verify_blockchain_tool()
            ]
            
            results = []
            for test in tests:
                result = await test
                results.append(result)
            
            # Summary
            print("\n" + "=" * 40)
            print("Test Summary:")
            passed = sum(1 for r in results if r)
            total = len(results)
            print(f"Passed: {passed}/{total}")
            
            if passed == total:
                print("🎉 All tests passed!")
            else:
                print("❌ Some tests failed")
        
        except Exception as e:
            print(f"Test suite error: {e}")
        
        finally:
            await self.cleanup()

async def main():
    """Main test function"""
    tester = MCPServerTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
