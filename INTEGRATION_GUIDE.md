# MidPay MCP Server Integration Guide

This guide explains how to integrate the MidPay MCP (Model Context Protocol) server with various AI clients and applications.

## Overview

The MidPay MCP server provides a standardized interface for AI models to interact with the MidPay escrow payment system. It supports:

- **Real-time account monitoring**
- **Transaction creation and management**
- **Blockchain verification**
- **Dispute handling**
- **Analytics and reporting**

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd midpay-mcp

# Install dependencies
pip install -r requirements.txt

# Set up environment (optional)
cp .env.example .env
# Edit .env with your MongoDB URI if needed
```

### 2. Run the Server

**Windows:**
```bash
start_mcp_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_mcp_server.sh
./start_mcp_server.sh
```

**Manual:**
```bash
python simple_mcp_server.py
```

### 3. Test the Server

```bash
python test_mcp_server.py
```

## Integration Methods

### Method 1: Direct JSON-RPC Communication

The MCP server uses JSON-RPC 2.0 over stdio. You can integrate it directly:

```python
import subprocess
import json

# Start the server
process = subprocess.Popen(
    ['python', 'simple_mcp_server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send initialization message
init_msg = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "my-client", "version": "1.0.0"}
    }
}

process.stdin.write(json.dumps(init_msg) + "\n")
process.stdin.flush()

# Read response
response = json.loads(process.stdout.readline())
print(response)
```

### Method 2: MCP Client Library Integration

If using an MCP-compatible client:

```json
{
  "mcpServers": {
    "midpay": {
      "command": "python",
      "args": ["simple_mcp_server.py"],
      "cwd": "/path/to/midpay-mcp"
    }
  }
}
```

### Method 3: Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "midpay-escrow": {
      "command": "python",
      "args": ["d:\\Project Archive\\midpay-mcp\\simple_mcp_server.py"],
      "cwd": "d:\\Project Archive\\midpay-mcp"
    }
  }
}
```

## Available Operations

### Resources

Access real-time data:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "resources/read",
  "params": {
    "uri": "midpay://accounts"
  }
}
```

Available resources:
- `midpay://accounts` - Account balances
- `midpay://blockchain` - Blockchain status
- `midpay://transactions/history` - Transaction history

### Tools

Execute operations:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "create_transaction",
    "arguments": {
      "amount": 500,
      "description": "Website development"
    }
  }
}
```

Available tools:
- `create_transaction` - Create new transactions
- `get_transaction_status` - Check transaction details
- `mark_service_completed` - Mark services complete
- `confirm_completion` - Confirm and release funds
- `cancel_transaction` - Cancel transactions
- `get_balance` - Get account balances
- `verify_blockchain` - Verify blockchain integrity
- `get_transaction_history` - Get filtered history

## Common Use Cases

### 1. Account Management

```bash
# Check balances
{
  "method": "tools/call",
  "params": {
    "name": "get_balance",
    "arguments": {"user": "A"}
  }
}

# View all accounts
{
  "method": "resources/read",
  "params": {"uri": "midpay://accounts"}
}
```

### 2. Transaction Workflow

```bash
# 1. Create transaction
{
  "method": "tools/call",
  "params": {
    "name": "create_transaction",
    "arguments": {
      "amount": 1000,
      "description": "Logo design project"
    }
  }
}

# 2. Mark service completed
{
  "method": "tools/call",
  "params": {
    "name": "mark_service_completed",
    "arguments": {"transaction_id": "1720000000"}
  }
}

# 3. Confirm completion
{
  "method": "tools/call",
  "params": {
    "name": "confirm_completion",
    "arguments": {"transaction_id": "1720000000"}
  }
}
```

### 3. Monitoring and Analytics

```bash
# Get transaction history
{
  "method": "tools/call",
  "params": {
    "name": "get_transaction_history",
    "arguments": {
      "status": "completed",
      "user": "A"
    }
  }
}

# Verify blockchain
{
  "method": "tools/call",
  "params": {
    "name": "verify_blockchain",
    "arguments": {}
  }
}
```

## Error Handling

The server returns standard JSON-RPC error responses:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Insufficient funds in A's account"
  }
}
```

Common error codes:
- `-32700` - Parse error
- `-32600` - Invalid request
- `-32601` - Method not found
- `-32602` - Invalid params
- `-32603` - Internal error

## Security Considerations

### Production Deployment

1. **Authentication**: Add API key validation
2. **Rate Limiting**: Implement request throttling
3. **Logging**: Enable audit logging
4. **Network Security**: Use secure connections
5. **Access Control**: Restrict server access

### Environment Variables

```bash
# Optional MongoDB connection
MONGODB_URI=mongodb://localhost:27017

# Logging level
MCP_LOG_LEVEL=info
```

## Troubleshooting

### Common Issues

1. **Server not starting**
   - Check Python installation
   - Verify dependencies: `pip install -r requirements.txt`
   - Check file permissions

2. **Connection refused**
   - Ensure server is running
   - Check stdio communication
   - Verify process is not terminated

3. **Import errors**
   - Install missing packages
   - Check Python path
   - Verify midpay.py exists

4. **MongoDB errors**
   - Check MONGODB_URI in .env
   - Verify MongoDB is running
   - Check network connectivity

### Debug Mode

Enable debug logging:

```bash
export MCP_LOG_LEVEL=debug
python simple_mcp_server.py
```

### Testing

Run the test suite:

```bash
python test_mcp_server.py
```

## API Reference

### Complete Tool Schema

See the source code in `simple_mcp_server.py` for complete input schemas for all tools.

### Resource URIs

- `midpay://accounts` - Account balances and escrow status
- `midpay://blockchain` - Blockchain verification and statistics
- `midpay://transactions/history` - Complete transaction history

### Example Client Implementation

```python
import asyncio
import json
import subprocess

class MidPayMCPClient:
    def __init__(self):
        self.process = None
        self.msg_id = 1
    
    async def connect(self):
        self.process = subprocess.Popen(
            ['python', 'simple_mcp_server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        
        # Initialize
        await self.send_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "example-client", "version": "1.0.0"}
        })
    
    async def send_message(self, method, params=None):
        message = {
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": method
        }
        if params:
            message["params"] = params
        
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()
        self.msg_id += 1
        
        response = json.loads(self.process.stdout.readline())
        return response
    
    async def create_transaction(self, amount, description):
        return await self.send_message("tools/call", {
            "name": "create_transaction",
            "arguments": {"amount": amount, "description": description}
        })
    
    async def get_accounts(self):
        return await self.send_message("resources/read", {
            "uri": "midpay://accounts"
        })

# Usage
async def main():
    client = MidPayMCPClient()
    await client.connect()
    
    # Get account balances
    accounts = await client.get_accounts()
    print(accounts)
    
    # Create transaction
    transaction = await client.create_transaction(100, "Test payment")
    print(transaction)

asyncio.run(main())
```

This integration guide provides everything needed to connect AI models and applications to the MidPay escrow system through the MCP protocol.
