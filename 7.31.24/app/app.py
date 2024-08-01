import os
import sys
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from threading import Thread
from queue import Queue, Empty

# Adjust the path to include the src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import main as run_hla_analysis

class TextRedirector:
    def __init__(self, queue):
        self.queue = queue

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass  # Required for compatibility with file-like objects

def get_application_path():
    """ Get the path of the application whether it's run by Python or as an executable"""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path

def show_app_path():
    app_path = get_application_path()
    messagebox.showinfo("Application Path", f"The application is running from: {app_path}")

def on_closing():
    print("Cleaning up resources...")
    app.destroy()

def run_analysis_thread(imgt_path, hla_path, micab_path, results_path, output_queue):
    sys.stdout = TextRedirector(output_queue)

    try:
        run_hla_analysis(imgt_path, results_path, hla_path, micab_path)
    except Exception as e:
        output_queue.put(f"Failed to run script: {str(e)}\n")
    finally:
        sys.stdout = sys.__stdout__

def run_analysis():
    imgt_path = imgt_entry.get()
    hla_path = hla_entry.get()
    micab_path = micab_entry.get()
    results_path = results_entry.get()
    output_text.insert(tk.END, 'Running Analysis...\n')

    output_queue = Queue()
    analysis_thread = Thread(target=run_analysis_thread, args=(imgt_path, hla_path, micab_path, results_path, output_queue))
    analysis_thread.start()
    app.after(100, process_output_queue, output_queue)

def process_output_queue(output_queue):
    try:
        while True:
            line = output_queue.get_nowait()
            output_text.insert(tk.END, line)
            output_text.see(tk.END)
    except Empty:
        pass
    app.after(100, process_output_queue, output_queue)

def select_imgt_path():
    path = os.path.join(filedialog.askdirectory(), 'alignments')
    if path:
        imgt_entry.delete(0, tk.END)
        imgt_entry.insert(0, path)

def select_hla_path():
    path = os.path.join(filedialog.askdirectory(), 'fasta')
    if path:
        hla_entry.delete(0, tk.END)
        hla_entry.insert(0, path)

def select_micab_path():
    path = os.path.join(filedialog.askdirectory(), 'fasta')
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
    for file in sorted(os.listdir(result_path)):
        if not os.path.getsize(f'{result_path}/{file}') == 0:
            output = ''
            with open(f'{result_path}/summary.csv', 'r') as summary:
                        reader = csv.reader(summary)
                        output = 'Stats:\n'
                        for row in reader:
                            if row[0] == file.split('_')[0]:
                                output += f'Differences: {row[1]}\nCoding Differences: {row[2]}\nMissing: {row[3]}\nNew: {row[4]}\nTotal: {row[5]} \n\n\n'
            with open(f'{result_path}/{file}', 'r') as f:
                if 'bases' in file:
                    output += 'Base Changes:\n'
                    for line in f:
                        output += line[:-1] + ':\n'
                        output += f.readline() + '\n'
                    bases[file] = output
                else:
                    for line in f:
                        output += f'{line[:-1]}:\n'
                        output += f.readline()
                        output += f.readline()
                        output += f.readline()
                        output += f.readline() + '\n'
                    whole_seq[file] = output
    return bases, whole_seq

# create list of alleles that have been modified
def allele_list(result_path):
    output = set()
    for file in sorted(os.listdir(result_path)):
        if not os.path.getsize(f'{result_path}/{file}') == 0:
            label = os.path.basename(file).split('_')[0]
            output.add(label)
    return sorted(output)

