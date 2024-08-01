import tkinter as tk
from tkinter import ttk

def on_treeview_select(event):
    selected_item = treeview.selection()
    if not selected_item:
        return

    selected_item = selected_item[0]
    item_text = treeview.item(selected_item, "text")

    # Clear the notebook before adding new tabs
    for tab in notebook.tabs():
        notebook.forget(tab)

    if item_text == "Option 1":
        tab1 = ttk.Frame(notebook)
        canvas1 = tk.Canvas(tab1, width=200, height=200, bg="lightblue")
        canvas1.pack(fill=tk.BOTH, expand=True)
        canvas1.create_text(100, 100, text="This is Option 1", font=("Arial", 16))
        notebook.add(tab1, text="Option 1 - Canvas 1")
        
        tab2 = ttk.Frame(notebook)
        canvas2 = tk.Canvas(tab2, width=200, height=200, bg="lightgreen")
        canvas2.pack(fill=tk.BOTH, expand=True)
        canvas2.create_text(100, 100, text="Another view for Option 1", font=("Arial", 16))
        notebook.add(tab2, text="Option 1 - Canvas 2")
        
    elif item_text == "Option 2":
        tab1 = ttk.Frame(notebook)
        canvas1 = tk.Canvas(tab1, width=200, height=200, bg="lightcoral")
        canvas1.pack(fill=tk.BOTH, expand=True)
        canvas1.create_text(100, 100, text="This is Option 2", font=("Arial", 16))
        notebook.add(tab1, text="Option 2 - Canvas 1")
        
        tab2 = ttk.Frame(notebook)
        canvas2 = tk.Canvas(tab2, width=200, height=200, bg="lightyellow")
        canvas2.pack(fill=tk.BOTH, expand=True)
        canvas2.create_text(100, 100, text="Another view for Option 2", font=("Arial", 16))
        notebook.add(tab2, text="Option 2 - Canvas 2")

app = tk.Tk()
app.title("Treeview with Canvas Tabs")

# Create the Treeview
treeview = ttk.Treeview(app, columns=("Description"))
treeview.heading("#0", text="Options")
treeview.heading("Description", text="Description")
treeview.insert("", "end", text="Option 1")
treeview.insert("", "end", text="Option 2")
treeview.pack(side=tk.LEFT, fill=tk.Y)

# Bind the selection event
treeview.bind("<<TreeviewSelect>>", on_treeview_select)

# Create the Notebook widget
notebook = ttk.Notebook(app)
notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

app.mainloop()
