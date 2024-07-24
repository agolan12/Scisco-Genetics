"""
parameters:
    name: the name of the sequence
    data: dict containing name, sequence pairs

returns:
    the next closest complete sequence
"""
def find_closest_coding_seq(allele_name: str, allele_data: dict[str, str]) -> dict[str, str]:
    sequence = allele_data[allele_name]
    while ('*' in sequence):
        allele_name = update_name(allele_name, allele_data)
        sequence = allele_data[allele_name]
    return {allele_name: sequence}

"""
parameters:
    name: the name of the allele
    data: dict containing name, sequence pairs

returns:
    the next closest name
"""
def update_name(name: str, data: dict[str, str]) -> str:
    if not name[-1].isdigit():
        name = name[:-1]
    while name[-2:] == "01":
        name = name[:-3]
    name = decrement_field(name)
    if name not in data.keys():
        filtered_keys = sorted({key for key in set(data.keys()) if key.startswith(name)})
        name = filtered_keys.pop()
    return name


"""
parameters:
    name: the name of the allele

returns:
    str: name with last field decremented by 1
"""
def decrement_field(name: str) -> str:
    index = max(name.rfind(':'), name.rfind('*'))
    num = int(name[(index + 1):])
    num_digits = max(2,len(str(num)))
    if num <= 10:
        return name[:-num_digits] + str(f'0{num - 1}')
    else:
        return name[:-num_digits] + str(f'{num - 1}')
