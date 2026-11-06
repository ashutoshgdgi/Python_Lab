numbers = [2, 3, 4, 5, 6, 7, 9, 12, 15]

result = [n**2 for n in numbers if n % 2 == 0 or n % 3 == 0]

print("Result:", result)