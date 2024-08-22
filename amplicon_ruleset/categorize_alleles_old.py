from typing import Dict, Set, List, Tuple
import itertools

# fastq1: first fastq file
# fastq2: second fastq file
# primer_len: length of primer
# threshold: % consensus for whether a group of alleles should be split or not
def main(fastq1, fastq2, primer_len=20, threshold=.9):

    fastq1_data = create_data_dict(fastq1)
    fastq2_data = create_data_dict(fastq2)
    fq1_buckets = categorize(fastq1_data, primer_len)
    fq2_buckets = categorize(fastq2_data, primer_len)
    
    print(f'num keys fq1: {len(fq1_buckets.keys())}')
    print(f'num keys fq2: {len(fq2_buckets.keys())}')

    # split buckets that have disagreements
    for i in range(6):
        split_dict(fq1_buckets, fastq1_data, threshold)
        split_dict(fq2_buckets, fastq2_data, threshold)

    print(f'num keys fq1: {len(fq1_buckets.keys())}')
    print(f'num keys fq2: {len(fq2_buckets.keys())}')
    return fq1_buckets, fq2_buckets

# splits buckets that have disagreements
# return dictionary with keys --> base index, values --> list of counts for each base
def split_dict(bucket_dict=dict, fastq_data=dict, threshold=0.9):
    for bucket in bucket_dict.copy():
        if '*' not in bucket:

            disagreements = base_mismatches(bucket_dict[bucket], fastq_data, threshold)
            if len(disagreements) == 0:
                reads = bucket_dict[bucket]
                bucket_dict.pop(bucket)
                bucket_dict[(f'{bucket}*')] = reads
            index = min(disagreements, key=lambda k: disagreements[k], default=None)
            if index == None:
                continue

            a_set, c_set, g_set, t_set = divide_bucket(index, bucket_dict[bucket], fastq_data)
            
            bucket_dict.pop(bucket)
            if len(a_set) != 0:
                bucket_dict[f'{bucket}_1'] = a_set
            if len(c_set) != 0:
                bucket_dict[f'{bucket}_2'] = c_set
            if len(g_set) != 0:
                bucket_dict[f'{bucket}_3'] = g_set
            if len(t_set) != 0:
                bucket_dict[f'{bucket}_4'] = t_set
    
    return bucket_dict

def create_data_dict(fastq: str) -> Dict[str, str]:
    """
    Takes a fastq file and returns a dictionary with keys --> id, values --> sequence.
    
    Parameters
    ----------
    fastq : str
        name of fastq file
    
    Returns
    -------
    Dict[str, str]
        dictionary with keys --> id, values --> sequence
    """

    output = {}
    with open(fastq, 'r') as fq1:
        while True:
            lines = list(itertools.islice(fq1, 4))
            if not lines:
                break
            id = lines[0].split()[0]
            sequence = lines[1]
            phred = lines[3]
            output[id] = sequence

    return output

def categorize(fastq_dict: Dict[str, str], primer_len: int=20) -> Dict[str, Set[str]]:
    """
    Divide fastq data into buckets based on there first 20 characters.

    Parameters
    ----------
    fastq_dict : Dict[str, str]
        dictionary with keys --> id, values --> sequence
    primer_len : int
        length of primer (default is 20)
    
    Returns
    -------
    Dict[str, Set[str]]
        dictionary with keys --> first 20 characters, values --> list of ids with those primer sequences
    """
    
    primers_dict = {}
    for id, sequence in fastq_dict.items():
        primer = sequence[0:primer_len]
        if primer not in primers_dict:
            primers_dict[primer] = set()
        primers_dict[primer].add(id)
    
    return primers_dict   

# return dictionary with keys --> id, values --> sequence
def create_bucket_dict(seq_bucket: Set[str], fastq_data: Dict[str, str]) -> Dict[str, str]:
    """
    Return dictionary of ids and sequences for the given set of ids.
    
    Parameters
    ----------
    seq_bucket : Set[str]
        set of ids
    fastq_data : Dict[str, str]
        dictionary with keys --> id, values --> sequence
    
    Returns
    -------
    Dict[str, str]
        dictionary with keys --> id, values --> sequence
    """

    output = {}
    for id in seq_bucket:
        output[id] = fastq_data[id]
    
    return output

