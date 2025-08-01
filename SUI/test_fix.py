#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправления проблемы с повторным запросом сети
"""

import utils
import os
from dotenv import load_dotenv

load_dotenv()

def test_network_persistence():
    print("Тестирование исправления проблемы с сетью...")
    print("=" * 50)
    
    # Первый вызов - должен запросить сеть только если её нет в .env
    print("1. Первый вызов get_network_rpc_url():")
    rpc_url1 = utils.get_network_rpc_url()
    print(f"   RPC URL: {rpc_url1}")
    
    # Второй вызов - должен использовать сохраненную сеть
    print("\n2. Второй вызов get_network_rpc_url():")
    rpc_url2 = utils.get_network_rpc_url()
    print(f"   RPC URL: {rpc_url2}")
    
    # Третий вызов - должен использовать сохраненную сеть
    print("\n3. Третий вызов get_network_rpc_url():")
    rpc_url3 = utils.get_network_rpc_url()
    print(f"   RPC URL: {rpc_url3}")
    
    # Проверяем, что все URL одинаковые
    if rpc_url1 == rpc_url2 == rpc_url3:
        print("\n✅ УСПЕХ: Все вызовы вернули одинаковый URL!")
    else:
        print("\n❌ ОШИБКА: URL различаются!")
    
    # Тестируем смену сети
    print("\n4. Тестирование смены сети:")
    new_network = utils.change_network()
    print(f"   Новая сеть: {new_network}")
    
    # Проверяем новый URL
    print("\n5. Проверка нового URL после смены сети:")
    new_rpc_url = utils.get_network_rpc_url()
    print(f"   Новый RPC URL: {new_rpc_url}")

if __name__ == "__main__":
    test_network_persistence() 