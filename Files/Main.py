"""
Stock Analysis Dashboard
This application provides a GUI interface for data analysis on
stock data fetched from Yahoo Finance.

Developer: Hayden Schmidt
Last update: Dec 4, 2025

Current Features:
Data Analysis
- Fetch and graph stock data
- Graph of linear regression and moving average
- Saving, loading, and fetching saved data

Simple GUI
- Generates a GUI with buttons that call functions
- Generates all graphs in the main window

Long-term:
Data Analysis
 - create list of stocks to automate

Split into multiple classes
Streamline automated trading
Revamp GUI
Machine Learning
update ML
Convert into application
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import shutil
from datetime import timedelta

"""
import trader
Add button functionality to GUI:
   trader.main()
"""

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Analysis Dashboard (Scrollable Inline Dashboard)")
        self.root.geometry("1100x800")
        self.root.configure(bg="#f8f9fa")

        # Data
        self.df = pd.DataFrame()

        # Save / Archive folders (use cwd subfolders to avoid user-specific paths)
        base = os.path.join(os.getcwd(), "Application")
        self.source_folder = os.path.join(base, "SavedData")
        self.archive_folder = os.path.join(base, "Archive")
        self.create_folders()

        # Track embedded canvases (for clearing)
        self.plot_canvases = []

        # Build GUI
        self.create_widgets()

    # Folder / Save Helpers
    def create_folders(self):
        os.makedirs(self.source_folder, exist_ok=True)
        os.makedirs(self.archive_folder, exist_ok=True)

    def save_and_archive(self, df, figs: list, notes: str, filename_prefix: str):
        """
        Save DataFrame as CSV, save each figure as PNG, save notes text.
        Then move saved files to archive.
        figs: list of tuples (fig_obj, suffix)
        """
        try:
            # CSV
            csv_path = os.path.join(self.source_folder, f"{filename_prefix}.csv")
            df.to_csv(csv_path, index=True)

            # PNGs
            for fig, suffix in figs:
                png_path = os.path.join(self.source_folder, f"{filename_prefix}_{suffix}.png")
                fig.savefig(png_path)

            # Notes
            txt_path = os.path.join(self.source_folder, f"{filename_prefix}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(notes)

        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving dashboard:\n{e}")
            return

        # Archive (move files to archive folder)
        self.archive_files()

    def archive_files(self):
        try:
            files = os.listdir(self.source_folder)
        except Exception as e:
            messagebox.showerror("Archive Error", f"Could not read folder:\n{e}")
            return

        moved = 0
        for file in files:
            src = os.path.join(self.source_folder, file)
            if os.path.isfile(src):
                try:
                    shutil.move(src, os.path.join(self.archive_folder, file))
                    moved += 1
                except Exception as e:
                    messagebox.showerror("Archive Error", f"Could not move {file}:\n{e}")

        messagebox.showinfo("Success", f"Saved & Archived {moved} file(s).")

    # GUI Layout
    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self.root,
            text="Stock Analysis Dashboard",
            font=("Segoe UI", 18, "bold"),
            bg="#f8f9fa",
            fg="#212529",
        )
        title_label.pack(pady=8)

        # Input frame
        input_frame = tk.Frame(self.root, bg="#f8f9fa")
        input_frame.pack(fill="x", padx=12, pady=6)

        tk.Label(input_frame, text="Ticker:", bg="#f8f9fa").grid(row=0, column=0, sticky="w")
        self.ticker_entry = tk.Entry(input_frame, width=10)
        self.ticker_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Period (e.g. 6mo, 1y):", bg="#f8f9fa").grid(row=0, column=2, sticky="w")
        self.period_entry = tk.Entry(input_frame, width=10)
        self.period_entry.insert(0, "6mo")
        self.period_entry.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="MA Days:", bg="#f8f9fa").grid(row=0, column=4, sticky="w")
        self.ma_entry = tk.Entry(input_frame, width=6)
        self.ma_entry.insert(0, "20")
        self.ma_entry.grid(row=0, column=5, padx=5)

        fetch_btn = tk.Button(
            input_frame, text="Fetch Data", command=self.fetch_data,
            bg="#0d6efd", fg="white", relief="flat", padx=8
        )
        fetch_btn.grid(row=0, column=6, padx=8)

        gen_btn = tk.Button(
            input_frame, text="Generate Dashboard", command=self.generate_dashboard,
            bg="#198754", fg="white", relief="flat", padx=8
        )
        gen_btn.grid(row=0, column=7, padx=8)

        save_btn = tk.Button(
            input_frame, text="Save Dashboard", command=self.save_dashboard,
            bg="#0d6efd", fg="white", relief="flat", padx=8
        )
        save_btn.grid(row=0, column=8, padx=8)

        load_btn = tk.Button(
            input_frame, text="Load Saved Data", command=self.load_saved_data,
            bg="#6f42c1", fg="white", relief="flat", padx=8
        )
        load_btn.grid(row=0, column=9, padx=8)

        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Enter a stock ticker to begin.",
            bg="#f8f9fa",
            fg="#6c757d",
            font=("Segoe UI", 10, "italic"),
        )
        self.status_label.pack(pady=4)

        # Create a frame that will hold a canvas + scrollbars for inner content
        outer_frame = tk.Frame(self.root, bg="#f8f9fa")
        outer_frame.pack(fill="both", expand=True, padx=12, pady=(0,12))

        # Vertical scrollbar
        v_scroll = tk.Scrollbar(outer_frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas
        self.canvas = tk.Canvas(outer_frame, bg="#ffffff", yscrollcommand=v_scroll.set)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

        v_scroll.config(command=self.canvas.yview)

        # Inner frame inside canvas where for charts and stats
        self.inner_frame = tk.Frame(self.canvas, bg="#ffffff")
        self.inner_id = self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw")

        # Bind resize/scroll events
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Help message inside inner frame
        self.placeholder_label = tk.Label(self.inner_frame, text="Dashboard will appear here after you generate it.",
                                          bg="#ffffff", fg="#6c757d", font=("Segoe UI", 12), padx=10, pady=20)
        self.placeholder_label.pack(pady=10)

    def _on_frame_configure(self, event=None):
        # Update scrollregion to match inner frame size
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Make inner frame width match canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.inner_id, width=canvas_width)

    # Data Fetching
    def fetch_data(self):
        ticker = self.ticker_entry.get().strip().upper()
        period = self.period_entry.get().strip()

        if not ticker:
            messagebox.showwarning("Input Error", "Please enter a ticker.")
            return

        try:
            df = yf.download(ticker, period=period, auto_adjust=True, progress=False)

            # If result has MultiIndex columns (rare), flatten them
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

            if df.empty:
                raise ValueError("No data returned for that ticker / period.")

            # Ensure DatetimeIndex
            if not isinstance(df.index, pd.DatetimeIndex):
                df = df.reset_index()
                # Ensure DatetimeIndex is proper
                if "Date" in df.columns:
                    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                    df.set_index("Date", inplace=True)

            self.df = df.copy()
            self.status_label.config(text=f"Loaded {ticker} ({period})", fg="#198754")

        except Exception as e:
            messagebox.showerror("Fetch Error", f"Failed to fetch data:\n{e}")
            self.status_label.config(text="Failed to load data", fg="#dc3545")

    # Dashboard (in-place, scrollable)
    def clear_dashboard(self):
        # Clear previous Matplotlib canvases and widgets inside inner_frame
        for canvas in self.plot_canvases:
            try:
                canvas.get_tk_widget().destroy()
            except Exception:
                pass
        self.plot_canvases = []

        # Destroy other widgets except keep placeholder ref handled below
        for child in self.inner_frame.winfo_children():
            child.destroy()

    def _create_matplotlib_canvas(self, fig, parent):
        """Helper: embed a Matplotlib figure into parent frame and track it for later clearing."""
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True, pady=8)
        self.plot_canvases.append(canvas)
        return canvas

    def generate_dashboard(self):
        """
        Build several plots and stats inside the inner scrollable frame.
        Each plot is its own Matplotlib figure so it stacks nicely and scrolls.
        """
        if self.df.empty:
            messagebox.showwarning("No Data", "Fetch data first.")
            return

        # Remove old contents
        self.clear_dashboard()

        # Stats panel (top)
        stats_frame = tk.Frame(self.inner_frame, bg="#f8f9fa", padx=8, pady=8)
        stats_frame.pack(fill="x", pady=(6, 6))

        ticker = self.ticker_entry.get().strip().upper() or "Ticker"
        # Compute stats
        try:
            close = self.df["Close"]
            avg = close.mean()
            vol = close.std()
            max_ = close.max()
            min_ = close.min()
            rows = len(self.df)
        except Exception as e:
            messagebox.showerror("Stats Error", f"Could not compute stats:\n{e}")
            return

        stats_text = (
            f"Ticker: {ticker}\n"
            f"Rows: {rows}\n"
            f"Average Close: ${avg:.2f}\n"
            f"Volatility (std): ${vol:.2f}\n"
            f"Max: ${max_:.2f}\n"
            f"Min: ${min_:.2f}"
        )

        lbl = tk.Label(stats_frame, text=stats_text, justify="left", font=("Segoe UI", 11), bg="#f8f9fa")
        lbl.pack(side="left", anchor="w")

        # Add small buttons near stats for quick actions
        btn_frame = tk.Frame(stats_frame, bg="#f8f9fa")
        btn_frame.pack(side="right", anchor="e")
        ttk.Button(btn_frame, text="Save Snapshot", command=self.save_dashboard).pack(side="right", padx=4)

        # Plot 1: Price + MA
        fig1 = plt.Figure(figsize=(10, 4))
        ax1 = fig1.add_subplot(111)

        try:
            ma_days = int(self.ma_entry.get())
            self.df["MA"] = self.df["Close"].rolling(ma_days).mean()
        except Exception:
            self.df["MA"] = self.df["Close"]

        ax1.plot(self.df.index, self.df["Close"], label="Close")
        ax1.plot(self.df.index, self.df["MA"], label=f"{self.ma_entry.get()}-Day MA")
        ax1.set_title(f"{ticker} Close Price + MA")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Price")
        ax1.legend()
        fig1.tight_layout()

        self._create_matplotlib_canvas(fig1, self.inner_frame)

        # Plot 2: Volume
        fig2 = plt.Figure(figsize=(10, 3))
        ax2 = fig2.add_subplot(111)
        ax2.bar(self.df.index, self.df["Volume"], width=0.8)
        ax2.set_title(f"{ticker} Volume")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Volume")
        fig2.tight_layout()

        self._create_matplotlib_canvas(fig2, self.inner_frame)

        # Plot 3: Forecast (Linear Regression)
        future_days = 30
        close_values = self.df["Close"].values
        x = np.arange(len(close_values))

        # Fit linear regression (degree=1)
        try:
            slope, intercept = np.polyfit(x, close_values, 1)
            trend = slope * x + intercept

            # Future x and dates
            x_future = np.arange(len(close_values) + future_days)
            trend_future = slope * x_future + intercept

            # Build future date index (start after last date)
            last_date = self.df.index[-1]
            future_index = pd.date_range(start=last_date + timedelta(days=1), periods=future_days)

            fig3 = plt.Figure(figsize=(10, 4))
            ax3 = fig3.add_subplot(111)

            ax3.plot(self.df.index, close_values, label="Actual")
            ax3.plot(self.df.index, trend, label="Trendline (linear fit)")
            # Plot forecast dotted (only the future portion)
            ax3.plot(future_index, trend_future[-future_days:], linestyle="--", label=f"{future_days}-day Forecast")
            ax3.set_title(f"{ticker} Linear Forecast (next {future_days} days)")
            ax3.set_xlabel("Date")
            ax3.set_ylabel("Price")
            ax3.legend()
            fig3.tight_layout()

            self._create_matplotlib_canvas(fig3, self.inner_frame)

        except Exception as e:
            # If regression fails, show a small message widget instead of a chart
            err_lbl = tk.Label(self.inner_frame, text=f"Could not compute forecast: {e}",
                               fg="red", bg="#ffffff", font=("Segoe UI", 10))
            err_lbl.pack(pady=6)

        # Final status update & scroll to top
        self.status_label.config(text=f"Dashboard generated for {ticker}", fg="#0d6efd")
        self.canvas.yview_moveto(0.0)

    # Save / Load / Delete saved data (for convenience)
    def save_dashboard(self):
        if self.df.empty:
            messagebox.showwarning("No Data", "Please fetch data first.")
            return

        # Ask for a filename prefix
        filename = filedialog.asksaveasfilename(
            title="Save Dashboard (will save CSV + PNGs temporarily then archive)",
            defaultextension=".csv",
            initialdir=self.source_folder,
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=f"{self.ticker_entry.get().strip().upper() or 'stock'}_data"
        )
        if not filename:
            return

        # Derive a filename prefix (without extension)
        prefix = os.path.splitext(os.path.basename(filename))[0]

        # Create figures again to save them
        figs_to_save = []

        try:
            # Price + MA
            fig1 = plt.Figure(figsize=(10, 4))
            ax1 = fig1.add_subplot(111)
            ax1.plot(self.df.index, self.df["Close"], label="Close")
            ax1.plot(self.df.index, self.df.get("MA", self.df["Close"]), label=f"{self.ma_entry.get()}-Day MA")
            ax1.set_title("Close Price + MA")
            ax1.legend()
            fig1.tight_layout()
            figs_to_save.append((fig1, "price_ma"))

            # Volume
            fig2 = plt.Figure(figsize=(10, 3))
            ax2 = fig2.add_subplot(111)
            ax2.bar(self.df.index, self.df["Volume"], width=0.8)
            ax2.set_title("Volume")
            fig2.tight_layout()
            figs_to_save.append((fig2, "volume"))

            # Forecast (same linear regression)
            future_days = 30
            close_values = self.df["Close"].values
            x = np.arange(len(close_values))
            slope, intercept = np.polyfit(x, close_values, 1)
            x_future = np.arange(len(close_values) + future_days)
            trend_future = slope * x_future + intercept
            last_date = self.df.index[-1]
            future_index = pd.date_range(start=last_date + timedelta(days=1), periods=future_days)

            fig3 = plt.Figure(figsize=(10, 4))
            ax3 = fig3.add_subplot(111)
            ax3.plot(self.df.index, close_values, label="Actual")
            ax3.plot(self.df.index, slope * x + intercept, label="Trend")
            ax3.plot(future_index, trend_future[-future_days:], linestyle="--", label=f"{future_days}-day Forecast")
            ax3.set_title("Forecast")
            ax3.legend()
            fig3.tight_layout()
            figs_to_save.append((fig3, "forecast"))

            notes = f"Saved dashboard for {self.ticker_entry.get().strip().upper()}\nRows: {len(self.df)}"

            self.save_and_archive(self.df, figs_to_save, notes, prefix)

        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save dashboard:\n{e}")

    # Load / Delete saved CSV from archive (optional helpers)
    def load_saved_data(self):
        file_path = filedialog.askopenfilename(
            title="Select Saved CSV",
            filetypes=[("CSV Files", "*.csv")],
            initialdir=self.archive_folder
        )
        if not file_path:
            return

        try:
            df = pd.read_csv(file_path)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                df.set_index("Date", inplace=True)
            self.df = df
            self.status_label.config(text=f"Loaded saved data: {os.path.basename(file_path)}", fg="#0d6efd")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load file:\n{e}")



# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
