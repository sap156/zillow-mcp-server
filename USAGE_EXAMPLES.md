# Zillow MCP Server: Usage Examples

This document provides examples of how to use the Zillow MCP server with Claude and other MCP clients. These examples demonstrate the server's capabilities and how it can enhance real estate research and analysis workflows.

## Property Search Examples

### Basic Property Search

**User**: "Find me houses for sale in Austin, Texas."

**Claude** will use the `search_properties` tool:

```python
search_properties(
    location="Austin, Texas",
    type="forSale"
)
```

**Response**:
```
I found 2 properties for sale in Austin, Texas:

1. 123 Main St, Austin, Texas
   Price: $450,000
   3 beds, 2 baths, 1,800 sqft
   Zestimate: $455,000

2. 456 Oak Ave, Austin, Texas
   Price: $550,000
   4 beds, 2.5 baths, 2,200 sqft
   Zestimate: $553,000
```

### Advanced Property Search with Filters

**User**: "Show me condos for rent in Miami under $3,000 per month with at least 2 bedrooms and a pool."

**Claude** will use the `search_properties` tool with filters:

```python
search_properties(
    location="Miami, FL",
    type="forRent",
    max_price=3000,
    beds_min=2,
    home_types=["condo"]
)
```

**Response**:
## Property Details Examples

### Get Property Information by ID

**User**: "Can you tell me more about the Zillow property with ID 12345?"

**Claude** will use the `get_property_details` tool:

```python
get_property_details(property_id="12345")
```

**Response**:
```
Here are the details for the property at 123 Main St, New York, NY:

Price: $450,000
3 beds, 2 baths, 1,800 sqft
Built in 2005
Single Family home on 0.25 acres
Last sold in 2018 for $410,000

Features:
- Central Air
- Fireplace
- Hardwood Floors
- Garage

Schools:
- Lincoln Elementary (0.6 miles) - Rating: 8/10
- Washington Middle (1.2 miles) - Rating: 7/10

Neighborhood: Downtown
Walk Score: 85/100
Transit Score: 75/100

Zillow Link: https://www.zillow.com/homedetails/12345
```

### Get Property Information by Address

**User**: "What's the property value history for 123 Main St, New York, NY?"

**Claude** will use the `get_zestimate` tool:

```python
get_zestimate(address="123 Main St, New York, NY")
```

**Response**:
```
Zillow's estimated value (Zestimate) for 123 Main St, New York, NY:

Current Zestimate: $455,000
Value Range: $440,000 - $470,000
Monthly Rent Estimate: $2,500

Value Change:
- Last 30 days: +$5,000
- Last year: +$15,000

## Market Analysis Examples

### Local Market Trends

**User**: "What are the current real estate trends in Seattle? How has the market changed over the past year?"

**Claude** will use the `get_market_trends` tool:

```python
get_market_trends(
    location="Seattle, WA",
    metrics=["median_list_price", "median_sale_price", "median_days_on_market"],
    time_period="1year"
)
```

**Response**:
```
Seattle Real Estate Market Trends:

Current Market Overview:
- Median Listing Price: $450,000 (+3.2% year-over-year)
- Median Sale Price: $445,000 (+2.8% year-over-year)
- Median Days on Market: 32 days (-5 days year-over-year)

This indicates a moderately competitive market with rising prices and decreasing time to sell. The Seattle market has shown steady appreciation over the past year, with homes selling faster than they did a year ago.
```

### Comparative Market Analysis

**User**: "Compare the housing markets in Austin, TX and Nashville, TN."

**Claude** will use the `get_market_trends` tool multiple times to create a comparison:

```python
austin_trends = get_market_trends(location="Austin, TX")
nashville_trends = get_market_trends(location="Nashville, TN")
```

**Response**:
```
Comparing Austin and Nashville Housing Markets:

Austin, TX:
- Median Listing Price: $450,000 (+3.2% year-over-year)
- Median Sale Price: $445,000 (+2.8% year-over-year)
- Median Days on Market: 32 days (-5 days year-over-year)

Nashville, TN:
- Median Listing Price: $425,000 (+4.5% year-over-year)
- Median Sale Price: $420,000 (+3.7% year-over-year)
- Median Days on Market: 28 days (-3 days year-over-year)

## Mortgage Examples

### Basic Mortgage Calculation

**User**: "What would my monthly mortgage payment be for a $500,000 house with 20% down and a 6.5% interest rate?"

**Claude** will use the `calculate_mortgage` tool:

```python
calculate_mortgage(
    home_price=500000,
    down_payment_percent=20,
    interest_rate=6.5
)
```

**Response**:
```
Mortgage Calculation for a $500,000 home:

Loan Details:
- Down Payment: $100,000 (20%)
- Loan Amount: $400,000
- Term: 30 years
- Interest Rate: 6.5%

Monthly Payments:
- Principal & Interest: $2,528.27
- Property Tax (est.): $458.33
- Homeowners Insurance (est.): $145.83
- PMI: $0 (not required with 20% down)
- Total Monthly Payment: $3,132.43

Loan Summary:
- Total Interest Paid: $510,177.20
- Total Cost of Home: $1,127,675.48
```

