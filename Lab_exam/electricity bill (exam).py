name = input("Enter consumer name: ")
units = int(input("Enter units consumed: "))

bill = 0

if units <= 100:
    bill = units * 2

elif units <= 200:
    bill = (100 * 2) + (units - 100) * 3

elif units <= 500:
    bill = (100 * 2) + (100 * 3) + (units - 200) * 5

else:
    bill = (100 * 2) + (100 * 3) + (300 * 5) + (units - 500) * 7

fixed_charge = 100

total = bill + fixed_charge

if total > 2000:
    surcharge = total * 0.05
else:
    surcharge = 0

final_bill = total + surcharge

print("\n========== ELECTRICITY BILL ==========")
print("Consumer Name     :", name)
print("Units Consumed    :", units)
print("Electricity Charge: ₹", bill)
print("Fixed Charge      : ₹", fixed_charge)
print("Bill Before Surcharge: ₹", total)
print("Surcharge (5%)    : ₹", surcharge)
print("--------------------------------------")
print("Total Bill        : ₹", final_bill)
print("======================================")