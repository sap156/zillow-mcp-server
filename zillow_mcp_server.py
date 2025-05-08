#!/usr/bin/env python3
"""
Zillow MCP Server

This server provides access to Zillow real estate data through the Model Context Protocol (MCP).
It connects to Zillow's Bridge API to retrieve property information, market trends, and more.
"""

import os
import json
import logging
import time
import backoff
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fastmcp import FastMCP, Context
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zillow-mcp")

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("Zillow-Data-Server")

# Get API key from environment variables
ZILLOW_API_KEY = os.getenv("ZILLOW_API_KEY")
ZILLOW_API_BASE_URL = "https://api.bridgeinteractive.com/v1"

# Set up a session with retries and timeouts
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Helper function to make API requests to Zillow Bridge API
@backoff.on_exception(backoff.expo, (requests.exceptions.RequestException, ValueError), max_tries=5)
def zillow_api_request(endpoint: str, params: Dict = None, method: str = "GET") -> Dict:
    """Make a request to the Zillow Bridge API with retries and error handling."""
    if not ZILLOW_API_KEY:
        raise ValueError("Zillow API key not found. Please set the ZILLOW_API_KEY environment variable.")
    
    headers = {
        "Authorization": f"Bearer {ZILLOW_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Zillow-MCP-Server/1.0"
    }
    
    url = f"{ZILLOW_API_BASE_URL}/{endpoint}"
    
    try:
        logger.info(f"Making {method} request to {endpoint}")
        
        if method.upper() == "GET":
            response = session.get(url, headers=headers, params=params, timeout=30)
        elif method.upper() == "POST":
            response = session.post(url, headers=headers, json=params, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Log response status
        logger.info(f"Response status code: {response.status_code}")
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return zillow_api_request(endpoint, params, method)
        
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        
        # Basic validation
        if not response_data:
            raise ValueError("Empty response from Zillow API")
            
        # Log success
        logger.info(f"Successfully received data from {endpoint}")
        
        return response_data
    except requests.exceptions.Timeout:
        logger.error(f"Request to {endpoint} timed out")
        raise ValueError("Zillow API request timed out. Please try again later.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        error_msg = f"Zillow API HTTP error: {e}"
        # Try to get more error details from response
        try:
            error_data = response.json()
            if 'error' in error_data:
                error_msg += f" - {error_data['error']}"
        except:
            pass
        raise ValueError(error_msg)
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise ValueError(f"Zillow API request failed: {str(e)}")

# Define MCP tools for Zillow data access

@mcp.tool()
def search_properties(
    location: str,
    type: str = "forSale",
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    beds_min: Optional[int] = None,
    beds_max: Optional[int] = None,
    baths_min: Optional[float] = None,
    baths_max: Optional[float] = None,
    home_types: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict:
    """
    Search for properties on Zillow based on criteria.
    
    Args:
        location: Address, city, ZIP code, or neighborhood
        type: Property listing type - "forSale", "forRent", or "sold"
        min_price: Minimum price in dollars
        max_price: Maximum price in dollars
        beds_min: Minimum number of bedrooms
        beds_max: Maximum number of bedrooms
        baths_min: Minimum number of bathrooms
        baths_max: Maximum number of bathrooms
        home_types: List of home types (e.g., ["house", "condo", "apartment"])
    
    Returns:
        Dictionary with property listings matching the criteria
    """
    if ctx:
        ctx.info(f"Searching for {type} properties in {location}")
    
    params = {
        "location": location,
        "type": type,
    }
    
    # Add optional parameters if provided
    if min_price is not None:
        params["price_min"] = min_price
    if max_price is not None:
        params["price_max"] = max_price
    if beds_min is not None:
        params["beds_min"] = beds_min
    if beds_max is not None:
        params["beds_max"] = beds_max
    if baths_min is not None:
        params["baths_min"] = baths_min
    if baths_max is not None:
        params["baths_max"] = baths_max
    if home_types is not None:
        params["home_types"] = home_types
    
    try:
        # Make the actual API call to Zillow Bridge API
        response = zillow_api_request("properties/search", params)
        
        # Process the response from the API
        if not response or 'properties' not in response:
            raise ValueError("No properties found or invalid API response")
            
        properties = response.get('properties', [])
        
        # Apply any additional filtering if needed
        if min_price is not None:
            properties = [p for p in properties if p.get('price', 0) >= min_price]
        if max_price is not None:
            properties = [p for p in properties if p.get('price', 0) <= max_price]
        if beds_min is not None:
            properties = [p for p in properties if p.get('bedrooms', 0) >= beds_min]
        if beds_max is not None:
            properties = [p for p in properties if p.get('bedrooms', 0) <= beds_max]
        if baths_min is not None:
            properties = [p for p in properties if p.get('bathrooms', 0) >= baths_min]
        if baths_max is not None:
            properties = [p for p in properties if p.get('bathrooms', 0) <= baths_max]
        if home_types is not None:
            properties = [p for p in properties if p.get('home_type', '').lower() in [t.lower() for t in home_types]]
        
        return {
            "success": True,
            "count": len(properties),
            "properties": properties,
            "searchCriteria": params,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "Zillow Data Server"
            }
        }
    except Exception as e:
        logger.error(f"Property search failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "searchCriteria": params
        }

@mcp.tool()
def get_property_details(property_id: str = None, address: str = None) -> Dict:
    """
    Get detailed information about a property by ID or address.
    
    Args:
        property_id: Zillow property ID (zpid)
        address: Full property address
    
    Returns:
        Detailed property information
    """
    if not property_id and not address:
        raise ValueError("Either property_id or address must be provided")
    
    params = {}
    if property_id:
        params["zpid"] = property_id
    else:
        params["address"] = address
    
    try:
        # Make the actual API call to Zillow Bridge API
        response = zillow_api_request("properties/details", params)
        
        # Process the response from the API
        if not response or 'property' not in response:
            raise ValueError("Property not found or invalid API response")
            
        property_data = response.get('property', {})
        
        return {
            "success": True,
            "property": property_data,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "Zillow Data Server"
            }
        }
    except Exception as e:
        logger.error(f"Property details lookup failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "searchCriteria": params
        }

@mcp.tool()
def get_zestimate(property_id: str = None, address: str = None) -> Dict:
    """
    Get Zillow's estimated value (Zestimate) for a property.
    
    Args:
        property_id: Zillow property ID (zpid)
        address: Full property address
    
    Returns:
        Zestimate information including current value and historical data
    """
    if not property_id and not address:
        raise ValueError("Either property_id or address must be provided")
    
    params = {}
    if property_id:
        params["zpid"] = property_id
    else:
        params["address"] = address
    
    try:
        # Make the actual API call to Zillow Bridge API
        response = zillow_api_request("zestimates", params)
        
        # Process the response from the API
        if not response or 'zestimate' not in response:
            raise ValueError("Zestimate not found or invalid API response")
            
        zestimate_data = response.get('zestimate', {})
        
        return {
            "success": True,
            "zestimate": zestimate_data,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "Zillow Data Server"
            }
        }
    except Exception as e:
        logger.error(f"Zestimate lookup failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "searchCriteria": params
        }

