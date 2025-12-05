import redis

# Kết nối Redis
r = redis.from_url("redis://localhost:6379/0")

# Lấy độ dài queue
queue_length = r.llen("chat_queue")
print("Số tin nhắn trong queue:", queue_length)

# Lấy danh sách tin nhắn (tối đa 10)
messages = r.lrange("chat_queue", 0, 9)
for i, msg in enumerate(messages, 1):
    print(f"{i}: {msg.decode()}")
