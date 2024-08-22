from typing import Dict, Set, List
from bucket import ReadBucket
import itertools


# fastq1: first fastq file
# fastq2: second fastq file
# primer_len: length of primer
# threshold: % consensus for whether a group of alleles should be split or not
def main(fastq1, fastq2, primer_len=20, threshold=.9):

    fq1_bucket_dict = create_bucket_dict(fastq1, primer_len)
    fq2_bucket_dict = create_bucket_dict(fastq2, primer_len)
    # split buckets that have disagreements
    for i in range(20):
        fq1_bucket_dict = split_buckets(fq1_bucket_dict, threshold)
        fq2_bucket_dict = split_buckets(fq2_bucket_dict, threshold)

    return fq1_bucket_dict, fq2_bucket_dict


def create_bucket_dict(fastq_file: str, primer_len: int=20) -> Dict[str, ReadBucket]:
    """
    Create dictionary of buckets from fastq file.

    Parameters
    ----------
    fastq_file : str
        fastq file
    primer_len : int, optional
        length of primer, by default 20

    Returns
    -------
    Dict[str, ReadBucket]
        dictionary with keys --> primer sequence, values --> ReadBucket objects
    """
    
    with open(fastq_file, 'r') as fq1:
        bucket_dict = {}
        while True:
            lines = list(itertools.islice(fq1, 4))
            if not lines:
                break
            id = lines[0].split()[0]
            sequence = lines[1].rstrip('\n')
            phred = lines[3]

            primer = sequence[0:primer_len]
            for bucket in bucket_dict:
                if x_char_diff(2, bucket, primer):
                    bucket_dict[bucket].add(id, sequence)
                    break
            else:
                bucket = ReadBucket(primer)
                bucket.add(id, sequence)
                bucket_dict[primer] = bucket
            
    return bucket_dict


def split_buckets(bucket_dict: Dict[str, ReadBucket], threshold: float=0.9) -> Dict[str, ReadBucket]:
    """
    Splits buckets that have disagreements (i.e. where there is less than a threshold % match between every base in the sequences).

    Parameters
    ----------
    bucket_dict : Dict[str, ReadBucket]
        dictionary with keys --> primer sequence, values --> ReadBucket objects
    threshold : float, optional
        % consensus for whether a group of alleles should be split or not, by default 0.9
    
    Returns
    -------
    Dict[str, ReadBucket]
        dictionary with keys --> primer sequence, values --> ReadBucket objects
    """
    keys = list(bucket_dict.keys())
    for primer in keys:
        bucket = bucket_dict[primer]
        if bucket.is_congruent():
            if "*" not in primer:
                bucket_dict[f'{primer}_*'] = bucket_dict.pop(primer)
        else:
            bucket_dict.pop(primer)
            split_index = bucket.lowest_threshold_index

            # create new buckets
            a_bucket = ReadBucket(f'{primer}_{split_index}A')
            c_bucket = ReadBucket(f'{primer}_{split_index}C')
            g_bucket = ReadBucket(f'{primer}_{split_index}G')
            t_bucket = ReadBucket(f'{primer}_{split_index}T')

            for id in bucket.get_ids():

                sequence = bucket.data[id]
                base = sequence[split_index]
                # add id's and sequences to new buckets
                if base == "A":
                    a_bucket.add(id, sequence)
                elif base == "C":
                    c_bucket.add(id, sequence)
                elif base == "G":
                    g_bucket.add(id, sequence)
                elif base == "T":
                    t_bucket.add(id, sequence)

            if len(a_bucket) > 0:
                bucket_dict[a_bucket.primer] = a_bucket
            if len(c_bucket) > 0:
                bucket_dict[c_bucket.primer] = c_bucket
            if len(g_bucket) > 0:
                bucket_dict[g_bucket.primer] = g_bucket
            if len(t_bucket) > 0:
                bucket_dict[t_bucket.primer] = t_bucket
    
    return bucket_dict

