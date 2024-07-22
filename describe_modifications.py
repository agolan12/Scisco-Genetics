"""
prints the modification made to each allele in the report

parameters:
    old_dict: the dictionary of the old report
    new_dict: the dictionary of the new report
    report: the report to read from
    output_file: the file to write to
"""

def modification_log(old_dict, new_dict, report, output_file):
    with open(report, 'r') as f:
        with open(output_file, 'w') as o:
            line = f.readline()
            cigar_string = ''
            while line:
                if "Modified" in line:
                    allele = line.split(',')[1]
                    cigar_string = f.readline()
                    o.write(f'>>> {allele}: \n')
                    o.write(parse_cigar(allele, cigar_string, old_dict, new_dict)+'\n\n')
                line = f.readline()

"""
goes through cigar string and prints the insertion and deletion indeces, aswell 
as the bases added or removed

parameters:
    allele: the name of the allele
    cigar_string: the cigar string to parse
    old_dict: the dictionary of the old report (of form allele: sequence)
    new_dict: the dictionary of the new report (of form allele: sequence)
"""
def parse_cigar(allele, cigar_string, old_dict, new_dict):
    head_index = ''
    tail_index = 0
    old_sequence = ""
    new_sequence = ""
    output = ""
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
                    output += (f'insertion at {int(tail_index) + 1}: \n')
                else:
                    output += (f'Insertion from {int(tail_index) + 1} to {int(head_index) + tail_index}\n')
                output +=(new_sequence[tail_index:int(head_index) + tail_index] + '\n')
            if curr == 'D':
                if int(int(head_index) == 1):
                    output += (f'Deletion at {int(tail_index) + 1}: \n')
                else:
                    output += (f'Deletion from {int(tail_index)+ 1} to {int(head_index) + tail_index}: \n')
                output += (old_sequence[tail_index:int(head_index) + tail_index]
                           + '\n')
            tail_index += int(head_index)
            head_index = ''
    return output

