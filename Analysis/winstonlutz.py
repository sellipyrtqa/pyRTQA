from io import BytesIO
import matplotlib.pyplot as plt
from pylinac import WinstonLutz
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image
from PIL import Image as PILImage
from logs.logger import setup_logger

log = setup_logger("winstonlutz.py")

styles = getSampleStyleSheet()
header_style = ParagraphStyle(
    'HeaderStyle',
    parent=styles['Title'],
    textColor=colors.darkblue
)
footer_style = ParagraphStyle(
    'FooterStyle',
    parent=styles['Normal'],
    textColor=colors.black
)

def process_winstonlutz(folder_path, bb_size):
    log.info(f"Winston Lutz Analysis started..")
    try:
        wl = WinstonLutz(folder_path)
        wl.analyze(bb_size_mm=bb_size)

        wl_results = wl.results()
        print(wl_results)
        elements = []
        add_wl_results_to_pdf(elements, wl, wl_results)
    except Exception as e:
        print(f"Error Found: {e}")
        log.error(f"Error Found :{e}")
        raise
    log.info("Winston Lutz Analysis Completed and report generated")
    return elements

def add_wl_results_to_pdf(elements, wl, wl_results):
    title = 'Winston-Lutz Analysis Report'
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    results_lines = wl.results().split('\n')
    for line in results_lines:
        elements.append(Paragraph(line, styles['Normal']))
    elements.append(Spacer(1, 12))

    def save_plot_with_fixed_legend(plot_func):
        buf = BytesIO()
        plot_func(show=False)
        plt.legend(loc="upper right")  # Avoid slow 'best' setting
        plt.savefig(buf, format='png')
        buf.seek(0)
        return Image(buf, width=6 * inch, height=4 * inch)

    elements.append(save_plot_with_fixed_legend(wl.plot_location))
    elements.append(save_plot_with_fixed_legend(wl.plot_summary))
    elements.append(save_plot_with_fixed_legend(wl.plot_images))
