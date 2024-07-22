


def find_closest_coding_seq(allele_name: str, allele_data: dict[str, str]) -> dict[str, str]:
    if not allele_name[-1].isdigit():
        allele_name = allele_name[:-1]
    sequence = allele_data[allele_name]
    prefix = allele_name[:-2]
    filtered_keys = set()
    while ('*' in sequence):
        if len(filtered_keys) == 0:
            filtered_keys = sorted({key for key in set(allele_data.keys()) if key.startswith(prefix)})
            prefix = updated_prefix(prefix)
        allele_name = filtered_keys.pop()
        sequence = allele_data[allele_name]
    return {allele_name: sequence}



def updated_prefix(prefix: str) -> str:
    prefix = prefix[:-1]
    index = prefix.rfind(':')
    if prefix[index + 1:].isdigit() and prefix[index + 1:] == "01":
        return updated_prefix(prefix[:-2])
    else:
        num = int(prefix[index + 1:])
        num_digits = max(2,len(str(num)))
        if num < 10:
            return prefix[:-num_digits] + str(f'0{num - 1}:')
        else:
            return prefix[:-num_digits] + str(f'{num - 1}:')





def retry(allele_name: str, allele_data: dict[str, str]) -> dict[str, str]:
    sequence = allele_data[allele_name]
    while ('*' in sequence):
        allele_name = update_name(allele_name, allele_data)
        sequence = allele_data[allele_name]
    return {allele_name: sequence}


def update_name(name: str, data: dict[str, str]) -> str:
    if not name[-1].isdigit():
        name = name[:-1]
    index = name.rfind(':')
    if name[index + 1:].isdigit() and name[index + 1:] == "01":
        prefix = find_prefix(name[:-3])
        name = sorted({key for key in set(data.keys()) if key.startswith(prefix)}).pop()
    else:
        num = int(name[index + 1:])
        num_digits = max(2,len(str(num)))
        if num < 10:
            return name[:-num_digits] + str(f'0{num - 1}')
        else:
            return name[:-num_digits] + str(f'{num - 1}')


def find_prefix(name: str) -> str:
    if name[-2:] == "01":
        return find_prefix(name[:-3])
    else:
        index = name.rfind(':')
        num = int(name[index + 1:])
        num_digits = max(2,len(str(num)))
        if num < 10:
            return name[:-num_digits] + str(f'0{num - 1}')
        else:
            return name[:-num_digits] + str(f'{num - 1}')

    
    
    

