import os
import sys
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from threading import Thread, Event
from queue import Queue, Empty

# Adjust the path to include the src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import main as run_hla_analysis

def get_config_path():
    """ Get the path to save the configuration file """
    home_dir = os.path.expanduser('~')
    config_dir = os.path.join(home_dir, '.hla_workshop_config')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return os.path.join(config_dir, 'default_config.txt')

class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class TextRedirector:
    def __init__(self, queue):
        self.queue = queue

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass  # Required for compatibility with file-like objects

def on_closing():
    print("Cleaning up resources...")
    app.destroy()

def run_analysis_thread(imgt_path, hla_path, micab_path, results_path, services, output_queue):
    sys.stdout = TextRedirector(output_queue)

    try:
        selected_hla_loci = [checkboxes.get(l).get() for l in ['class_1', 'dpa', 'dpb', 'dpb1_bridge45', 'dqa', 'dqb', 'drb', 'gapped_bridge', 'ungapped_bridge']]
        
        if checkboxes.get('micab').get() == tk.TRUE:
            if not micab_path:
                raise CustomException("Must provide MICAB_Ruleset_Sciscloud path for 'micab' analysis.")
        if any(selected_hla_loci):
            if not imgt_path or not hla_path:
                raise CustomException("All paths must be provided for analysis.")
        if any([var.get() for var in checkboxes.values()]):
            if not results_path:
                raise CustomException("Must provide a Results Path.")
        run_hla_analysis(imgt_path, results_path, hla_path, micab_path, services)
    except Exception as e:
        output_queue.put(f"Failed to run script: {str(e)}\n\n")
    finally:
        sys.stdout = sys.__stdout__

def run_analysis():
    global analysis_thread, stop_event
    imgt_path = imgt_entry.get()
    hla_path = hla_entry.get()
    micab_path = micab_entry.get()
    results_path = results_entry.get()

    services = [locus for locus, var in checkboxes.items() if var.get()]
    
    if len(services) < 1:
        output_text.insert(tk.END, f'No Analyses Selected\n')
        return
    
    output_text.insert(tk.END, f'Running Analysis for {services}\n\n')

    stop_event = Event()
    output_queue = Queue()
    analysis_thread = Thread(target=run_analysis_thread, args=(imgt_path, hla_path, micab_path, results_path, services, output_queue))
    analysis_thread.start()
    app.after(100, process_output_queue, output_queue)

def stop_analysis():
    global analysis_thread, stop_event
    if 'analysis_thread' in globals() and analysis_thread and analysis_thread.is_alive():
        stop_event.set()
        output_text.insert(tk.END, 'Stopping Analysis...\n')
        run_button.configure(bg='SystemButtonFace', fg='black')
        stop_button.configure(bg='SystemButtonFace', fg='black')
        analysis_thread.join()
    else:
        output_text.insert(tk.END, 'No Analysis Running...\n')

def process_output_queue(output_queue):
    try:
        while True:
            line = output_queue.get_nowait()
            output_text.insert(tk.END, line)
            output_text.see(tk.END)
    except Empty:
        pass
    app.after(100, process_output_queue, output_queue)

def save_default_paths():

    imgt_path = imgt_entry.get()
    hla_path = hla_entry.get()
    micab_path = micab_entry.get()

    with open(get_config_path(), 'w') as config_file:
        lead = '' if output_text.get('1.0', tk.END) == "\n" else '\n'
        output_text.insert('end', f"{lead}Saving Default Paths at: {get_config_path()}\n\n")
        config_file.write(f'imgt_path: {imgt_path}\n')
        config_file.write(f'hla_path: {hla_path}\n')
        config_file.write(f'micab_path: {micab_path}\n')

def set_default_paths():
    config_path = get_config_path()

    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            paths_dict = {}
            for line in config_file:
                key, value = line.strip().split(": ", 1)
                paths_dict[key] = value
    else:
        return

    imgt_entry.delete(0, tk.END)
    imgt_entry.insert(0, paths_dict.get('imgt_path'))

    hla_entry.delete(0, tk.END)
    hla_entry.insert(0, paths_dict.get('hla_path'))

    micab_entry.delete(0, tk.END)
    micab_entry.insert(0, paths_dict.get('micab_path'))

def select_imgt_path():
    path = os.path.join(filedialog.askdirectory(), 'alignments')
    output_text.insert(tk.END, f"imgt_path: {path}\n")
    if path:
        imgt_entry.delete(0, tk.END)
        imgt_entry.insert(0, path)

