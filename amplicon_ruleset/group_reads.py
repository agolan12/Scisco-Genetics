"""
group the two dictionaries of reads into groups based on their id and
bucket. add them to dictionary. Then create a consensus looking at the first
100 characters from each read pair.
"""

def group_reads(fq1_data=dict, fq2_data=dict, fq1_buckets=dict, fq2_buckets=dict):
    new_groups = {}

    for bin1 in fq1_buckets:
        r_one_key = bin1

        for id in fq1_buckets[bin1]:
            r_one = fq1_data[id]
            r_two = fq2_data[id]

            subkey_two = r_two[:20]
            for key in fq2_buckets.keys():
                if subkey_two in key:
                    if id in fq2_buckets[key]:
                        r_two_key = key
                        break

            if (r_one_key, r_two_key) not in new_groups and (r_two_key, r_one_key) not in new_groups:
                new_groups[(r_one_key, r_two_key)] = [id]

    return new_groups
        
            