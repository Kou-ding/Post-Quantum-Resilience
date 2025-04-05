import time

# RSA Brute force
n = 42373973
counter = 0

# Brute force factorization
start_time = time.time()
for i in range(1,n):
    if n%i == 0:
        print(i)
        counter = counter + 1
        if counter == 3:
            break
end_time = time.time()

print(f"Time taken: {end_time - start_time} seconds")
