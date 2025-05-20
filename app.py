import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ChoreSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chore Scheduler")

        self.chores = []
        self.dependencies = []

        chore_frame = tk.LabelFrame(root, text="Chores (Chore,Time)")
        chore_frame.pack(fill="x", padx=10, pady=5)
        self.chore_listbox = tk.Listbox(chore_frame, height=5)
        self.chore_listbox.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        chore_btn_frame = tk.Frame(chore_frame)
        chore_btn_frame.pack(side="right", fill="y")
        tk.Button(chore_btn_frame, text="Add", command=self.add_chore).pack(fill="x")
        tk.Button(chore_btn_frame, text="Remove", command=self.remove_chore).pack(fill="x")

        dep_frame = tk.LabelFrame(root, text="Dependencies (Before,After)")
        dep_frame.pack(fill="x", padx=10, pady=5)
        self.dep_listbox = tk.Listbox(dep_frame, height=5)
        self.dep_listbox.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        dep_btn_frame = tk.Frame(dep_frame)
        dep_btn_frame.pack(side="right", fill="y")
        tk.Button(dep_btn_frame, text="Add", command=self.add_dependency).pack(fill="x")
        tk.Button(dep_btn_frame, text="Remove", command=self.remove_dependency).pack(fill="x")

        sel_frame = tk.Frame(root)
        sel_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(sel_frame, text="Start:").pack(side="left")
        self.start_var = tk.StringVar()
        self.start_menu = ttk.Combobox(sel_frame, textvariable=self.start_var, state="readonly")
        self.start_menu.pack(side="left", padx=5)
        tk.Label(sel_frame, text="End:").pack(side="left")
        self.end_var = tk.StringVar()
        self.end_menu = ttk.Combobox(sel_frame, textvariable=self.end_var, state="readonly")
        self.end_menu.pack(side="left", padx=5)
        tk.Button(sel_frame, text="Update Choices", command=self.update_choices).pack(side="left", padx=5)

        tk.Button(root, text="Find Optimal Path", command=self.find_path).pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def add_chore(self):
        entry = simpledialog.askstring("Add Chore", "Enter chore and time (e.g. Laundry,120):")
        if entry and "," in entry:
            name, time = entry.split(",", 1)
            name, time = name.strip(), time.strip()
            if not time.isdigit():
                messagebox.showerror("Error", "Time must be a number.")
                return
            self.chores.append((name, int(time)))
            self.chore_listbox.insert("end", f"{name},{time}")
            self.update_choices()

    def remove_chore(self):
        sel = self.chore_listbox.curselection()
        if sel:
            idx = sel[0]
            self.chore_listbox.delete(idx)
            del self.chores[idx]
            self.update_choices()

    def add_dependency(self):
        entry = simpledialog.askstring("Add Dependency", "Enter dependency (Before,After):")
        if entry and "," in entry:
            before, after = entry.split(",", 1)
            before, after = before.strip(), after.strip()
            self.dependencies.append((before, after))
            self.dep_listbox.insert("end", f"{before},{after}")

    def remove_dependency(self):
        sel = self.dep_listbox.curselection()
        if sel:
            idx = sel[0]
            self.dep_listbox.delete(idx)
            del self.dependencies[idx]

    def update_choices(self):
        names = [c[0] for c in self.chores]
        self.start_menu['values'] = names
        self.end_menu['values'] = names
        if names:
            self.start_var.set(names[0])
            self.end_var.set(names[0])

    def find_path(self):
        if not self.chores or not self.dependencies:
            messagebox.showerror("Error", "Please add chores and dependencies.")
            return
        G = nx.DiGraph()
        for name, time in self.chores:
            G.add_node(name, time=time)
        for before, after in self.dependencies:
            if before not in G.nodes or after not in G.nodes:
                messagebox.showerror("Error", f"Dependency {before}->{after} includes unknown chore.")
                return
            G.add_edge(before, after, weight=G.nodes[after]['time'])
        start = self.start_var.get()
        end = self.end_var.get()
        try:
            path = nx.shortest_path(G, source=start, target=end, weight='weight')
            total_time = sum(G.nodes[n]['time'] for n in path)
            messagebox.showinfo("Optimal Path", f"{' -> '.join(path)}\nTotal time: {total_time} minutes")
            self.draw_graph(G, path, start, end)
        except nx.NetworkXNoPath:
            messagebox.showerror("No Path", "No path between selected chores. Please check your dependencies.")

    def draw_graph(self, G, path, start, end):
        self.ax.clear()
        pos = nx.circular_layout(G)
        node_colors = []
        for node in G.nodes():
            if node == start:
                node_colors.append('skyblue')
            elif node == end:
                node_colors.append('orange')
            elif node in path:
                node_colors.append('lightgreen')
            else:
                node_colors.append('lightgrey')
        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=2500, font_size=14, font_weight='bold', ax=self.ax)
        nx.draw_networkx_edges(G, pos, edgelist=[(path[i], path[i+1]) for i in range(len(path)-1)], width=8, edge_color='r', ax=self.ax)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='blue', ax=self.ax)
        self.ax.set_title("Optimal Chore Schedule Path")
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChoreSchedulerApp(root)
    root.mainloop()
