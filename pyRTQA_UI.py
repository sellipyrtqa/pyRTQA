import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import logging
from logs.logger import setup_logger

log = setup_logger("pyRTQA_UI.py")
class pyRTQAApp:
    def __init__(self, root):
        self.root = root
        self.root.title('pyRTQA')
        self.root.geometry('700x670')
        self.root.configure(bg='#f0f0f0')

        # Initialize results storage
        # self.results = None
        self.generated_elements = []

        # Create a main frame
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        self.title_label = tk.Label(main_frame, text='pyRTQA', font=('Arial', 24, 'bold'), bg='#004080', fg='white')
        self.title_label.pack(fill=tk.X)

        # Add a toolbar
        self.create_toolbar(main_frame)
        # Form frame
        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(padx=20, pady=20, anchor=tk.W, fill=tk.X)

        self.create_form_widgets(form_frame)

        # Create a frame to hold the button and label
        file_frame = tk.Frame(main_frame, bg='#f0f0f0')
        file_frame.pack(anchor=tk.W, padx=20, pady=5)

        # Create the upload file button
        self.file_path_name = tk.Button(file_frame, text='Upload File/Folder:', bg='#f0f0f0', command=self.upload_file)
        self.file_path_name.pack(side=tk.LEFT)

        # Create the file path label
        self.file_path_label = tk.Label(file_frame, text='', bg='#f0f0f0')
        self.file_path_label.pack(side=tk.LEFT, padx=(10, 0))

        # Dynamic fields
        self.dynamic_fields_frame = tk.Frame(main_frame, bg='#f0f0f0')
        self.dynamic_fields_frame.pack(padx=20, pady=10, anchor=tk.W, fill=tk.X)

        # Results text box
        self.results_label = tk.Label(main_frame, text='Results', bg='#f0f0f0', font=('Arial', 12, 'bold'))
        self.results_label.pack(anchor=tk.W, padx=20, pady=5)
        self.results_text = tk.Text(main_frame, height=3, wrap=tk.WORD, bg='#ffffff', fg='#000000')
        self.results_text.pack(anchor=tk.W, padx=20, pady=5, fill=tk.X)

        # Button frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(anchor=tk.W, padx=20, pady=5)

        self.process_button = tk.Button(button_frame, text='Process', command=self.process_qa, bg='#004080', fg='white')
        self.process_button.pack(side=tk.LEFT, padx=20, pady=5)

        self.download_button = tk.Button(button_frame, text='Download PDF', command=self.download_pdf, bg='#004080', fg='white')
        self.download_button.pack(side=tk.LEFT, padx=20, pady=5)

        # Footer label
        self.developed_by_label = tk.Label(main_frame, text='Developed by Selli_MedPhy', font=('Arial', 8), bg='#f0f0f0')
        self.developed_by_label.pack(side=tk.RIGHT, anchor=tk.SE, padx=10, pady=10)

    def create_toolbar(self, parent):
        toolbar = tk.Menu(parent)
        self.root.config(menu=toolbar)

        # Analysis menu
        analysis_menu = tk.Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label='Analysis', menu=analysis_menu)
        analysis_menu.add_command(label='FFF Field Analysis-AERB',
                                  command=lambda: self.select_qa_type('FFF Field Analysis-AERB', 'event'))
        analysis_menu.add_command(label='Field Analysis',
                                  command=lambda: self.select_qa_type('Field Analysis', 'event'))
        analysis_menu.add_command(label='WinstonLutz',
                                  command=lambda: self.select_qa_type('WinstonLutz QA', 'event'))
        analysis_menu.add_command(label='PicketFence',
                                  command=lambda: self.select_qa_type('PicketFence', 'event'))
        analysis_menu.add_command(label='StarShot',
                                  command=lambda: self.select_qa_type('StarShot', 'event'))
        analysis_menu.add_command(label='CatPhantom',
                                  command=lambda: self.select_qa_type('CatPhantom', 'event'))

        # File menu
        file_menu = tk.Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label='Tools', menu=file_menu)
        file_menu.add_command(label='Upload File/Folder', command=self.upload_file)
        file_menu.add_command(label='Process', command=self.process_qa)
        file_menu.add_command(label='Save Report', command=self.download_pdf)
        file_menu.add_command(label="Exit", command=self.exit_action)

                # About menu
        about_menu = tk.Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label='Help', menu=about_menu)
        about_menu.add_command(label='Instructions', command=self.show_instruction)
        about_menu.add_command(label='About pyRTQA', command=self.show_about)
        about_menu.add_command(label='Credits', command=self.show_credits)

    def create_form_widgets(self, parent):

        self.institution_label = tk.Label(parent, text='Institution Name:', bg='#f0f0f0', anchor=tk.W)
        self.institution_label.grid(row=1, column=0, pady=5, sticky='w')
        self.institution_entry = tk.Entry(parent, width=70, highlightcolor="blue", highlightthickness=1)
        self.institution_entry.grid(row=1, column=1, pady=5, sticky='ew')

        self.department_label = tk.Label(parent, text='Department Name:', bg='#f0f0f0', anchor=tk.W)
        self.department_label.grid(row=2, column=0, pady=5, sticky='w')
        self.department_entry = tk.Entry(parent, width=70, highlightcolor="blue", highlightthickness=1)
        self.department_entry.grid(row=2, column=1, pady=5, sticky='ew')

        self.measured_by_label = tk.Label(parent, text='Measured by:', bg='#f0f0f0', anchor=tk.W)
        self.measured_by_label.grid(row=3, column=0, pady=5, sticky='w')
        self.measured_by_entry = tk.Entry(parent, width=70, highlightcolor="blue", highlightthickness=1)
        self.measured_by_entry.grid(row=3, column=1, pady=5, sticky='ew')

        # ComboBox for QA Type Selection
        self.qa_type_label = tk.Label(parent, text='QA Type:', bg='#f0f0f0', anchor=tk.W)
        self.qa_type_label.grid(row=4, column=0, pady=5, sticky='w')
        self.qa_type_var = tk.StringVar()
        self.qa_type_combobox = ttk.Combobox(parent, textvariable=self.qa_type_var,
                                             values=["FFF Field Analysis-AERB", "Field Analysis", "WinstonLutz QA",
                                                     "PicketFence", "StarShot", "CatPhantom"],
                                             state="readonly")
        self.qa_type_combobox.grid(row=4, column=1, pady=5, sticky='ew')
        self.qa_type_combobox.bind('<<ComboboxSelected>>', self.update_ui_for_qa_type)


    def exit_action(self):
        root.quit()

    def select_qa_type(self, qa_type, event):
        self.qa_type_var.set(qa_type)

        self.update_ui_for_qa_type(event)
    def update_ui_for_qa_type(self, event):
        # Clear the results text box when a different analysis is selected
        self.results_text.delete(1.0, tk.END)
        qa_type = self.qa_type_var.get()

        # Clear previous dynamic fields
        for widget in self.dynamic_fields_frame.winfo_children():
            widget.destroy()

        if qa_type == 'FFF Field Analysis-AERB':
            # Add Radio buttons for RFA or 2D Image Data
            self.data_type_var = tk.StringVar(value='RFA')
            self.rfa_radiobutton = tk.Radiobutton(self.dynamic_fields_frame, text='Use RFA data',
                                                  variable=self.data_type_var, value='RFA', bg='#f0f0f0')
            self.rfa_radiobutton.grid(row=0, column=0, pady=5, sticky='w')

            self.image_radiobutton = tk.Radiobutton(self.dynamic_fields_frame, text='Use 2D Image data',
                                                    variable=self.data_type_var, value='2D Image', bg='#f0f0f0')
            self.image_radiobutton.grid(row=0, column=1, pady=5, sticky='w')


            self.energy_label = tk.Label(self.dynamic_fields_frame, text='Energy(MV):', bg='#f0f0f0', anchor=tk.W)
            self.energy_label.grid(row=1, column=0, pady=5, sticky='w')
            self.energy_entry = tk.Entry(self.dynamic_fields_frame)
            self.energy_entry.grid(row=1, column=1, pady=5, sticky='ew')

            self.depth_label = tk.Label(self.dynamic_fields_frame, text='Depth(cm):', bg='#f0f0f0', anchor=tk.W)
            self.depth_label.grid(row=1, column=2, pady=5, sticky='w')
            self.depth_entry = tk.Entry(self.dynamic_fields_frame)
            self.depth_entry.grid(row=1, column=3, pady=5, sticky='ew')

        elif qa_type == 'Field Analysis':

            self.energy_label = tk.Label(self.dynamic_fields_frame, text='Energy(MV):', bg='#f0f0f0', anchor=tk.W)
            self.energy_label.grid(row=1, column=0, pady=5, sticky='w')
            self.energy_entry = tk.Entry(self.dynamic_fields_frame)
            self.energy_entry.grid(row=1, column=1, pady=5, sticky='ew')

            self.depth_label = tk.Label(self.dynamic_fields_frame, text='Depth(cm):', bg='#f0f0f0', anchor=tk.W)
            self.depth_label.grid(row=1, column=2, pady=5, sticky='w')
            self.depth_entry = tk.Entry(self.dynamic_fields_frame)
            self.depth_entry.grid(row=1, column=3, pady=5, sticky='ew')

        elif qa_type == 'WinstonLutz QA':
            self.bb_size_label = tk.Label(self.dynamic_fields_frame, text='BB Size(mm):', bg='#f0f0f0', anchor=tk.W)
            self.bb_size_label.grid(row=0, column=0, pady=5, sticky='w')
            self.bb_size_entry = tk.Entry(self.dynamic_fields_frame)
            self.bb_size_entry.grid(row=0, column=1, pady=5, sticky='ew')
        elif qa_type == 'CatPhantom':
            self.phantom_type_label = tk.Label(self.dynamic_fields_frame, text='Phantom Type:', bg='#f0f0f0', anchor=tk.W)
            self.phantom_type_label.grid(row=0, column=0, pady=5, sticky='w')
            self.phantom_type_combobox = ttk.Combobox(self.dynamic_fields_frame,
                                                  values=['CatPhan503', 'CatPhan504', 'CatPhan600', 'CatPhan604'])
            self.phantom_type_combobox.grid(row=0, column=1, pady=5, sticky='ew')

        elif qa_type == 'PicketFence':
            self.mlc_type_label = tk.Label(self.dynamic_fields_frame, text='MLC Type:', bg='#f0f0f0', anchor=tk.W)
            self.mlc_type_label.grid(row=0, column=0, pady=5, sticky='w')
            self.mlc_type_combobox = ttk.Combobox(self.dynamic_fields_frame, values=['Millennium','HD_MILLENNIUM', 'AGILITY', 'BMOD','MLCI', 'HALCYON_DISTAL', 'HALCYON_PROXIMAL'])
            self.mlc_type_combobox.grid(row=0, column=1, pady=5, sticky='ew')

            self.separate_leaves_var = tk.BooleanVar()
            self.separate_leaves_checkbutton = tk.Checkbutton(self.dynamic_fields_frame, text='Separate Leaves',
                                                              bg='#f0f0f0', variable=self.separate_leaves_var,
                                                              command=self.toggle_nominal_gap)
            self.separate_leaves_checkbutton.grid(row=0, column=2, pady=5, sticky='w')

            self.nominal_gap_label = tk.Label(self.dynamic_fields_frame, text='Nominal Gap (mm):', bg='#f0f0f0',
                                              anchor=tk.W)
            self.nominal_gap_label.grid(row=0, column=3, pady=5, sticky='w')
            self.nominal_gap_entry = tk.Entry(self.dynamic_fields_frame, state='disabled')
            self.nominal_gap_entry.grid(row=0, column=4, pady=5, sticky='ew')

            self.tolerance_label = tk.Label(self.dynamic_fields_frame, text='Tolerance:', bg='#f0f0f0', anchor=tk.W)
            self.tolerance_label.grid(row=1, column=0, pady=5, sticky='w')
            self.tolerance_entry = tk.Entry(self.dynamic_fields_frame)
            self.tolerance_entry.grid(row=1, column=1, pady=5, sticky='ew')

            self.action_level_label = tk.Label(self.dynamic_fields_frame, text='Action Level:', bg='#f0f0f0', anchor=tk.W)
            self.action_level_label.grid(row=1, column=2, pady=5, sticky='w')
            self.action_level_entry = tk.Entry(self.dynamic_fields_frame)
            self.action_level_entry.grid(row=1, column=3, pady=5, sticky='ew')

    def toggle_nominal_gap(self):
        if self.separate_leaves_var.get():
            self.nominal_gap_entry.config(state='normal')
        else:
            self.nominal_gap_entry.config(state='disabled')

    def upload_file(self):
        qa_type = self.qa_type_var.get()
        # Clear the results text box when a new file is uploaded
        self.results_text.delete(1.0, tk.END)
        if qa_type == 'WinstonLutz QA':
            file_path = filedialog.askdirectory()
        elif qa_type == 'CatPhantom':
            file_path = filedialog.askdirectory()
        else:
            file_path = filedialog.askopenfilename()

        self.file_path_label.config(text=file_path)


    def process_qa(self):
        log.info("Starting QA processing...")
        try:
            qa_type = self.qa_type_var.get()
            # qa_type = self.qa_type_combobox.get()
            file_path = self.file_path_label.cget("text").replace("File Path: ", "")

            self.results_text.delete(1.0, tk.END)

            elements = []
            if qa_type == 'FFF Field Analysis-AERB':
                from Analysis.fffanalysis import process_fff_analysis
                from Analysis.FFF_FA_2D import process_fffFA_analysis
                self.energy = self.energy_entry.get()
                self.depth = self.depth_entry.get()
                file_type = 'DICOM' if file_path.lower().endswith('.dcm') else 'TIFF'
                if not self.energy or not self.depth:
                    messagebox.showwarning("Warning", "Please enter energy and depth for FFF Analysis.")
                    return
                if self.data_type_var.get() == 'RFA':
                    elements = process_fff_analysis(file_path, self.energy, self.depth)
                else:  # For '2D Image Data'
                    elements = process_fffFA_analysis(file_path, file_type, self.energy, self.depth)
            elif qa_type == 'Field Analysis':
                from Analysis.FieldAnalysis import process_FA
                self.energy = self.energy_entry.get()
                self.depth = self.depth_entry.get()
                if not self.energy or not self.depth:
                    messagebox.showwarning("Warning", "Please enter energy and depth for FFF Analysis.")
                    return
                elements = process_FA(file_path, self.energy, self.depth)
            elif qa_type == 'WinstonLutz QA':
                from Analysis.winstonlutz import process_winstonlutz
                try:
                    bb_size = float(self.bb_size_entry.get()) if self.bb_size_entry else 8.0
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid BB size.")
                    return
                elements = process_winstonlutz(file_path, bb_size)
            elif qa_type == 'CatPhantom':
                from Analysis.catphantom import process_catphantom
                phantom_type = self.phantom_type_combobox.get()
                elements = process_catphantom(file_path, phantom_type)
            elif qa_type == 'PicketFence':
                from Analysis.picketfenceqa import process_picketfence
                try:
                    tolerance = float(self.tolerance_entry.get()) if self.tolerance_entry else 0.2
                    action_level = float(self.action_level_entry.get()) if self.action_level_entry else 0.1
                    mlc_type = self.mlc_type_combobox.get()
                    separate_leaves = self.separate_leaves_var.get()

                    # Convert nominal_gap to float if separate_leaves is true
                    nominal_gap = float(
                        self.nominal_gap_entry.get()) if separate_leaves and self.nominal_gap_entry.get() else None

                except ValueError:
                    messagebox.showerror("Error",
                                         "Please enter valid numeric values for tolerance, action level, and nominal gap.")
                    return

                    # Call the function with nominal_gap if separate_leaves is true, otherwise pass None
                elements = process_picketfence(file_path, tolerance, action_level, mlc_type,
                                               separate_leaves=separate_leaves, nominal_gap=nominal_gap)
            elif qa_type == 'StarShot':
                from Analysis.StarShot import process_starshot

                elements = process_starshot(file_path)

            # Display results
            self.results_text.insert(tk.END,
                                     "Processing complete. Click 'Download PDF' to review the results and   save the report.")
            self.generated_elements = elements
            log.info("QA Process completed.")
        except Exception as e:
            log.error(f"Error in QA Processing: {e}")


    def download_pdf(self):
        log.info("PDF generation started")
        try:
            from Analysis.generatepdf import generate_pdf
            institution = self.institution_entry.get()
            department = self.department_entry.get()
            measured_by = self.measured_by_entry.get()
            if not institution or not department or not measured_by:
                messagebox.showwarning("Input Error", "Please fill in all the required fields.")
                return

            pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if pdf_path:
                generate_pdf(self.generated_elements, institution, department, measured_by, pdf_path)
                messagebox.showinfo("Success", "PDF report generated successfully!")
            log.info("PDF generation completed")
        except Exception as e:
            log.error(f"Error in report generation: {e}")

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
        file_path = os.path.abspath('instructions.html')  # Ensure correct file path
        if os.path.exists(file_path):
            webbrowser.open(f'file://{file_path}')  # Open in default browser
        else:
            tk.messagebox.showerror("Error", "instructions.html file not found")


    def show_credits(self):
        # Create a new window to display credits
        credits_window = tk.Toplevel(self.root)
        credits_window.title('Credits')

        # Add a scrolled text widget to display the file content
        text_area = scrolledtext.ScrolledText(credits_window, wrap=tk.WORD, width=60, height=20)
        text_area.pack(expand=True, fill='both')

        # Open and read the credits file
        try:
            with open('CREDITS.md', 'r', encoding="utf-8") as file:
                credits_content = file.read()
                text_area.insert(tk.END, credits_content)  # Display the credits in the text box
        except FileNotFoundError:
            text_area.insert(tk.END, 'CREDITS.md file not found')

        text_area.config(state=tk.DISABLED)  # Make text read-only

if __name__ == "__main__":
    root = tk.Tk()
    app = pyRTQAApp(root)
    root.mainloop()
