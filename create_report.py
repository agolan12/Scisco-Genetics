import os
from Bio import Align


"""
parameters: 
    dir1: first directory
    dir2: second directory

returns:
    directory_1_not_in_directory_2: files in dir1 that are not in dir2
    directory_2_not_in_directory_1: files in dir2 that are not in dir1
"""
def directory_diff(dir1, dir2):
    files1 = os.listdir(dir1)
    files2 = os.listdir(dir2)
    directory1_not_in_directory2 = list(set(files1) - set(files2))
    directory2_not_in_directory1 = list(set(files2) - set(files1))
    return (directory1_not_in_directory2, directory2_not_in_directory1)

"""
parameters:
    dir1: first directory
    dir2: second directory

returns:
    the intersection of the two directories
"""
def directory_intersection(dir1, dir2):
    files1 = os.listdir(dir1)
    files2 = os.listdir(dir2)
    return list(sorted(set(files1)) & sorted(set(files2)))


"""
parameters:
    file1: first file
    file2: second file

returns:
    True if files are the same, False otherwise
"""
def same_file(file1, file2):
    with open(file1, 'r') as f1:
        with open(file2, 'r') as f2:
            line1 = f1.readline()
            line2 = f2.readline()
            while line1 and line2:
                if line1 != line2:
                    return False
                line1 = f1.readline()
                line2 = f2.readline()
            if line1 or line2:
                return False
            return True


"""
paremeters:
    file1: first file
    file2: second file

returns:
    a set ofthe alleles that are in file1 but not in file2, and the a set of the 
    alleles that are in file2 but not in file1    
"""
def allele_diff(file1, file2):
    dict1 = allele_dict(file1)
    dict2 = allele_dict(file2)
    output = (sorted(set(dict1.keys()) - set(dict2.keys()))), sorted((set(dict2.keys()) - set(dict1.keys())))
    return output


"""
parameters:
    dict1: first file
    dict2: second file

returns:
    the intersection of alleles of the two dictionaries
"""
def allele_intersection(dict1, dict2):
    return sorted(set(dict1.keys()) & set(dict2.keys()))


"""
prints every new allele and deleted allele in a text file.
Compares the sequences of every allele that is in both files and 
outputs the differences in there sequences into a text file
parameters:
    file1: first file (new file)
    file2: second file (old file)

output:
text file with differences between the two files
"""
def allele_comparison(file1, file2, output_file):
    dict1 = allele_dict(file1)
    dict2 = allele_dict(file2)
    with open(f'{output_file}', 'w') as f:
        f.write("Results: \n")
        for allele in allele_diff(file1, file2)[0]:
            f.write("New," + str(allele) + ",\n")
        for allele in allele_diff(file1, file2)[1]:
            f.write("Deleted," + str(allele) + ",\n")
        for allele in allele_intersection(dict1, dict2):
            sequence1 = ""
            for line in dict1[allele]:
                sequence1 += line[:-1]
            sequence2 = ""
            for line in dict2[allele]:
                sequence2 += line[:-1]
            if hash(sequence1) != hash(sequence2):
                f.write("Modified," + str(allele) + ",\n")
                alignment = Align.PairwiseAligner().align(sequence1, sequence2)
                sequences = format(alignment[0], 'fasta').split('\n')
                sequence1 = sequences[1]
                sequence2 = sequences[3]
                f.write(f'{generate_cigar(sequence2, sequence1)}\n')
                

"""
helper method to create dictionary of alleles and there sequences
parameters:
    file: the file to read from

returns:
    a dictionary of the form {allele: sequence}
"""
def allele_dict(file):
    dict = {}
    with open(file, 'r') as f:
        line = f.readline()
        while line:
            if line[0] == '>':
                name = ""
                index = line.index(' ') + 1
                while line[index] != ' ':
                    name += line[index]
                    index += 1
                dict[name] = []
            else:
                dict[name].append(line)
            line = f.readline()
    return dict       


"""
parameters:
    seq1: first sequence
    seq2: second sequence

returns:
    the cigar string
"""
def generate_cigar(seq1, seq2):
    cigar = []
    count = 0
    operation = ''

    for i in range(len(seq1)):
        if seq1[i] == seq2[i]:
            if operation == 'M':
                count += 1
            else:
                if count > 0:
                    cigar.append(f"{count}{operation}")
                operation = 'M'
                count = 1
        elif seq1[i] == '-':
            if operation == 'I':
                count += 1
            else:
                if count > 0:
                    cigar.append(f"{count}{operation}")
                operation = 'I'
                count = 1
        elif seq2[i] == '-':
            if operation == 'D':
                count += 1
            else:
                if count > 0:
                    cigar.append(f"{count}{operation}")
                operation = 'D'
                count = 1
        else:
            if operation == 'M':
                count += 1
            else:
                if count > 0:
                    cigar.append(f"{count}{operation}")
                operation = 'M'
                count = 1

    if count > 0:
        cigar.append(f"{count}{operation}")

    return ''.join(cigar)