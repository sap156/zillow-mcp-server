# Zillow MCP Server

A Model Context Protocol (MCP) server that provides real-time access to Zillow real estate data, built with Python and FastMCP.

## Features

- 🏠 **Property Search**: Search for properties by location, price range, and property features
- 💰 **Property Details**: Get detailed information about specific properties
- 📊 **Zestimates**: Access Zillow's proprietary home valuation data
- 📈 **Market Trends**: View real estate market trends for any location
- 🧮 **Mortgage Calculator**: Calculate mortgage payments based on various inputs
- 🔍 **Health Check**: Verify API connectivity and monitor performance

## Installation

### Prerequisites

- Python 3.8 or higher
- A Zillow Bridge API key (request access at api@bridgeinteractive.com)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/zillow-mcp-server.git
   cd zillow-mcp-server
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Zillow API key:
   ```
   ZILLOW_API_KEY=your_zillow_api_key_here
   ```

### Running the Server

Run the server with options:

```bash
# Standard stdio mode (for Claude Desktop)
python zillow_mcp_server.py

# HTTP server mode (for remote access)
python zillow_mcp_server.py --http --port 8000

# Debug mode for more verbose logging
python zillow_mcp_server.py --debug
```

### Docker Deployment

You can also run the server using Docker:

```bash
# Build the Docker image
docker build -t zillow-mcp-server .

# Run with environment variables
docker run -p 8000:8000 -e ZILLOW_API_KEY=your_key_here zillow-mcp-server

# Or using an env file
docker run -p 8000:8000 --env-file .env zillow-mcp-server
```

## Usage with Claude Desktop

Add the Zillow MCP server to your Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zillow": {
      "command": "python",
      "args": ["/path/to/zillow_mcp_server.py"]
    }
  }
}
```

For remote HTTP server:

```json
{
  "mcpServers": {
    "zillow-remote": {
      "command": "npx",
      "args": ["mcp-remote", "https://your-mcp-server-url.com/sse"]
    }
  }
}
```

## Available Tools

### Search Properties

Search for properties based on various criteria:

```python
search_properties(
    location: str,
    type: str = "forSale",
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    beds_min: Optional[int] = None,
    beds_max: Optional[int] = None,
    baths_min: Optional[float] = None,
    baths_max: Optional[float] = None,
    home_types: Optional[List[str]] = None
)
```

Example usage in Claude:
```
Please search for properties in Seattle with prices between $500,000 and $800,000.
```

### Get Property Details

Get detailed information about a specific property:

```python
get_property_details(
    property_id: str = None,
    address: str = None
)
```

Example usage in Claude:
```
Can you get the details for the property with ID 12345?
```

### Get Zestimate

Get Zillow's estimated value for a property:

```python
get_zestimate(
    property_id: str = None,
    address: str = None
)
```

Example usage in Claude:
```
What's the Zestimate for 123 Main St, Seattle, WA?
```

### Get Market Trends

Get real estate market trends for a specific location:

```python
get_market_trends(
    location: str,
    metrics: List[str] = ["median_list_price", "median_sale_price", "median_days_on_market"],
    time_period: str = "1year"
)
```

Example usage in Claude:
```
What are the current real estate trends in Boston over the past year?
```

### Calculate Mortgage

Calculate mortgage payments and related costs:

```python
calculate_mortgage(
    home_price: int,
    down_payment: int = None,
    down_payment_percent: float = None,
    loan_term: int = 30,
    interest_rate: float = 6.5,
    annual_property_tax: int = None,
    annual_homeowners_insurance: int = None,
    monthly_hoa: int = 0,
    include_pmi: bool = True
)
```

Example usage in Claude:
```
Calculate the monthly mortgage payment for a $600,000 house with 20% down and a 6% interest rate.
```

### Check Health

Verify the Zillow API connection and get server status:

```python
check_health()
```

Example usage in Claude:
```
Please check if the Zillow API is currently responsive.
```

### Get Server Tools

Get a list of all available tools on this server:

```python
get_server_tools()
```

Example usage in Claude:
```
What tools are available in the Zillow MCP server?
```

## Available Resources

### Property Resource

Get property information as a formatted text resource:

```
zillow://property/{property_id}
```

### Market Trends Resource

Get market trends information as a formatted text resource:

```
zillow://market-trends/{location}
```

## Error Handling

The server implements robust error handling with:

- Automatic retries with exponential backoff
- Detailed error logging
- Rate limit handling
- Connection timeouts
- Graceful degradation

## Submitting to MCP.so

To submit this server to [MCP.so](https://mcp.so), follow these steps:

1. Host your code in a GitHub repository
2. Visit [MCP.so](https://mcp.so) and submit your server for inclusion
3. Provide the server configuration:

```json
{
  "mcpServers": {
    "zillow": {
      "command": "npx",
      "args": ["-y", "zillow-mcp-server"],
      "env": {
        "ZILLOW_API_KEY": "<YOUR_API_KEY>"
      }
    }
  }
}
```

## Technical Architecture

This MCP server is built using:

- **FastMCP**: A Pythonic framework for building Model Context Protocol servers
- **Requests**: For making HTTP requests to the Zillow Bridge API with connection pooling and retries
- **Backoff**: For implementing exponential backoff retry logic
- **python-dotenv**: For managing environment variables

The server provides both tools (interactive functions) and resources (static data) that Claude can access to provide real estate information to users.

## Limitations and Considerations

- Zillow's API has usage limits (typically 1,000 requests per day per dataset)
- Zillow's terms of service prohibit storing data locally; all requests must be dynamic
- You must properly attribute data to Zillow in the user interface
- The Bridge API format may change; refer to Zillow's documentation for updates

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for the Pythonic MCP implementation
- [Zillow](https://www.zillow.com) for providing real estate data APIs
- [Model Context Protocol](https://modelcontextprotocol.io) for the standard protocol specification