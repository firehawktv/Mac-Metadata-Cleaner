import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import threading
from datetime import datetime
from tkinter.font import Font
import windnd
import shutil

class DotCleanerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mac Metadata Cleaner")
        self.root.geometry("600x400")
        self.root.minsize(400, 300)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Status variables
        self.status_var = tk.StringVar(value="Drop folders here or click Browse")
        self.progress_var = tk.StringVar(value="")
        self.files_removed = 0
        self.folders_removed = 0
        self.total_size_cleaned = 0
        
        # Define macOS patterns to clean
        self.mac_patterns = {
            'files': [
                '.DS_Store',     # macOS folder metadata
                '._.DS_Store',   # resource fork of .DS_Store
                '.apdisk',       # Apple disk image metadata
            ],
            'file_prefixes': [
                '._',           # resource fork files
            ],
            'folders': [
                '__MACOSX',     # macOS metadata folder
                '.fseventsd',   # Filesystem event metadata
                '.Spotlight-V100', # Spotlight index
                '.TemporaryItems', # Temporary items
            ]
        }
        
        self.create_widgets(main_frame)
        
        # Enable drag and drop for the main window and log area
        windnd.hook_dropfiles(self.root, func=self.handle_drop)
        windnd.hook_dropfiles(self.log_area, func=self.handle_drop)

    def create_widgets(self, frame):
        # Browse button
        browse_btn = ttk.Button(frame, text="Browse", command=self.browse_directory)
        browse_btn.grid(row=0, column=0, pady=5, sticky=tk.W)
        
        # Status label
        status_lbl = ttk.Label(frame, textvariable=self.status_var)
        status_lbl.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Log area
        self.log_area = scrolledtext.ScrolledText(frame, height=15, width=70)
        self.log_area.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Progress frame
        progress_frame = ttk.Frame(frame)
        progress_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        self.progress.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress label
        progress_lbl = ttk.Label(progress_frame, textvariable=self.progress_var)
        progress_lbl.grid(row=0, column=1, padx=(5, 0))
        
        # Try to set monospace font
        try:
            log_font = Font(family="Consolas", size=9)
            self.log_area.configure(font=log_font)
        except:
            pass  # Fall back to default font if Consolas isn't available
            
        self.log_message("Application started successfully")
        self.log_message("Drag and drop folders here or use Browse button")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)

    def handle_drop(self, files):
        """Handle drag and dropped files/folders"""
        for file in files:
            try:
                # Convert bytes to string and normalize path
                path = Path(file.decode('gbk'))  # handles Chinese and other Windows character sets
                if path.is_dir():
                    self.process_directory(str(path))
                else:
                    self.log_message(f"Skipped: {path} (not a directory)")
            except Exception as e:
                self.log_message(f"Error processing dropped item: {str(e)}")

    def browse_directory(self):
        directory = filedialog.askdirectory(parent=self.root)
        if directory:
            self.process_directory(directory)

    def count_cleanable_items(self, directory):
        """Count all files and folders that need to be cleaned."""
        count = 0
        try:
            for root, dirs, files in os.walk(directory):
                # Count matching folders
                count += sum(1 for d in dirs if d in self.mac_patterns['folders'])
                
                # Count matching files
                count += sum(1 for f in files if f in self.mac_patterns['files'])
                count += sum(1 for f in files if any(f.startswith(prefix) for prefix in self.mac_patterns['file_prefixes']))
                
        except Exception as e:
            self.log_message(f"Error counting items: {str(e)}")
        return count

    def process_directory(self, directory):
        try:
            # Reset progress bar
            self.progress['value'] = 0
            self.progress_var.set("Counting items...")
            self.status_var.set(f"Processing: {directory}")
            
            # Count files in a separate thread to prevent GUI freezing
            def start_processing():
                total_items = self.count_cleanable_items(directory)
                if total_items > 0:
                    self.log_message(f"Found {total_items} items to clean")
                    # Start the cleaning process
                    self.clean_directory(directory, total_items)
                else:
                    self.log_message("No macOS metadata found to clean")
                    self.status_var.set("Ready - No items to clean")
                    self.progress_var.set("")
            
            thread = threading.Thread(target=start_processing)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.status_var.set("Error processing directory")
            messagebox.showerror("Error", f"Failed to process directory: {str(e)}")

    def clean_directory(self, directory, total_items):
        try:
            self.files_removed = 0
            self.folders_removed = 0
            self.total_size_cleaned = 0
            items_processed = 0
            
            self.log_message(f"Starting to clean directory: {directory}")
            
            # Walk the directory tree from bottom to top
            for root, dirs, files in os.walk(directory, topdown=False):
                # Remove matching files
                for file in files:
                    file_path = Path(root) / file
                    try:
                        if (file in self.mac_patterns['files'] or 
                            any(file.startswith(prefix) for prefix in self.mac_patterns['file_prefixes'])):
                            size = file_path.stat().st_size
                            file_path.unlink()
                            self.files_removed += 1
                            self.total_size_cleaned += size
                            self.log_message(f"Removed file: {file_path}")
                            items_processed += 1
                            progress = (items_processed / total_items) * 100
                            self.root.after(0, self.update_progress, progress)
                    except Exception as e:
                        self.log_message(f"Error removing file {file_path}: {str(e)}")
                
                # Remove matching folders
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        if dir_name in self.mac_patterns['folders']:
                            # Get folder size before removal
                            size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                            shutil.rmtree(dir_path)
                            self.folders_removed += 1
                            self.total_size_cleaned += size
                            self.log_message(f"Removed folder: {dir_path}")
                            items_processed += 1
                            progress = (items_processed / total_items) * 100
                            self.root.after(0, self.update_progress, progress)
                    except Exception as e:
                        self.log_message(f"Error removing folder {dir_path}: {str(e)}")
            
            self.log_message("\nSummary:")
            self.log_message(f"Files removed: {self.files_removed}")
            self.log_message(f"Folders removed: {self.folders_removed}")
            self.log_message(f"Total space cleaned: {self.total_size_cleaned:,} bytes")
            self.log_message("-" * 50)
            
            self.root.after(0, self.status_var.set, "Ready for next folder")
            self.root.after(0, self.progress_var.set, f"Completed: {self.files_removed + self.folders_removed} items")
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Failed to clean directory: {str(e)}")

    def update_progress(self, value):
        """Update progress bar and label."""
        self.progress['value'] = value
        self.progress_var.set(f"{value:.1f}%")

    def run(self):
        self.root.mainloop()

def main():
    app = DotCleanerGUI()
    app.run()

if __name__ == '__main__':
    main()