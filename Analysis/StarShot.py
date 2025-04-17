from io import BytesIO
import matplotlib.pyplot as plt
from pylinac import Starshot
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image
from logs.logger import setup_logger

log = setup_logger("StarShot.py")

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

def process_starshot(file_path):
    log.info(f"StarShot Analysis started..")
    try:
        ss = Starshot(file_path)
        ss.analyze()
        print(ss.results())
        elements = []
        add_ss_results_to_pdf(elements, ss)
    except Exception as e:
        log.error(f"Error found {e}")
        raise
    log.info(f"StarShot Analysis completed and report generated")
    return elements

def add_ss_results_to_pdf(elements, ss):
    title = 'StarShot Analysis Report'
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    results_lines = ss.results().split('\n')
    for line in results_lines:
        elements.append(Paragraph(line, styles['Normal']))
    buf = BytesIO()
    ss.plot_analyzed_image(show=False, )
    plt.savefig(buf, format='png')
    buf.seek(0)
    analyzed_img = Image(buf, width=6 * inch, height=4 * inch)
    elements.append(analyzed_img)

    buf_hist = BytesIO()
    ss.plot_analyzed_subimage(show=False)
    plt.savefig(buf_hist, format='png')
    buf_hist.seek(0)
    hist_img = Image(buf_hist, width=6 * inch, height=4 * inch)
    elements.append(hist_img)
