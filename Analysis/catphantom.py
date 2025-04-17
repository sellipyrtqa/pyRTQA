import logging
from logs.logger import setup_logger

log = setup_logger("catphantom.py")

from pylinac import CatPhan503, CatPhan504, CatPhan600, CatPhan604
from io import BytesIO
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image

styles = getSampleStyleSheet()


def process_catphantom(file_path, phantom_type):
    log.info(f"Processing CatPhantom: {phantom_type} from {file_path}")

    # Map the string from combobox to the correct pylinac class
    phantom_classes = {
        "CatPhan503": CatPhan503,
        "CatPhan504": CatPhan504,
        "CatPhan600": CatPhan600,
        "CatPhan604": CatPhan604
    }

    if phantom_type not in phantom_classes:
        log.error(f"Invalid phantom type: {phantom_type}")
        raise ValueError(f"Invalid phantom type: {phantom_type}")

    phantom_class = phantom_classes[phantom_type]
    my_cbct = phantom_class(file_path)
    # my_cbct.hu_origin_slice_variance = 670
    my_cbct.analyze()

    log.info("CatPhantom analysis completed.")

    cp_results = my_cbct.results()
    # log.info(f"Analysis Results: {cp_results}")

    elements = []
    add_cp_results_to_pdf(elements, my_cbct, cp_results)

    return elements


def add_cp_results_to_pdf(elements, my_cbct, cp_results):
    log.info("Generating PDF report for CatPhantom analysis.")

    title = 'Cat Phantom Analysis Report'
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    results_lines = cp_results.split('\n')
    for line in results_lines:
        elements.append(Paragraph(line, styles['Normal']))
    elements.append(Spacer(1, 15))

    subimages = ['hu', 'un', 'sp', 'lc', 'mtf', 'lin', 'prof', 'side']

    for sub in subimages:
        buf = BytesIO()
        my_cbct.plot_analyzed_subimage(subimage=sub, show=False)
        plt.savefig(buf, format='png')
        buf.seek(0)
        analyzed_img = Image(buf, width=6 * inch, height=3 * inch)
        elements.append(analyzed_img)
        elements.append(Spacer(1, 12))

    log.info("PDF report generation completed.")


if __name__ == "__main__":
    log.info("Running CatPhantom analysis standalone.")