@mcp.tool()
def get_market_trends(
    location: str,
    metrics: List[str] = ["median_list_price", "median_sale_price", "median_days_on_market"],
    time_period: str = "1year"  # Options: "1month", "3months", "6months", "1year", "5years", "10years", "all"
) -> Dict:
    """
    Get real estate market trends for a specific location.
    
    Args:
        location: City, ZIP code, or neighborhood
        metrics: List of metrics to retrieve
        time_period: Time period for historical data
    
    Returns:
        Market trend data for the specified location and metrics
    """
    params = {
        "location": location,
        "metrics": metrics,
        "time_period": time_period
    }
    
    try:
        # Make the actual API call to Zillow Bridge API
        api_params = {
            "location": location,
            "metrics": metrics,
            "time_period": time_period
        }
        response = zillow_api_request("market/trends", api_params)
        
        # Process the response from the API
        if not response or 'trends' not in response:
            raise ValueError("Market trends not found or invalid API response")
            
        trend_data = response.get('trends', {})
        
        return {
            "success": True,
            "location": location,
            "trends": trend_data,
            "time_period": time_period,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "Zillow Data Server"
            }
        }
    except Exception as e:
        logger.error(f"Market trends lookup failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "searchCriteria": params
        }

@mcp.tool()
def calculate_mortgage(
    home_price: int,
    down_payment: int = None,
    down_payment_percent: float = None,
    loan_term: int = 30,  # Years
    interest_rate: float = 6.5,  # Percentage
    annual_property_tax: int = None,
    annual_homeowners_insurance: int = None,
    monthly_hoa: int = 0,
    include_pmi: bool = True
) -> Dict:
    """
    Calculate mortgage payments and related costs.
    
    Args:
        home_price: Price of the home in dollars
        down_payment: Down payment amount in dollars
        down_payment_percent: Down payment as a percentage of home price
        loan_term: Loan term in years
        interest_rate: Annual interest rate as a percentage
        annual_property_tax: Annual property tax in dollars
        annual_homeowners_insurance: Annual homeowners insurance in dollars
        monthly_hoa: Monthly HOA fees in dollars
        include_pmi: Whether to include PMI for down payments less than 20%
    
    Returns:
        Dictionary with mortgage payment details
    """
    # Calculate down payment if not provided
    if down_payment is None and down_payment_percent is None:
        down_payment_percent = 20.0
    
    if down_payment is None:
        down_payment = int(home_price * (down_payment_percent / 100))
    else:
        down_payment_percent = (down_payment / home_price) * 100
    
    # Calculate loan amount
    loan_amount = home_price - down_payment
    
    # Calculate monthly interest rate
    monthly_interest_rate = (interest_rate / 100) / 12
    
    # Calculate total number of payments
    total_payments = loan_term * 12
    
    # Calculate principal and interest payment
    if monthly_interest_rate > 0:
        monthly_principal_interest = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments) / ((1 + monthly_interest_rate) ** total_payments - 1)
    else:
        monthly_principal_interest = loan_amount / total_payments
    
    # Calculate PMI (Private Mortgage Insurance)
    monthly_pmi = 0
    if include_pmi and down_payment_percent < 20:
        # Typical PMI is around 0.5% to 1% of the loan amount annually
        monthly_pmi = (loan_amount * 0.007) / 12
    
    # Calculate property tax payment if provided
    monthly_property_tax = 0
    if annual_property_tax is not None:
        monthly_property_tax = annual_property_tax / 12
    else:
        # Estimate property tax if not provided (varies by location, using 1.1% as average)
        annual_property_tax = int(home_price * 0.011)
        monthly_property_tax = annual_property_tax / 12
    
    # Calculate homeowners insurance payment if provided
    monthly_homeowners_insurance = 0
    if annual_homeowners_insurance is not None:
        monthly_homeowners_insurance = annual_homeowners_insurance / 12
    else:
        # Estimate homeowners insurance if not provided
        annual_homeowners_insurance = int(home_price * 0.0035)
        monthly_homeowners_insurance = annual_homeowners_insurance / 12
    
    # Calculate total monthly payment
    monthly_payment = monthly_principal_interest + monthly_pmi + monthly_property_tax + monthly_homeowners_insurance + monthly_hoa
    
    # Calculate total cost over the life of the loan
    total_cost = (monthly_payment * total_payments) + down_payment
    
    return {
        "success": True,
        "mortgage_details": {
            "home_price": home_price,
            "down_payment": down_payment,
            "down_payment_percent": round(down_payment_percent, 2),
            "loan_amount": loan_amount,
            "loan_term_years": loan_term,
            "interest_rate": interest_rate,
            "monthly_payment": round(monthly_payment, 2),
            "monthly_principal_interest": round(monthly_principal_interest, 2),
            "monthly_property_tax": round(monthly_property_tax, 2),
            "monthly_homeowners_insurance": round(monthly_homeowners_insurance, 2),
            "monthly_hoa": monthly_hoa,
            "monthly_pmi": round(monthly_pmi, 2),
            "total_interest_paid": round((monthly_principal_interest * total_payments) - loan_amount, 2),
            "total_payments": round(monthly_payment * total_payments, 2),
            "total_cost": round(total_cost, 2)
        },
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "source": "Zillow Mortgage Calculator"
        }
    }

