from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os
import uuid
import io

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkblue
        ))
        
        # Normal style with better spacing
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
    
    def generate_patient_report(self, patient_info, prediction_result, scan_type, image_path=None):
        """Generate a comprehensive patient report (saves to file)"""
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"report_{scan_type}_{timestamp}_{unique_id}.pdf"
        
        # Ensure reports directory exists
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        filepath = os.path.join(reports_dir, filename)
        
        # Create the PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Add header
        story.append(Paragraph("MedScan AI - Medical Imaging Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Add patient information section
        story.append(Paragraph("Patient Information", self.styles['CustomSubtitle']))
        
        patient_data = [
            ['Patient Name:', patient_info.get('name', 'N/A')],
            ['Age:', patient_info.get('age', 'N/A')],
            ['Gender:', patient_info.get('gender', 'N/A')],
            ['Date of Scan:', patient_info.get('scan_date', datetime.now().strftime("%Y-%m-%d"))],
            ['Report Date:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['Report ID:', f"RPT-{timestamp}-{unique_id}"]
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 3*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # Add scan information
        story.append(Paragraph(f"Scan Analysis - {scan_type.upper()}", self.styles['CustomSubtitle']))
        
        scan_data = [
            ['Scan Type:', scan_type.upper()],
            ['Prediction:', prediction_result.get('prediction', 'N/A')],
            ['Confidence:', f"{prediction_result.get('confidence', 0):.2f}%"],
            ['Analysis Time:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        # Add additional info if available
        if prediction_result.get('message'):
            scan_data.append(['Additional Info:', prediction_result['message']])
        
        scan_table = Table(scan_data, colWidths=[2*inch, 3*inch])
        scan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.lightcyan),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(scan_table)
        story.append(Spacer(1, 20))
        
        # Add medical findings
        story.append(Paragraph("Medical Findings", self.styles['CustomSubtitle']))
        
        findings_text = self._generate_findings_text(prediction_result, scan_type)
        story.append(Paragraph(findings_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Add recommendations
        story.append(Paragraph("Medical Recommendations", self.styles['CustomSubtitle']))
        
        recommendations_text = self._generate_recommendations_text(prediction_result, scan_type)
        story.append(Paragraph(recommendations_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Add disclaimer
        story.append(Paragraph("Important Disclaimer", self.styles['CustomSubtitle']))
        disclaimer_text = (
            "This report was generated by an AI system and should be reviewed by a qualified "
            "medical professional. The AI predictions are meant to assist healthcare providers "
            "and should not be used as the sole basis for medical diagnosis or treatment decisions. "
            "Always consult with a qualified healthcare provider for medical diagnosis and treatment."
        )
        story.append(Paragraph(disclaimer_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 30))
        
        # Add footer
        footer_text = (
            "Generated by MedScan AI | For medical professional use only | "
            f"Page 1 of 1 | Report ID: RPT-{timestamp}-{unique_id}"
        )
        story.append(Paragraph(footer_text, self.styles['CustomNormal']))
        
        # Build PDF
        try:
            doc.build(story)
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'report_id': f"RPT-{timestamp}-{unique_id}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_patient_report_to_bytes(self, patient_info, prediction_result, scan_type, image_path=None):
        """Generate a comprehensive patient report and return as bytes (for database storage)"""
        # Create unique report ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        report_id = f"RPT-{timestamp}-{unique_id}"
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Add header
        story.append(Paragraph("MedScan AI - Medical Imaging Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Add patient information section
        story.append(Paragraph("Patient Information", self.styles['CustomSubtitle']))
        
        patient_data = [
            ['Patient Name:', patient_info.get('name', 'N/A')],
            ['Age:', patient_info.get('age', 'N/A')],
            ['Gender:', patient_info.get('gender', 'N/A')],
            ['Date of Scan:', patient_info.get('scan_date', datetime.now().strftime("%Y-%m-%d"))],
            ['Report Date:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['Report ID:', report_id]
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 3*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # Add scan information
        story.append(Paragraph(f"Scan Analysis - {scan_type.upper()}", self.styles['CustomSubtitle']))
        
        scan_data = [
            ['Scan Type:', scan_type.upper()],
            ['Prediction:', prediction_result.get('prediction', 'N/A')],
            ['Confidence:', f"{prediction_result.get('confidence', 0):.2f}%"],
            ['Analysis Time:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        # Add additional info if available
        if prediction_result.get('message'):
            scan_data.append(['Additional Info:', prediction_result['message']])
        
        scan_table = Table(scan_data, colWidths=[2*inch, 3*inch])
        scan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.lightcyan),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(scan_table)
        story.append(Spacer(1, 20))
        
        # Add medical findings
        story.append(Paragraph("Medical Findings", self.styles['CustomSubtitle']))
        
        findings_text = self._generate_findings_text(prediction_result, scan_type)
        story.append(Paragraph(findings_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Add recommendations
        story.append(Paragraph("Medical Recommendations", self.styles['CustomSubtitle']))
        
        recommendations_text = self._generate_recommendations_text(prediction_result, scan_type)
        story.append(Paragraph(recommendations_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Add disclaimer
        story.append(Paragraph("Important Disclaimer", self.styles['CustomSubtitle']))
        disclaimer_text = (
            "This report was generated by an AI system and should be reviewed by a qualified "
            "medical professional. The AI predictions are meant to assist healthcare providers "
            "and should not be used as the sole basis for medical diagnosis or treatment decisions. "
            "Always consult with a qualified healthcare provider for medical diagnosis and treatment."
        )
        story.append(Paragraph(disclaimer_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 30))
        
        # Add footer
        footer_text = (
            "Generated by MedScan AI | For medical professional use only | "
            f"Page 1 of 1 | Report ID: {report_id}"
        )
        story.append(Paragraph(footer_text, self.styles['CustomNormal']))
        
        # Build PDF
        try:
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return {
                'success': True,
                'pdf_bytes': pdf_bytes,
                'report_id': report_id
            }
        except Exception as e:
            buffer.close()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_findings_text(self, prediction_result, scan_type):
        """Generate medical findings text based on prediction"""
        prediction = prediction_result.get('prediction', 'Unknown')
        confidence = prediction_result.get('confidence', 0)
        
        if scan_type.lower() == 'brain':
            if 'Tumor' in prediction:
                return (
                    f"The AI analysis indicates a {confidence:.1f}% confidence level for tumor detection. "
                    "The system has identified patterns consistent with abnormal brain tissue. "
                    "Further medical evaluation including neurological examination and additional imaging "
                    "studies may be recommended."
                )
            else:
                return (
                    f"The AI analysis shows a {confidence:.1f}% confidence level for normal brain tissue. "
                    "No apparent tumor-like abnormalities were detected in the provided scan. "
                    "However, this does not rule out all possible conditions, and clinical correlation "
                    "with symptoms and physical examination is essential."
                )
        elif scan_type.lower() == 'chest':
            if 'Pneumonia' in prediction:
                return (
                    f"The AI analysis indicates a {confidence:.1f}% confidence level for pneumonia. "
                    "The system has identified patterns consistent with lung inflammation and infection. "
                    "Clinical correlation with patient symptoms, physical examination findings, and "
                    "laboratory tests is recommended for definitive diagnosis."
                )
            else:
                return (
                    f"The AI analysis shows a {confidence:.1f}% confidence level for normal lung tissue. "
                    "No apparent pneumonia-like abnormalities were detected in the provided chest X-ray. "
                    "However, other pulmonary conditions may not be detected by this analysis, and "
                    "clinical correlation with patient presentation is essential."
                )
        else:
            return f"AI analysis shows {prediction} with {confidence:.1f}% confidence level."
    
    def _generate_recommendations_text(self, prediction_result, scan_type):
        """Generate medical recommendations based on prediction"""
        prediction = prediction_result.get('prediction', 'Unknown')
        
        if scan_type.lower() == 'brain':
            if 'Tumor' in prediction:
                return (
                    "1. Immediate consultation with a neurologist or neurosurgeon is recommended.\n"
                    "2. Consider advanced imaging studies (MRI with contrast, CT scan).\n"
                    "3. Neurological examination and cognitive assessment.\n"
                    "4. Possible referral for biopsy if clinically indicated.\n"
                    "5. Regular monitoring and follow-up imaging as recommended by specialist."
                )
            else:
                return (
                    "1. Routine follow-up with primary care physician.\n"
                    "2. Continue regular health monitoring.\n"
                    "3. Seek medical attention if new symptoms develop.\n"
                    "4. Consider routine screening as per standard medical guidelines."
                )
        elif scan_type.lower() == 'chest':
            if 'Pneumonia' in prediction:
                return (
                    "1. Immediate medical consultation with healthcare provider.\n"
                    "2. Clinical assessment including respiratory examination.\n"
                    "3. Laboratory tests including complete blood count and inflammatory markers.\n"
                    "4. Consider chest X-ray follow-up after treatment.\n"
                    "5. Monitor for respiratory distress and seek emergency care if needed."
                )
            else:
                return (
                    "1. Follow up with primary care physician for routine care.\n"
                    "2. Monitor for any respiratory symptoms.\n"
                    "3. Maintain regular health check-ups.\n"
                    "4. Seek medical attention if respiratory symptoms develop."
                )
        else:
            return "Consult with a qualified healthcare provider for proper medical evaluation and treatment."
