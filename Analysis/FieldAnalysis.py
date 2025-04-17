from pylinac import FieldProfileAnalysis, Centering, Normalization, Edge
from pylinac.metrics.profile import (
    PenumbraLeftMetric, PenumbraRightMetric,
    SymmetryAreaMetric, SymmetryPointDifferenceQuotientMetric,
    FlatnessDifferenceMetric, FlatnessRatioMetric
)
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image
from reportlab.lib.utils import ImageReader
from io import BytesIO
from logs.logger import setup_logger

log = setup_logger("FieldAnalysis.py")

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


def add_fa_results_to_pdf(elements, field_analyzer, energy, depth):
    title = 'Field Profile Analysis Report'
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    info = Paragraph(f"Energy (MV) = {energy}<br/>Depth (cm) = {depth}", styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 12))

    # Add analysis results text
    results_lines = field_analyzer.results().split('\n')
    for line in results_lines:
        elements.append(Paragraph(line, styles['Normal']))

    # Call plot_analyzed_images once to get all figures
    figures = field_analyzer.plot_analyzed_images(show=False)
    for fig in figures:
        buf = BytesIO()

        # Save figure to buffer
        fig.savefig(buf, format='png')
        buf.seek(0)

        # Load buffer as PIL Image, then wrap in ImageReader for ReportLab
        pil_image = PILImage.open(buf)
        reportlab_image = ImageReader(pil_image)  # ImageReader keeps PIL image in memory

        # Add the ReportLab-compatible image to the elements
        analyzed_img = Image(reportlab_image, width=6 * inch, height=4 * inch)
        elements.append(analyzed_img)
        elements.append(Spacer(1, 12))

        # Close the buffer and figure to free resources
        buf.close()
        plt.close(fig)


def process_FA(file_path, energy, depth):
    log.info("Field Analysis started")
    field_analyzer = FieldProfileAnalysis(file_path)
    field_analyzer.analyze(
        centering=Centering.BEAM_CENTER,
        x_width=0.02,
        y_width=0.02,
        normalization=Normalization.BEAM_CENTER,
        edge_type=Edge.INFLECTION_DERIVATIVE,
        ground=True,
        metrics=(
            PenumbraLeftMetric(), PenumbraRightMetric(),
            SymmetryAreaMetric(), SymmetryPointDifferenceQuotientMetric(),
            FlatnessDifferenceMetric(), FlatnessRatioMetric(),
        ),
    )
    print(field_analyzer.results())
    elements = []
    add_fa_results_to_pdf(elements, field_analyzer, energy, depth)
    log.info("Field Analysis and report generation completed")
    return elements