@mcp.tool()
def get_server_tools() -> Dict:
    """
    Get a list of all available tools on this server.
    
    Returns:
        Dictionary with information about all available tools
    """
    tools = [
        {
            "name": "search_properties",
            "description": "Search for properties on Zillow based on criteria",
            "parameters": {
                "location": "Address, city, ZIP code, or neighborhood",
                "type": "Property listing type - 'forSale', 'forRent', or 'sold'",
                "min_price": "Minimum price in dollars",
                "max_price": "Maximum price in dollars",
                "beds_min": "Minimum number of bedrooms",
                "beds_max": "Maximum number of bedrooms",
                "baths_min": "Minimum number of bathrooms",
                "baths_max": "Maximum number of bathrooms",
                "home_types": "List of home types (e.g., ['house', 'condo', 'apartment'])"
            }
        },
        {
            "name": "get_property_details",
            "description": "Get detailed information about a property by ID or address",
            "parameters": {
                "property_id": "Zillow property ID (zpid)",
                "address": "Full property address"
            }
        },
        {
            "name": "get_zestimate",
            "description": "Get Zillow's estimated value (Zestimate) for a property",
            "parameters": {
                "property_id": "Zillow property ID (zpid)",
                "address": "Full property address"
            }
        },
        {
            "name": "get_market_trends",
            "description": "Get real estate market trends for a specific location",
            "parameters": {
                "location": "City, ZIP code, or neighborhood",
                "metrics": "List of metrics to retrieve",
                "time_period": "Time period for historical data"
            }
        },
        {
            "name": "calculate_mortgage",
            "description": "Calculate mortgage payments and related costs",
            "parameters": {
                "home_price": "Price of the home in dollars",
                "down_payment": "Down payment amount in dollars",
                "down_payment_percent": "Down payment as a percentage of home price",
                "loan_term": "Loan term in years",
                "interest_rate": "Annual interest rate as a percentage",
                "annual_property_tax": "Annual property tax in dollars",
                "annual_homeowners_insurance": "Annual homeowners insurance in dollars",
                "monthly_hoa": "Monthly HOA fees in dollars",
                "include_pmi": "Whether to include PMI for down payments less than 20%"
            }
        },
        {
            "name": "check_health",
            "description": "Check the health and status of the Zillow API connection",
            "parameters": {}
        },
        {
            "name": "get_server_tools",
            "description": "Get a list of all available tools on this server",
            "parameters": {}
        }
    ]
    
    resources = [
        {
            "name": "zillow://property/{property_id}",
            "description": "Get property information as a formatted text resource",
            "parameters": {
                "property_id": "Zillow property ID (zpid)"
            }
        },
        {
            "name": "zillow://market-trends/{location}",
            "description": "Get market trends information as a formatted text resource",
            "parameters": {
                "location": "City, ZIP code, or neighborhood"
            }
        }
    ]
    
