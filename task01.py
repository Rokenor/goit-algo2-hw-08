import random
import time
from collections import OrderedDict

class LRUCache:
    '''Реализація LRU-кешу'''
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: tuple) -> int:
        '''Отримуємо значення з кешу за ключем'''
        if key not in self.cache:
            return -1
        else:
            self.cache.move_to_end(key)
            return self.cache[key]
        
    def put(self, key: tuple, value: int) -> None:
        '''Додатємо або оновлюємо пару ключ-значення в кеші'''
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def get_keys(self) -> list:
        '''Повертає список ключів у кеші'''
        return list(self.cache.keys())
    
    def delete(self, key: tuple) -> None:
        '''Видаляє пару ключ-значення з кешу'''
        if key in self.cache:
            del self.cache[key]

def range_sum_no_cache(array: list, left: int, right: int) -> int:
    '''Обчислює суму диапазону без кешування'''
    return sum(array[left : right + 1])

def update_no_cache(array: list, index: int, value: int) -> None:
    '''Оновлює значення в масиві без кешування'''
    array[index] = value

def range_sum_with_cache(array: list, left: int, right: int, cache: LRUCache) -> int:
    '''Обчислює суму диапазону з LRU-кешуванням'''
    key = (left, right)

    # Спроба отримати значення з кешу
    cached_value = cache.get(key)

    if cached_value != -1:
        # Значення знайдено в кеші
        return cached_value
    else:
        # Значення не знайдено в кеші, обчислюємо и зберігаємо суму
        actual_sum = sum(array[left : right + 1])
        cache.put(key, actual_sum)
        return actual_sum

def update_with_cache(array: list, index: int, value: int, cache: LRUCache) -> None:
    '''Оновлює значення в масиві з LRU-кешуванням'''
    # Оновлюємо сам масив
    array[index] = value

    # Інвалідуємо кеш
    keys_to_check = cache.get_keys()

    for key in keys_to_check:
        left, right = key
        # Якщо оновлений індекс знаходиться в діапазоні кешованого запиту, видаляємо його з кешу
        if left <= index <= right:
            cache.delete(key)

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    '''Генерує список запитів'''
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        # ~3% запитів — Update
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 # ~97% — Range
            if random.random() < p_hot:       # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:                             # 5% — випадкові діапазони
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries

def main():
    '''Головна функція для виконання порівняння кешованих і некешованих запитів'''
    # Параметри симуляції
    N = 100_000      # Розмір масиву
    Q = 50_000     # Кількість запитів
    K = 1_000     # Розмір кешу

    print(f"Симуляція доступу до даних...")
    print(f"Розмір масиву (N): {N:,}")
    print(f"Кількість запитів (Q): {Q:,}")
    print(f"Ємність LRU-кешу (K): {K:,}")
    print("-" * 30)

    # Генерація початкових даних
    # Створюємо один "майстер" масив
    master_array = [random.randint(1, 100) for _ in range(N)]
    # Генеруємо єдиний список запитів
    queries = make_queries(N, Q)

    print("Запуск тесту без кешу...")

    # Тест без кешу
    array_no_cache = master_array.copy()
    start_no_cache = time.perf_counter()

    for query in queries:
        q_type = query[0]
        if q_type == "Range":
            range_sum_no_cache(array_no_cache, query[1], query[2])
        else:
            update_no_cache(array_no_cache, query[1], query[2])

    end_no_cache = time.perf_counter()
    time_no_cache = end_no_cache - start_no_cache

    print("Запуск тесту з LRU-кешем...")

    # Тест з LRU-кешем
    array_with_cache = master_array.copy()
    lru_cache = LRUCache(capacity=K)
    start_cache = time.perf_counter()

    for query in queries:
        q_type = query[0]
        if q_type == "Range":
            range_sum_with_cache(array_with_cache, query[1], query[2], lru_cache)
        else:
            update_with_cache(array_with_cache, query[1], query[2], lru_cache)
    
    end_cache = time.perf_counter()
    time_with_cache = end_cache - start_cache

    # Виведення результатів
    print("\n" + "Результати тестування")

    print(f"Без кешу : {time_no_cache:>6.2f} c")
    
    if time_with_cache > 0:
        acceleration = time_no_cache / time_with_cache
        print(f"LRU-кеш : {time_with_cache:>6.2f} c  (прискорення ×{acceleration:.1f})")
    else:
        print(f"LRU-кеш : {time_with_cache:>6.2f} c")

if __name__ == "__main__":
    main()