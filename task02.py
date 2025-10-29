import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    '''Реалізація лімітатора швидкості з використанням ковзного вікна'''
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        # Словник для зберігання історії запитів
        self.user_requests: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        '''Видаляє застарілі часові мітки з вікна користувача'''
        if user_id in self.user_requests:
            window = self.user_requests[user_id]
            # Розраховуємо початкову точку вікна
            window_start = current_time - self.window_size

            # Поки в черзі є елементи І найстаріший елемент (зліва)
            # знаходиться за межами вікна, видаляємо його
            while window and window[0] < window_start:
                window.popleft()

            # Якщо вікно спорожніло, видаляємо запис про користувача
            if not window:
                del self.user_requests[user_id]

    def can_send_message(self, user_id: str) -> bool:
        '''Перевіряє, чи може користувач відправити повідомлення ЗАРАЗ'''
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # Якщо запису про користувача немає, це його перший запит
        if user_id not in self.user_requests:
            return True
        
        # Перевіряємо, чи не перевищено ліміт
        return len(self.user_requests[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        '''Намагається записати нове повідомлення'''
        current_time = time.time()

        # Спочатку очищуємо вікно від старих записів
        self._cleanup_window(user_id, current_time)

        # Отримуємо вікно користувача
        window = self.user_requests.setdefault(user_id, deque())

        # Перевірка ліміту
        if len(window) < self.max_requests:
            # Ліміт не досягнуто, додаємо поточну часову мітку
            window.append(current_time)
            return True
        else:
            # Ліміт досягнуто, повідомлення відхилено
            return False

    def time_until_next_allowed(self, user_id: str) -> float:
        '''Розраховує час в секундах до наступного дозволеного повідомлення'''
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_requests:
            # Користувач не надсилав повідомлень (або вони застаріли)
            return 0.0
        
        window = self.user_requests[user_id]

        if len(window) < self.max_requests:
            # Ліміт не досягнуто, повідомлення можна відправити зараз
            return 0.0
        
        # Якщо ліміт досягнуто нам потрібно почекати, поки найстаріший запит вийде за межі вікна
        oldest_request_time = window[0]

        # Час, коли найстаріший запит вийде за межі вікна
        expiry_time = oldest_request_time + self.window_size

        # Час, що залишився до звільнення
        wait_time = expiry_time - current_time

        # Повертаємо 0.0, якщо час очікування негативний
        return max(0.0, wait_time)

# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