def select_hla_path():
    path = os.path.join(filedialog.askdirectory(), 'fasta')
    output_text.insert(tk.END, f"hla_path: {path}\n")
    if path:
        hla_entry.delete(0, tk.END)
        hla_entry.insert(0, path)

def select_micab_path():
    path = os.path.join(filedialog.askdirectory(), 'fasta')
    output_text.insert(tk.END, f"micab_path: {path}\n")
    if path:
        micab_entry.delete(0, tk.END)
        micab_entry.insert(0, path)

def select_results_path():
    path = filedialog.askdirectory()
    if path:
        results_entry.delete(0, tk.END)
        results_entry.insert(0, path)


# creates two dictionaries with keys as file names and values as the output text for the files
# bases: dictionary for base changes file
# whole_seq: dictionary for whole sequence changes file
def create_output_text(result_path):
    bases = dict()
    whole_seq = dict()
    for file in sorted(os.listdir(os.path.join(result_path, 'verify', 'sequences'))):
        if not os.path.getsize(os.path.join(result_path, 'verify', 'sequences', file)) == 0:
            output = ''
            with open(os.path.join(result_path, 'verify', 'summary.csv'), 'r') as summary:
                reader = csv.reader(summary)
                output = 'Summary:\n'
                for row in reader:
                    if row[0] == file.split('_')[0]:
                        output += f'Differences: {row[1]}\nCoding Differences: {row[2]}\nMissing: {row[3]}\nNew: {row[4]}\nTotal: {row[5]} \n\n\n'
            with open(os.path.join(result_path, 'verify', 'sequences', file), 'r') as f:
                if 'bases' in file:
                    output += 'Base Changes:\n'
                    for line in f:
                        output += line[:-1] + ':\n'
                        output += f.readline() + '\n'
                    bases[file] = output
                else:
                    if (file.split('_')[0] + '_bases.txt') not in bases.keys():
                        bases[file.split('_')[0] + '_bases.txt'] = output + "No Base Changes"
                    
                    output = ''
                    for line in f:
                        output += f'{line[:-1]}:\n'
                        output += f.readline()
                        output += f.readline()
                        output += f.readline()
                        output += f.readline() + '\n'
                    whole_seq[file] = output

    return bases, whole_seq

#  create dict with keys as file names and values as output text for log files
def log_data(log_file_path):
    output = dict()
    for file in sorted(os.listdir(log_file_path)):
        with open(f'{log_file_path}/{file}', 'r') as f:
            output[normalize_name(file)] = f.read()
    return output

# normalize allele names
def normalize_name(name):
    if '_exclusion.txt' in name:
        name = (name[:-len('_exclusion.txt')])
    else:
        name = (name[:-len('.txt')])
    return name.replace('EX_', 'exon').replace('-', '_')

# create list of alleles that have been modified
def allele_list(result_path):
    output = set()
    for file in sorted(os.listdir(result_path)):
        if not os.path.getsize(f'{result_path}/{file}') == 0:
            label = os.path.basename(file).split('_')[0]
            output.add(label)
    return sorted(output)

# create list of log files
def log_list(log_path):
    output = set()
    for dir in sorted(os.listdir(log_path)):
        for file in sorted(os.listdir(f'{log_path}/{dir}')):
            file = normalize_name(file)
            output.add(file)
    return sorted(output)

# Create the Treeview for quality control/results
def on_treeview_select(event):
    selected_item = treeview1.selection()
    if not selected_item:
        return
    
    selected_item = selected_item[0]
    item_text = treeview1.item(selected_item, "text")

    for tab in notebook.tabs():
        notebook.forget(tab)

    base_key = item_text + '_bases.txt'
    whole_seq_key = item_text + '_whole_seq.txt'
    
    # create tab 1
    if base_key in bases_data.keys():
        create_tab(notebook, bases_data, base_key, 'Bases')

    # create tab 2
    create_tab(notebook, whole_seq_data, whole_seq_key, 'Whole Sequence')


# Treeview for log
def log_treeview_select(event):
    selected_item = treeview2.selection()
    if not selected_item:
        return
    
    selected_item = selected_item[0]
    item_text = treeview2.item(selected_item, "text")

    for tab in log_notebook.tabs():
        log_notebook.forget(tab)
    
    key = item_text
    if key in exclusions_data.keys():
        create_tab(log_notebook, exclusions_data, key, 'Exclusions')
    
    if key in padding_data.keys():
        create_tab(log_notebook, padding_data, key, 'Padding')
    
    if key in propagate_data.keys():
        create_tab(log_notebook, propagate_data, key, 'Propagate')
    

