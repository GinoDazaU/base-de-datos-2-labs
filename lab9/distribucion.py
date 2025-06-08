import numpy as np

A = [(1, 20211), (2, 17346), (3, 17786), (4, 73485), (5, 85707), (6, 20117), (7, 52245), (8, 21126), (9, 23580)]
# A = [(1, 20211), (2, 17346), (3, 17786), (4, 73485)]
# A = [(1, 10), (2, 10), (3, 5), (4, 5)]

def calc(A):
    B = [([], [], [])]
    for i in A:
        size = len(B)
        for j in range(size):
            k1 = (B[j][0].copy(), B[j][1].copy(), B[j][2].copy())
            k2 = (B[j][0].copy(), B[j][1].copy(), B[j][2].copy())
            B[j][0].append(i)
            k1[1].append(i)
            k2[2].append(i)
            B.append(k1)
            B.append(k2)
    C = []
    for i in B:
        if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0:
            C.append(i)
    return C

min_val = -1
min_pos = -1
B = calc(A)
for pos, i in enumerate(B):
    sum1 = 0
    sum2 = 0
    sum3 = 0
    for j in i[0]:
        sum1 += j[1]
    for j in i[1]:
        sum2 += j[1]
    for j in i[2]:
        sum3 += j[1]
    std = np.std([sum1, sum2, sum3])
    if min_val == -1 or std < min_val:
        min_val = std
        min_pos = pos
print(B[min_pos])

for i, partition in enumerate(B[min_pos]):
    sum = 0
    for j in partition:
        sum += j[1]
    print(f"Partition {i}:\n\tattributes: {[j[0] for j in partition]}\n\tsum: {sum}")