@mcp.tool()
def check_health() -> Dict:
    """
    Check the health and status of the Zillow API connection.
    
    Returns:
        Dictionary with health status information
    """
    start_time = datetime.now()
    status = {
        "success": False,
        "api_available": False,
        "response_time_ms": 0,
        "timestamp": start_time.isoformat(),
        "version": "1.0.0"
    }
    
    try:
        # Perform a lightweight API call to check connection
        response = zillow_api_request("health", method="GET")
        
        # Calculate response time
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000  # ms
        
        # Update status
        status.update({
            "success": True,
            "api_available": True,
            "response_time_ms": round(response_time, 2),
            "zillow_api_status": response.get("status", "OK"),
            "api_version": response.get("version", "unknown")
        })
    except Exception as e:
        # API call failed
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000  # ms
        
        # Update status with error info
        status.update({
            "success": False,
            "api_available": False,
            "response_time_ms": round(response_time, 2),
            "error": str(e)
        })
    
    return status

@mcp.resource("zillow://property/{property_id}")
def get_property_resource(property_id: str) -> str:
    """
    Get property information as a resource.
    
    Args:
        property_id: Zillow property ID (zpid)
    
    Returns:
        Property information as a formatted string
    """
    try:
        # Get property details directly from API
        params = {"zpid": property_id} if property_id else {"address": property_id}
        response = zillow_api_request("properties/details", params)
        
        if not response or not response.get('success', False):
            error = response.get('error', 'Unknown error')
            return f"Error retrieving property information: {error}"
        
        property_info = response.get('property', {})
        
        # Format property information as a string - handle potentially missing fields
        info = [f"# Property Details for {property_info.get('address', 'Unknown Address')}"]
        
        # Add basic property details with safety checks
        if 'price' in property_info:
            info.append(f"- **Price**: ${property_info['price']:,}")
        if 'zestimate' in property_info:
            info.append(f"- **Zestimate**: ${property_info['zestimate']:,}")
        if 'bedrooms' in property_info:
            info.append(f"- **Bedrooms**: {property_info['bedrooms']}")
        if 'bathrooms' in property_info:
            info.append(f"- **Bathrooms**: {property_info['bathrooms']}")
        if 'sqft' in property_info:
            info.append(f"- **Square Feet**: {property_info['sqft']:,}")
        if 'year_built' in property_info:
            info.append(f"- **Year Built**: {property_info['year_built']}")
        if 'lot_size' in property_info:
            info.append(f"- **Lot Size**: {property_info['lot_size']} acres")
        if 'home_type' in property_info:
            info.append(f"- **Home Type**: {property_info['home_type']}")
        if 'last_sold_date' in property_info and 'last_sold_price' in property_info:
            info.append(f"- **Last Sold**: {property_info['last_sold_date']} for ${property_info['last_sold_price']:,}")
        
        # Add features if available
        if 'features' in property_info and property_info['features']:
            info.extend(["", "## Features"])
            features_list = property_info.get('features', [])
            if features_list:
                info.append("- " + "\n- ".join(features_list))
        
        # Add schools if available
        if 'schools' in property_info and property_info['schools']:
            info.extend(["", "## Schools"])
            for school in property_info.get('schools', []):
                name = school.get('name', 'Unknown School')
                level = school.get('level', 'Unknown Level')
                rating = school.get('rating', 'N/A')
                distance = school.get('distance', 'Unknown')
                info.append(f"- **{name}** ({level}): Rating {rating}/10, {distance} miles away")
        
        # Add neighborhood info if available
        neighborhood_info = []
        if 'neighborhood' in property_info:
            neighborhood_info.append(f"- **Neighborhood**: {property_info['neighborhood']}")
        if 'walk_score' in property_info:
            neighborhood_info.append(f"- **Walk Score**: {property_info['walk_score']}/100")
        if 'transit_score' in property_info:
            neighborhood_info.append(f"- **Transit Score**: {property_info['transit_score']}/100")
        
        if neighborhood_info:
            info.extend(["", "## Neighborhood"])
            info.extend(neighborhood_info)
        
        # Add Zillow link if available
        if 'url' in property_info:
            info.extend(["", f"View on Zillow: {property_info['url']}"])
        
        return "\n".join(info)
    except Exception as e:
        logger.error(f"Property resource lookup failed: {e}")
        return f"Error: {str(e)}"

