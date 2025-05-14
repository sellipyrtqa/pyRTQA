from io import BytesIO
import matplotlib.pyplot as plt
from pylinac import PicketFence
from pylinac.picketfence import MLC
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image
from logs.logger import setup_logger

log = setup_logger("picketfenceqa.py")

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

def process_picketfence(file_path, tolerance, action_level, mlc_type, separate_leaves=False, nominal_gap=None):

    log.info(f"Picket Fence analysis started")

    # Convert nominal_gap to float if separate_leaves is True
    if separate_leaves:
        try:
            nominal_gap = float(nominal_gap)
        except ValueError:
            print("Error: Nominal gap must be a valid number.")
            return []

    # Initialize PicketFence with the specified MLC type
    pf = PicketFence(file_path, mlc=MLC[mlc_type])

    try:
        if separate_leaves:
            # Perform analysis with separate leaves and nominal gap
            pf.analyze(tolerance=tolerance, action_tolerance=action_level, separate_leaves=True,
                       nominal_gap_mm=nominal_gap)
        else:
            # Perform analysis without separate leaves
            pf.analyze(tolerance=tolerance, action_tolerance=action_level, separate_leaves=False)

    except ValueError as e:
        if 'cannot convert float NaN to integer' in str(e):
            print("Error: Encountered NaN value in analysis. Please check input data.")
            return []
        else:
            log.error(f"Error found:{e}")
            raise e

    pf_results = pf.results()
    print(pf_results)
    elements = []
    add_picketfence_results_to_pdf(elements, pf, pf_results)
    log.info("Picket Fence Analysis Completed")
    return elements
def add_picketfence_results_to_pdf(elements, pf, pf_results):
    title = 'PicketFence Analysis Report'
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    results_lines = pf.results().split('\n')
    for line in results_lines:
        elements.append(Paragraph(line, styles['Normal']))
    buf = BytesIO()
    pf.plot_analyzed_image(show=False, )
    plt.savefig(buf, format='png')
    buf.seek(0)
    analyzed_img = Image(buf, width=6 * inch, height=4 * inch)
    elements.append(analyzed_img)

    buf_hist = BytesIO()
    pf.plot_histogram(show=False)
    plt.savefig(buf_hist, format='png')
    buf_hist.seek(0)
    hist_img = Image(buf_hist, width=6 * inch, height=4 * inch)
    elements.append(hist_img)