def divide_bucket(index: int, seq_bucket: Set[str], fastq_data: Dict[str, str]):
    """
    Return sets of ids, divided according to their base at the given index.
    
    Parameters
    ----------
    index : int
        base index
    seq_bucket : Set[str]
        set of ids
    fastq_data : Dict[str, str]
        dictionary with keys --> id, values --> sequence
    
    Returns
    -------
    Set[str] -> a_set
        set of ids with 'A' at the given index
    Set[str] -> c_set
        set of ids with 'C' at the given index
    Set[str] -> g_set
        set of ids with 'G' at the given index
    Set[str] -> t_set
        set of ids with 'T' at the given index
    """

    a_set = set()
    c_set = set()
    g_set = set()
    t_set = set()
    for sequence_id in seq_bucket:
        sequence = fastq_data[sequence_id]
        if sequence[index] == 'A':
            a_set.add(sequence_id)
        elif sequence[index] == 'C':
            c_set.add(sequence_id)
        elif sequence[index] == 'G':
            g_set.add(sequence_id)
        elif sequence[index] == 'T':
            t_set.add(sequence_id)
    return a_set, c_set, g_set, t_set


def base_mismatches(seq_bucket: Set[str], fastq_data: Dict[str, str], threshold: float=0.9) -> Dict[int, float]:
    """
    Return list of base indexes where there is less than a threshold % match between the sequences.

    Parameters
    ----------
    seq_bucket : Set[str]
        set of ids
    fastq_data : Dict[str, str]
        dictionary with keys --> id, values --> sequence
    threshold : float, optional
        % consensus for whether a group of alleles should be split or not, by default 0.9
    
    Returns
    -------
    Dict[int, float]
        base indexes where there is less than a threshold % match between the sequences
    """

    base_disagreements = {}
    base_count = count_bases(seq_bucket, fastq_data)
    for base in base_count:
        max_count = max(base_count[base])
        if max_count/len(seq_bucket) < threshold:
            base_disagreements[base] = max_count/len(seq_bucket)

    return base_disagreements


# return dictionary with keys --> base index, values --> list of counts for each base
def count_bases(seq_bucket: Set[str], fastq_data: Dict[str, str]) -> Dict[int, List[int]]:
    """
    Return dictionary with keys --> base indeces, values --> list of counts for each base.

    Parameters
    ----------
    seq_bucket : Set[str]
        set of ids
    fastq_data : Dict[str, str]
        dictionary with keys --> id, values --> sequence
    
    Returns
    -------
    Dict[int, List[int]]
        dictionary with keys --> base index, values --> list of counts for each base
    """

    bases_count = {}
    for base in range(0, 251):
        bases_count[base] = [0,0,0,0]
        for id in seq_bucket:
            sequence = fastq_data[id]
            if sequence[base] == 'A':
                bases_count[base][0] += 1
            elif sequence[base] == 'C':
                bases_count[base][1] += 1
            elif sequence[base] == 'G':
                bases_count[base][2] += 1
            elif sequence[base] == 'T':
                bases_count[base][3] += 1
    return bases_count


def create_consensus(bases_count: Dict[int, List[int]]) -> str:
    """
    Returns string consensus sequence for the given dictionary of base counts.
    
    Parameters
    ----------
    bases_count : Dict[int, List[int]]
        dictionary with keys --> base indeces, values --> list of counts for each base
    
    Returns
    -------
    str
        consensus sequence
    """

    sequence = ''
    for key in bases_count:
        max_base = bases_count[key].index(max(bases_count[key]))
        if max_base == 0:
            sequence += 'A'
        elif max_base == 1:
            sequence += 'C'
        elif max_base == 2:
            sequence += 'G'
        elif max_base == 3:
            sequence += 'T'

    return sequence

def simple_alignment(sequence: str, seq_bucket: Set[str], fastq_data: Dict[str, str], output_file: str=None) -> None:
    """
    Aligns sequences in the set to the given sequence. Writes to output_file.

    Parameters
    ----------
    sequence : str
        given sequence
    seq_bucket : Set[str]
        set of ids
    fastq_data : Dict[str, str]
        dictionary with keys --> id, values --> sequence
    output_file : str
        name of file to write to
    
    Returns
    -------
    None
    """

    with open(output_file, 'w') as out:
        out.write(f'{sequence}\n')
        for allele in seq_bucket:
            comparison_seq = fastq_data[allele]
            for i in range(len(sequence)):
                if sequence[i] == comparison_seq[i]:
                    out.write(' ')
                else:
                    out.write(f'{comparison_seq[i]}')
            out.write('\n')