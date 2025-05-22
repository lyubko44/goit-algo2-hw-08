import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        # Dictionary to store user message timestamps using deque
        self.user_messages: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Remove messages that are outside the current time window."""
        if user_id not in self.user_messages:
            return

        # Remove messages older than window_size
        while (self.user_messages[user_id] and 
               current_time - self.user_messages[user_id][0] >= self.window_size):
            self.user_messages[user_id].popleft()

        # If no messages left, remove the user from the dictionary
        if not self.user_messages[user_id]:
            del self.user_messages[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """Check if a user can send a message."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # If user has no messages or messages count is less than max_requests
        if (user_id not in self.user_messages or 
            len(self.user_messages[user_id]) < self.max_requests):
            return True

        # Check if enough time has passed since the oldest message
        oldest_message_time = self.user_messages[user_id][0]
        return (current_time - oldest_message_time) >= self.window_size

    def record_message(self, user_id: str) -> bool:
        """Record a message attempt and return whether it was allowed."""
        if not self.can_send_message(user_id):
            return False

        current_time = time.time()
        
        # Initialize deque for new users
        if user_id not in self.user_messages:
            self.user_messages[user_id] = deque()
            
        self.user_messages[user_id].append(current_time)
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        """Calculate time until the next message is allowed."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_messages or len(self.user_messages[user_id]) < self.max_requests:
            return 0.0

        # Calculate time until the oldest message exits the window
        oldest_message_time = self.user_messages[user_id][0]
        time_to_wait = (oldest_message_time + self.window_size) - current_time
        return max(0.0, time_to_wait)

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