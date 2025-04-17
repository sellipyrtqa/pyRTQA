import io
from decimal import Decimal, getcontext
from tkinter import messagebox
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle
import logging
from logs.logger import setup_logger

log = setup_logger("fffanalysis.py")

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

getcontext().prec = 2

class PointXY:
    maxSlope = float('-inf')
    minSlope = float('inf')
    Y1 = 0
    Y2 = 0

    def __init__(self, index, x, y):
        self.index = index
        self.x = x
        self.y = y
        self.slope = -2222

    def calcSlope(self, p):
        dy = p.y - self.y
        dx = p.x - self.x
        self.slope = dy / dx if dx != 0 else float('inf')
        if self.slope > PointXY.maxSlope:
            PointXY.maxSlope = self.slope
            PointXY.Y1 = self.y
        if self.slope < PointXY.minSlope:
            PointXY.minSlope = self.slope
            PointXY.Y2 = self.y

class Process:
    @staticmethod
    def calculate(points):
        for i in range(len(points) - 1):
            points[i].calcSlope(points[i + 1])

        max_slope = Decimal(PointXY.maxSlope)
        min_slope = Decimal(PointXY.minSlope)

        RDV = (PointXY.Y1 + PointXY.Y2) / 2
        upperY = RDV * 1.6
        lowerY = RDV * 0.4

        negUpperX = Process.predictX(upperY, points, -1)
        posUpperX = Process.predictX(upperY, points, 1)

        negLowerX = Process.predictX(lowerY, points, -1)
        posLowerX = Process.predictX(lowerY, points, 1)

        deltaNegativeX = abs(negLowerX - negUpperX)
        deltaPositiveX = abs(posLowerX - posUpperX)

        negAvgX = Process.predictX(RDV, points, -1)
        posAvgX = Process.predictX(RDV, points, 1)
        diffAvgX = posAvgX - negAvgX

        negX90Y = Process.predictX(90, points, -1)
        posX90Y = Process.predictX(90, points, 1)
        diffX90Y = posX90Y - negX90Y

        negX75Y = Process.predictX(75, points, -1)
        posX75Y = Process.predictX(75, points, 1)
        diffX75Y = posX75Y - negX75Y

        negX60Y = Process.predictX(60, points, -1)
        posX60Y = Process.predictX(60, points, 1)
        diffX60Y = posX60Y - negX60Y

        results = {
            'max_slope': max_slope,
            'min_slope': min_slope,
            'RDV': RDV,
            'PLu': negUpperX,
            'PLd': negLowerX,
            'Penumbra_Left(mm)': deltaNegativeX * 10,
            'PRu': posUpperX,
            'PRd': posLowerX,
            'Penumbra_Right(mm)': deltaPositiveX * 10,
            'IPL': negAvgX,
            'IPR': posAvgX,
            'Field size(mm)': diffAvgX * 10,
            '90-': negX90Y,
            '90+': posX90Y,
            'X90%': diffX90Y,
            '75-': negX75Y,
            '75+': posX75Y,
            'X75%': diffX75Y,
            '60-': negX60Y,
            '60+': posX60Y,
            'X60%': diffX60Y
        }

        for key, value in results.items():
            print(f"{key} = {value:.2f}")

        return results

    @staticmethod
    def predictX(y, points, isNeg):
        minDiffWithY = float('inf')
        predictedX = float('inf')

        for p in points:
            diffWithY = abs(p.y - y)
            if diffWithY < minDiffWithY and (p.x * isNeg) > 0:
                minDiffWithY = diffWithY
                predictedX = p.x

        return predictedX

def read_excel_to_points(file_path):
    xl = pd.ExcelFile(file_path)

    required_sheets = ['Inline', 'Crossline']
    required_columns = {
        'Inline': ['Inline(cm)', 'Inline(mm)'],
        'Crossline': ['Crossline(cm)', 'Crossline(mm)']
    }

    points1, points2 = None, None

    # Check for required sheets
    for sheet in required_sheets:
        if sheet not in xl.sheet_names:
            raise ValueError(f"Required sheet '{sheet}' not found in the Excel file.")

    # Process Inline sheet
    points_sheet1 = xl.parse('Inline')
    if 'Inline(cm)' in points_sheet1.columns:
        points1 = [PointXY(index, row['Inline(cm)'], row['Dose(%)']) for index, row in points_sheet1.iterrows()]
    elif 'Inline(mm)' in points_sheet1.columns:
        points1 = [PointXY(index, row['Inline(mm)'] / 10.0, row['Dose(%)']) for index, row in points_sheet1.iterrows()]
    else:
        raise ValueError("Required columns 'Inline(cm)' or 'Inline(mm)' not found in the 'Inline' sheet.")

    # Process Crossline sheet
    points_sheet2 = xl.parse('Crossline')
    if 'Crossline(cm)' in points_sheet2.columns:
        points2 = [PointXY(index, row['Crossline(cm)'], row['Dose(%)']) for index, row in points_sheet2.iterrows()]
    elif 'Crossline(mm)' in points_sheet2.columns:
        points2 = [PointXY(index, row['Crossline(mm)'] / 10.0, row['Dose(%)']) for index, row in
                   points_sheet2.iterrows()]
    else:
        raise ValueError("Required columns 'Crossline(cm)' or 'Crossline(mm)' not found in the 'Crossline' sheet.")

    return points1, points2

