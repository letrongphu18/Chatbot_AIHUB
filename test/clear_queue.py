import redis

# Kết nối Redis
r = redis.from_url("redis://localhost:6379/0")

# Xóa queue chat_queue
r.delete("chat_queue")
print("✅ Đã xóa toàn bộ tin nhắn trong chat_queue")
