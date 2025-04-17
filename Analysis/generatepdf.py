import os
import sys
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from logs.logger import setup_logger

log = setup_logger("generatepdf.py")


def generate_pdf(elements, institution, department, measured_by, pdf_path):
    log.info(f"PDF generation started..")
    try:
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
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        content = []

        # Header text
        header_text = Paragraph(f"{institution}<br/>{department}", header_style)

        def resource_path(relative_path):
            """ Get the absolute path to the resource, works for development and PyInstaller """
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        # Path to the image
        image_path = resource_path('pyRTQA.png')
        img = Image(image_path)
        img.drawHeight = 1.0 * inch
        img.drawWidth = 1.3 * inch

        # Create a table with two columns: text on the left, image on the right
        header_data = [[header_text, img]]
        header_table = Table(header_data, colWidths=[5.5 * inch, 1.5 * inch])

        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        footer = Paragraph(f"Measured by: {measured_by}<br/> Printed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style)

        content.append(header_table)
        content.append(Spacer(1, 12))
        content.extend(elements)
        content.append(Spacer(1, 5))
        content.append(footer)

        doc.build(content)
    except Exception as e:
        log.error(f"Error found in pdf generation : {e}")
        raise
    log.info(f"Generate pdf completed")
