import tkinter as tk
from tkinter import ttk, messagebox

from logic.rep_logic import add_rep, get_all_reps, set_rep_status, update_rep


class RepsUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")
        self._editing_id = None

        tk.Label(
            self,
            text="Reps",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
        ).pack(pady=12)

        self.mode_label = tk.Label(
            self,
            text="New rep",
            font=("Arial", 11, "italic"),
            bg="#ecf0f1",
        )
        self.mode_label.pack()

        form = tk.LabelFrame(self, text="Details", bg="#ecf0f1")
        form.pack(fill="x", padx=16, pady=8)
        tk.Label(form, text="Name *", bg="#ecf0f1").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.name_e = tk.Entry(form, width=40)
        self.name_e.grid(row=0, column=1, padx=6, pady=6, sticky="we")

        btn_row = tk.Frame(self, bg="#ecf0f1")
        btn_row.pack(pady=8)
        for text, cmd, color in (
            ("Add rep", self._add_rep, "#27ae60"),
            ("Save changes", self._save_changes, "#2980b9"),
            ("Clear / new", self._clear_form, "#7f8c8d"),
            ("Load selected", self._load_selected, "#34495e"),
        ):
            tk.Button(
                btn_row,
                text=text,
                command=cmd,
                bg=color,
                fg="white",
                relief="flat",
                width=14,
            ).pack(side="left", padx=4)

        btn_row2 = tk.Frame(self, bg="#ecf0f1")
        btn_row2.pack(pady=4)
        tk.Button(
            btn_row2,
            text="Deactivate selected",
            command=lambda: self._set_status_selected("inactive"),
            bg="#c0392b",
            fg="white",
            relief="flat",
            width=18,
        ).pack(side="left", padx=4)
        tk.Button(
            btn_row2,
            text="Activate selected",
            command=lambda: self._set_status_selected("active"),
            bg="#16a085",
            fg="white",
            relief="flat",
            width=18,
        ).pack(side="left", padx=4)

        list_frame = tk.LabelFrame(self, text="All reps", bg="#ecf0f1")
        list_frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("ID", "Name", "Status")
        self.table = ttk.Treeview(list_frame, columns=columns, show="headings", height=14)
        for col, w in zip(columns, (50, 280, 100)):
            self.table.heading(col, text=col)
            self.table.column(col, width=w)
        vs = ttk.Scrollbar(list_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vs.set)
        self.table.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        self.table.bind("<Double-1>", lambda _e: self._load_selected())

        self._clear_form()
        self._refresh_table()

    def _clear_form(self):
        self._editing_id = None
        self.mode_label.config(text="New rep")
        self.name_e.delete(0, tk.END)

    def _refresh_table(self):
        for iid in self.table.get_children():
            self.table.delete(iid)
        for r in get_all_reps():
            self.table.insert("", "end", values=(r.id, r.name, r.status))

    def _add_rep(self):
        try:
            add_rep(self.name_e.get())
        except ValueError as exc:
            messagebox.showerror("Reps", str(exc))
            return
        self._clear_form()
        self._refresh_table()
        messagebox.showinfo("Reps", "Rep added.")

    def _save_changes(self):
        if self._editing_id is None:
            messagebox.showinfo("Reps", "Load a rep first, or use Add rep.")
            return
        try:
            update_rep(self._editing_id, self.name_e.get())
        except ValueError as exc:
            messagebox.showerror("Reps", str(exc))
            return
        self._refresh_table()
        messagebox.showinfo("Reps", "Saved.")

    def _load_selected(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showinfo("Reps", "Select a row in the table.")
            return
        vals = self.table.item(sel[0], "values")
        try:
            rid = int(vals[0])
        except (ValueError, IndexError):
            return
        reps = {r.id: r for r in get_all_reps()}
        r = reps.get(rid)
        if not r:
            self._refresh_table()
            return
        self._editing_id = rid
        self.mode_label.config(text=f"Editing rep #{rid}")
        self.name_e.delete(0, tk.END)
        self.name_e.insert(0, r.name)

    def _set_status_selected(self, status):
        sel = self.table.selection()
        if not sel:
            messagebox.showinfo("Reps", "Select a row in the table.")
            return
        try:
            rid = int(self.table.item(sel[0], "values")[0])
        except (ValueError, IndexError):
            return
        try:
            set_rep_status(rid, status)
        except ValueError as exc:
            messagebox.showerror("Reps", str(exc))
            return
        self._refresh_table()
        if self._editing_id == rid:
            self._clear_form()
