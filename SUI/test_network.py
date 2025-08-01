#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности выбора сети
"""

import utils
import os
from dotenv import load_dotenv

load_dotenv()

def test_network_selection():
    print("Тестирование выбора сети...")
    print("=" * 50)
    
    # Проверяем текущую сеть
    current_network = os.getenv("SUI_NETWORK", "не выбрана")
    print(f"Текущая сеть: {current_network}")
    
    # Получаем RPC URL
    rpc_url = utils.get_network_rpc_url()
    print(f"RPC URL: {rpc_url}")
    
    # Тестируем смену сети
    print("\nТестирование смены сети...")
    new_network = utils.select_network()
    print(f"Выбрана сеть: {new_network}")
    
    # Обновляем в .env
    utils.set_key(".env", "SUI_NETWORK", new_network)
    print(f"Сеть сохранена в .env: {new_network}")
    
    # Проверяем новый RPC URL
    new_rpc_url = utils.get_network_rpc_url()
    print(f"Новый RPC URL: {new_rpc_url}")

if __name__ == "__main__":
    test_network_selection() 