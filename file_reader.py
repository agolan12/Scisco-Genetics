import os
from Bio import pairwise2
from Bio.pairwise2 import format_alignment

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
    return list(set(files1) & set(files2))


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
    output = (set(dict1.keys()) - set(dict2.keys())), (set(dict2.keys()) - set(dict1.keys()))
    return output


"""
parameters:
    file1: first file
    file2: second file

returns:
    the intersection of alleles of the two files
"""
def allele_intersection(file1, file2):
    dict1 = allele_dict(file1)
    dict2 = allele_dict(file2)
    return set(dict1.keys()) & set(dict2.keys())


"""
compares every matching allele between two files and outputs the differences in there sequences
into a text file
parameters:
    file1: first file
    file2: second file

output:
text file with differences between the two files
"""
def allele_comparison(file1, file2):
    dict1 = allele_dict(file1)
    dict2 = allele_dict(file2)
    with open('output_file.txt', 'w') as f:
        different_alleles = set()
        for allele in allele_intersection(file1, file2):
            sequence1 = ""
            for line in dict1[allele]:
                sequence1 += line[:-1]
            sequence2 = ""
            for line in dict2[allele]:
                sequence2 += line[:-1]
            if sequence1 == sequence2:
                print("The sequence of " + str(allele) + " is the same in both files\n")
            else:
                different_alleles.add(allele)
                alignments = pairwise2.align.globalxx(sequence1, sequence2)
                print(format_alignment(*alignments[0]))
                

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


