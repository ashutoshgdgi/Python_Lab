words = ["cat", "apple", "dog", "banana", "pen", "mango"]

result = [word.upper() for word in words if len(word) > 3]

print("Result:", result)