@mcp.resource("zillow://market-trends/{location}")
def get_market_trends_resource(location: str) -> str:
    """
    Get market trends information as a resource.
    
    Args:
        location: City, ZIP code, or neighborhood
    
    Returns:
        Market trends information as a formatted string
    """
    try:
        # Make direct API call to get market trends
        api_params = {
            "location": location,
            "metrics": ["median_list_price", "median_sale_price", "median_days_on_market"],
            "time_period": "1year"
        }
        response = zillow_api_request("market/trends", api_params)
        
        if not response or not response.get('success', False):
            error = response.get('error', 'Unknown error')
            return f"Error retrieving market trends: {error}"
        
        trends = response.get('trends', {})
        
        # Format trends information as a string - handle potentially missing data
        info = [
            f"# Real Estate Market Trends for {location}",
            "",
            "## Current Market Overview"
        ]
        
        # Add current metrics with safety checks
        if 'median_list_price' in trends and 'current' in trends['median_list_price'] and 'change_1year' in trends['median_list_price']:
            info.append(f"- **Median Listing Price**: ${trends['median_list_price']['current']:,} ({trends['median_list_price']['change_1year']:+.1f}% year-over-year)")
        
        if 'median_sale_price' in trends and 'current' in trends['median_sale_price'] and 'change_1year' in trends['median_sale_price']:
            info.append(f"- **Median Sale Price**: ${trends['median_sale_price']['current']:,} ({trends['median_sale_price']['change_1year']:+.1f}% year-over-year)")
        
        if 'median_days_on_market' in trends and 'current' in trends['median_days_on_market'] and 'change_1year' in trends['median_days_on_market']:
            info.append(f"- **Median Days on Market**: {trends['median_days_on_market']['current']} days ({trends['median_days_on_market']['change_1year']:+.0f} days year-over-year)")
        
        # Add historical section header if we have historical data
        has_historical = any('historical' in metric_data for metric_data in trends.values() if isinstance(metric_data, dict))
        if has_historical:
            info.append("")
            info.append("## Historical Trends (Last 12 Months)")
            
            # Add historical data for each metric
            for metric_name, metric_data in trends.items():
                if not isinstance(metric_data, dict) or 'historical' not in metric_data:
                    continue
                    
                if metric_name == "median_list_price":
                    display_name = "Median Listing Price"
                    prefix = "$"
                    suffix = ""
                elif metric_name == "median_sale_price":
                    display_name = "Median Sale Price"
                    prefix = "$"
                    suffix = ""
                else:  # median_days_on_market
                    display_name = "Median Days on Market"
                    prefix = ""
                    suffix = " days"
                
                info.append(f"\n### {display_name}")
                for point in metric_data.get("historical", []):
                    if 'date' in point and 'value' in point:
                        info.append(f"- {point['date']}: {prefix}{point['value']:,}{suffix}")
        
        return "\n".join(info)
    except Exception as e:
        logger.error(f"Market trends resource lookup failed: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Zillow MCP Server")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server instead of stdio")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Configure logging based on arguments
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print some info
    print("Starting Zillow MCP Server...")
    print(f"API Key Present: {'Yes' if ZILLOW_API_KEY else 'No - Please set ZILLOW_API_KEY environment variable'}")
    
    # Check API connectivity
    if ZILLOW_API_KEY:
        try:
            # Try a simple API call to verify connectivity
            zillow_api_request("health", method="GET")
            print("✅ Successfully connected to Zillow API")
        except Exception as e:
            print(f"⚠️ Warning: Could not connect to Zillow API: {e}")
    
    # Run the server with appropriate transport
    if args.http:
        print(f"Running as HTTP server on {args.host}:{args.port}")
        mcp.run(transport="streamable_http", host=args.host, port=args.port)
    else:
        print("Running as stdio server")
        mcp.run()
