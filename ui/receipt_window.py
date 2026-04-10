import os
import platform
import tempfile
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, filedialog

from logic.sales_logic import get_sale_by_id

RECEIPT_DISCLAIMER = (
    "This receipt is issued for distribution records only. "
    "Verify batch numbers and expiry on physical packaging before use. "
    "No warranty beyond manufacturer terms."
)


def format_receipt_text(data):
    """Plain-text receipt body from get_sale_by_id() dict."""
    lines = []
    w = 52
    lines.append("PHARMA DISTRIBUTION — SALES RECEIPT".center(w))
    lines.append("=" * w)
    lines.append(f"Bill No:     {data['sale_id']}")
    lines.append(f"Sale Date:   {data['date']}")
    lines.append(f"Issued:      {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Rep:         {data['rep_name']}")
    lines.append(f"Area:        {data['area_name']}")
    cust = data.get("customer_name") or "—"
    lines.append(f"Customer:    {cust}")
    lines.append("=" * w)

    for row in data["lines"]:
        lines.append(f"{row['product_name']}  (batch: {row['batch']})")
        lines.append(
            f"  MRP {row['mrp']:.2f}  TP {row['trade_price']:.2f}  "
            f"Qty {row['quantity']}  Line disc {row['discount']:.2f}"
        )
        lines.append(
            f"  Net unit {row['unit_net']:.2f}  Line total {row['line_total']:.2f}"
        )
        lines.append("-" * w)

    lines.append(f"Total line discounts:     {data['total_discount']:.2f}")
    lines.append(f"BILL TOTAL:               {data['net_amount']:.2f}")
    lines.append("=" * w)
    lines.append(RECEIPT_DISCLAIMER)
    lines.append("")
    return "\n".join(lines)


def _write_temp_receipt(text):
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="pharma_receipt_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        os.close(fd)
        raise
    return path


def _remove_later(path, delay_sec=8.0):
    def _run():
        time.sleep(delay_sec)
        try:
            os.remove(path)
        except OSError:
            pass

    threading.Thread(target=_run, daemon=True).start()


def print_receipt_text(text, parent=None):
    """Send plain text to default printer on Windows; else prompt to save."""
    path = _write_temp_receipt(text)
    try:
        if platform.system() == "Windows":
            os.startfile(path, "print")
            _remove_later(path)
        else:
            if parent:
                messagebox.showinfo(
                    "Print",
                    "Use Save copy, then print the file from your system.",
                    parent=parent,
                )
            try:
                os.remove(path)
            except OSError:
                pass
    except Exception:
        try:
            os.remove(path)
        except OSError:
            pass
        raise


def open_receipt_window(parent, sale_id):
    """Show receipt UI for sale_id. Returns True if window was opened."""
    data = get_sale_by_id(sale_id)
    if not data:
        messagebox.showerror("Not found", f"No sale with ID {sale_id}.", parent=parent)
        return False
    ReceiptWindow(parent, sale_id, data)
    return True


class ReceiptWindow(tk.Toplevel):
    def __init__(self, parent, sale_id, data):
        super().__init__(parent)
        self._sale_id = sale_id
        self.title(f"Receipt — Sale #{sale_id}")
        self.geometry("520x640")
        self.minsize(400, 400)

        self._text_body = format_receipt_text(data)

        tk.Label(
            self,
            text=f"Receipt — Bill #{sale_id}",
            font=("Arial", 14, "bold"),
        ).pack(pady=8)

        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=4)

        scroll = tk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")

        self.txt = tk.Text(
            frame,
            wrap="word",
            font=("Consolas", 10),
            yscrollcommand=scroll.set,
            state="normal",
        )
        self.txt.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.txt.yview)

        self.txt.insert("1.0", self._text_body)
        self.txt.config(state="disabled")

        btn_row = tk.Frame(self)
        btn_row.pack(pady=10)

        tk.Button(btn_row, text="Print", command=self._on_print, width=12).pack(
            side="left", padx=5
        )
        tk.Button(btn_row, text="Save copy…", command=self._on_save, width=12).pack(
            side="left", padx=5
        )
        tk.Button(btn_row, text="Close", command=self.destroy, width=12).pack(
            side="left", padx=5
        )

        self.transient(parent)
        self.grab_set()

    def _on_print(self):
        try:
            print_receipt_text(self._text_body, parent=self)
        except OSError as exc:
            messagebox.showerror("Print failed", str(exc), parent=self)

    def _on_save(self):
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
            initialfile=f"receipt_sale_{self._sale_id}.txt",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._text_body)
            messagebox.showinfo("Saved", f"Receipt saved to:\n{path}", parent=self)
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc), parent=self)
