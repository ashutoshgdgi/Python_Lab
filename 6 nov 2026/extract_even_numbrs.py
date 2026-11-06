numbers = [2, 4, 6, 8, 10, 12, 14]

even = [n for n in numbers if n % 2 == 0]
squares = [n**2 for n in even]
result = [n for n in squares if n > 100]

print("Even numbers:", even)
print("Squares:", squares)
print("Squares greater than 100:", result)