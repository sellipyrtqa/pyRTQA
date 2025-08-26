import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import logging
import os

# Assuming logs.logger exists and setup_logger is defined there
# If not, you might need a simple logger setup for standalone execution:
try:
    from logs.logger import setup_logger

    log = setup_logger("pyRTQA_UI.py")
except ImportError:
    # Fallback logger if logs.logger is not available
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger("pyRTQA_UI.py")
    log.warning("Could not import custom logger. Using basic logging configuration.")


class pyRTQAApp:
    def __init__(self, root):
        self.root = root
        self.root.title('pyRTQA - Radiation Therapy QA Tool')
        self.root.geometry('700x600')  # Further reduced height and width
        self.root.resizable(True, True)  # Allow resizing
        self.root.configure(bg='#ECF0F1')  # Lighter grey background (Clouds)

        # Apply a modern theme and refined styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 'clam' provides good base for customization

        # General Styles
        self.style.configure('TFrame', background='#ECF0F1')
        self.style.configure('TLabel', background='#ECF0F1', foreground='#34495E', font=('Segoe UI', 8))  # Reduced font
        self.style.configure('TButton', background='#3498DB', foreground='white', font=('Segoe UI', 8, 'bold'),
                             # Reduced font
                             padding=[7, 3], relief='flat', borderwidth=0, focuscolor='#3498DB',  # Reduced padding
                             focusthickness=0)  # Remove focus border
        self.style.map('TButton', background=[('active', '#2980B9')])  # Darker blue on hover

        self.style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=3,
                             # Reduced padding
                             font=('Segoe UI', 8), foreground='#34495E')  # Reduced font
        self.style.configure('TCombobox', fieldbackground='white', borderwidth=1, relief='solid', padding=3,
                             # Reduced padding
                             font=('Segoe UI', 8), foreground='#34495E')  # Reduced font
        self.style.configure('TRadiobutton', background='#ECF0F1', foreground='#34495E',
                             font=('Segoe UI', 8))  # Reduced font
        self.style.configure('TCheckbutton', background='#ECF0F1', foreground='#34495E',
                             font=('Segoe UI', 8))  # Reduced font

        # Specific styles for LabelFrames
        self.style.configure('TLabelframe', background='#ECF0F1', bordercolor='#BDC3C7', relief='solid', borderwidth=1)
        self.style.configure('TLabelframe.Label', background='#ECF0F1', foreground='#2C3E50',
                             font=('Segoe UI', 9, 'bold'))  # Reduced font

        # Text widget for results (not a ttk widget, so direct config)
        # self.style.configure('TText', background='white', foreground='#333333', font=('Consolas', 10))

        # Initialize results storage
        self.generated_elements = []

        # Create a main frame
        main_frame = ttk.Frame(root, padding="10 10 10 10")  # Reduced main frame padding
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Removed the large 'pyRTQA' title label as requested.
        # The application title is now solely in the window's native title bar.

        # Add a toolbar
        self.create_toolbar()

        # Using grid for main_frame content for better layout control
        main_frame.columnconfigure(0, weight=1)  # Make the single column expandable

        row_idx = 0

        # Form frame (General Information)
        form_frame = ttk.LabelFrame(main_frame, text="  General Information  ", padding="8 8 8 8")  # Reduced padding
        form_frame.grid(row=row_idx, column=0, padx=8, pady=(0, 8), sticky='ew')  # Reduced pady
        self.create_form_widgets(form_frame)
        row_idx += 1

        # File Input frame
        file_frame = ttk.LabelFrame(main_frame, text="  Data Input  ", padding="8 8 8 8")  # Reduced padding
        file_frame.grid(row=row_idx, column=0, padx=8, pady=(0, 8), sticky='ew')  # Reduced pady
        # Create the upload file button
        self.file_path_name = ttk.Button(file_frame, text='📂 Upload File/Folder', command=self.upload_file)
        self.file_path_name.pack(side=tk.LEFT, padx=(0, 8))  # Reduced padx
        # Create the file path label
        self.file_path_label = ttk.Label(file_frame, text='No file or folder selected.', foreground='#555555',
                                         font=('Segoe UI', 7, 'italic'))  # Reduced font
        self.file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        row_idx += 1

        # Dynamic fields frame (QA Specific Parameters)
        self.dynamic_fields_frame = ttk.LabelFrame(main_frame, text="  QA Specific Parameters  ",
                                                   padding="8 8 8 8")  # Reduced padding
        self.dynamic_fields_frame.grid(row=row_idx, column=0, padx=8, pady=(0, 8), sticky='nsew')  # Reduced pady
        main_frame.rowconfigure(row_idx,
                                weight=1)  # This row should have weight=1 to allow dynamic content to push height
        row_idx += 1

        # Results text box
        self.results_label = ttk.Label(main_frame, text='Results Overview', font=('Segoe UI', 9, 'bold'),
                                       foreground='#34495E')  # Reduced font
        self.results_label.grid(row=row_idx, column=0, padx=8, pady=(8, 4), sticky='w')  # Reduced padding
        row_idx += 1
        self.results_text = tk.Text(main_frame, height=3, wrap=tk.WORD, bg='#ffffff', fg='#34495E',  # Reduced height
                                    font=('Consolas', 7), relief='flat', borderwidth=1,  # Reduced font
                                    highlightbackground='#BDC3C7', highlightthickness=1, padx=6,
                                    pady=6)  # Reduced padding
        self.results_text.grid(row=row_idx, column=0, padx=8, pady=(0, 8), sticky='ew')  # Reduced pady
        main_frame.rowconfigure(row_idx, weight=0)  # This row should not expand vertically
        row_idx += 1

        # Button frame (Process and Download)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row_idx, column=0, padx=8, pady=4, sticky='ew')  # Reduced padding
        button_frame.columnconfigure(0, weight=1)  # Center buttons
        button_frame.columnconfigure(1, weight=1)  # Center buttons

        self.process_button = ttk.Button(button_frame, text='⚙️ Process QA', command=self.process_qa)
        self.process_button.grid(row=0, column=0, padx=8, pady=4, sticky='e')  # Reduced padding
        self.download_button = ttk.Button(button_frame, text='⬇️ Download PDF Report', command=self.download_pdf)
        self.download_button.grid(row=0, column=1, padx=8, pady=4, sticky='w')  # Reduced padding
        main_frame.rowconfigure(row_idx, weight=0)  # This row should not expand vertically
        row_idx += 1

        # Footer label
        self.developed_by_label = ttk.Label(main_frame, text='Developed by Sambasivaselli_R@pyRTQA',
                                            font=('Segoe UI', 6, 'italic'),  # Reduced font
                                            foreground='#666666')
        self.developed_by_label.grid(row=row_idx, column=0, sticky='se', padx=8, pady=8)  # Reduced padding
        main_frame.rowconfigure(row_idx, weight=0)  # This row should not expand vertically

        # Configure main_frame rows to ensure proper distribution and prevent pushing off-screen
        # Explicitly set weights for each row index to ensure dynamic_fields_frame gets priority
        main_frame.rowconfigure(0, weight=0)  # General Information frame
        main_frame.rowconfigure(1, weight=0)  # Data Input frame
        main_frame.rowconfigure(2, weight=1)  # QA Specific Parameters frame (dynamic content)
        main_frame.rowconfigure(3, weight=0)  # Results label
        main_frame.rowconfigure(4, weight=0)  # Results text box
        main_frame.rowconfigure(5, weight=0)  # Button frame
        main_frame.rowconfigure(6, weight=0)  # Footer label

    def create_toolbar(self):
        toolbar = tk.Menu(self.root)
        self.root.config(menu=toolbar)

        # Analysis menu
        analysis_menu = tk.Menu(toolbar, tearoff=0, font=('Segoe UI', 8))  # Reduced font
        toolbar.add_cascade(label='Analysis', menu=analysis_menu)
        analysis_menu.add_command(label='FFF Field Analysis-AERB',
                                  command=lambda: self.select_qa_type('FFF Field Analysis-AERB', 'event'))
        analysis_menu.add_command(label='Field Analysis',
                                  command=lambda: self.select_qa_type('Field Analysis', 'event'))
        analysis_menu.add_command(label='WinstonLutz QA',
                                  command=lambda: self.select_qa_type('WinstonLutz QA', 'event'))
        analysis_menu.add_command(label='PicketFence',
                                  command=lambda: self.select_qa_type('PicketFence', 'event'))
        analysis_menu.add_command(label='StarShot',
                                  command=lambda: self.select_qa_type('StarShot', 'event'))
        analysis_menu.add_command(label='CatPhantom',
                                  command=lambda: self.select_qa_type('CatPhantom', 'event'))
        analysis_menu.add_command(label='Leeds TOR',
                                  command=lambda: self.select_qa_type('LeedsTOR', 'event'))

        # File menu
        file_menu = tk.Menu(toolbar, tearoff=0, font=('Segoe UI', 8))  # Reduced font
        toolbar.add_cascade(label='Tools', menu=file_menu)
        file_menu.add_command(label='Upload File/Folder', command=self.upload_file)
        file_menu.add_command(label='Process QA', command=self.process_qa)
        file_menu.add_command(label='Save Report', command=self.download_pdf)
        file_menu.add_command(label="Exit", command=self.exit_action)

        # About menu
        about_menu = tk.Menu(toolbar, tearoff=0, font=('Segoe UI', 8))  # Reduced font
        toolbar.add_cascade(label='Help', menu=about_menu)
        about_menu.add_command(label='Instructions', command=self.show_instruction)
        about_menu.add_command(label='About pyRTQA', command=self.show_about)
        about_menu.add_command(label='Credits', command=self.show_credits)

    def create_form_widgets(self, parent):
        parent.columnconfigure(1, weight=1)  # Make the second column (entry column) expandable

        row_idx = 0
        self.institution_label = ttk.Label(parent, text='Institution Name:')
        self.institution_label.grid(row=row_idx, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
        self.institution_entry = ttk.Entry(parent)
        self.institution_entry.grid(row=row_idx, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady
        row_idx += 1

        self.department_label = ttk.Label(parent, text='Department Name:')
        self.department_label.grid(row=row_idx, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
        self.department_entry = ttk.Entry(parent)
        self.department_entry.grid(row=row_idx, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady
        row_idx += 1

        self.linac_ID_label = ttk.Label(parent, text='Machine ID/Name:')
        self.linac_ID_label.grid(row=row_idx, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
        self.linac_ID_entry = ttk.Entry(parent)
        self.linac_ID_entry.grid(row=row_idx, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady
        row_idx += 1

        self.measured_by_label = ttk.Label(parent, text='Measured by:')
        self.measured_by_label.grid(row=row_idx, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
        self.measured_by_entry = ttk.Entry(parent)
        self.measured_by_entry.grid(row=row_idx, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady
        row_idx += 1

        # ComboBox for QA Type Selection
        self.qa_type_label = ttk.Label(parent, text='Select QA Type:')  # More descriptive label
        self.qa_type_label.grid(row=row_idx, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
        self.qa_type_var = tk.StringVar()
        self.qa_type_combobox = ttk.Combobox(parent, textvariable=self.qa_type_var,
                                             values=["FFF Field Analysis-AERB", "Field Analysis", "WinstonLutz QA",
                                                     "PicketFence", "StarShot", "CatPhantom", "LeedsTOR"],
                                             state="readonly")
        self.qa_type_combobox.grid(row=row_idx, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady
        self.qa_type_combobox.bind('<<ComboboxSelected>>', self.update_ui_for_qa_type)
        self.qa_type_combobox.set("--- Choose a QA Analysis ---")  # More prominent placeholder

    def exit_action(self):
        self.root.quit()

    def select_qa_type(self, qa_type, event):
        self.qa_type_var.set(qa_type)
        self.update_ui_for_qa_type(event)
        self.root.update_idletasks()  # Ensure main window updates after dynamic content changes

    def update_ui_for_qa_type(self, event):
        # Clear the results text box when a different analysis is selected
        self.results_text.delete(1.0, tk.END)
        qa_type = self.qa_type_var.get()

        # Clear previous dynamic fields
        for widget in self.dynamic_fields_frame.winfo_children():
            widget.destroy()

        # Force redraw to process widget destruction
        self.dynamic_fields_frame.update_idletasks()

        # Configure columns for dynamic fields frame to ensure proper expansion
        self.dynamic_fields_frame.columnconfigure(1, weight=1)
        self.dynamic_fields_frame.columnconfigure(3, weight=1)
        self.dynamic_fields_frame.columnconfigure(4, weight=1)  # For nominal gap entry

        # Reset all row weights in dynamic_fields_frame before adding new widgets
        # This ensures previous row configurations don't interfere
        for i in range(5):  # Assuming max 5 rows for dynamic content
            self.dynamic_fields_frame.rowconfigure(i, weight=0)

        if qa_type == 'FFF Field Analysis-AERB':
            # Add Radio buttons for RFA or 2D Image Data
            self.data_type_var = tk.StringVar(value='RFA')
            self.rfa_radiobutton = ttk.Radiobutton(self.dynamic_fields_frame, text='Use RFA Data',
                                                   variable=self.data_type_var, value='RFA')
            self.rfa_radiobutton.grid(row=0, column=0, pady=4, sticky='w', padx=5)  # Reduced pady

            self.image_radiobutton = ttk.Radiobutton(self.dynamic_fields_frame, text='Use 2D Image Data',
                                                     variable=self.data_type_var, value='2D Image')
            self.image_radiobutton.grid(row=0, column=1, pady=4, sticky='w', padx=5)  # Reduced pady

            self.energy_label = ttk.Label(self.dynamic_fields_frame, text='Energy (MV):')
            self.energy_label.grid(row=1, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
            self.energy_entry = ttk.Entry(self.dynamic_fields_frame)
            self.energy_entry.grid(row=1, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady

            self.depth_label = ttk.Label(self.dynamic_fields_frame, text='Depth (cm):')
            self.depth_label.grid(row=1, column=2, pady=4, sticky='w', padx=5)  # Reduced pady
            self.depth_entry = ttk.Entry(self.dynamic_fields_frame)
            self.depth_entry.grid(row=1, column=3, pady=4, sticky='ew', padx=5)  # Reduced pady

            # Give weight to rows that contain content to ensure vertical expansion
            self.dynamic_fields_frame.rowconfigure(0, weight=1)
            self.dynamic_fields_frame.rowconfigure(1, weight=1)

        elif qa_type == 'Field Analysis':
            self.energy_label = ttk.Label(self.dynamic_fields_frame, text='Energy (MV):')
            self.energy_label.grid(row=0, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
            self.energy_entry = ttk.Entry(self.dynamic_fields_frame)
            self.energy_entry.grid(row=0, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady

            self.depth_label = ttk.Label(self.dynamic_fields_frame, text='Depth (cm):')
            self.depth_label.grid(row=0, column=2, pady=4, sticky='w', padx=5)  # Reduced pady
            self.depth_entry = ttk.Entry(self.dynamic_fields_frame)
            self.depth_entry.grid(row=0, column=3, pady=4, sticky='ew', padx=5)  # Reduced pady
            self.dynamic_fields_frame.rowconfigure(0, weight=1)

        elif qa_type == 'WinstonLutz QA':
            self.bb_size_label = ttk.Label(self.dynamic_fields_frame, text='BB Size (mm):')
            self.bb_size_label.grid(row=0, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
            self.bb_size_entry = ttk.Entry(self.dynamic_fields_frame)
            self.bb_size_entry.grid(row=0, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady
            self.dynamic_fields_frame.rowconfigure(0, weight=1)

        elif qa_type == 'CatPhantom':
            self.phantom_type_label = ttk.Label(self.dynamic_fields_frame, text='Phantom Type:')
            self.phantom_type_label.grid(row=0, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
            self.phantom_type_combobox = ttk.Combobox(self.dynamic_fields_frame,
                                                      values=['CatPhan503', 'CatPhan504', 'CatPhan600', 'CatPhan604'],
                                                      state="readonly")
            self.phantom_type_combobox.grid(row=0, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady
            self.phantom_type_combobox.set("--- Select Phantom Type ---")
            self.dynamic_fields_frame.rowconfigure(0, weight=1)


        elif qa_type == 'PicketFence':
            self.pf_type_var = tk.StringVar(value='Single')
            self.single_radiobutton = ttk.Radiobutton(self.dynamic_fields_frame, text='Single Image',
                                                      variable=self.pf_type_var, value='Single')
            self.single_radiobutton.grid(row=0, column=0, pady=4, sticky='w', padx=5)  # Reduced pady

            self.multiple_radiobutton = ttk.Radiobutton(self.dynamic_fields_frame, text='Multiple Images',
                                                        variable=self.pf_type_var, value='Multiple')
            self.multiple_radiobutton.grid(row=0, column=1, pady=4, sticky='w', padx=5)  # Reduced pady

            self.mlc_type_label = ttk.Label(self.dynamic_fields_frame, text='MLC Type:')
            self.mlc_type_label.grid(row=1, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
            self.mlc_type_combobox = ttk.Combobox(self.dynamic_fields_frame,
                                                  values=['MILLENNIUM', 'HD_MILLENNIUM', 'AGILITY',
                                                          'BMOD', 'MLCI', 'HALCYON_DISTAL', 'HALCYON_PROXIMAL'],
                                                  state="readonly")
            self.mlc_type_combobox.grid(row=1, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady
            self.mlc_type_combobox.set("--- Select MLC Type ---")

            self.separate_leaves_var = tk.BooleanVar()
            self.separate_leaves_checkbutton = ttk.Checkbutton(self.dynamic_fields_frame, text='Separate Leaves',
                                                               variable=self.separate_leaves_var,
                                                               command=self.toggle_nominal_gap)
            self.separate_leaves_checkbutton.grid(row=1, column=2, pady=4, sticky='w', padx=5)  # Reduced pady

            self.nominal_gap_label = ttk.Label(self.dynamic_fields_frame, text='Nominal Gap (mm):')
            self.nominal_gap_label.grid(row=1, column=3, pady=4, sticky='w', padx=5)  # Reduced pady
            self.nominal_gap_entry = ttk.Entry(self.dynamic_fields_frame, state='disabled')
            self.nominal_gap_entry.grid(row=1, column=4, pady=4, sticky='ew', padx=5)  # Reduced pady

            self.tolerance_label = ttk.Label(self.dynamic_fields_frame, text='Tolerance (%):')
            self.tolerance_label.grid(row=2, column=0, pady=4, sticky='w', padx=5)  # Reduced pady
            self.tolerance_entry = ttk.Entry(self.dynamic_fields_frame)
            self.tolerance_entry.grid(row=2, column=1, pady=4, sticky='ew', padx=5)  # Reduced pady

            self.action_level_label = ttk.Label(self.dynamic_fields_frame, text='Action Level (%):')
            self.action_level_label.grid(row=2, column=2, pady=4, sticky='w', padx=5)  # Reduced pady
            self.action_level_entry = ttk.Entry(self.dynamic_fields_frame)
            self.action_level_entry.grid(row=2, column=3, pady=4, sticky='ew', padx=5)  # Reduced pady

            self.dynamic_fields_frame.rowconfigure(0, weight=1)
            self.dynamic_fields_frame.rowconfigure(1, weight=1)
            self.dynamic_fields_frame.rowconfigure(2, weight=1)

        # Force an update of the dynamic_fields_frame to ensure it resizes
        self.dynamic_fields_frame.update_idletasks()

    def toggle_nominal_gap(self):
        if self.separate_leaves_var.get():
            self.nominal_gap_entry.config(state='normal')
        else:
            self.nominal_gap_entry.config(state='disabled')

    def upload_file(self):
        qa_type = self.qa_type_var.get()
        # Clear the results text box when a new file is uploaded
        self.results_text.delete(1.0, tk.END)
        file_path = ""  # Initialize file_path

        if qa_type == 'WinstonLutz QA':
            file_path = filedialog.askdirectory(title="Select Folder for Winston-Lutz QA")
        elif qa_type == 'CatPhantom':
            file_path = filedialog.askdirectory(title="Select Folder for CatPhantom QA")
        elif qa_type == 'PicketFence':
            # Check if single or multi mode is selected
            pf_mode = self.pf_type_var.get()
            if pf_mode == "Multiple":
                file_path = filedialog.askdirectory(title="Select Folder for PicketFence (Multiple Images)")
            else:
                file_path = filedialog.askopenfilename(title="Select DICOM File for PicketFence (Single Image)",
                                                       filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")])
        else:
            file_path = filedialog.askopenfilename(title="Select File for QA Analysis",
                                                   filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")])

        if file_path:  # Only update if a path was selected
            self.file_path_label.config(text=file_path)
        else:
            self.file_path_label.config(text="No file or folder selected.")

    def process_qa(self):
        log.info("Starting QA processing...")
        try:
            from Analysis.fffanalysis import process_fff_analysis
            from Analysis.FFF_FA_2D import process_fffFA_analysis
            from Analysis.FieldAnalysis import process_FA
            from Analysis.winstonlutz import process_winstonlutz
            from Analysis.catphantom import process_catphantom
            from Analysis.picketfenceqa import process_picketfence
            from Analysis.Picketfence_batch import analyze_picketfence_multiple
            from Analysis.StarShot import process_starshot
            from Analysis.Leeds_TOR import process_leedsTOR
            from Analysis.generatepdf import generate_pdf  # Import here to ensure it's available

            qa_type = self.qa_type_var.get()
            file_path = self.file_path_label.cget("text")  # Get current path from label

            if not file_path or file_path == "No file or folder selected.":
                messagebox.showwarning("Input Error", "Please upload a file or select a folder first.")
                return
            if qa_type == "--- Choose a QA Analysis ---" or not qa_type:  # Check for placeholder or empty
                messagebox.showwarning("Input Error", "Please select a QA Type from the dropdown menu.")
                return

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Processing... Please wait.\n")
            self.root.update_idletasks()  # Update UI to show message

            elements = []
            if qa_type == 'FFF Field Analysis-AERB':
                energy = self.energy_entry.get()
                depth = self.depth_entry.get()
                file_type = 'DICOM' if file_path.lower().endswith('.dcm') else 'TIFF'  # Assuming TIFF for non-DICOM
                if not energy or not depth:
                    messagebox.showwarning("Warning", "Please enter Energy and Depth for FFF Analysis.")
                    return
                try:
                    energy = float(energy)
                    depth = float(depth)
                except ValueError:
                    messagebox.showerror("Error", "Energy and Depth must be numeric values.")
                    return

                if self.data_type_var.get() == 'RFA':
                    elements = process_fff_analysis(file_path, energy, depth)
                else:  # For '2D Image Data'
                    elements = process_fffFA_analysis(file_path, file_type, energy, depth)
            elif qa_type == 'Field Analysis':
                energy = self.energy_entry.get()
                depth = self.depth_entry.get()
                if not energy or not depth:
                    messagebox.showwarning("Warning", "Please enter Energy and Depth for Field Analysis.")
                    return
                try:
                    energy = float(energy)
                    depth = float(depth)
                except ValueError:
                    messagebox.showerror("Error", "Energy and Depth must be numeric values.")
                    return
                elements = process_FA(file_path, energy, depth)
            elif qa_type == 'WinstonLutz QA':
                bb_size_str = self.bb_size_entry.get()
                try:
                    bb_size = float(bb_size_str) if bb_size_str else 8.0  # Default BB size
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid numeric BB size (e.g., 8.0).")
                    return
                elements = process_winstonlutz(file_path, bb_size)
            elif qa_type == 'CatPhantom':
                phantom_type = self.phantom_type_combobox.get()
                if not phantom_type or phantom_type == "--- Select Phantom Type ---":  # Check for placeholder
                    messagebox.showwarning("Input Error", "Please select a Phantom Type for CatPhantom QA.")
                    return
                elements = process_catphantom(file_path, phantom_type)
            elif qa_type == 'PicketFence':
                try:
                    tolerance_str = self.tolerance_entry.get()
                    action_level_str = self.action_level_entry.get()
                    mlc_type = self.mlc_type_combobox.get()
                    separate_leaves = self.separate_leaves_var.get()

                    tolerance = float(tolerance_str) if tolerance_str else 0.2
                    action_level = float(action_level_str) if action_level_str else 0.1

                    if not mlc_type or mlc_type == "--- Select MLC Type ---":  # Check for placeholder
                        messagebox.showwarning("Input Error", "Please select an MLC Type for PicketFence QA.")
                        return

                    nominal_gap = None
                    if separate_leaves and self.nominal_gap_entry.get():
                        nominal_gap = float(self.nominal_gap_entry.get())

                except ValueError:
                    messagebox.showerror("Error",
                                         "Please enter valid numeric values for tolerance, action level, and nominal gap.")
                    return

                if self.pf_type_var.get() == 'Multiple':
                    elements = analyze_picketfence_multiple(file_path, tolerance, action_level, mlc_type,
                                                            separate_leaves=separate_leaves, nominal_gap=nominal_gap)
                else:
                    elements = process_picketfence(file_path, tolerance, action_level, mlc_type,
                                                   separate_leaves=separate_leaves, nominal_gap=nominal_gap)
            elif qa_type == 'StarShot':
                elements = process_starshot(file_path)

            elif qa_type == 'LeedsTOR':
                elements = process_leedsTOR(file_path)
            else:
                messagebox.showwarning("Invalid QA Type", "Please select a valid QA type to proceed.")
                return

            # Display results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END,
                                     "Processing complete. Click 'Download PDF' to review the results and save the report.")
            self.generated_elements = elements
            log.info("QA Process completed successfully.")
        except Exception as e:
            log.error(f"Error during QA Processing: {e}", exc_info=True)
            messagebox.showerror("Processing Error",
                                 f"An unexpected error occurred during processing: {e}\nCheck logs for more details.")

    def download_pdf(self):
        log.info("PDF generation started.")
        try:
            from Analysis.generatepdf import generate_pdf
            institution = self.institution_entry.get()
            department = self.department_entry.get()
            linac_ID = self.linac_ID_entry.get()
            measured_by = self.measured_by_entry.get()

            if not institution or not department or not measured_by:
                messagebox.showwarning("Input Error",
                                       "Please fill in Institution Name, Department Name, and Measured by fields before generating PDF.")
                return
            if not self.generated_elements:
                messagebox.showwarning("No Results", "No QA results to generate PDF. Please process QA first.")
                return

            pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],
                                                    title="Save QA Report As")
            if pdf_path:
                generate_pdf(self.generated_elements, institution, department, linac_ID, measured_by, pdf_path)
                messagebox.showinfo("Success", "PDF report generated successfully!")
                log.info(f"PDF generation completed. Report saved to: {pdf_path}")
            else:
                log.info("PDF generation cancelled by user.")
        except ImportError:
            log.error("Could not import Analysis.generatepdf. Make sure the module exists.", exc_info=True)
            messagebox.showerror("Error", "PDF generation module not found. Cannot generate report.")
        except Exception as e:
            log.error(f"Error during PDF report generation: {e}", exc_info=True)
            messagebox.showerror("Report Generation Error",
                                 f"An unexpected error occurred while generating the PDF: {e}\nCheck logs for more details.")

    def show_about(self):
        messagebox.showinfo("About pyRTQA", "pyRTQA v3.2.0\n"
                                            "Developed by Sambasivaselli R, Medical Physicist, India\n"
                                            "Quality Assurance Tool for Radiation Therapy\n"
                                            "License: BSD 3-Clause License\n"
                                            "© 2025 pyRTQA\n"
                                            "This is free software, and you are welcome to modify and distribute it \n"
                                            "under the terms of the BSD 3-Clause License."
                            )

    def show_instruction(self):
        import webbrowser
        import os
        # Ensure instructions.html is in the same directory as the script or adjust path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'instructions.html')

        if os.path.exists(file_path):
            webbrowser.open(f'file://{file_path}')
        else:
            messagebox.showerror("Error",
                                 f"Instructions file not found at: {file_path}\nPlease ensure 'instructions.html' is in the same directory as the script.")

    def show_credits(self):
        credits_window = tk.Toplevel(self.root)
        credits_window.title('Credits')
        credits_window.geometry('500x400')  # Set a default size for the credits window
        credits_window.transient(self.root)  # Make it appear on top of the main window
        credits_window.grab_set()  # Make it modal

        text_area = scrolledtext.ScrolledText(credits_window, wrap=tk.WORD, width=60, height=20,
                                              font=('Consolas', 8), bg='#F8F8F8', fg='#333333',  # Reduced font
                                              relief='flat', borderwidth=1, highlightbackground='#CCCCCC',
                                              highlightthickness=1)
        text_area.pack(expand=True, fill='both', padx=8, pady=8)  # Reduced padding

        try:
            # Ensure CREDITS.md is in the same directory as the script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            credits_file_path = os.path.join(current_dir, 'CREDITS.md')

            with open(credits_file_path, 'r', encoding="utf-8") as file:
                credits_content = file.read()
                text_area.insert(tk.END, credits_content)
        except FileNotFoundError:
            text_area.insert(tk.END, f'CREDITS.md file not found at: {credits_file_path}')
        except Exception as e:
            text_area.insert(tk.END, f'Error loading CREDITS.md: {e}')

        text_area.config(state=tk.DISABLED)  # Make text read-only

        # Add a close button to the credits window
        close_button = ttk.Button(credits_window, text="Close", command=credits_window.destroy)
        close_button.pack(pady=8)  # Reduced padding


if __name__ == "__main__":
    root = tk.Tk()
    app = pyRTQAApp(root)
    root.mainloop()
