"""
Utility functions for the pneumonia detection system
"""
import os
import random
import numpy as np
import cv2
import io
import logging
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)  # Added logger initialization

def process_xray_image(image_path):
    """
    Analyze X-ray image for pneumonia detection
    
    This is a simulation function. In a real-world scenario, this would use
    a trained deep learning model to analyze the X-ray image.
    
    Args:
        image_path: Path to the X-ray image file
        
    Returns:
        tuple: (result, confidence_score)
            result: 'positive' for pneumonia detected, 'negative' for normal
            confidence_score: Confidence score between 0-100
    """
    # In a real implementation, this would load a trained model
    # model = load_model(os.path.join(settings.AI_MODEL_PATH, 'pneumonia_model.h5'))
    
    try:
        # Load and preprocess the image
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            logger.error(f"Failed to load X-ray image: {image_path}")
            return 'negative', 60.0
        
        # Resize image to standard size
        img = cv2.resize(img, (224, 224))
        
        # Normalize pixel values
        img = img / 255.0
        
        # In a real implementation, this would predict using the model
        # prediction = model.predict(np.expand_dims(img, axis=0))
        
        # For simulation, generate random results with some bias
        # This simulates approximately 30% positive cases
        is_pneumonia = random.random() < 0.3
        
        if is_pneumonia:
            # Positive case (pneumonia detected)
            result = 'positive'
            # Generate confidence between 65% and 95%
            confidence = random.uniform(65.0, 95.0)
        else:
            # Negative case (normal)
            result = 'negative'
            # Generate confidence between 70% and 98%
            confidence = random.uniform(70.0, 98.0)
        
        logger.info(f"X-ray analysis result: {result}, confidence: {confidence:.1f}%")
        return result, round(confidence, 1)
        
    except Exception as e:
        logger.error(f"Error analyzing X-ray {image_path}: {str(e)}")
        return 'negative', 60.0

def generate_pdf_report(xray, report):
    """
    Generate a PDF report for an X-ray analysis
    
    Args:
        xray: XRay model instance
        report: Report model instance
        
    Returns:
        ContentFile: PDF file content
    """
    logger.info(f"Generating PDF for X-ray ID: {xray.id}, Report ID: {report.id}")
    logger.info(f"X-ray upload_date: {xray.upload_date}, analyzed_at: {xray.analyzed_at}, Report created_at: {report.created_at}")

    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center alignment
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Build the document content
    content = []
    
    # Title
    content.append(Paragraph("Child Pneumonia Detection System", title_style))
    content.append(Paragraph("Medical Report", title_style))
    content.append(Spacer(1, 0.25*inch))
    
    # Patient Information
    content.append(Paragraph("Patient Information", heading_style))
    
    patient_data = [
        ["Patient ID:", xray.patient.patient_id],
        ["Name:", xray.patient.name],
        ["Age:", f"{xray.patient.age} years"],
        ["Gender:", "Male" if xray.patient.gender == 'M' else "Female"],
        ["Guardian:", xray.patient.guardian_name or "Not specified"],
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(patient_table)
    content.append(Spacer(1, 0.25*inch))
    
    # X-ray Information
    content.append(Paragraph("X-ray Information", heading_style))
    
    xray_data = [
        ["Upload Date:", xray.upload_date.strftime("%Y-%m-%d %H:%M:%S") if xray.upload_date else "Not available"],
        ["AI Analysis:", "Pneumonia Detected" if xray.ai_result == 'positive' else "Normal" if xray.ai_result == 'negative' else "Not analyzed"],
        ["Confidence Score:", f"{xray.confidence_score:.2f}%" if xray.confidence_score is not None else "N/A"],
        ["Analyzed By:", xray.analyzed_by.get_full_name() or xray.analyzed_by.username if xray.analyzed_by else "N/A"],
        ["Analysis Date:", xray.analyzed_at.strftime("%Y-%m-%d %H:%M:%S") if xray.analyzed_at else "Not analyzed"],
    ]
    
    xray_table = Table(xray_data, colWidths=[2*inch, 4*inch])
    xray_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(xray_table)
    content.append(Spacer(1, 0.25*inch))
    
    # X-ray Image
    try:
        img_path = xray.image.path
        img = Image(img_path, width=4*inch, height=4*inch)
        content.append(img)
    except Exception as e:
        logger.warning(f"Failed to include X-ray image: {str(e)}")
        content.append(Paragraph("X-ray image not available", normal_style))
    
    content.append(Spacer(1, 0.25*inch))
    
    # Medical Assessment
    content.append(Paragraph("Medical Assessment", heading_style))
    
    content.append(Paragraph("<b>Diagnosis:</b>", normal_style))
    content.append(Paragraph(report.diagnosis or "N/A", normal_style))
    content.append(Spacer(1, 0.1*inch))
    
    content.append(Paragraph("<b>Recommendations:</b>", normal_style))
    content.append(Paragraph(report.recommendations or "None", normal_style))
    content.append(Spacer(1, 0.1*inch))
    
    if report.severity:
        content.append(Paragraph(f"<b>Severity:</b> {report.severity.capitalize()}", normal_style))
    
    content.append(Spacer(1, 0.5*inch))
    
    # Doctor Information
    content.append(Paragraph("Report Information", heading_style))
    
    doctor_data = [
        ["Doctor:", report.doctor.get_full_name() or report.doctor.username],
        ["Report Date:", report.created_at.strftime("%Y-%m-%d %H:%M:%S") if report.created_at else "Not available"],
    ]
    
    doctor_table = Table(doctor_data, colWidths=[2*inch, 4*inch])
    doctor_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(doctor_table)
    
    # Build the PDF
    doc.build(content)
    
    # Get the PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return ContentFile(pdf_content)