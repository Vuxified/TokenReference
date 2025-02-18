import re

# Example sell messages
sell_message_1 = """
🔴 [SELL Hakimi](https://solscan.io/tx/4p3z5ewvMH4mxYkQokj95GV6pfACXU5Qr6PcwXfbDNhLimLP3kUxCuuZV2cqKc8tKmrZVbNCSHNSpvwaTi1LTsGT) on RAYDIUM
[🔹](https://solscan.io/account/JDd3hy3gQn2V982mi1zqhNqUw1GfV2UL6g76STojCJPN) **Kev**

🔹[**Kev**](https://solscan.io/account/JDd3hy3gQn2V982mi1zqhNqUw1GfV2UL6g76STojCJPN) swapped **20,068,786.77** ($243.28) [**Hakimi**](https://solscan.io/token/95vyUqpkqx2GEnAaXbUZRBGmmfsmhTsh8AuF6UeHpump) for **1.24** [**SOL**](https://solscan.io/token/So11111111111111111111111111111111111111112) @$0.0000121
➖Sold: 100%
📈PnL: **+3.39** SOL (+96.79%)

🔗 **#Hakimi** | **MC**: $12.12K | **Seen**: 34m: [BE](https://birdeye.so/token/95vyUqpkqx2GEnAaXbUZRBGmmfsmhTsh8AuF6UeHpump?chain=solana) | [DS](https://dexscreener.com/solana/95vyUqpkqx2GEnAaXbUZRBGmmfsmhTsh8AuF6UeHpump) | [PH](https://photon-sol.tinyastro.io/en/r/@RayBot/95vyUqpkqx2GEnAaXbUZRBGmmfsmhTsh8AuF6UeHpump) | [Bullx](https://neo.bullx.io/terminal?chainId=1399811149&address=95vyUqpkqx2GEnAaXbUZRBGmmfsmhTsh8AuF6UeHpump&r=IXFHAMJ1FN9) | [GMGN](https://gmgn.ai/sol/token/qOlUmSn7_95vyUqpkqx2GEnAaXbUZRBGmmfsmhTsh8AuF6UeHpump) | [AXI](https://axiom.trade/t/95vyUqpkqx2GEnAaXbUZRBGmmfsmhTsh8AuF6UeHpump/@raybot) | [👥INFO](https://t.me/ray_obsidian_bot?start=t__95vyUqpkqx2GEnAaXbUZRBGmmfsmhTsh8AuF6UeHpump)
`95vyUqpkqx2GEnAaXbUZRBGmmfsmhTsh8AuF6UeHpump`
"""

sell_message_2 = """
🔴 [SELL Donald ](https://solscan.io/tx/4595cPURVCMRGzrEbLN9xvo7xTq7naf6eQCspVKJoBnzRTURL2oPQL4QLuodq97HGRSJCBrfGCGzEDMc6ssKBweW) on RAYDIUM
[🔹](https://solscan.io/account/JDd3hy3gQn2V982mi1zqhNqUw1GfV2UL6g76STojCJPN) **Kev**

🔹[**Kev**](https://solscan.io/account/JDd3hy3gQn2V982mi1zqhNqUw1GfV2UL6g76STojCJPN) swapped **38,865,570.8** ($1,823.24) [**Donald **](https://solscan.io/token/6ZgGK4ykLG8PsMY56UPngvgWoqBBSZLA3ixrXbx3pump) for **9.3** [**SOL**](https://solscan.io/token/So11111111111111111111111111111111111111112) @$0.0000469
➖Sold: 100%
📉PnL: **-0.7** SOL (-6.98%)

🔗 **#Donald**** ** | **MC**: $46.76K | **Seen**: 30+d: [BE](https://birdeye.so/token/6ZgGK4ykLG8PsMY56UPngvgWoqBBSZLA3ixrXbx3pump?chain=solana) | [DS](https://dexscreener.com/solana/6ZgGK4ykLG8PsMY56UPngvgWoqBBSZLA3ixrXbx3pump) | [PH](https://photon-sol.tinyastro.io/en/r/@RayBot/6ZgGK4ykLG8PsMY56UPngvgWoqBBSZLA3ixrXbx3pump) | [Bullx](https://neo.bullx.io/terminal?chainId=1399811149&address=6ZgGK4ykLG8PsMY56UPngvgWoqBBSZLA3ixrXbx3pump&r=IXFHAMJ1FN9) | [GMGN](https://gmgn.ai/sol/token/qOlUmSn7_6ZgGK4ykLG8PsMY56UPngvgWoqBBSZLA3ixrXbx3pump) | [AXI](https://axiom.trade/t/6ZgGK4ykLG8PsMY56UPngvgWoqBBSZLA3ixrXbx3pump/@raybot) | [👥INFO](https://t.me/ray_obsidian_bot?start=t__6ZgGK4ykLG8PsMY56UPngvgWoqBBSZLA3ixrXbx3pump)
`6ZgGK4ykLG8PsMY56UPngvgWoqBBSZLA3ixrXbx3pump`
"""

# Function to extract information
def extract_info(message):
    token_name = re.search(r'\[SELL ([^\]]+)\]', message).group(1)
    wallet_name = re.search(r"🔹\[\*\*(.*?)\*\*\]", message).group(1)    
    marketcap_pattern = re.search(r"\*\*MC\*\*:\s*(\$\d+\.?\d*[KMB]?)", message).group(1)
    solana_sold_pattern = re.search(r"for\s+\*\*([\d,]+\.\d+)\*\*\s+\[\*\*SOL\*\*", message).group(1)
    sold_percentage_pattern = re.search(r"➖Sold:\s*(\d+%)?", message).group(1)
    pnl_result = re.search(r"""
        PnL:.*?          # Match 'PnL:' and any characters (non-greedy)
        \*\*([+-]?\d+\.\d+)\*\*  # Capture the PnL value (e.g., +3.39 or -0.7)
        \s+SOL.*?        # Match 'SOL' and any characters (non-greedy)
        \(([+-]?\d+\.\d+%)\)  # Capture the PnL percentage (e.g., +96.79% or -6.98%)
    """, message, re.VERBOSE)
    pnl_value = pnl_result.group(1)
    pnl_percentage = pnl_result.group(2)

    
    print(f"Wallet Name: {wallet_name}")
    print(f"Token Name: {token_name}")
    print(f"Market Cap: {marketcap_pattern}")
    print(f"SOL Recieved: {solana_sold_pattern}")
    print(f"Amount Sold Precent: {sold_percentage_pattern}")
    print(f"PNL: {pnl_value}%, PNL Percentage: {pnl_percentage}")
    print("-" * 50)  
# Extract and print information
info_1 = extract_info(sell_message_1)
info_2 = extract_info(sell_message_2)

print("Message 1:", info_1)
print("Message 2:", info_2)