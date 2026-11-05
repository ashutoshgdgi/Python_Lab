t1 = (10, 20, 30, 40)
t2 = (20, 40, 50, 60)

common = tuple(set(t1) & set(t2))

print("Common elements:", common)