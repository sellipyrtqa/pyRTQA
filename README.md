# pyRTQA 🌀

**pyRTQA** is a Quality Assurance (QA) tool for Radiation Therapy.  
It's built using Python and Tkinter, and integrates with [pylinac](https://github.com/jrkerns/pylinac) to analyze CatPhan phantoms.

## 🎯 Features

- Analyze CatPhan images (503, 504, 600, 604 supported)
- Picket Fence, Starshot, Winston-Lutz QA, Field analysis support
- FFF Profile Analysis for AERB compliance
- User-friendly GUI built with Tkinter
- EXE version available for non-Python users
- Modern light-themed interface
- Robust error handling
- Automatically creates log files to track application activity and errors

## 📦 Installation

### If you're running from source:
```bash
pip install -r requirements.txt
python pyRTQA_UI.py
```

### If you're using the `.exe`:
Just follow this link https://drive.google.com/drive/folders/1n-JEvBPtIEMTov594SJsx_6MZdOk3I38?usp=drive_link and double-click the `pyRTQA_UI.exe` file — no installation needed!

## 📘 QA Instructions

### **FFF Analysis - AERB:**

1. **RFA Data**
   - Measure beam profiles with:
     - Field Size: 20 cm x 20 cm  
     - Depth: 10 cm  
     - SSD: 90 cm
   - Normalize to 100% and export to Excel with 2 sheets:
     - **Inline Sheet**: `Inline (cm)` and `Dose (%)` columns  
     - **Crossline Sheet**: `Crossline (cm)` and `Dose (%)` columns  
   - Include energy and depth info in the file.

2. **2D Image Data**
   - Upload an EPID image (.dcm or .tiff)
   - Use a 10 cm slab phantom, SSD 90 cm
   - Enter energy and depth info

---

### **Winston-Lutz QA:**

1. Place all `.dcm` images in a folder
2. Use valid filenames like:
   - `MyWL-gantry0-coll90-couch315.dcm`
   - `gantry90_stuff_coll45-couch0.dcm`
   - `abc-couch45-gantry315-coll0.dcm`
   - `01-gantry0-abcd-coll30couch10abc.dcm`
   - `abc-gantry30.dcm`
   - `coll45abc.dcm`
3. Avoid invalid names like:
   - `gantry=0-coll=90-couch=315.dcm`
   - `gan45_collimator30-table270.dcm`
4. Specify the ball bearing size (in mm)

---

### **Picket Fence:**

1. Upload a `.dcm` or `.tiff` file
2. Enter tolerance and action level
3. For individual leaf analysis:
   - Check "Separate Leaves"
4. For combined analysis:
   - Leave "Separate Leaves" unchecked
5. Input the expected picket gap (in mm)
   - Only needed for separate leaf mode
   - You may need to adjust for DLG & EPID effects

---

### **Starshot:**

1. Upload a `.dcm` or `.tiff` file for analysis

---

### **CatPhantom:**

1. Upload a folder of CBCT/CT `.dcm` images

---

## 📂 Folder Structure

```
pyRTQA/
├── pyRTQA_UI.py               # Main launcher script
├── gui/                       # Tkinter GUI modules
│   └── ...
├── analysis/                  # QA analysis modules (CatPhan, WL, etc.)
│   └── ...
├── logs/                      # Auto-generated log files
│   └── pyRTQA.log
├── dist/                      # Executable output from pyinstaller
│   └── pyRTQA.exe
├── requirements.txt
├── LICENSE
├── CREDITS.md
├── README.md
├── .gitignore
└── instructions.txt
```

## 🛠️ Technologies

- Python
- Tkinter
- pylinac

## 📜 License

BSD Clause3 License — see [LICENSE](LICENSE)

---

## 🚧 In Development

- Database support
- User authentication
- QA report exporting

---

Made with ❤️ by Sambasivaselli