### Advanced Mortgage Scenario

**User**: "Compare mortgage payments for a $600,000 house with 10% down vs. 20% down, with a 15-year vs. 30-year loan term, at current interest rates."

**Claude** will use the `calculate_mortgage` tool multiple times to create a comparison:

```python
scenario1 = calculate_mortgage(home_price=600000, down_payment_percent=10, loan_term=30, interest_rate=6.5)
scenario2 = calculate_mortgage(home_price=600000, down_payment_percent=20, loan_term=30, interest_rate=6.5)
scenario3 = calculate_mortgage(home_price=600000, down_payment_percent=10, loan_term=15, interest_rate=6.0)
scenario4 = calculate_mortgage(home_price=600000, down_payment_percent=20, loan_term=15, interest_rate=6.0)
```

**Response**:
```
Comparison of Mortgage Scenarios for a $600,000 home:

Scenario 1: 10% Down, 30-Year Term (6.5%)
- Down Payment: $60,000
- Monthly Payment: $4,230.67 (includes PMI)
- Total Interest: $699,531.06
- Total Cost: $1,521,952.81

Scenario 2: 20% Down, 30-Year Term (6.5%)
- Down Payment: $120,000
- Monthly Payment: $3,758.92 (no PMI)
- Total Interest: $612,212.52
- Total Cost: $1,473,213.38

Scenario 3: 10% Down, 15-Year Term (6.0%)
- Down Payment: $60,000
- Monthly Payment: $5,279.38 (includes PMI)
- Total Interest: $352,587.29
- Total Cost: $1,110,291.59

Scenario 4: 20% Down, 15-Year Term (6.0%)
- Down Payment: $120,000
- Monthly Payment: $4,641.48 (no PMI)
- Total Interest: $315,466.92
- Total Cost: $1,035,466.92

Analysis:
The 15-year term saves significantly on interest but requires higher monthly payments. The 20% down payment scenarios avoid PMI and reduce total interest paid. The most cost-effective option is Scenario 4 (20% down, 15-year term), while Scenario 2 (20% down, 30-year term) offers the lowest monthly payment while still avoiding PMI.
```

## Multi-Step Analysis Examples

### Home Buying Decision Support

**User**: "I'm relocating to Denver with a budget of $500,000-$700,000 for a 4-bedroom house. I need good schools and a reasonable commute to downtown. What neighborhoods should I consider, what can I expect to find, and what would my monthly costs look like?"

**Claude** would use multiple tools to provide a comprehensive analysis:

1. First, search for properties in Denver:
```python
properties = search_properties(
    location="Denver, CO",
    type="forSale",
    min_price=500000,
    max_price=700000,
    beds_min=4
)
```

2. Analyze market trends:
```python
trends = get_market_trends(location="Denver, CO")
```

3. Calculate mortgage scenarios:
```python
mortgage = calculate_mortgage(
    home_price=600000,  # Midpoint of budget
    down_payment_percent=20,
    interest_rate=6.5
)
```

4. Combine the information to provide a detailed recommendation that covers neighborhoods, property types, school ratings, commute considerations, and financial projections.

## Resource Usage Examples

### Property Resource

**User**: "Tell me everything you can about property with ID 12345."

**Claude** would access the property resource:

```
zillow://property/12345
```

This would return a formatted document with all the property details that Claude can then present to the user.

### Market Trends Resource

**User**: "What's happening in the Seattle real estate market right now?"

**Claude** would access the market trends resource:

```
zillow://market-trends/Seattle, WA
```

This would return a formatted document with market trends that Claude can present to the user.

### Server Tools Discovery

**User**: "What tools are available in the Zillow MCP server?"

**Claude** will use the `get_server_tools` tool:

```python
get_server_tools()
```

**Response**:
```
The Zillow MCP server provides the following tools:

1. search_properties
   - Search for properties on Zillow based on criteria
   - Parameters: location, type, price range, bedrooms, bathrooms, home types

2. get_property_details
   - Get detailed information about a property by ID or address
   - Parameters: property_id OR address

3. get_zestimate
   - Get Zillow's estimated value for a property
   - Parameters: property_id OR address

4. get_market_trends
   - Get real estate market trends for a specific location
   - Parameters: location, metrics, time_period

5. calculate_mortgage
   - Calculate mortgage payments and related costs
   - Parameters: home_price, down_payment, interest_rate, etc.

6. check_health
   - Check the health and status of the Zillow API connection

7. get_server_tools
   - Get a list of all available tools on this server

Available Resources:
- zillow://property/{property_id}
- zillow://market-trends/{location}
```

## Health Check Example

**User**: "Is the Zillow API working properly right now?"

**Claude** will use the `check_health` tool:

```python
check_health()
```

**Response**:
```
Zillow API Status Check:

✅ API is available and responsive
Response Time: 245.67 ms
API Version: 1.2.3
Last Updated: 2025-05-08T10:15:32Z

All systems are operational. You can proceed with your real estate queries.
```

These examples demonstrate the power and flexibility of the Zillow MCP server in providing real estate insights and analysis through Claude.