def merge_buckets(bucket_dict: Dict[str, ReadBucket]) -> None:
    """
    Merges buckets that have the same consensus sequence.
    
    Parameters
    ----------
    bucket_dict : Dict[str, ReadBucket]
        dictionary with keys --> primer sequence, values --> ReadBucket objects

    """
    sorted_buckets = sorted(bucket_dict.items(), key=lambda item: item[1].create_consensus()[20:150])
    i = 0
    while i < len(sorted_buckets) - 1:
        curr_primer = sorted_buckets[i][0]
        next_primer = sorted_buckets[i + 1][0]
        while(x_char_diff(2, bucket_dict[curr_primer].create_consensus()[20:150], bucket_dict[next_primer].create_consensus()[20:150])):
            for id in bucket_dict[next_primer].get_ids():
                bucket_dict[curr_primer].add(id, bucket_dict[next_primer].data[id])
            del bucket_dict[next_primer]
            del sorted_buckets[i + 1]
            next_primer = sorted_buckets[i + 1][0]
        i += 1

def sift_buckets(bucket_dict: Dict[str, ReadBucket], consensus_dict: Dict[str, ReadBucket], end_index: int) -> None:
    """
    Sifts through bucket dictionary. If a read bucket is congruent then it is added to the consensus dictionary. Else
    if the buckets consensus matches a consensus read bucket in the consensus dictionary, it is added to that bucket.
    
    Parameters
    ----------
    bucket_dict : Dict[str, ReadBucket]
        dictionary with keys --> primer sequence, values --> ReadBucket objects
    consensus_dict : Dict[str, ReadBucket]
        dictionary with keys --> consensus sequence, values --> ReadBucket objects
    end_index : int
        end index of the consensus
        
    Returns
    -------
    None
    """
    remove_list = []

    for primer in bucket_dict:

        consensus = bucket_dict[primer].create_consensus()[20:end_index]
        match_consensus = get_consensus_match(consensus, consensus_dict, end_index)

        if match_consensus != "":
            union_bucket = union_read_buckets(bucket_dict[primer], consensus_dict[match_consensus])
            if union_bucket.is_congruent():
                print(f'adding sequences {primer} to consensuses')
                consensus_dict[match_consensus] = union_bucket
                remove_list.append(primer)

        elif "*" in primer and len(bucket_dict[primer]) > 10:
            print(f'adding bucket {primer} to consensus')
            consensus_dict[consensus] = ReadBucket(consensus)
            for id in bucket_dict[primer].get_ids():
                consensus_dict[consensus].add(id, bucket_dict[primer].data[id])
            remove_list.append(primer)

    for remove in remove_list:
        del bucket_dict[remove]

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


def x_char_diff(x, s1, s2):
    return sum(c1 != c2 for c1, c2 in zip(s1, s2)) <= x


def get_consensus_match(input_sequence: str, consensus_dict: Dict[str, ReadBucket], end_index: int) -> str:
    """
    Finds a matching consensus in the consensus dictionary.

    Parameters
    ----------
    input_sequence : str
        consensus sequence
    consensus_dict : Dict[str, ReadBucket]
        dictionary with keys --> consensus sequence, values --> ReadBucket objects
    end_index : int
        end index of the consensus

    Returns
    -------
    str
        returns the consensus sequence that matches the input sequence, else returns an empty string
    """
    output = ""

    for consensus in consensus_dict:
        if x_char_diff(.1 * (end_index - 20), consensus, input_sequence):
            output = consensus
            break

    return output



def union_read_buckets(main_bucket: ReadBucket, sub_bucket: ReadBucket) -> ReadBucket:
    """
    Merges two read buckets into one.

    Parameters
    ----------
    bucket1 : ReadBucket
        first read bucket
    bucket2 : ReadBucket
        second read bucket

    Returns
    -------
    ReadBucket
        new read bucket
    """
    new_bucket = ReadBucket(main_bucket.primer)
    for id in main_bucket.get_ids():
        new_bucket.add(id, main_bucket.data[id])
    for id in sub_bucket.get_ids():
        new_bucket.add(id, sub_bucket.data[id])
    return new_bucket
