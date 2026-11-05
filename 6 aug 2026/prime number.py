number=29
is_prime=True
if number<=1:
    is_prime=False
else:
    for i in range(2,number):
        if number%i==0:
            is_prime=False
            break
print("Prime" if is_prime else "Not Prime")