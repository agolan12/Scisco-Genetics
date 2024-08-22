import random


"""
path_to_fasta: path to fasta file that contains sequences
output_filename: name of output file
read_count: number of reads to generate
paired: if true, generate paired reads
"""
def main(path_to_fasta=str, output_filename=str, read_count=int, paired=bool):
    fasta = ""
    with open(path_to_fasta, 'r') as f:
        for line in f:
            if line[0] == '>':
                fasta += '\n' + line
            else:
                fasta += line.strip('\n')
    
    fasta_list = fasta.split('\n')
    line_indices = set()
    while len(line_indices) < read_count:
        rand = random.randint(1, len(fasta_list) - 2)
        if rand % 2 != 1:
            rand += 1
        line_indices.add(rand)

    with open(output_filename, 'w') as out:
        for i in line_indices:
            out.write(fasta_list[i].replace('>', '@') + '\n')
            out.write(fasta_list[i + 1] + '\n')
            out.write('+\n')
            out.write(f'{generate_phred(fasta_list[i + 1])}\n')


def generate_phred(sequence):
    return "test"
