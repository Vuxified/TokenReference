from bot_tracker import BotTracker

   

if __name__ == "__main__":
    tracker = BotTracker()
    
    # Using real Solana USDC token address
    usdc_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
     # Test finding token in message
    test_message = "NEW CA DETECTED: KiJ6Yf3ehuGrGo1rEBnGpR5H6DXGmy7oEyXKXgypump TICKER: MOLOCH"
    found_ca = tracker.find_token(test_message)
    print(f"Found CA in message: {found_ca}")
    
    # Test adding bots with same CA
    tracker.add_bot("@gem_tools_calls", found_ca)
    tracker.add_bot("@solbixsignal", found_ca)
    
    # Test adding same bot with different CA
    tracker.add_bot("@gem_tools_calls", usdc_address)
    
    # Test adding multiple calls from same bot
    tracker.add_bot("@gem_tools_calls", found_ca)
    tracker.add_bot("@gem_tools_calls", found_ca)
    
    
    # Test check_requirements
    print("\nTesting check_requirements:")
    tracker.check_requirements("@gem_tools_calls", found_ca)
    tracker.check_requirements("@solbixsignal", found_ca)
    tracker.check_requirements("@gem_tools_calls", usdc_address)
    
    # Print final token calls
    print("\nFinal token calls:")
    print(tracker.token_calls)
