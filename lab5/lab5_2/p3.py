from p2 import InvertedIndex

idx = InvertedIndex()
idx.build_from_db()

def AND(list1, list2):
    # Implementar la intersección de dos listas O(n +m)
    res = []
    p1 = 0
    p2 = 0
    while p1 < len(list1) and p2 < len(list2):
        e1 = list1[p1]
        e2 = list2[p2]
        if e1[0] == e2[0]:
            res.append(e1)
            p1 += 1
            p2 += 1
        elif e1[0] > e2[0]:
            p2 += 1
        else:
            p1 += 1
    return res
        

def OR(list1, list2):
    # Implementar la unión de dos listas O(n +m)
    res = []
    p1 = 0
    p2 = 0
    while p1 < len(list1) and p2 < len(list2):
        e1 = list1[p1]
        e2 = list2[p2]
        if e1[0] == e2[0]:
            p1 += 1
            p2 += 1
        elif e1[0] > e2[0]:
            res.append(e2)
            p2 += 1
        else:
            res.append(e1)
            p1 += 1
    while p1 < len(list1):
        e1 = list1[p1]
        res.append(e1)
    while p2 < len(list2):
        e2 = list2[p2]
        res.append(e2)
    return res

def AND_NOT(list1, list2):
    # Implementar la diferencia de dos listas O(n +m)
    res = []
    p1 = 0
    p2 = 0
    while p1 < len(list1) and p2 < len(list2):
        e1 = list1[p1]
        e2 = list2[p2]
        if e1[0] == e2[0]:
            p1 += 1
            p2 += 1
        elif e1[0] > e2[0]:
            p2 += 1
        else:
            res.append(e1)
            p1 += 1
    while p1 < len(list1):
        e1 = list1[p1]
        res.append(e1)

# Prueba 1
result = AND(idx.L("sostenibilidad"), AND(idx.L("ambiente"), idx.L("renovables")))
print("sostenibilidad AND ambiente AND renovable: ", idx.showDocuments(result))

# Prueba 2
result = AND(idx.L("tecnología"), OR(idx.L("banca"), idx.L("finanzas")))
print("tecnología AND (banca OR finanzas): ", idx.showDocuments(result))

# Prueba 3
result = AND_NOT(idx.L("economía"), idx.L("inflación"))
print("economía AND-NOT inflación: " , idx.showDocuments(result))