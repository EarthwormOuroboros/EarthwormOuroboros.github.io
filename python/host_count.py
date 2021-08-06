
host_list = ["a", "b", "a"]

occurrences = collections.Counter(host_list)

# object resembles a dictionary

print(occurrences)
# Counter({'a': 2, 'b': 1})
print(occurrences["a"])
# 2
