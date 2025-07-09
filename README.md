# MidPay MCP Server

MidPay MCP Server is a Model Context Protocol implementation that provides AI models with access to an escrow payment system. It enables AI-powered transaction management, account monitoring, and blockchain operations.

## Features

- **MCP Protocol**: Model Context Protocol server for AI integration
- **Blockchain Integration**: Immutable transaction records using proof-of-work
- **Digital Signatures**: RSA-based cryptographic verification of transactions
- **Escrow Payments**: Secure fund transfers with an escrow holding system
- **Transaction Management**: Create, complete, confirm, and cancel transactions
- **Account Tracking**: Monitor balances for both parties and the escrow account
- **Transaction History**: Blockchain-verified transaction history

## Architecture

```
AI Model/Client
       ↓
MCP Protocol (stdio)
       ↓
MidPay MCP Server
       ↓
MidPay Core System
       ↓
[Bank JSON Files, MongoDB, Blockchain]
```

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Required packages: cryptography, pymongo, python-dotenv

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd midpay-mcp
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the MCP Server:

   **Simple MCP Server**:
   ```bash
   python simple_mcp_server.py
   ```
   
   **Or use the startup scripts**:
   - Windows: `start_mcp_server.bat`
   - Linux/Mac: `./start_mcp_server.sh`

4. Test the MCP Server:
   ```bash
   python test_mcp_server.py
   ```

## MCP Resources

The MCP server provides real-time access to:

- **`midpay://accounts`** - Current account balances and escrow status
- **`midpay://blockchain`** - Blockchain verification and statistics  
- **`midpay://transactions/history`** - Complete transaction history

## MCP Tools

The MCP server provides the following tools for AI interaction:

- **`create_transaction`** - Create new escrow transactions
- **`get_transaction_status`** - Check transaction details
- **`mark_service_completed`** - Mark services as completed
- **`confirm_completion`** - Confirm completion and release funds
- **`cancel_transaction`** - Cancel transactions
- **`get_balance`** - Get user account balances
- **`verify_blockchain`** - Verify blockchain integrity
- **`get_transaction_history`** - Get filtered transaction history

## Configuration

### Environment Variables

Create a `.env` file in the project root with optional MongoDB configuration:

```env
MONGODB_URI=mongodb://localhost:27017
# or for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password
```

### MCP Client Configuration

For integration with MCP-compatible clients, add to your configuration:

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

## File Structure

- **`simple_mcp_server.py`**: Main MCP server implementation
- **`midpay.py`**: Core MidPay escrow system logic
- **`blockchain.py`**: Blockchain implementation with digital signatures
- **`test_mcp_server.py`**: Test suite for the MCP server
- **`start_mcp_server.bat`**: Windows startup script
- **`start_mcp_server.sh`**: Linux/Mac startup script
- **`requirements.txt`**: Python dependencies
- **`A_bank.json`**: Party A's account balance and transaction history
- **`B_bank.json`**: Party B's account balance and transaction history
- **`mcp_config.json`**: MCP client configuration example
- **`INTEGRATION_GUIDE.md`**: Detailed integration instructions
- **`MCP_README.md`**: MCP server overview

## Usage Examples

### Basic Transaction Flow

1. **Create a transaction**:
   ```json
   {
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

2. **Mark service completed**:
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "mark_service_completed",
       "arguments": {"transaction_id": "1720000000"}
     }
   }
   ```

3. **Confirm completion**:
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "confirm_completion",
       "arguments": {"transaction_id": "1720000000"}
     }
   }
   ```

### Account Monitoring

Check account balances:
```json
{
  "method": "resources/read",
  "params": {"uri": "midpay://accounts"}
}
```

Verify blockchain integrity:
```json
{
  "method": "tools/call",
  "params": {
    "name": "verify_blockchain",
    "arguments": {}
  }
}
```

## Documentation

For detailed information, see:
- **`MCP_README.md`** - MCP server overview and features
- **`INTEGRATION_GUIDE.md`** - Complete integration instructions
- **`test_mcp_server.py`** - Example usage and testing

## Security Notes

This is a simulation designed for AI integration and not intended for real-world financial transactions. While it demonstrates blockchain concepts, a production system would require additional security measures including:

- User authentication and authorization
- Secure key storage
- Network communication encryption
- Additional validation and security checks

## License

[MIT License](LICENSE)
