l = [
    [3], #0
    [3], #1
    [3], #2
    [1], #3
    [1], #4
    [0], #5
    [0], #6
    [0], #7
    [2], #8
]

def findN(id, index, n):
    if (l[index][0] != id):
        return n
    else:
        return findN(id, index + 1, n + 1)

l2 = []
n = findN(0, 5, 0)
print(n)
print(l[5])
print(l[5 + n - 1])
print(str(list(range(5, 5 + findN(0, 5, 0) - 1))))
for i in range(5, 5 + findN(0, 5, 0)):
    l2.append(l[i])

print(l2)