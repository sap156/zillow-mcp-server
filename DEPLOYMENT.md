# Zillow MCP Server Deployment Guide

This guide provides detailed instructions for deploying and configuring the Zillow MCP server in various environments.

## Prerequisites

Before deploying the Zillow MCP server, you need:

1. **Zillow Bridge API Access**: Request an API key by emailing api@bridgeinteractive.com
2. **Python 3.8+**: The server requires Python 3.8 or higher
3. **Dependencies**: Install required packages with `pip install -r requirements.txt`

## Local Deployment

### Method 1: Direct Python Execution

This is the simplest method for local development and testing.

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Zillow API key:
   ```
   ZILLOW_API_KEY=your_zillow_api_key_here
   ```

3. Run the server:
   ```bash
   # Standard stdio mode (for Claude Desktop)
   python zillow_mcp_server.py
   
   # HTTP server mode (for remote access)
   python zillow_mcp_server.py --http --port 8000
   
   # Debug mode for more verbose logging
   python zillow_mcp_server.py --debug
   ```

### Method 2: Using FastMCP's Install Command

FastMCP provides a convenient way to install your server for use with Claude Desktop:

1. Install FastMCP globally:
   ```bash
   pip install fastmcp
   ```

2. Use the `install` command to set up your server:
   ```bash
   fastmcp install zillow_mcp_server.py --name "Zillow Real Estate Data" -v ZILLOW_API_KEY=your_api_key_here
   ```

This will create an isolated environment and configure Claude Desktop to use it.

## Docker Deployment

For containerized deployment using Docker:

1. Build the Docker image:
   ```bash
   # Build without API key (will need to provide it at runtime)
   docker build -t zillow-mcp-server .
   
   # Or build with API key included in image (not recommended for public images)
   docker build -t zillow-mcp-server --build-arg ZILLOW_API_KEY=your_key_here .
   ```

2. Run the container:
   ```bash
   # If API key was provided at build time
   docker run -p 8000:8000 zillow-mcp-server
   
   # If API key needs to be provided at runtime
   docker run -p 8000:8000 -e ZILLOW_API_KEY=your_key_here zillow-mcp-server
   
   # Or using an env file
   docker run -p 8000:8000 --env-file .env zillow-mcp-server
   
   # To run in stdio mode instead of HTTP mode
   docker run -it --rm -e ZILLOW_API_KEY=your_key_here zillow-mcp-server --
   ```

3. Health check:
   ```bash
   curl http://localhost:8000/health
   ```

## Cloud Deployment

### Method 1: Deploying to Cloud Run (Google Cloud)

1. Build and push the Docker image:
   ```bash
   # Tag the image for Google Container Registry
   docker tag zillow-mcp-server gcr.io/[PROJECT-ID]/zillow-mcp-server
   
   # Push to GCR
   docker push gcr.io/[PROJECT-ID]/zillow-mcp-server
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy zillow-mcp --image gcr.io/[PROJECT-ID]/zillow-mcp-server --platform managed --set-env-vars ZILLOW_API_KEY=your_key_here
   ```

### Method 2: AWS Elastic Beanstalk

1. Create a `Procfile` in your project directory:
   ```
   web: python zillow_mcp_server.py --http --host 0.0.0.0 --port $PORT
   ```

2. Install AWS EB CLI:
   ```bash
   pip install awsebcli
   ```

3. Initialize and deploy:
   ```bash
   eb init
   eb create zillow-mcp-environment
   ```

4. Set environment variables:
   ```bash
   eb setenv ZILLOW_API_KEY=your_key_here
   ```


## Connecting to the Server

### Claude Desktop

Edit the Claude Desktop configuration file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

#### For Local Server:
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

#### For Remote Server:
```json
{
  "mcpServers": {
    "zillow-remote": {
      "command": "npx",
      "args": ["mcp-remote", "https://your-mcp-server.example.com/sse"]
    }
  }
}
```

## Security Best Practices

1. **API Key Security**:
   - Store your API key in environment variables or secure vaults
   - Never commit API keys to version control
   - Rotate keys periodically

2. **Transport Security**:
   - Always use HTTPS for remote deployments
   - Implement authentication for remote deployments
   - Use OAuth 2.0 for MCP client authentication

3. **Input Validation**:
   - The server implements input validation, but additional validation is recommended
   - Consider implementing rate limiting and request throttling

4. **Logging and Monitoring**:
   - Enable detailed logging in production
   - Set up monitoring to detect unusual patterns
   - Configure alerts for high error rates or API failures

## Troubleshooting

### Common Issues and Solutions

1. **API Connection Errors**:
   - Error: `Zillow API HTTP error: 401`
     - Solution: Check that your API key is valid and correctly set in the environment
   - Error: `Zillow API HTTP error: 429`
     - Solution: You've exceeded rate limits. The server implements backoff, but you may need to reduce request frequency

2. **Server Not Starting**:
   - Error: `ModuleNotFoundError: No module named 'fastmcp'`
     - Solution: Run `pip install -r requirements.txt` to install dependencies
   - Error: `Address already in use`
     - Solution: Change the port with `--port 8001` or stop the process using the current port

3. **Client Connection Issues**:
   - Error: `No session ID found`
     - Solution: Ensure the server is running and the path in client configuration is correct
   - Error: `Connection refused`
     - Solution: Check the host and port settings and any firewall configurations

### Checking Server Status

Test if the server is running and API is accessible:

1. For HTTP mode:
   ```bash
   curl http://localhost:8000/health
   ```

2. Using the health check tool:
   ```
   # In Claude:
   Please call the check_health tool to verify the Zillow API connection.
   ```

## Performance Optimization

For high-traffic deployments:

1. **Connection Pooling**: The server already uses connection pooling for HTTP requests

2. **Request Caching**: Consider implementing a caching layer to reduce API calls:
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def cached_api_request(endpoint, param_key, param_value):
       # Convert mutable params to immutable for caching
       return zillow_api_request(endpoint, {param_key: param_value})
   ```

3. **Horizontal Scaling**: For HTTP mode, deploy multiple instances behind a load balancer

## Support and Community

If you encounter issues or have questions:

1. Open an issue on the GitHub repository
2. Join the [MCP Discord community](https://discord.gg/modelcontextprotocol)
3. For Zillow API issues, contact support at api@bridgeinteractive.com
