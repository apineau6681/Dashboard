import requests

api_key = '4d11109e3520d4b0570eaf21c78a7adb'


# The Graph endpoint with your API key and subgraph ID
UNISWAP_V3_SUBGRAPH_URL = f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/HUZDsRpEVP2AvzDCyzDHtdc64dyDxx8FQjzsmqSg4H3B"

def query_uniswap_v3_graphql(query):
    try:
        response = requests.post(
            UNISWAP_V3_SUBGRAPH_URL,
            json={'query': query}
        )
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def get_pool_data(token0_address, token1_address):
    # Define the GraphQL query for fetching pool data
    query = f"""
    {{
      pools(first: 1, where: {{token0: "{token0_address}", token1: "{token1_address}"}}) {{
        id
        token0 {{
          id
          symbol
        }}
        token1 {{
          id
          symbol
        }}
        liquidity
        sqrtPrice
        feeTier
        ticks(first: 1) {{
          id
          tickIdx
          liquidityGross
          liquidityNet
          feeGrowthOutside0X128
          feeGrowthOutside1X128
        }}
      }}
    }}
    """
    
    data = query_uniswap_v3_graphql(query)
    
    pools = data.get('data', {}).get('pools', [])
    if not pools:
        print("No pool found for the given token addresses.")
        return
    
    pool = pools[0]
    pool_id = pool['id']
    
    print(f"Pool ID: {pool_id}")
    print(f"Token0: {pool['token0']['symbol']} ({pool['token0']['id']})")
    print(f"Token1: {pool['token1']['symbol']} ({pool['token1']['id']})")
    print(f"Liquidity: {pool['liquidity']}")
    print(f"SqrtPrice: {pool['sqrtPrice']}")
    print(f"Fee Tier: {pool['feeTier']}")
    
    # Define the GraphQL query for recent swaps
    swaps_query = f"""
    {{
      swaps(first: 5, where: {{pool: "{pool_id}"}}) {{
        id
        amount0In
        amount1In
        amount0Out
        amount1Out
        timestamp
      }}
    }}
    """
    
    swap_data = query_uniswap_v3_graphql(swaps_query)
    
    swaps = swap_data.get('data', {}).get('swaps', [])
    if not swaps:
        print("No swaps found for this pool.")
        return
    
    print("\nRecent Swaps:")
    for swap in swaps:
        print(f"Swap ID: {swap['id']}")
        print(f"Amount0 In: {swap['amount0In']}")
        print(f"Amount1 In: {swap['amount1In']}")
        print(f"Amount0 Out: {swap['amount0Out']}")
        print(f"Amount1 Out: {swap['amount1Out']}")
        print(f"Timestamp: {swap['timestamp']}")
        print("-" * 20)

if __name__ == '__main__':
    # Replace with actual token addresses
    IXS_token_address = '0x73d7c860998ca3c01ce8c808f5577d94d545d1b4'
    USDT_token_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
    
    get_pool_data(IXS_token_address, USDT_token_address)


# 
