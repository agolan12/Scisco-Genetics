from networkx import intersection
import json


def compare_reports(gen_file, nuc_file, imgt_file):
    gen_dict = create_dict(gen_file)
    nuc_dict = create_dict(nuc_file)
    scisco_dict = gen_dict | nuc_dict
    imgt_dict = create_dict(imgt_file)
    matches = set()
    key_mismatch = set()
    for key in (set(scisco_dict.keys()) & set(imgt_dict.keys())):
        if scisco_dict[key] == imgt_dict[key]:
            matches.add(key)
        else:
            key_mismatch.add(key)
    missing_imgt_report = set() # key in scisco report but not in imgt
    for key in (set(scisco_dict.keys()) - set(imgt_dict.keys())):
        missing_imgt_report.add(key)

    missing_scisco_report = set() # key in imgt report but not in scisco
    for key in (set(imgt_dict.keys()) - set(scisco_dict.keys())):
        missing_scisco_report.add(key)
    return matches, key_mismatch, missing_imgt_report, missing_scisco_report
    



def create_dict(file):
    with open(file, 'r') as f:
        line = f.readline()
        dict = {}
        while line:
            if "New" not in line and "Modified" not in line and "Deleted" not in line:
                pass
            else:
                name = ""
                index = line.index(',') + 1
                while line[index] != ',':
                    name += line[index]
                    index += 1
                dict[name] = []
                if "New" in line:
                    dict[name].append("New")
                if "Modified" in line:
                    dict[name].append("Modified")
                if "Deleted" in line:
                    dict[name].append("Deleted")
            line = f.readline()
    return dict


def write_comparison(gen_report, nuc_report,imgt_report, output_file):
    good, bad, missing_imgt, missing_scisco = compare_reports('gen_report_file.txt', 'nuc_report_file.txt', '/Users/Assaf/IMGTHLA/version_report.txt')
    total_len = len(good) + len(bad) + len(missing_imgt) + len(missing_scisco)
    gen_dict = create_dict(f'{gen_report}')
    nuc_dict = create_dict(f'{nuc_report}')
    scisco_dict = gen_dict | nuc_dict
    imgt_dict = create_dict(f'{imgt_report}')
    with open (f'{output_file}', 'w') as f:
        f.write('correct: \n')
        f.write (f'{100 *(len(good) / total_len)} %\n')
        f.write(f'{len(good)}\n')
        f.write("mismatch values (i.e. Scisco says new, imgt says modified):\n ")
        f.write (f'{100 *(len(bad) / total_len)} %\n')
        f.write(f'{len(bad)}\n')
        f.write("missing from imgt: \n")
        f.write(f'{100*(len(missing_imgt) / total_len)} %\n')
        f.write(f'{len(missing_imgt)}\n')
        f.write("missing from scisco: \n")
        f.write(f'{100 * len(missing_scisco) / total_len}%\n')
        f.write(f'{len(missing_scisco)}\n')
        f.write('\n\n\n Comparing mismatched values: \n')
        f.write(f'name:\t\t\t\tScisco:\t\t\timgt:\n')
        for key in bad:
            f.write(f'{key}:\t\t\t{scisco_dict[key]}\t\t\t{imgt_dict[key]} \n')
        f.write('\n\n\n Missing from IMGT: \n')
        for key in sorted(missing_imgt):
            f.write(f'{key}:\t\t{scisco_dict[key]}\n')
        output = parse_deleted(missing_imgt, scisco_dict)
        f.write(f'\n\n{json.dumps(output, indent = 4)}\n')
        f.write('\n\n\n Missing from Scisco: \n')
        for key in missing_scisco:
            f.write(f'{key}:\t\t{imgt_dict[key]}\n')


def parse_deleted(missing_set, scisco_dict):
    output = {}
    for key in missing_set:
        if scisco_dict[key] == ['Deleted']:
            output[key] = []
            deleted_key = key
            if key[len(key) - 1] == "N":
                deleted_key = key[:-1]
            for allele in scisco_dict.keys():
                if deleted_key != allele and deleted_key in allele:
                    output[key].append(allele)
    return output
