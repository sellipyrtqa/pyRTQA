import io
from decimal import Decimal, getcontext
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
import pydicom
from PIL import Image as PILImage  # Alias PIL's Image to PILImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle
import logging
from logs.logger import setup_logger

log = setup_logger("FFF_FA_2D.py")

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

def invert_image(pixel_array):
    """Inverts the pixel values of an image."""
    max_value = np.max(pixel_array)
    inverted_pixel_array = max_value - pixel_array  # Invert the pixel values
    return inverted_pixel_array

def read_dicom(file_path):
    """Reads a DICOM file, inverts its pixel values, and returns both the original and inverted arrays."""
    dataset = pydicom.dcmread(file_path)
    pixel_array = dataset.pixel_array
    inverted_pixel_array = invert_image(pixel_array)  # Invert the pixel array
    return pixel_array, inverted_pixel_array

def read_tiff(file_path):
    """Reads a TIFF file, inverts its pixel values, and returns the inverted array."""
    img = PILImage.open(file_path)  # Use PILImage to open TIFF
    pixel_array = np.array(img)  # Convert to NumPy array
    inverted_pixel_array = invert_image(pixel_array)  # Invert the pixel array
    return inverted_pixel_array  # Return only the inverted array


def extract_profile_points(pixel_array, axis=0):
    """Extracts profile points from an inverted DICOM or TIFF image along a specified axis,
    with the center of the image as 0 on the x-axis."""

    if axis == 1:  # Swapped: Inline (vertical) profile
        profile = pixel_array[:, pixel_array.shape[1] // 2]  # Middle column (vertical)
        image_height = profile.shape[0]
        half_height = image_height // 2
        x_values = np.linspace(-half_height, half_height, image_height)

    else:  # Swapped: Crossline (horizontal) profile
        profile = pixel_array[pixel_array.shape[0] // 2, :]  # Middle row (horizontal)
        image_width = profile.shape[0]
        half_width = image_width // 2
        x_values = np.linspace(-half_width, half_width, image_width)

    max_val = np.max(profile)
    norm_profile = (profile / max_val) * 100  # Normalize to percentage

    # Create PointXY objects with x-values centered around 0
    points = [PointXY(i, x_values[i] / 40, norm_profile[i]) for i in range(len(norm_profile))]

    return points

def process_dicom_or_tiff(file_path, file_type):
    """Main function to process the DICOM or TIFF file and return points and the original image."""
    if file_type == 'DICOM':
        original_pixel_array, pixel_array = read_dicom(file_path)  # DICOM returns both original and inverted
    elif file_type == 'TIFF':
        original_pixel_array = None  # No original for TIFF
        pixel_array = read_tiff(file_path)  # TIFF returns the inverted pixel array only
    else:
        raise ValueError("Unsupported file type")

    # Extract points for inline and crossline profiles
    points_inline = extract_profile_points(pixel_array, axis=0)
    points_crossline = extract_profile_points(pixel_array, axis=1)

    return points_inline, points_crossline, original_pixel_array, pixel_array  # Return pixel_array for TIFF


def plot_image_with_inline_crossline(pixel_array, image_type):
    """
    Plot the DICOM or TIFF image with Inline (vertical) and Crossline (horizontal) axes.
    Returns the image with axes as a BytesIO object.
    """
    plt.figure(figsize=(9, 9))
    plt.imshow(pixel_array, cmap='gray')  # Display the image in grayscale

    # Add Inline (vertical) and Crossline (horizontal) axes
    plt.axvline(pixel_array.shape[1] // 2, color='blue', linestyle='--', label='Inline')  # Inline axis (vertical)
    plt.axhline(pixel_array.shape[0] // 2, color='green', linestyle='--', label='Crossline')  # Crossline axis (horizontal)

    # Labeling the axes Inline (vertical) and Crossline (horizontal)
    plt.text(pixel_array.shape[1] // 2 + 20, pixel_array.shape[0] // 2 - 50, 'Inline', color='blue', fontsize=12,
             fontweight='bold', rotation=90)
    plt.text(pixel_array.shape[1] // 2 - 150, pixel_array.shape[0] // 2 + 40, 'Crossline', color='green', fontsize=12,
             fontweight='bold')

    plt.title(f'{image_type} Image with Inline and Crossline Axes')

    # Save the plot to a BytesIO object in PNG format
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return buf  # Return BytesIO object containing the PNG image


def plot_to_image(points, results, profile_type):
    """Plot the profile points and return the image as bytes, with labeled points and larger point sizes."""
    x = [point.x for point in points]
    y = [point.y for point in points]

    plt.figure(figsize=(10, 6))

    # Plot the profile line (with larger markers for visibility)
    plt.plot(x, y, marker='o', linestyle='-', color='b', markersize=3)  # Increase marker size to 5

    # Plot the 90%, 75%, and 60% dose lines
    plt.plot([results['90-'], results['90+']], [90, 90], 'm-', lw=1.5, label="90% Dose")
    plt.plot([results['75-'], results['75+']], [75, 75], 'y-', lw=1.5, label="75% Dose")
    plt.plot([results['60-'], results['60+']], [60, 60], 'k-', lw=1.5, label="60% Dose")

    # Plot RDV*1.6 and RDV*0.4 lines
    plt.plot([results['PLu'], results['PRu']], [results['RDV'] * 1.6, results['RDV'] * 1.6], 'g-', lw=1.5,
             label="1.6 * RDV")
    plt.plot([results['PLd'], results['PRd']], [results['RDV'] * 0.4, results['RDV'] * 0.4], 'c-', lw=1.5,
             label="0.4 * RDV")

    # Plot the IPL and IPR line (midline)
    plt.plot([results['IPL'], results['IPR']], [results['RDV'], results['RDV']], 'r-', lw=1.5, label="RDV")

    # Scatter and label key points (increase point size and add labels)
    point_labels = [
        ('PLu', results['PLu'], results['RDV'] * 1.6),
        ('PRu', results['PRu'], results['RDV'] * 1.6),
        ('PLd', results['PLd'], results['RDV'] * 0.4),
        ('PRd', results['PRd'], results['RDV'] * 0.4),
        ('IPL', results['IPL'], results['RDV']),
        ('IPR', results['IPR'], results['RDV']),
    ]

    offset = 1.8  # Offset for label positions

    for label, x_value, y_value in point_labels:
        # Plot scatter points with larger red dots
        plt.scatter(x_value, y_value, color='red', s=30, zorder=5)  # Use a larger size for scatter points

        # Adjust label positioning based on whether x_value is negative or positive
        if x_value < 0:
            # Left side (negative x-values), label should appear to the left of the point
            ha = 'right'
            x_offset = -offset  # Move label to the left
        else:
            # Right side (positive x-values), label should appear to the right of the point
            ha = 'left'
            x_offset = offset  # Move label to the right

        # Add label with the adjusted horizontal alignment and offset
        bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white")
        plt.text(x_value + x_offset, y_value, label, color='black', ha=ha, fontsize=10, bbox=bbox_props)

    # X-axis centered at 0
    plt.axvline(0, color='gray', linestyle='--', lw=1)  # Add a vertical line at x = 0 for reference

    # Set labels and title
    plt.xlabel('Field width (cm)', fontsize=12)
    plt.ylabel('Dose (%)', fontsize=12)

    if profile_type == 'Inline':
        plt.title('Beam Profile Inline', fontsize=14, fontweight='bold')
    elif profile_type == 'Crossline':
        plt.title('Beam Profile Crossline', fontsize=14, fontweight='bold')
    else:
        plt.title('Beam Profile', fontsize=14, fontweight='bold')

    # Set x-axis limits (optional: to ensure points are visible)
    plt.xlim([min(x) * 1.1, max(x) * 1.1])

    # Set y-axis limits to ensure full range of the dose is visible (optional)
    plt.ylim([min(y) * 0.9, max(y) * 1.1])

    # Add a grid and background color
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().set_facecolor('lightgrey')

    # Add legend
    plt.legend(loc='upper right')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return buf


def add_FAresults_to_pdf(elements, results, profile_type, img_data, energy, depth):
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
def process_fffFA_analysis(file_path, file_type, energy, depth):
    log.info(f"Processing FFF FA Analysis for {file_type} file: {file_path}")
    try:
        # Now capture both the original and the processed pixel arrays
        points_inline, points_crossline, original_pixel_array, pixel_array = process_dicom_or_tiff(file_path, file_type)
    except Exception as e:
        log.error(f"Error processing image: {e}")
        messagebox.showerror("Error", str(e))
        return []

    elements = []
    log.info("Generating analysis report")

    # Add the DICOM or TIFF image with Inline and Crossline axes to the PDF
    if original_pixel_array is not None:
        # Use original DICOM array if available
        img_data_with_axes = plot_image_with_inline_crossline(original_pixel_array, file_type)
    else:
        # Use processed inverted pixel array for TIFF
        img_data_with_axes = plot_image_with_inline_crossline(pixel_array, file_type)

    # Embed the image into the PDF
    pdf_image = Image(img_data_with_axes, 4 * inch, 4 * inch)  # Directly use BytesIO object

    elements.append(Paragraph(f'PROFILE ANALYSIS - AERB METHOD', styles['Title']))
    elements.append(pdf_image)
    elements.append(Spacer(1, 12))

    # Process inline and crossline points
    if points_inline:
        results_inline = Process.calculate(points_inline)
        img_data_inline = plot_to_image(points_inline, results_inline, 'Inline')
        add_FAresults_to_pdf(elements, results_inline, 'Inline', img_data_inline, energy, depth)

    if points_crossline:
        results_crossline = Process.calculate(points_crossline)
        img_data_crossline = plot_to_image(points_crossline, results_crossline, 'Crossline')
        add_FAresults_to_pdf(elements, results_crossline, 'Crossline', img_data_crossline, energy, depth)
    log.info("Analysis report generation completed successfully")
    return elements

