import os
from io import BytesIO
import matplotlib.pyplot as plt
from pydicom import dcmread
from pylinac import PicketFence
from pylinac.picketfence import MLC
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image
from reportlab.platypus import TableStyle

from logs.logger import setup_logger

log = setup_logger("Picketfence_batch.py")

styles = getSampleStyleSheet()
header_style = ParagraphStyle(
    'HeaderStyle',
    parent=styles['Title'],
    textColor=colors.darkblue

)
footer_style = ParagraphStyle('FooterStyle',
    parent=styles['Normal'],
    textColor=colors.black
 )
def analyze_picketfence_multiple(image_folder, tolerance, action_level, mlc_type, separate_leaves=False, nominal_gap=None):
    image_results = []
    elements = []
    # Convert nominal_gap to float if separate_leaves is True
    if separate_leaves:
        try:
            nominal_gap = float(nominal_gap)
        except ValueError:
            print("Error: Nominal gap must be a valid number.")
            return []

    for file in sorted(os.listdir(image_folder)):
        if file.lower().endswith(".dcm"):
            filepath = os.path.join(image_folder, file)
            pf = PicketFence(filepath, mlc=MLC[mlc_type])
            pf.analyze(
                tolerance=tolerance,
                action_tolerance=action_level,
                separate_leaves=separate_leaves,
                nominal_gap_mm=nominal_gap if separate_leaves else None
            )

            # Extract DICOM metadata
            ds = dcmread(filepath)
            gantry = getattr(ds, "GantryAngle", "N/A")
            gantry_str = str(int(round(gantry))) if isinstance(gantry, (int, float)) else str(gantry)

            # Save for summary
            image_results.append({
                "filename": file,
                "gantry": gantry,
                "gantry_str": gantry_str,
                "max_error": pf.max_error,
                "max_leaf": pf.max_error_leaf,
                "max_picket": pf.max_error_picket,
                "pf": pf  # Save reference for plotting later
            })

    # Summary table
    data = [["Gantry", "Max Error (mm)", "Max Error Leaf", "Max Error Picket No", "Filename"]]
    for r in image_results:
        data.append([r["gantry_str"], f"{r['max_error']:.2f}", str(r["max_leaf"]), str(r["max_picket"]), r["filename"]])

    from reportlab.platypus import Table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(Paragraph("Summary of Picket Fence Results", styles['Heading2']))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Add detailed result for each
    for r in image_results:
        elements.append(Paragraph(f"Image: {r['filename']} (Gantry: {r['gantry_str']}°)", styles['Heading3']))
        results_lines = r['pf'].results().split('\n')
        for line in results_lines:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 3))

        # Plot image
        buf_img = BytesIO()
        r['pf'].plot_analyzed_image(show=False)
        plt.savefig(buf_img, format='png')
        buf_img.seek(0)
        elements.append(Image(buf_img, width=5*inch, height=3*inch))
        plt.close()

        # Plot histogram
        buf_hist = BytesIO()
        r['pf'].plot_histogram(show=False)
        plt.savefig(buf_hist, format='png')
        buf_hist.seek(0)
        elements.append(Image(buf_hist, width=5*inch, height=3*inch))
        plt.close()

        elements.append(Spacer(1, 12))

    return elements