def create_tab(notebook, data, key, label):
    tab = ttk.Frame(notebook)
    canvas = tk.Canvas(tab)
    canvas.pack(fill=tk.BOTH, expand=True)

    test = f'{data[key]}'
    inner_text = tk.Text(canvas, width=100, height=50)
    inner_text.insert(tk.END, test)
    canvas.create_window((0, 0), window=inner_text, anchor='nw')
    notebook.add(tab, text=label)


def toggle_all_checkboxes():
    state = all_var.get()
    for locus, var in checkboxes.items():
        var.set(state)

def create_fake_button(parent, text, command, bg, fg='black'):
    label = tk.Label(parent, text=text, bg=bg, fg=fg, padx=10, pady=5, cursor='hand2')
    label.bind('<Button-1>', lambda e: command())
    return label

def select_results_path():
    path = filedialog.askdirectory()
    if path:
        results_entry.delete(0, tk.END)
        results_entry.insert(0, path)

def load_results_data():
    result_path = filedialog.askdirectory()
    if not result_path:
        messagebox.showwarning("Warning", "Please select a results path.")
        return

    # create output text dictionaries
    global bases_data, whole_seq_data
    global exclusions_data, padding_data, propagate_data
    bases_data, whole_seq_data = create_output_text(result_path)
    exclusions_data = log_data(os.path.join(result_path, 'logs/exclusions/'))
    padding_data = log_data(os.path.join(result_path, 'logs/padding/'))
    propagate_data = log_data(os.path.join(result_path, 'logs/propagate/'))


    # Populate Treeview with allele list
    for allele in allele_list(os.path.join(result_path, 'verify', 'sequences')):
        treeview1.insert("", "end", text=allele)

    # Populate log Treeview with log list
    for allele in log_list(os.path.join(result_path, 'logs')):
        treeview2.insert("", "end", text=allele)

# Create the main window
app = tk.Tk()
app.title('HLA/MICAB Ruleset Configuration')

# Set the window size
app.geometry('1200x800')  # Adjusted size to fit the content better

# Create the tab control
tab_control = ttk.Notebook(app)
analysis_tab = ttk.Frame(tab_control)
tab_control.add(analysis_tab, text='Analyze')
result_tab = ttk.Frame(tab_control)
tab_control.add(result_tab, text='Quality Control')
tab_control.grid(row=0, column=0, sticky="nsew")
log_tab = ttk.Frame(tab_control)
tab_control.add(log_tab, text='Logs')


# Configure the main window to use grid
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)
tab_control.grid_rowconfigure(0, weight=1)
tab_control.grid_columnconfigure(0, weight=1)

# Create a frame to hold all the widgets in the analysis tab
analysis_frame = tk.Frame(analysis_tab)
analysis_frame.grid(padx=20, pady=20, sticky="nsew")
analysis_tab.grid_rowconfigure(0, weight=1)
analysis_tab.grid_columnconfigure(0, weight=1)

# Create another frame inside analysis_frame to center the content
frame = tk.Frame(analysis_frame)
frame.grid(padx=20, pady=20, sticky="nsew")
analysis_frame.grid_rowconfigure(0, weight=1)
analysis_frame.grid_columnconfigure(0, weight=1)

# Configure grid weight for the frame
for i in range(7):
    frame.grid_rowconfigure(i, weight=1)

# Set the minimum size for the label column
frame.grid_columnconfigure(0, minsize=150, weight=0)
# Set the weight for the entry columns
frame.grid_columnconfigure(1, weight=1)
frame.grid_columnconfigure(2, weight=1)
frame.grid_columnconfigure(3, weight=1)

imgt_label = tk.Label(frame, text='IMGTHLA Path:')
imgt_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
imgt_entry = tk.Entry(frame)
imgt_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
imgt_button = tk.Button(frame, text='Select Path', command=select_imgt_path)
imgt_button.grid(row=1, column=3, padx=5, pady=5)

hla_label = tk.Label(frame, text='HLA_Ruleset_Sciscloud Path:')
hla_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
hla_entry = tk.Entry(frame)
hla_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
hla_button = tk.Button(frame, text='Select Path', command=select_hla_path)
hla_button.grid(row=2, column=3, padx=5, pady=5)

micab_label = tk.Label(frame, text='MICAB_Ruleset_Sciscloud Path:')
micab_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
micab_entry = tk.Entry(frame)
micab_entry.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
micab_button = tk.Button(frame, text='Select Path', command=select_micab_path)
micab_button.grid(row=3, column=3, padx=5, pady=5)

