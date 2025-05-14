from io import BytesIO
import matplotlib.pyplot as plt
from pylinac import LeedsTOR
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image
from logs.logger import setup_logger

log = setup_logger("Leeds_TOR.py")

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

def process_leedsTOR(file_path):
    log.info(f"LeedsTOR Analysis started..")
    try:
        let = LeedsTOR(file_path)
        let.analyze(low_contrast_threshold=0.01, high_contrast_threshold=0.5)
        print(let.results())
        elements = []
        add_let_results_to_pdf(elements, let)
    except Exception as e:
        log.error(f"Error found {e}")
        raise
    log.info(f"LeedsTOR Analysis completed and report generated")
    return elements

def add_let_results_to_pdf(elements, let):
    title = 'Leeds TOR Analysis Report'
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    results_lines = let.results().split('\n')
    for line in results_lines:
        elements.append(Paragraph(line, styles['Normal']))


    buf = BytesIO()
    let.plot_analyzed_image(show=False, image=True, low_contrast=False, high_contrast=False)
    plt.savefig(buf, format='png')
    buf.seek(0)
    analyzed_img = Image(buf, width=4 * inch, height=4 * inch)
    elements.append(analyzed_img)

    buf = BytesIO()
    let.plot_analyzed_image(show=False, image=False, low_contrast=True, high_contrast=False)
    plt.savefig(buf, format='png')
    buf.seek(0)
    analyzed_img = Image(buf, width=4 * inch, height=4 * inch)
    elements.append(analyzed_img)

    buf = BytesIO()
    let.plot_analyzed_image(show=False, image=False, low_contrast=False, high_contrast=True)
    plt.savefig(buf, format='png')
    buf.seek(0)
    analyzed_img = Image(buf, width=4 * inch, height=4 * inch)
    elements.append(analyzed_img)