# Create the Treeview
def on_treeview_select(event):
    selected_item = treeview.selection()
    if not selected_item:
        return
    
    selected_item = selected_item[0]
    item_text = treeview.item(selected_item, "text")

    for tab in notebook.tabs():
        notebook.forget(tab)

    base_key = item_text + '_bases.txt'
    whole_seq_key = item_text + '_whole_seq.txt'
    
    if base_key in bases_data.keys():
        #create tab 1
        tab1 = ttk.Frame(notebook)
        canvas1 = tk.Canvas(tab1)
        canvas1.pack(fill=tk.BOTH, expand=True)

        # Create a text widget inside the canvas
        text = f'{bases_data[base_key]}'
        inner_text = tk.Text(canvas1, width=100, height=50)
        inner_text.insert(tk.END, text)
        canvas1.create_window((0, 0), window=inner_text, anchor='nw')
        notebook.add(tab1, text='Bases')

    # create tab 2
    tab2 = ttk.Frame(notebook)
    canvas2 = tk.Canvas(tab2)
    canvas2.pack(fill='both', expand=True)

    # Create a text widget inside the canvas
    text = f'{whole_seq_data[whole_seq_key]}'
    inner_text = tk.Text(canvas2, width=100, height=50)
    inner_text.insert(tk.END, text)
    canvas2.create_window((0, 0), window=inner_text, anchor='nw')
    notebook.add(tab2, text='Whole Sequence')


app = tk.Tk()
app.title('HLA/MICAB Ruleset Configuration')

# Set the window size
app.geometry('1000x650')

# Create results tab
tab_control = ttk.Notebook(app)
analysis_tab = ttk.Frame(tab_control)
tab_control.add(analysis_tab, text='Analyze')
result_tab = ttk.Frame(tab_control)
tab_control.add(result_tab, text='Results')
tab_control.grid(row=0, column=0, sticky="nsew")

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
for i in range(3):
    frame.grid_columnconfigure(i, weight=1)

path_button = tk.Button(frame, text="Show Application Path", command=show_app_path)
path_button.grid(row=0, column=0, columnspan=3, pady=10)

imgt_label = tk.Label(frame, text='IMGTHLA Path:')
imgt_label.grid(row=1, column=0, sticky="e")
imgt_entry = tk.Entry(frame)
imgt_entry.grid(row=1, column=1, sticky="ew", padx=5)
imgt_button = tk.Button(frame, text='Select Path', command=select_imgt_path)
imgt_button.grid(row=1, column=2, padx=5, sticky="ew")

hla_label = tk.Label(frame, text='HLA_Ruleset_Sciscloud Path:')
hla_label.grid(row=2, column=0, sticky="e")
hla_entry = tk.Entry(frame)
hla_entry.grid(row=2, column=1, sticky="ew", padx=5)
hla_button = tk.Button(frame, text='Select Path', command=select_hla_path)
hla_button.grid(row=2, column=2, padx=5, sticky="ew")

micab_label = tk.Label(frame, text='MICAB_Ruleset_Sciscloud Path:')
micab_label.grid(row=3, column=0, sticky="e")
micab_entry = tk.Entry(frame)
micab_entry.grid(row=3, column=1, sticky="ew", padx=5)
micab_button = tk.Button(frame, text='Select Path', command=select_micab_path)
micab_button.grid(row=3, column=2, padx=5, sticky="ew")

results_label = tk.Label(frame, text='Results Path:')
results_label.grid(row=4, column=0, sticky="e")
results_entry = tk.Entry(frame)
results_entry.grid(row=4, column=1, sticky="ew", padx=5)
results_button = tk.Button(frame, text='Select Path', command=select_results_path)
results_button.grid(row=4, column=2, padx=5, sticky="ew")

run_button = tk.Button(frame, text='Run', command=run_analysis)
run_button.grid(row=5, column=0, columnspan=3, pady=10)

output_text = scrolledtext.ScrolledText(frame, height=20)
output_text.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=10)

# Create Treeview
treeview = ttk.Treeview(result_tab, columns=("Allele"))
treeview.heading("#0", text="Allele")
for allele in allele_list('/Users/assafgolan/Projects/Scisco-Genetics/7.31.24/out/verify/sequences/'):
    treeview.insert("", "end", text=allele)
treeview.pack(side=tk.LEFT, fill=tk.Y)

# create output text dictionaries
bases_data, whole_seq_data = create_output_text('/Users/assafgolan/Projects/Scisco-Genetics/7.31.24/out/verify/sequences/')

# Bind the selection event
treeview.bind("<<TreeviewSelect>>", on_treeview_select)

notebook = ttk.Notebook(result_tab)
notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

frame.rowconfigure(6, weight=1)

app.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()
