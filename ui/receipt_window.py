import os
import platform
import tempfile
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, filedialog

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

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
    lines.append("NEW QUETTA SURGICAL & MEDICINE DISTRIBUTOR".center(w))
    lines.append("SALES RECEIPT".center(w))
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
        base_amt = row['trade_price'] * row['quantity']
        pct = (row['discount'] / base_amt * 100) if base_amt > 0 else 0
        discount_str = f"{row['discount']:.2f} ({pct:g}%)" if pct > 0 else f"{row['discount']:.2f}"
        
        lines.append(f"{row['product_name']}  (batch: {row['batch']})")
        lines.append(
            f"  MRP {row['mrp']:.2f}  TP {row['trade_price']:.2f}  "
            f"Qty {row['quantity']}  Discount {discount_str}"
        )
        lines.append(
            f"  Net unit {row['unit_net']:.2f}  Line total {row['line_total']:.2f}"
        )
        lines.append("-" * w)

    lines.append(f"Total discount:           {data['total_discount']:.2f}")
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


def generate_receipt_pdf(data, path):
    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading3'], alignment=1)
    
    elements = []
    elements.append(Paragraph("NEW QUETTA SURGICAL & MEDICINE DISTRIBUTOR", title_style))
    elements.append(Paragraph("SALES RECEIPT", subtitle_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    info_data = [
        [f"Bill No: {data['sale_id']}", f"Sale Date: {data['date']}"],
        [f"Rep: {data['rep_name']}", f"Area: {data['area_name']}"],
        [f"Customer: {data.get('customer_name') or '—'}", f"Issued: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    ]
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.2 * inch))
    
    table_data = [["Product", "Batch", "MRP", "TP", "Qty", "Discount", "Net Unit", "Total"]]
    for row in data["lines"]:
        base_amt = row['trade_price'] * row['quantity']
        pct = (row['discount'] / base_amt * 100) if base_amt > 0 else 0
        discount_str = f"{row['discount']:.2f} ({pct:g}%)" if pct > 0 else f"{row['discount']:.2f}"
        table_data.append([
            row['product_name'][:30],
            row['batch'],
            f"{row['mrp']:.2f}",
            f"{row['trade_price']:.2f}",
            str(row['quantity']),
            discount_str,
            f"{row['unit_net']:.2f}",
            f"{row['line_total']:.2f}"
        ])
        
    t = Table(table_data, colWidths=[2.1*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.4*inch, 1.2*inch, 0.7*inch, 0.9*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2c3e50")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('ALIGN', (0,0), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.2 * inch))
    
    summary_data = [
        ["", "Total discount:", f"{data['total_discount']:.2f}"],
        ["", "BILL TOTAL:", f"{data['net_amount']:.2f}"]
    ]
    sum_t = Table(summary_data, colWidths=[4.8*inch, 1.5*inch, 1*inch])
    sum_t.setStyle(TableStyle([
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (1,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (1,1), (-1,1), 11),
    ]))
    elements.append(sum_t)
    elements.append(Spacer(1, 0.4 * inch))
    
    elements.append(Paragraph(RECEIPT_DISCLAIMER, styles["Normal"]))
    doc.build(elements)


def print_receipt_pdf(data, parent=None):
    fd, path = tempfile.mkstemp(suffix=".pdf", prefix="pharma_receipt_")
    os.close(fd)
    try:
        generate_receipt_pdf(data, path)
        if platform.system() == "Windows":
            os.startfile(path, "print")
            _remove_later(path)
        else:
            if parent:
                messagebox.showinfo("Print", "Use Save copy, then print.", parent=parent)
    except Exception as exc:
        messagebox.showerror("Print failed", str(exc), parent=parent)


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
        self._data = data
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
            print_receipt_pdf(self._data, parent=self)
        except OSError as exc:
            messagebox.showerror("Print failed", str(exc), parent=self)

    def _on_save(self):
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All", "*.*")],
            initialfile=f"receipt_sale_{self._sale_id}.pdf",
        )
        if not path:
            return
        try:
            generate_receipt_pdf(self._data, path)
            messagebox.showinfo("Saved", f"Receipt saved to:\n{path}", parent=self)
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc), parent=self)
