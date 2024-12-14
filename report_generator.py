"""
PDF report generation functionality for dental X-ray analysis.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from PIL import Image as PILImage
import io
import logging
from ui_components import DiagnosisData

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Handles PDF report generation for dental X-ray analysis."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        # Create custom styles with unique names
        self.styles.add(ParagraphStyle(
            name='ReportTitle',  # Changed from Heading1
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='DiagnosisText',  # Changed from Diagnosis
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',  # Changed from SectionHeader
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CaseNumber',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1976d2'),
            spaceBefore=10,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=30
        ))

    def generate_report(self, file_path: str, cases: list):
        """Generate PDF report from analyzed cases."""
        try:
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            story = []
            self._add_header(story)
            
            for idx, case in enumerate(cases, 1):
                self._add_case(story, case, idx)
                story.append(Spacer(1, 30))
            
            doc.build(story)
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {str(e)}")
            raise

    def _add_header(self, story: list):
        """Add report header."""
        # Add logo and title in a table
        logo_text = "🦷"  # Dental emoji as logo
        header_data = [[
            Paragraph(logo_text, self.styles['ReportTitle']),  # Changed style name
            Paragraph("DentAI Pro - Dental X-Ray Analysis Report", self.styles['ReportTitle'])  # Changed style name
        ]]
        header_table = Table(header_data, colWidths=[1*inch, 6*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(header_table)
        
        # Add date and report info
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated on: {date_str}", self.styles['Normal']))
        story.append(Paragraph(
            "Powered by AI for accurate dental pathology detection", 
            self.styles['Subtitle']  # Using the new style name
        ))

    def _add_case(self, story: list, case: dict, case_number: int):
        """Add a single case to the report."""
        # Add case number
        story.append(Paragraph(
            f"Case #{case_number}",
            self.styles['CaseNumber']  # Using the new style name
        ))

        # Add image
        try:
            img = PILImage.open(case['image_path'])
            img_width = 400
            aspect = img.height / img.width
            img_height = int(img_width * aspect)
            
            img_data = io.BytesIO()
            img.save(img_data, format='PNG')
            img_data.seek(0)
            
            img_for_pdf = Image(img_data, width=img_width, height=img_height)
            story.append(img_for_pdf)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            logger.error(f"Failed to add image to report: {str(e)}")
            story.append(Paragraph("Error: Could not load image", self.styles['Normal']))

        # Add diagnosis and confidence in a table
        diag_data = [[
            Paragraph(f"Diagnosis: {case['diagnosis']}", self.styles['DiagnosisText']),  # Changed style name
            Paragraph(f"Confidence: {case['confidence']:.1f}%", self.styles['Normal'])
        ]]
        diag_table = Table(diag_data, colWidths=[4*inch, 3*inch])
        diag_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(diag_table)
        story.append(Spacer(1, 20))

        # Add findings
        self._add_section(story, "Initial Radiographic Assessment", case['findings'])
        
        # Add management plan
        if 'management' in case:
            self._add_section(story, "Immediate Action Required", case['management']['Immediate Action'])
            self._add_section(story, "Long-term Management Plan", case['management']['Long-term Plan'])

        # Add recommendations
        if 'recommendations' in case:
            self._add_section(story, "Clinical Recommendations", 
                            [f"{rec[0]} {rec[1]}" for rec in case['recommendations']])

    def _add_section(self, story: list, title: str, items: list):
        """Add a section with title and items."""
        story.append(Paragraph(title, self.styles['SectionTitle']))  # Changed style name
        
        # Create a table for items with alternating background
        data = [[Paragraph(f"• {item}", self.styles['Normal'])] for item in items]
        if data:
            table = Table(data, colWidths=[6.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa') if i % 2 else colors.white)
                for i in range(len(data))
            ] + [
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(table)
        story.append(Spacer(1, 10))

def prepare_case_data(image_card) -> dict:
    """Prepare case data from ImageCard widget."""
    return {
        'image_path': image_card.image_path,
        'diagnosis': image_card.primary_diagnosis.title(),
        'confidence': image_card.predictions[0][1] * 100,
        'findings': [f"{item[0]} {item[1]}" for item in image_card._get_findings_for_diagnosis()],
        'recommendations': image_card._get_recommendations(),
        'management': DiagnosisData.MANAGEMENT_MAP.get(image_card.primary_diagnosis, {})
    }