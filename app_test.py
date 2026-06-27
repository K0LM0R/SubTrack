import json
import os
import tempfile
from app import app, load_db, save_db, get_user_data

# --- Допоміжна функція для створення тестового користувача ---
def setup_test_user():
    """Створює тимчасового користувача з тестовими підписками."""
    db = load_db()
    
    # Очищаємо тестового користувача, якщо він існує, щоб тести не заважали один одному
    if 'test_user' in db['users']:
        del db['users']['test_user']
    
    # Додаємо тестового користувача з двома підписками
    db['users']['test_user'] = {
        'password': 'hash',
        'theme': 'dark',
        'currency': '₴',
        'cards': [],
        'connectedServices': {},
        'syncLog': [],
        'subscriptions': [
            {"id": "1", "name": "Netflix", "price": 15.99, "billing": "monthly", "date": "2026-07-15", "category": "Стрімінг", "currency": "₴", "card": "", "note": ""},
            {"id": "2", "name": "Spotify", "price": 9.99, "billing": "monthly", "date": "2026-07-10", "category": "Музика", "currency": "₴", "card": "", "note": ""},
            {"id": "3", "name": "Amazon Prime", "price": 8.99, "billing": "yearly", "date": "2026-07-01", "category": "Стрімінг", "currency": "₴", "card": "", "note": ""}
        ]
    }
    save_db(db)
    return 'test_user'

# ============================================================
# ТЕСТ 1: Перевірка розрахунку суми за місяць
# ============================================================
def test_monthly_sum():
    print("\n🔍 Запуск тесту 1: Розрахунок суми за місяць...")
    username = setup_test_user()
    user_data = get_user_data(username)
    subs = user_data['subscriptions']
    
    # Логіка, яка має бути у вашому застосунку:
    # Якщо підписка щомісячна (monthly) - беремо її ціну.
    # Якщо річна (yearly) - ділимо на 12.
    expected_total = 15.99 + 9.99 + (8.99 / 12)
    expected_total = round(expected_total, 2)
    
    actual_total = 0
    for s in subs:
        if s['billing'] == 'monthly':
            actual_total += s['price']
        elif s['billing'] == 'yearly':
            actual_total += s['price'] / 12
    
    actual_total = round(actual_total, 2)
    
    assert actual_total == expected_total, f"❌ Помилка! Очікувалось {expected_total}, отримано {actual_total}"
    print(f"✅ Тест 1 пройдено! Сума за місяць = {actual_total}")

# ============================================================
# ТЕСТ 2: Перевірка пошуку найдорожчої підписки
# ============================================================
def test_most_expensive():
    print("\n🔍 Запуск тесту 2: Пошук найдорожчої підписки...")
    username = setup_test_user()
    user_data = get_user_data(username)
    subs = user_data['subscriptions']
    
    # Шукаємо підписку з максимальною щомісячною ціною
    most_expensive = max(subs, key=lambda x: x['price'])
    
    expected_name = "Netflix"
    expected_price = 15.99
    
    assert most_expensive['name'] == expected_name, f"❌ Помилка! Очікувалось {expected_name}, отримано {most_expensive['name']}"
    assert most_expensive['price'] == expected_price, f"❌ Помилка! Очікувалось {expected_price}, отримано {most_expensive['price']}"
    
    print(f"✅ Тест 2 пройдено! Найдорожча: {most_expensive['name']} ({most_expensive['price']})")

# ============================================================
# ТЕСТ 3: Перевірка обробки порожнього списку
# ============================================================
def test_empty_list():
    print("\n🔍 Запуск тесту 3: Робота з порожнім списком...")
    db = load_db()
    
    # Створюємо порожнього користувача
    if 'empty_user' in db['users']:
        del db['users']['empty_user']
    
    db['users']['empty_user'] = {
        'password': 'hash',
        'theme': 'dark',
        'currency': '₴',
        'cards': [],
        'connectedServices': {},
        'syncLog': [],
        'subscriptions': []
    }
    save_db(db)
    
    user_data = get_user_data('empty_user')
    subs = user_data['subscriptions']
    
    total = sum(s['price'] for s in subs)
    
    assert total == 0, f"❌ Помилка! Для порожнього списку очікувалось 0, отримано {total}"
    print(f"✅ Тест 3 пройдено! Порожній список повертає {total}")

# ============================================================
# ЗАПУСК ВСІХ ТЕСТІВ
# ============================================================
if __name__ == '__main__':
    print("=" * 40)
    print("🧪 ЗАПУСК АВТОМАТИЗОВАНИХ ТЕСТІВ ДЛЯ SUBTRACK")
    print("=" * 40)
    
    try:
        test_monthly_sum()
        test_most_expensive()
        test_empty_list()
        
        print("\n" + "=" * 40)
        print("🎉 ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
        print("=" * 40)
    except AssertionError as e:
        print("\n" + "=" * 40)
        print(f"❌ ТЕСТ НЕ ПРОЙДЕНО: {e}")
        print("=" * 40)
    except Exception as e:
        print("\n" + "=" * 40)
        print(f"❌ СТАЛАСЯ ПОМИЛКА: {e}")
        print("=" * 40)