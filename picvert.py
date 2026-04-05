import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

DND_AVAILABLE = False

SUPPORTED_INPUTS = [
    ("Image files", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif *.gif"),
    ("All files", "*.*")
]
OUTPUT_FORMATS = ["Auto", "PNG", "JPEG", "WEBP", "BMP", "TIFF", "GIF"]
VALID_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif"}

THEMES = {
    "dark": {
        "bg": "#111827", "card": "#1f2937", "card2": "#0f172a", "fg": "#f9fafb",
        "muted": "#9ca3af", "accent": "#22c55e", "entry": "#111827", "list": "#0b1220", "sel": "#2563eb"
    },
    "light": {
        "bg": "#f3f4f6", "card": "#ffffff", "card2": "#e5e7eb", "fg": "#111827",
        "muted": "#6b7280", "accent": "#16a34a", "entry": "#ffffff", "list": "#f9fafb", "sel": "#2563eb"
    }
}

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Picvert")
        self.root.geometry("1120x760")
        self.root.minsize(980, 680)
        try:
            self.root.iconbitmap("app.ico")
        except Exception:
            pass

        self.selected_files = []
        self.thumb_refs = []
        self.preview_image = None
        self.output_folder = tk.StringVar(value=os.getcwd())
        self.output_format = tk.StringVar(value="Auto")
        self.resize_enabled = tk.BooleanVar(value=False)
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.quality_var = tk.IntVar(value=95)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_text = tk.StringVar(value="Processed: 0/0 | Remaining: 0 | ETA: --")
        self.status_text = tk.StringVar(value="Ready")
        self.success_text = tk.StringVar(value="Success: 0")
        self.failed_text = tk.StringVar(value="Failed: 0")
        self.theme_mode = tk.StringVar(value="dark")
        self.is_converting = False
        self.start_time = None

        self.setup_style()
        self.build_ui()
        self.apply_theme()

    def colors(self):
        return THEMES[self.theme_mode.get()]

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def apply_theme(self):
        c = self.colors()
        self.root.configure(bg=c["bg"])
        self.style.configure("Dark.TFrame", background=c["bg"])
        self.style.configure("Card.TFrame", background=c["card"])
        self.style.configure("Dark.TLabel", background=c["bg"], foreground=c["fg"], font=("Segoe UI", 10))
        self.style.configure("Muted.TLabel", background=c["bg"], foreground=c["muted"], font=("Segoe UI", 9))
        self.style.configure("Card.TLabel", background=c["card"], foreground=c["fg"], font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background=c["bg"], foreground=c["fg"], font=("Segoe UI", 20, "bold"))
        self.style.configure("SubTitle.TLabel", background=c["bg"], foreground=c["muted"], font=("Segoe UI", 10))
        self.style.configure("Dark.TLabelframe", background=c["card"], foreground=c["fg"])
        self.style.configure("Dark.TLabelframe.Label", background=c["card"], foreground=c["fg"], font=("Segoe UI", 10, "bold"))
        self.style.configure("Dark.TButton", background="#2563eb", foreground="white", padding=8, relief="flat")
        self.style.map("Dark.TButton", background=[("active", "#1d4ed8")])
        self.style.configure("Secondary.TButton", background="#374151", foreground="white", padding=8, relief="flat")
        self.style.map("Secondary.TButton", background=[("active", "#4b5563")])
        self.style.configure("Dark.TCheckbutton", background=c["card"], foreground=c["fg"])
        self.style.configure("Dark.TRadiobutton", background=c["bg"], foreground=c["fg"])
        self.style.configure("Dark.TCombobox", fieldbackground=c["entry"], background=c["entry"], foreground=c["fg"])
        self.style.configure("Horizontal.TProgressbar", troughcolor=c["list"], background=c["accent"], bordercolor=c["list"], lightcolor=c["accent"], darkcolor=c["accent"])

        if hasattr(self, "file_listbox"):
            self.file_listbox.configure(bg=c["list"], fg=c["fg"], selectbackground=c["sel"], selectforeground="white", highlightbackground="#334155")
            self.canvas.configure(bg=c["list"], highlightbackground="#334155")
            
            self.output_entry.configure(bg=c["entry"], fg=c["fg"], insertbackground=c["fg"])
            self.width_entry.configure(bg=c["entry"], fg=c["fg"], insertbackground=c["fg"])
            self.height_entry.configure(bg=c["entry"], fg=c["fg"], insertbackground=c["fg"])
            self.refresh_thumbnails()

    def build_ui(self):
        main = ttk.Frame(self.root, style="Dark.TFrame", padding=16)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main, style="Dark.TFrame")
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="Picvert", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Batch convert, preview, resize, and monitor progress", style="SubTitle.TLabel").pack(anchor="w", pady=(4, 0))

        theme_row = ttk.Frame(header, style="Dark.TFrame")
        theme_row.pack(anchor="e", pady=(6, 0))
        ttk.Label(theme_row, text="Theme:", style="Dark.TLabel").pack(side="left", padx=(0, 8))
        ttk.Radiobutton(theme_row, text="Dark", variable=self.theme_mode, value="dark", style="Dark.TRadiobutton", command=self.apply_theme).pack(side="left")
        ttk.Radiobutton(theme_row, text="Light", variable=self.theme_mode, value="light", style="Dark.TRadiobutton", command=self.apply_theme).pack(side="left", padx=(8, 0))

        body = ttk.Frame(main, style="Dark.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body, style="Dark.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ttk.Frame(body, style="Dark.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        file_frame = ttk.LabelFrame(left, text="1) Select Images", style="Dark.TLabelframe", padding=12)
        file_frame.pack(fill="both", expand=True, pady=(0, 10))

        btn_row = ttk.Frame(file_frame, style="Card.TFrame")
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Add Images", style="Dark.TButton", command=self.add_images).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Add Folder", style="Secondary.TButton", command=self.add_folder).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Remove Selected", style="Secondary.TButton", command=self.remove_selected).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Clear List", style="Secondary.TButton", command=self.clear_files).pack(side="left")
        self.file_count_label = ttk.Label(btn_row, text="No files selected", style="Card.TLabel")
        self.file_count_label.pack(side="right")

        self.file_listbox = tk.Listbox(file_frame, height=8, bd=0, highlightthickness=1)
        self.file_listbox.pack(fill="x", pady=(10, 8))
        self.file_listbox.bind("<<ListboxSelect>>", self.show_preview)

        thumb_container = ttk.Frame(file_frame, style="Card.TFrame")
        thumb_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(thumb_container, height=340, bd=0, highlightthickness=1)
        self.canvas.pack(side="left", fill="both", expand=True)

        thumb_scroll = ttk.Scrollbar(thumb_container, orient="vertical", command=self.canvas.yview)
        thumb_scroll.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=thumb_scroll.set)
        self.thumb_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.thumb_frame, anchor="nw")
        self.thumb_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.drop_hint = ttk.Label(file_frame, text="Use Add Images or Add Folder to load files", style="Muted.TLabel")
        self.drop_hint.pack(anchor="w", pady=(8, 0))

        settings_frame = ttk.LabelFrame(right, text="2) Conversion Settings", style="Dark.TLabelframe", padding=12)
        settings_frame.pack(fill="x", pady=(0, 10))

        fmt_row = ttk.Frame(settings_frame, style="Card.TFrame")
        fmt_row.pack(fill="x", pady=6)
        ttk.Label(fmt_row, text="Output Format:", style="Card.TLabel", width=18).pack(side="left")
        ttk.Combobox(fmt_row, textvariable=self.output_format, values=OUTPUT_FORMATS, state="readonly", width=16, style="Dark.TCombobox").pack(side="left")
        ttk.Label(fmt_row, text="(Auto = keep same format)", style="Muted.TLabel").pack(side="left", padx=(10, 0))

        quality_row = ttk.Frame(settings_frame, style="Card.TFrame")
        quality_row.pack(fill="x", pady=6)
        ttk.Label(quality_row, text="Quality:", style="Card.TLabel", width=18).pack(side="left")
        ttk.Scale(quality_row, from_=1, to=100, variable=self.quality_var, orient="horizontal").pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Label(quality_row, textvariable=self.quality_var, style="Card.TLabel", width=4).pack(side="left")

        resize_row = ttk.Frame(settings_frame, style="Card.TFrame")
        resize_row.pack(fill="x", pady=6)
        ttk.Checkbutton(resize_row, text="Resize image", variable=self.resize_enabled, style="Dark.TCheckbutton").pack(side="left")
        ttk.Label(resize_row, text="Width:", style="Card.TLabel").pack(side="left", padx=(16, 4))
        self.width_entry = tk.Entry(resize_row, textvariable=self.width_var, width=8, relief="flat")
        self.width_entry.pack(side="left")
        ttk.Label(resize_row, text="Height:", style="Card.TLabel").pack(side="left", padx=(12, 4))
        self.height_entry = tk.Entry(resize_row, textvariable=self.height_var, width=8, relief="flat")
        self.height_entry.pack(side="left")

        output_frame = ttk.LabelFrame(right, text="3) Output Folder", style="Dark.TLabelframe", padding=12)
        output_frame.pack(fill="x", pady=(0, 10))
        out_row = ttk.Frame(output_frame, style="Card.TFrame")
        out_row.pack(fill="x")
        self.output_entry = tk.Entry(out_row, textvariable=self.output_folder, relief="flat")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=6)
        ttk.Button(out_row, text="Browse", style="Secondary.TButton", command=self.select_output_folder).pack(side="left")

        progress_frame = ttk.LabelFrame(right, text="4) Progress", style="Dark.TLabelframe", padding=12)
        progress_frame.pack(fill="x", pady=(0, 10))
        ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style="Horizontal.TProgressbar").pack(fill="x", pady=(0, 8))
        ttk.Label(progress_frame, textvariable=self.progress_text, style="Card.TLabel").pack(anchor="w")
        stats = ttk.Frame(progress_frame, style="Card.TFrame")
        stats.pack(fill="x", pady=(6, 0))
        ttk.Label(stats, textvariable=self.success_text, style="Card.TLabel").pack(side="left")
        ttk.Label(stats, textvariable=self.failed_text, style="Card.TLabel").pack(side="left", padx=(20, 0))
        ttk.Label(progress_frame, textvariable=self.status_text, style="Muted.TLabel").pack(anchor="w", pady=(4, 0))

        action_frame = ttk.Frame(right, style="Dark.TFrame")
        action_frame.pack(fill="x")
        ttk.Button(action_frame, text="Convert Images", style="Dark.TButton", command=self.start_conversion).pack(side="left")
        ttk.Button(action_frame, text="Open Output Folder", style="Secondary.TButton", command=self.open_output_folder).pack(side="left", padx=(8, 0))

    def add_images(self):
        files = filedialog.askopenfilenames(title="Select image(s)", filetypes=SUPPORTED_INPUTS)
        self._add_files(files, "Added")

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing images")
        if not folder:
            return
        files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.splitext(f.lower())[1] in VALID_EXTS]
        self._add_files(files, "Folder added")

    def _add_files(self, files, prefix):
        if not files:
            return
        added = 0
        for file in files:
            if os.path.isfile(file) and file not in self.selected_files:
                self.selected_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
                added += 1
        self.update_file_count()
        self.refresh_thumbnails()
        self.status_text.set(f"{prefix}: {added} image(s)")
        if self.file_listbox.size() > 0 and not self.file_listbox.curselection():
            self.file_listbox.selection_set(0)
            self.show_preview()

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except:
            pass


    def remove_selected(self):
        if self.is_converting:
            return
        sel = list(self.file_listbox.curselection())
        if not sel:
            return
        for index in reversed(sel):
            del self.selected_files[index]
            self.file_listbox.delete(index)
        self.update_file_count()
        self.refresh_thumbnails()
        self.status_text.set("Removed selected image(s)")
        if self.file_listbox.size() > 0:
            self.file_listbox.selection_set(0)
            self.show_preview()
        else:
            self.preview_label.config(image="", text="Preview will appear here")

    def clear_files(self):
        if self.is_converting:
            return
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.preview_label.config(image="", text="Preview will appear here")
        self.preview_image = None
        self.update_file_count()
        self.refresh_thumbnails()
        self.progress_var.set(0)
        self.progress_text.set("Processed: 0/0 | Remaining: 0 | ETA: --")
        self.success_text.set("Success: 0")
        self.failed_text.set("Failed: 0")
        self.status_text.set("File list cleared")

    def update_file_count(self):
        count = len(self.selected_files)
        self.file_count_label.config(text=f"{count} file(s) selected" if count else "No files selected")

    def refresh_thumbnails(self):
        for w in self.thumb_frame.winfo_children():
            w.destroy()
        self.thumb_refs.clear()
        c = self.colors()
        cols = 3
        for i, path in enumerate(self.selected_files[:80]):
            try:
                img = Image.open(path)
                img.thumbnail((180, 180))
                photo = ImageTk.PhotoImage(img)
                self.thumb_refs.append(photo)
                cell = tk.Frame(self.thumb_frame, bg=c["card"], bd=1, relief="flat")
                cell.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="nsew")
                lbl = tk.Label(cell, image=photo, bg=c["card"])
                lbl.pack(padx=8, pady=(8, 4))
                name = os.path.basename(path)
                tk.Label(cell, text=(name[:22] + "…") if len(name) > 23 else name, bg=c["card"], fg=c["fg"], font=("Segoe UI", 9)).pack(padx=4, pady=(0, 8))
            except:
                pass

    def show_preview(self, event=None):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        path = self.selected_files[selection[0]]
        try:
            img = Image.open(path)
            img.thumbnail((420, 360))
            self.preview_image = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_image, text="")
        except Exception as e:
            self.preview_label.config(text=f"Preview failed: {e}", image="")

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_folder.set(folder)
            self.status_text.set("Output folder set")

    def open_output_folder(self):
        folder = self.output_folder.get()
        if os.path.isdir(folder):
            os.startfile(folder) if os.name == 'nt' else os.system(f'xdg-open "{folder}"')
        else:
            messagebox.showerror("Error", "Output folder does not exist.")

    def start_conversion(self):
        if self.is_converting:
            return
        threading.Thread(target=self.convert_images, daemon=True).start()

    def convert_images(self):
        if not self.selected_files:
            messagebox.showwarning("No Images", "Please add at least one image.")
            return

        output_dir = self.output_folder.get().strip()
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Invalid Folder", "Please choose a valid output folder.")
            return

        resize = self.resize_enabled.get()
        width = height = None
        if resize:
            try:
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                if width <= 0 or height <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Size", "Please enter valid width and height.")
                return

        self.is_converting = True
        self.start_time = time.time()
        total = len(self.selected_files)
        success = 0
        failed = 0
        failed_files = []

        for i, path in enumerate(self.selected_files, start=1):
            try:
                with Image.open(path) as img:
                    source_ext = os.path.splitext(path)[1].lower().replace(".", "")
                    fmt = self.output_format.get().upper()
                    if fmt == "AUTO":
                        fmt = "JPEG" if source_ext == "jpg" else source_ext.upper()
                        if fmt == "JPG":
                            fmt = "JPEG"
                        if fmt == "TIF":
                            fmt = "TIFF"

                    if resize:
                        img = img.resize((width, height))

                    if fmt == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                        if path.lower().endswith(".png"):
                            self.root.after(0, lambda: self.status_text.set("Warning: PNG transparency will be removed when saving as JPG"))
                        img = img.convert("RGB")

                    base = os.path.splitext(os.path.basename(path))[0]
                    ext = "jpg" if fmt == "JPEG" else fmt.lower()
                    out_path = os.path.join(output_dir, f"{base}_converted.{ext}")

                    save_kwargs = {}
                    if fmt in ["JPEG", "WEBP"]:
                        save_kwargs["quality"] = int(self.quality_var.get())
                    if fmt == "JPEG":
                        save_kwargs["optimize"] = True

                    img.save(out_path, fmt, **save_kwargs)
                    success += 1
            except Exception as e:
                failed += 1
                failed_files.append(f"{os.path.basename(path)} -> {e}")

            elapsed = time.time() - self.start_time
            avg = elapsed / i
            remaining = total - i
            eta = int(avg * remaining)
            eta_text = f"{eta}s" if eta < 60 else f"{eta//60}m {eta%60}s"
            percent = (i / total) * 100

            self.root.after(0, self.progress_var.set, percent)
            self.root.after(0, self.progress_text.set, f"Processed: {i}/{total} | Remaining: {remaining} | ETA: {eta_text}")
            self.root.after(0, self.success_text.set, f"Success: {success}")
            self.root.after(0, self.failed_text.set, f"Failed: {failed}")
            self.root.after(0, self.status_text.set, f"Converting: {os.path.basename(path)}")

        self.is_converting = False
        final_msg = f"Successfully converted {success} image(s).\nFailed: {failed}"
        if failed_files:
            final_msg += "\n\nFailed files:\n" + "\n".join(failed_files[:10])
        self.root.after(0, self.status_text.set, "Conversion complete")
        self.root.after(0, lambda: messagebox.showinfo("Conversion Complete", final_msg))

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        raise SystemExit("Pillow is required. Install it using: pip install pillow")

    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()
