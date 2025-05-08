from p2 import InvertedIndex

idx = InvertedIndex()
idx.build_from_db()

def AND(list1, list2):
    # Implementar la intersección de dos listas O(n +m)
    pass

def OR(list1, list2):
    # Implementar la unión de dos listas O(n +m)
    pass

def AND_NOT(list1, list2):
    # Implementar la diferencia de dos listas O(n +m)
    pass

# Prueba 1
result = AND(idx.L("sostenibilidad"), AND(idx.L("ambiente"), idx.L("renovables")))
print("sostenibilidad AND ambiente AND renovable: ", idx.showDocuments(result))

# Prueba 2
result = AND(idx.L("tecnología"), OR(idx.L("banca"), idx.L("finanzas")))
print("tecnología AND (banca OR finanzas): ", idx.showDocuments(result))

# Prueba 3
result = AND_NOT(idx.L("economía"), idx.L("inflación"))
print("economía AND-NOT inflación: " , idx.showDocuments(result))