results_label = tk.Label(frame, text='Results Path:')
results_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
results_entry = tk.Entry(frame)
results_entry.grid(row=4, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
results_button = tk.Button(frame, text='Select Path', command=select_results_path)
results_button.grid(row=4, column=3, padx=5, pady=5)

set_default_paths()

# Create a frame for the Run and Stop buttons to group them together
button_frame = tk.Frame(frame)
button_frame.grid(row=5, column=1, columnspan=2, pady=10)

run_button = create_fake_button(button_frame, 'Run', run_analysis, bg='#49be25')
run_button.pack(side=tk.LEFT, anchor='w', padx=5)

stop_button = create_fake_button(button_frame, 'Stop', stop_analysis, bg='#be4d25')
stop_button.pack(side=tk.LEFT, padx=5)

save_defaults_button = create_fake_button(frame, 'Save Defaults', save_default_paths, bg='grey')
save_defaults_button.grid(row=5, column=3, pady=10)

# New frame for HLA locus checkboxes
checkbox_frame = tk.Frame(frame)
checkbox_frame.grid(row=1, column=4, rowspan=10, padx=20, pady=10, sticky="nsew")
checkbox_label = tk.Label(checkbox_frame, text="HLA Locus Selection:")
checkbox_label.pack(anchor="w")
checkboxes = {}
# 'All' checkbox
all_var = tk.BooleanVar()
all_checkbox = tk.Checkbutton(checkbox_frame, text='all', variable=all_var, command=toggle_all_checkboxes)
all_checkbox.pack(anchor="w")
for locus in ['class_1', 'dpa', 'dpb', 'dpb1_bridge45', 'dqa', 'dqb', 'drb', 'gapped_bridge', 'ungapped_bridge', 'micab']:
    var = tk.BooleanVar()
    chk = tk.Checkbutton(checkbox_frame, text=locus, variable=var)
    chk.pack(anchor="w")
    checkboxes[locus] = var

output_text = scrolledtext.ScrolledText(frame, height=20)
output_text.grid(row=7, column=0, columnspan=5, sticky="nsew", padx=5, pady=10)

# Create a frame to hold all the widgets in the result tab
result_frame = tk.Frame(result_tab)
result_frame.grid(padx=20, pady=20, sticky="nsew")
result_tab.grid_rowconfigure(0, weight=1)
result_tab.grid_columnconfigure(0, weight=1)

# Create another frame inside result_frame to center the content
r_frame = tk.Frame(result_frame)
r_frame.grid(padx=20, pady=20, sticky="nsew")
result_frame.grid_rowconfigure(0, weight=1)
result_frame.grid_columnconfigure(0, weight=1)

# Create Treeview for quality control
treeview1 = ttk.Treeview(r_frame, columns=("Allele"))
treeview1.heading("#0", text="Allele")
treeview1.grid(row=0, column=0, sticky="nsew")

# Bind the selection event
treeview1.bind("<<TreeviewSelect>>", on_treeview_select)

# Create a frame to hold all the widgets in the log tab
logs_frame = tk.Frame(log_tab)
logs_frame.grid(padx=20, pady=20, sticky="nsew")
log_tab.grid_rowconfigure(0, weight=1)
log_tab.grid_columnconfigure(0, weight=1)

# Create another frame inside logs_frame to center the content
l_frame = tk.Frame(logs_frame)
l_frame.grid(padx=20, pady=20, sticky="nsew")
logs_frame.grid_rowconfigure(0, weight=1)
logs_frame.grid_columnconfigure(0, weight=1)

# Create Treeview for log 
treeview2 = ttk.Treeview(logs_frame, columns=("Description"))
treeview2.heading("#0", text="Description")
treeview2.grid(row=0, column=1, sticky="nsew")

treeview2.bind("<<TreeviewSelect>>", log_treeview_select)

notebook = ttk.Notebook(r_frame)
notebook.grid(row=0, column=1, sticky="nsew")

log_notebook = ttk.Notebook(l_frame)
log_notebook.grid(row=0, column=1, sticky="nsew")

# Configure grid weight for r_frame
r_frame.grid_rowconfigure(0, weight=1)
r_frame.grid_columnconfigure(0, minsize=150, weight=0)
r_frame.grid_columnconfigure(1, weight=1)

# Configure grid weight for l_frame
l_frame.grid_rowconfigure(0, weight=1)
l_frame.grid_columnconfigure(0, minsize=150, weight=0)
l_frame.grid_columnconfigure(1, weight=1)

# Load Results button in result_tab
load_results_button = create_fake_button(r_frame, 'Load Results', load_results_data, bg='#49be25')
load_results_button.grid(row=1, column=0, columnspan=2, pady=10)

app.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()
