numbers = [10, 15, 20, 25, 30, 35]

added = [n + 10 for n in numbers]
result = [n for n in added if n > 30]

print("After adding 10:", added)
print("Elements greater than 30:", result)