def plot_to_image(points, results, profile_type):
    x = [point.x for point in points]
    y = [point.y for point in points]

    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='b', markersize=2)  # Thin points

    plt.plot([results['90-'], results['90+']], [90, 90], 'm-', lw=1.5)
    plt.plot([results['75-'], results['75+']], [75, 75], 'y-', lw=1.5)
    plt.plot([results['60-'], results['60+']], [60, 60], 'k-', lw=1.5)

    plt.plot([results['PLu'], results['PRu']], [results['RDV'] * 1.6, results['RDV'] * 1.6], 'g-', lw=1.5)
    plt.plot([results['PLd'], results['PRd']], [results['RDV'] * 0.4, results['RDV'] * 0.4], 'c-', lw=1.5)

    plt.plot([results['IPL'], results['IPR']], [results['RDV'], results['RDV']], 'r-', lw=1.5)

    line_labels = {
        'RDV': ('r', results['RDV']),
        '1.6*RDV': ('g', results['RDV'] * 1.6),
        '0.4*RDV': ('c', results['RDV'] * 0.4),
        '90% Dose': ('m', 90),
        '75% Dose': ('y', 75),
        '60% Dose': ('k', 60)
    }

    for label, (color, y_value) in line_labels.items():
        plt.text(0, y_value, label, color=color, ha='center', va='bottom', fontsize=10, weight='bold')

    point_labels = [
        ('PLu', results['PLu'], results['RDV'] * 1.6),
        ('PRu', results['PRu'], results['RDV'] * 1.6),
        ('PLd', results['PLd'], results['RDV'] * 0.4),
        ('PRd', results['PRd'], results['RDV'] * 0.4),
        ('IPL', results['IPL'], results['RDV']),
        ('IPR', results['IPR'], results['RDV']),
    ]

    offset = 1.2  # Offset for label positions

    for label, x_value, y_value in point_labels:
        plt.scatter(x_value, y_value, color='red', s=20)  # Different color and size for scatter points
        if x_value < (max(x) + min(x)) / 2:
            ha = 'left'
            x_offset = -offset
        else:
            ha = 'right'
            x_offset = offset
        bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white")
        plt.text(x_value + x_offset, y_value, label, color='black', ha=ha, bbox=bbox_props)

    plt.xlabel('Field width (cm)', fontsize=12)
    plt.ylabel('Dose (%)', fontsize=12)

    if profile_type == 'Inline':
        plt.title('Beam Profile Inline', fontsize=14, fontweight='bold')
    elif profile_type == 'Crossline':
        plt.title('Beam Profile Crossline', fontsize=14, fontweight='bold')
    else:
        plt.title('Beam Profile', fontsize=14, fontweight='bold')

    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().set_facecolor('lightgrey')  # Background color for the graph

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def add_fffresults_to_pdf(elements, results, profile_type, img_data, energy, depth):
    title = f'FFF Analysis Report - {profile_type}'
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    info = Paragraph(f"Energy(MV)= {energy}<br/>Depth(cm)= {depth}", styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 12))

    data = [['Parameter', 'Value']]
    for key, value in results.items():
        if key not in ['max_slope', 'min_slope']:  # Exclude these parameters
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            data.append([key, formatted_value])

    table = Table(data, colWidths=[3 * inch, 3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    image = Image(img_data)
    image.drawHeight = 5 * inch
    image.drawWidth = 7 * inch
    elements.append(image)
    elements.append(Spacer(1, 12))
def process_fff_analysis(file_path, energy, depth):
    log.info("FFF profile analysis started")
    try:
        points1, points2 = read_excel_to_points(file_path)
    except ValueError as e:
        log.error(f"Profile analysis error:{e}")
        messagebox.showerror("Error", str(e))
        return []

    elements = []
    log.info("FFF profile analysis completed")
    if points1:
        results = Process.calculate(points1)
        img_data = plot_to_image(points1, results, 'Inline')
        add_fffresults_to_pdf(elements, results, 'Inline', img_data, energy, depth)

    if points2:
        results = Process.calculate(points2)
        img_data = plot_to_image(points2, results, 'Crossline')
        add_fffresults_to_pdf(elements, results, 'Crossline', img_data, energy, depth)
    log.info("Analysis report generation completed successfully")
    return elements