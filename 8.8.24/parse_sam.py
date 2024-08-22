# create a list of the reference names
def list_references(sam_file_path):
    output = list()
    with open(sam_file_path, 'r') as f:
        for line in f:
            if line.startswith('@SQ'):
                output.append(line.split('\t')[1][3:])
    return output


# returns dict with reference name as key and number of matches as value
# filter out matches with mapq < min_mapq
def filtered_match_count(sam_file_path, min_mapq):
    matches = dict()
    with open(sam_file_path, 'r') as f:
        for line in f:
            if line.startswith('@'):
                continue
            else:
                r_name = return_field(line, 3)
                mapq = int(return_field(line, 5))
                if r_name != "*" and mapq >= min_mapq:
                    if r_name in matches:
                        matches[r_name] += 1
                    else:
                        matches[r_name] = 1
    return matches

# returns dict with reference name as key and average quality as value
def display_quality(sam_file_path):
    output = dict()
    with open(sam_file_path, 'r') as f:
        for line in f:
            if line.startswith('@'):
                continue
            elif return_field(line, 11) != "*":
                output[return_field(line, 1)] = qual_to_phred(return_field(line, 11))
    return output

# return number of attempted allignments
def count_allignments(sam_file_path):
    output = dict()
    with open(sam_file_path, 'r') as f:
        for line in f:
            if line.startswith('@'):
                continue
            else:
                q_name = return_field(line, 1)
                r_name = return_field(line, 3)
                output[q_name] = set()
                output[q_name].add(r_name)
    return output

# returns dict with reference name as key and sum of column as value
def column_average(sam_file_path, column):
    output = dict()
    count = dict()
    with open(sam_file_path, 'r') as f:
        for line in f:
            if line.startswith('@'):
                continue
            else:
                r_name = return_field(line, 3)
                val = int(return_field(line, column))
                if r_name not in output:
                    output[r_name] = [0, 0, 0]
                    count[r_name] = 0
                    min = val
                    max = val
                    output[r_name][1] = min
                    output[r_name][2] = max
                output[r_name][0] = output[r_name][0] + val
                count[r_name] += 1
                if val < output[r_name][1]:
                    output[r_name][1] = val
                if val > output[r_name][2]:
                    output[r_name][2] = val
    
    for k, v in output.items():
        output[k][0] = v[0] / count[k]
    
    return output

    

# create a dict with reference name as key and set of column values as value
def reference_column_dict(sam_file_path, column):
    output = dict()
    with open(sam_file_path, 'r') as f:
        for line in f:
            if line.startswith('@'):
                continue
            else:
                if return_field(line, "RNAME") not in output:
                    output[return_field(line, "RNAME")] = set()
                output[return_field(line, 'RNAME')].add(return_field(line, column))
    return output

def create_report(sam_file_path, min_mapq=0): 
    # list of references
    references = list_references(sam_file_path)

    # k: reference name, v: number of matches
    filtered_matches = filtered_match_count(sam_file_path, min_mapq)

    # k: query name, v: reference name
    allignment_count = count_allignments(sam_file_path)

    # k: reference name, v: total mapq
    mapq = column_average(sam_file_path, "MAPQ")

    pos = column_average(sam_file_path, "POS")

    tlen = column_average(sam_file_path, 9)

    sorted_filtered_matches = dict(sorted(filtered_matches.items(), key=lambda item: item[1], reverse=True))

    reference_tlen_dict = reference_column_dict(sam_file_path, "TLEN")

    with open('report.txt', 'w') as f:
        f.write('Total number of reference sequences: ' + str(len(references)) + '\n')
        f.write(f'number of reference sequences with matches: {len(filtered_matches.keys())} \n')
        f.write(f'Number of matches: {sum(filtered_matches.values())} \n')
        f.write(f'Min mapq: {min_mapq} \n\n')
        f.write(f'\nReference\t\tNumber of matches\n')

        
        for k, v in sorted_filtered_matches.items():
            f.write('{:<40}{}\n'.format(k, v))
        """for k, v in sorted_filtered_matches.items():
            f.write('{:<40}{:<4}{}\n'.format(k, v, pos[k]))"""       

# return a given category of a given line
def return_field(line, field=str):
    if field == 1 or str(field).upper() == 'QNAME':
        return line.split('\t')[0]
    if field == 2 or  str(field).upper() == 'FLAG':
        return line.split('\t')[1]
    if field == 3 or str(field).upper() == 'RNAME':
        return line.split('\t')[2]
    if field == 4 or str(field).upper() == 'POS':
        return line.split('\t')[3]
    if field == 5 or str(field).upper() == 'MAPQ':
        return line.split('\t')[4]
    if field == 6 or str(field).upper() == 'CIGAR':
        return line.split('\t')[5]
    if field == 7 or str(field).upper() == 'RNEXT':
        return line.split('\t')[6]
    if field == 8 or str(field).upper() == 'PNEXT':
        return line.split('\t')[7]
    if field == 9 or str(field).upper() == 'TLEN':
        return line.split('\t')[8]
    if field == 10 or str(field).upper() == 'SEQ':
        return line.split('\t')[9]
    if field == 11 or str(field).upper() == 'QUAL':
        return line.split('\t')[10]


# convert QUAL string to a list of Phred scores
def qual_to_phred(qual_string):
    """
    Convert QUAL string to a list of Phred scores.
    
    :param qual_string: A string of ASCII characters representing the QUAL field.
    :return: A list of Phred quality scores.
    """
    phred_scores = [ord(c) - 33 for c in qual_string]
    return phred_scores



def parse_bitwise_flag(flag):
    """
    Parses the bitwise flag from a SAM file and returns a dictionary of boolean values 
    representing the state of each flag.

    Args:
        flag (int): The bitwise flag from a SAM file.

    Returns:
        dict: A dictionary with the decoded information.
    """
    return {
        'paired': bool(flag & 0x1),
        'proper_pair': bool(flag & 0x2),
        'unmapped': bool(flag & 0x4),
        'mate_unmapped': bool(flag & 0x8),
        'reverse_strand': bool(flag & 0x10),
        'mate_reverse_strand': bool(flag & 0x20),
        'first_in_pair': bool(flag & 0x40),
        'second_in_pair': bool(flag & 0x80),
        'not_primary_alignment': bool(flag & 0x100),
        'failed_quality_check': bool(flag & 0x200),
        'duplicate': bool(flag & 0x400),
        'supplementary_alignment': bool(flag & 0x800),
    }