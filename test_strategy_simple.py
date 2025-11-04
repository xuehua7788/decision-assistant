#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

API_URL = "http://127.0.0.1:8000"

print("="*60)
print("Test: Evaluate Strategy")
print("="*60)

strategy_id = "TSLA_20251102_193836_lynch"

try:
    response = requests.post(
        f"{API_URL}/api/strategy/evaluate",
        json={"strategy_id": strategy_id},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            eval_data = result['evaluation']
            print(f"\nStrategy ID: {eval_data['strategy_id']}")
            print(f"Symbol: {eval_data['symbol']}")
            print(f"Buy Price: ${eval_data['backtest']['strategy_buy_price']}")
            print(f"Current Price: ${eval_data['backtest']['current_real_price']}")
            print(f"Strategy Return: {eval_data['backtest']['strategy_return']}%")
            print(f"Actual Return: {eval_data['backtest']['actual_return']}%")
            print(f"Outperformance: {eval_data['backtest']['outperformance']}%")
            print(f"\nConclusion: {eval_data['conclusion']}")
        else:
            print(f"Error: {result.get('message')}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()


