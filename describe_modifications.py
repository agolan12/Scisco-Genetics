def modification_log(report, old_dict, new_dict):
    with open(report, 'r') as f:
        line = f.readline()
        cigar_string = ''
        while line:
            if "Modified" in line:
                allele = line.split(',')[1]
                cigar_string = f.readline()
                print(allele)
                parse_cigar(allele, cigar_string, old_dict, new_dict)
            line = f.readline()

def parse_cigar(allele, cigar_string, old_dict, new_dict):
    head_index = ''
    tail_index = 0
    old_sequence = ""
    new_sequence = ""
    for line in old_dict[allele]:
         old_sequence += line[:-1]
    for line in new_dict[allele]:
        new_sequence += line[:-1]
    for i in range(len(cigar_string) - 1):
        curr = cigar_string[i]
        if curr.isdigit():
            head_index += curr
        else:
            if curr == 'I':
                if int(int(head_index) == 1):
                    print(f'insertion at {int(tail_index) + 1}')
                print(f'Insertion from {int(tail_index) + 1} to {int(head_index) + tail_index}')
                print(new_sequence[tail_index:int(head_index) + tail_index])
            if curr == 'D':
                if int(int(head_index) == 1):
                    print(f'Deletion at {int(tail_index) + 1}')
                else:
                    print(f'Deletion from {int(tail_index)+ 1} to {int(head_index) + tail_index}')
                print(old_sequence[tail_index:int(head_index) + tail_index])
            tail_index += int(head_index)
            head_index = ''

