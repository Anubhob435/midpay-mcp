# MidPay MCP Server

This directory contains the Model Context Protocol (MCP) server for the MidPay escrow payment system. The MCP server allows AI models to interact with the MidPay system through a standardized protocol.

## Features

The MidPay MCP server provides:

### Resources
- **Account Balances**: Real-time balance information for users A, B, and escrow account
- **Blockchain Status**: Current blockchain verification status and integrity
- **Transaction History**: Complete transaction history from the blockchain

### Tools
- **create_transaction**: Create new escrow transactions
- **get_transaction_status**: Check transaction status and details
- **mark_service_completed**: Mark services as completed
- **confirm_completion**: Confirm service completion and release funds
- **cancel_transaction**: Cancel transactions and return funds
- **get_balance**: Get user account balances
- **verify_blockchain**: Verify blockchain integrity
- **create_dispute**: Create transaction disputes
- **resolve_dispute**: Resolve existing disputes
- **create_multi_party_transaction**: Create multi-party transactions
- **get_transaction_history**: Get filtered transaction history
- **get_analytics**: Get transaction volume analytics

## Installation

1. Install the MCP library:
```bash
pip install mcp
```

2. Install project dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
MONGODB_URI=mongodb://localhost:27017
# or for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

## Running the MCP Server

### Standalone Mode
```bash
python mcp_server.py
```

### With MCP Client Integration

For integration with MCP-compatible AI clients, the server uses stdio communication:

```bash
python mcp_server.py
```

## Usage Examples

Once connected through an MCP client, you can:

### Check Account Balances
```
Get the current balance for user A
```

### Create a Transaction
```
Create a transaction of $100 for "Website development services"
```

### Complete Transaction Flow
```
1. Create transaction: amount=500, description="Logo design"
2. Mark service completed for transaction ID: [transaction_id]
3. Confirm completion for transaction ID: [transaction_id]
```

### Blockchain Operations
```
Verify the blockchain integrity
```

### Analytics
```
Get transaction volume analytics for the past month
```

## Integration with AI Models

This MCP server is designed to work with AI models that support the Model Context Protocol. The server provides:

- **Type-safe interactions**: All tools have defined input schemas
- **Real-time data**: Direct access to current MidPay system state
- **Comprehensive operations**: Full access to MidPay functionality
- **Error handling**: Graceful error responses for invalid operations

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

## Security Considerations

- The MCP server provides direct access to the MidPay system
- In production, consider adding authentication and rate limiting
- API key validation is optional and requires MongoDB configuration
- All transactions are logged to the blockchain for audit purposes

## Development

To extend the MCP server:

1. Add new tools in the `handle_list_tools()` method
2. Implement tool logic in the `handle_call_tool()` method
3. Add new resources in the `handle_list_resources()` method
4. Update the README with new functionality

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure `mcp` library is installed: `pip install mcp`
2. **MongoDB connection**: Check `MONGODB_URI` environment variable
3. **File permissions**: Ensure read/write access to bank JSON files
4. **Port conflicts**: MCP uses stdio, no port configuration needed

### Logs

Enable debug logging by setting environment variable:
```bash
export MCP_LOG_LEVEL=debug
```
