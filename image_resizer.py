import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import Canvas, Scrollbar
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os
from pathlib import Path
import threading

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer & Optimizer")
        self.root.geometry("900x600")
        self.root.minsize(750, 500)

        # Variables
        self.image_files = []
        self.preview_images = {}
        self.current_preview_idx = 0
        self.processing = False

        # Create UI
        self.create_widgets()

    def create_scrollable_frame(self, parent):
        """Create a scrollable frame"""
        canvas = Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        return scrollable_frame

    def create_widgets(self):
        # Main container with two panels
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        # Left panel container (scrollable)
        left_container = ttk.Frame(main_container)
        left_container.pack(side='left', fill='both', expand=True, padx=(0, 3))

        # Create scrollable left panel
        left_panel = self.create_scrollable_frame(left_container)

        # Drop zone
        self.create_drop_zone(left_panel)

        # File list
        self.create_file_list(left_panel)

        # Control buttons
        self.create_control_buttons(left_panel)

        # Settings
        self.create_settings(left_panel)

        # Process button
        self.create_process_button(left_panel)

        # Right panel - Preview
        self.create_preview_panel(main_container)

    def create_drop_zone(self, parent):
        drop_frame = ttk.LabelFrame(parent, text="Drop Images Here", padding=5)
        drop_frame.pack(fill='x', pady=(0, 5))

        self.drop_label = tk.Label(
            drop_frame,
            text="Drag & Drop or Click",
            bg='#e8f4f8',
            fg='#2c3e50',
            font=('Arial', 9),
            relief='ridge',
            borderwidth=2,
            height=2,
            cursor='hand2'
        )
        self.drop_label.pack(fill='x', pady=3)

        # Enable drag and drop
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_label.bind('<Button-1>', lambda e: self.browse_images())

    def create_file_list(self, parent):
        list_frame = ttk.LabelFrame(parent, text="Image Files", padding=5)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        # Listbox
        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode='extended',
            font=('Arial', 9)
        )
        self.file_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # Bind selection event
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

    def create_control_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=(0, 5))

        ttk.Button(btn_frame, text="Add", command=self.browse_images, width=8).pack(side='left', padx=1)
        ttk.Button(btn_frame, text="Remove", command=self.remove_selected, width=8).pack(side='left', padx=1)
        ttk.Button(btn_frame, text="Clear", command=self.clear_all, width=8).pack(side='left', padx=1)

        # File count label
        self.file_count_label = ttk.Label(btn_frame, text="0 files", foreground='gray', font=('Arial', 8))
        self.file_count_label.pack(side='right', padx=3)

    def create_settings(self, parent):
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding=5)
        settings_frame.pack(fill='x', pady=(0, 5))

        # Resize mode
        mode_frame = ttk.LabelFrame(settings_frame, text="Resize Mode", padding=3)
        mode_frame.pack(fill='x', pady=(0, 5))

        self.resize_mode = tk.StringVar(value="percentage")

        ttk.Radiobutton(
            mode_frame,
            text="Percentage",
            variable=self.resize_mode,
            value="percentage",
            command=self.update_resize_mode
        ).pack(anchor='w')

        ttk.Radiobutton(
            mode_frame,
            text="Dimensions (W x H)",
            variable=self.resize_mode,
            value="dimensions",
            command=self.update_resize_mode
        ).pack(anchor='w')

        ttk.Radiobutton(
            mode_frame,
            text="Width (auto height)",
            variable=self.resize_mode,
            value="width",
            command=self.update_resize_mode
        ).pack(anchor='w')

        ttk.Radiobutton(
            mode_frame,
            text="Height (auto width)",
            variable=self.resize_mode,
            value="height",
            command=self.update_resize_mode
        ).pack(anchor='w')

        # Resize inputs
        self.resize_input_frame = ttk.Frame(settings_frame)
        self.resize_input_frame.pack(fill='x', pady=(0, 5))

        self.create_resize_inputs()

        # Compression quality
        quality_frame = ttk.LabelFrame(settings_frame, text="Compression", padding=3)
        quality_frame.pack(fill='x', pady=(0, 5))

        self.enable_compression = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            quality_frame,
            text="Enable",
            variable=self.enable_compression
        ).pack(anchor='w')

        quality_slider_frame = ttk.Frame(quality_frame)
        quality_slider_frame.pack(fill='x', pady=2)

        ttk.Label(quality_slider_frame, text="Quality:", font=('Arial', 8)).pack(side='left', padx=(0, 3))
        self.quality_var = tk.IntVar(value=85)
        self.quality_slider = ttk.Scale(
            quality_slider_frame,
            from_=1,
            to=100,
            orient='horizontal',
            variable=self.quality_var,
            command=self.update_quality_label
        )
        self.quality_slider.pack(side='left', fill='x', expand=True, padx=3)

        self.quality_label = ttk.Label(quality_slider_frame, text="85%", width=4, font=('Arial', 8))
        self.quality_label.pack(side='left')

        # Output format
        format_frame = ttk.LabelFrame(settings_frame, text="Format", padding=3)
        format_frame.pack(fill='x', pady=(0, 5))

        self.output_format = tk.StringVar(value="same")

        format_row = ttk.Frame(format_frame)
        format_row.pack(fill='x')

        ttk.Radiobutton(format_row, text="Same", variable=self.output_format, value="same").pack(side='left', padx=2)
        ttk.Radiobutton(format_row, text="JPG", variable=self.output_format, value="jpg").pack(side='left', padx=2)
        ttk.Radiobutton(format_row, text="PNG", variable=self.output_format, value="png").pack(side='left', padx=2)
        ttk.Radiobutton(format_row, text="WEBP", variable=self.output_format, value="webp").pack(side='left', padx=2)

        # Rename pattern
        rename_frame = ttk.LabelFrame(settings_frame, text="Rename", padding=3)
        rename_frame.pack(fill='x', pady=(0, 5))

        self.enable_rename = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            rename_frame,
            text="Enable",
            variable=self.enable_rename,
            command=self.toggle_rename
        ).pack(anchor='w')

        pattern_frame = ttk.Frame(rename_frame)
        pattern_frame.pack(fill='x', pady=2)

        ttk.Label(pattern_frame, text="Pattern:", font=('Arial', 8)).pack(side='left', padx=(0, 3))
        self.rename_pattern = ttk.Entry(pattern_frame, font=('Arial', 8))
        self.rename_pattern.pack(side='left', fill='x', expand=True)
        self.rename_pattern.insert(0, "image_{num:03d}")
        self.rename_pattern.config(state='disabled')

        ttk.Label(
            rename_frame,
            text="Ex: photo_{num:03d} → photo_001.jpg",
            font=('Arial', 7),
            foreground='gray'
        ).pack(anchor='w')

    def create_resize_inputs(self):
        # Clear existing widgets
        for widget in self.resize_input_frame.winfo_children():
            widget.destroy()

        mode = self.resize_mode.get()

        if mode == "percentage":
            frame = ttk.Frame(self.resize_input_frame)
            frame.pack(fill='x')
            ttk.Label(frame, text="Scale:").pack(side='left', padx=(0, 5))
            self.percentage_entry = ttk.Spinbox(frame, from_=1, to=500, width=10)
            self.percentage_entry.pack(side='left', padx=(0, 5))
            self.percentage_entry.set(100)
            ttk.Label(frame, text="%").pack(side='left')

        elif mode == "dimensions":
            frame = ttk.Frame(self.resize_input_frame)
            frame.pack(fill='x')
            ttk.Label(frame, text="Width:").pack(side='left', padx=(0, 5))
            self.width_entry = ttk.Entry(frame, width=10)
            self.width_entry.pack(side='left', padx=(0, 5))
            ttk.Label(frame, text="Height:").pack(side='left', padx=(5, 5))
            self.height_entry = ttk.Entry(frame, width=10)
            self.height_entry.pack(side='left', padx=(0, 5))
            ttk.Label(frame, text="px").pack(side='left')

        elif mode == "width":
            frame = ttk.Frame(self.resize_input_frame)
            frame.pack(fill='x')
            ttk.Label(frame, text="Width:").pack(side='left', padx=(0, 5))
            self.width_entry = ttk.Entry(frame, width=10)
            self.width_entry.pack(side='left', padx=(0, 5))
            ttk.Label(frame, text="px (height auto)").pack(side='left')

        elif mode == "height":
            frame = ttk.Frame(self.resize_input_frame)
            frame.pack(fill='x')
            ttk.Label(frame, text="Height:").pack(side='left', padx=(0, 5))
            self.height_entry = ttk.Entry(frame, width=10)
            self.height_entry.pack(side='left', padx=(0, 5))
            ttk.Label(frame, text="px (width auto)").pack(side='left')

    def create_process_button(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=(0, 5))

        self.process_btn = tk.Button(
            btn_frame,
            text="Process Images",
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            command=self.process_images,
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=10
        )
        self.process_btn.pack(fill='x')

        # Progress bar
        self.progress_frame = ttk.Frame(parent)
        self.progress_frame.pack(fill='x', pady=5)

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', pady=2)

        self.progress_label = ttk.Label(self.progress_frame, text="", foreground='gray')
        self.progress_label.pack()

    def create_preview_panel(self, parent):
        preview_frame = ttk.LabelFrame(parent, text="Preview", padding=5)
        preview_frame.pack(side='right', fill='both', expand=True)

        # Canvas for image preview
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill='both', expand=True)

        self.preview_canvas = Canvas(canvas_frame, bg='#f0f0f0')
        self.preview_canvas.pack(fill='both', expand=True)

        # Image info
        self.info_frame = ttk.Frame(preview_frame)
        self.info_frame.pack(fill='x', pady=5)

        self.original_info_label = ttk.Label(self.info_frame, text="Original: -", font=('Arial', 9))
        self.original_info_label.pack(anchor='w')

        self.preview_info_label = ttk.Label(self.info_frame, text="After resize: -", font=('Arial', 9), foreground='blue')
        self.preview_info_label.pack(anchor='w')

        # Navigation
        nav_frame = ttk.Frame(preview_frame)
        nav_frame.pack(fill='x', pady=5)

        ttk.Button(nav_frame, text="◄ Previous", command=self.prev_preview, width=12).pack(side='left', padx=2)
        self.preview_label = ttk.Label(nav_frame, text="No images")
        self.preview_label.pack(side='left', expand=True)
        ttk.Button(nav_frame, text="Next ►", command=self.next_preview, width=12).pack(side='right', padx=2)

    def update_resize_mode(self):
        self.create_resize_inputs()
        self.update_preview_info()

    def update_quality_label(self, value=None):
        self.quality_label.config(text=f"{int(float(value))}%")
        self.update_preview_info()

    def toggle_rename(self):
        if self.enable_rename.get():
            self.rename_pattern.config(state='normal')
        else:
            self.rename_pattern.config(state='disabled')

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        self.add_images(files)

    def browse_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )
        if files:
            self.add_images(files)

    def add_images(self, files):
        for file in files:
            file = file.strip('{}')  # Remove curly braces from drag-drop
            if os.path.isfile(file) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')):
                if file not in self.image_files:
                    self.image_files.append(file)
                    filename = os.path.basename(file)
                    self.file_listbox.insert('end', filename)

        self.update_file_count()
        if self.image_files and self.current_preview_idx == 0:
            self.show_preview(0)

    def remove_selected(self):
        selected = self.file_listbox.curselection()
        for idx in reversed(selected):
            self.file_listbox.delete(idx)
            del self.image_files[idx]

        self.update_file_count()

        if self.image_files:
            new_idx = min(self.current_preview_idx, len(self.image_files) - 1)
            self.show_preview(new_idx)
        else:
            self.clear_preview()

    def clear_all(self):
        self.file_listbox.delete(0, 'end')
        self.image_files.clear()
        self.preview_images.clear()
        self.current_preview_idx = 0
        self.update_file_count()
        self.clear_preview()

    def update_file_count(self):
        count = len(self.image_files)
        self.file_count_label.config(text=f"{count} file{'s' if count != 1 else ''}")

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            idx = selection[0]
            self.show_preview(idx)

    def show_preview(self, idx):
        if 0 <= idx < len(self.image_files):
            self.current_preview_idx = idx
            image_path = self.image_files[idx]

            try:
                # Load and display original image
                img = Image.open(image_path)
                original_size = img.size
                original_file_size = os.path.getsize(image_path)

                # Display on canvas
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()

                if canvas_width > 1 and canvas_height > 1:
                    display_img = img.copy()
                    display_img.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)

                    self.preview_photo = ImageTk.PhotoImage(display_img)
                    self.preview_canvas.delete("all")
                    self.preview_canvas.create_image(
                        canvas_width // 2, canvas_height // 2,
                        image=self.preview_photo
                    )

                # Update info
                self.original_info_label.config(
                    text=f"Original: {original_size[0]}x{original_size[1]} px, {original_file_size / 1024:.1f} KB"
                )

                self.update_preview_info()

                # Update navigation
                self.preview_label.config(text=f"{idx + 1} / {len(self.image_files)}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")

    def update_preview_info(self):
        if not self.image_files or self.current_preview_idx >= len(self.image_files):
            return

        try:
            image_path = self.image_files[self.current_preview_idx]
            img = Image.open(image_path)
            original_size = img.size

            new_size = self.calculate_new_size(original_size)

            if new_size:
                quality = self.quality_var.get() if self.enable_compression.get() else 95
                estimated_size = self.estimate_file_size(img, new_size, quality)

                self.preview_info_label.config(
                    text=f"After resize: {new_size[0]}x{new_size[1]} px, ~{estimated_size / 1024:.1f} KB"
                )
            else:
                self.preview_info_label.config(text="After resize: (invalid settings)")

        except Exception as e:
            self.preview_info_label.config(text="After resize: -")

    def calculate_new_size(self, original_size):
        mode = self.resize_mode.get()
        width, height = original_size

        try:
            if mode == "percentage":
                percentage = float(self.percentage_entry.get()) / 100
                new_width = int(width * percentage)
                new_height = int(height * percentage)
                return (new_width, new_height)

            elif mode == "dimensions":
                new_width = int(self.width_entry.get())
                new_height = int(self.height_entry.get())
                return (new_width, new_height)

            elif mode == "width":
                new_width = int(self.width_entry.get())
                aspect_ratio = height / width
                new_height = int(new_width * aspect_ratio)
                return (new_width, new_height)

            elif mode == "height":
                new_height = int(self.height_entry.get())
                aspect_ratio = width / height
                new_width = int(new_height * aspect_ratio)
                return (new_width, new_height)

        except (ValueError, tk.TclError):
            return None

    def estimate_file_size(self, img, new_size, quality):
        # Rough estimation based on dimensions and quality
        pixels = new_size[0] * new_size[1]
        base_size = pixels * 3  # RGB

        if quality >= 90:
            compression = 10
        elif quality >= 75:
            compression = 15
        elif quality >= 50:
            compression = 25
        else:
            compression = 40

        return base_size / compression

    def prev_preview(self):
        if self.image_files and self.current_preview_idx > 0:
            self.show_preview(self.current_preview_idx - 1)
            self.file_listbox.selection_clear(0, 'end')
            self.file_listbox.selection_set(self.current_preview_idx)

    def next_preview(self):
        if self.image_files and self.current_preview_idx < len(self.image_files) - 1:
            self.show_preview(self.current_preview_idx + 1)
            self.file_listbox.selection_clear(0, 'end')
            self.file_listbox.selection_set(self.current_preview_idx)

    def clear_preview(self):
        self.preview_canvas.delete("all")
        self.original_info_label.config(text="Original: -")
        self.preview_info_label.config(text="After resize: -")
        self.preview_label.config(text="No images")

    def process_images(self):
        if not self.image_files:
            messagebox.showwarning("Warning", "Please add images first")
            return

        # Validate settings
        new_size = self.calculate_new_size((100, 100))  # Test with dummy size
        if not new_size:
            messagebox.showerror("Error", "Invalid resize settings")
            return

        # Select output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return

        # Start processing in thread
        self.processing = True
        self.process_btn.config(state='disabled', bg='gray')
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Processing...")

        thread = threading.Thread(
            target=self.process_images_thread,
            args=(output_dir,),
            daemon=True
        )
        thread.start()

    def process_images_thread(self, output_dir):
        total = len(self.image_files)
        success_count = 0
        errors = []

        for idx, image_path in enumerate(self.image_files):
            try:
                # Load image
                img = Image.open(image_path)

                # Calculate new size
                new_size = self.calculate_new_size(img.size)

                if new_size and new_size != img.size:
                    # Resize
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Determine output filename
                if self.enable_rename.get():
                    pattern = self.rename_pattern.get()
                    base_name = pattern.replace('{num}', str(idx + 1))
                    base_name = base_name.replace('{num:03d}', f'{idx + 1:03d}')
                    base_name = base_name.replace('{num:04d}', f'{idx + 1:04d}')
                else:
                    base_name = Path(image_path).stem

                # Determine output format
                output_fmt = self.output_format.get()
                if output_fmt == "same":
                    ext = Path(image_path).suffix
                else:
                    ext = f".{output_fmt}"

                output_path = os.path.join(output_dir, f"{base_name}{ext}")

                # Convert image mode if needed
                if ext.lower() in ['.jpg', '.jpeg']:
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Convert to RGB
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = rgb_img

                # Save with compression
                save_kwargs = {}
                if self.enable_compression.get():
                    quality = self.quality_var.get()

                    if ext.lower() in ['.jpg', '.jpeg']:
                        save_kwargs['quality'] = quality
                        save_kwargs['optimize'] = True
                    elif ext.lower() == '.png':
                        save_kwargs['optimize'] = True
                        save_kwargs['compress_level'] = 9 - (quality // 11)
                    elif ext.lower() == '.webp':
                        save_kwargs['quality'] = quality

                img.save(output_path, **save_kwargs)
                success_count += 1

            except Exception as e:
                errors.append(f"{Path(image_path).name}: {str(e)}")

            # Update progress
            progress = (idx + 1) / total * 100
            self.root.after(0, self.update_progress, progress, f"Processing {idx + 1}/{total}")

        # Finished
        self.root.after(0, self.processing_complete, success_count, total, errors, output_dir)

    def update_progress(self, value, text):
        self.progress_bar['value'] = value
        self.progress_label.config(text=text)

    def processing_complete(self, success, total, errors, output_dir):
        self.processing = False
        self.process_btn.config(state='normal', bg='#27ae60')
        self.progress_bar['value'] = 100

        if errors:
            error_msg = f"Processed {success}/{total} images\n\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... and {len(errors) - 5} more errors"
            messagebox.showwarning("Processing Complete with Errors", error_msg)
        else:
            messagebox.showinfo(
                "Success",
                f"Successfully processed {success} images!\n\nSaved to:\n{output_dir}"
            )

        self.progress_label.config(text="Complete!")

def main():
    root = TkinterDnD.Tk()
    app = ImageResizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
