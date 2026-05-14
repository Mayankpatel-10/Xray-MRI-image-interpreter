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
        # Title style - More Clinical
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1A237E'), # Navy Blue
            fontName='Helvetica-Bold'
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
            fontSize=11,
            leading=14,
            spaceAfter=12,
            alignment=TA_LEFT
        ))

        # Signature style
        self.styles.add(ParagraphStyle(
            name='SignatureStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceBefore=30
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
    
    def generate_patient_report_to_bytes(self, patient_info, prediction_result, scan_type, heatmap_buffer=None, original_image_buffer=None):
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
        story.append(Paragraph("<font size=10>Diagnostic Analysis Document</font>", self.styles['CustomNormal']))
        
        # Horizontal line
        story.append(Spacer(1, 5))
        from reportlab.platypus import HRFlowable
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1A237E'), spaceAfter=20))
        
        # Add patient information section
        story.append(Paragraph("Patient Information", self.styles['CustomSubtitle']))
        
        patient_data = [
            ['Patient Name:', patient_info.get('name', 'N/A')],
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
        
        # Add visual analysis if images provided
        if original_image_buffer and heatmap_buffer:
            story.append(Paragraph("Imaging Analysis", self.styles['CustomSubtitle']))
            
            # Reset buffers to beginning
            original_image_buffer.seek(0)
            heatmap_buffer.seek(0)
            
            # Create Images
            # Create Images - INCREASED SIZE
            orig_img = Image(original_image_buffer, width=3.8*inch, height=3.5*inch)
            heat_img = Image(heatmap_buffer, width=3.8*inch, height=3.5*inch)
            
            image_data = [
                [orig_img, heat_img],
                [Paragraph("<b>Original Scan</b>", self.styles['CustomNormal']), 
                 Paragraph("<b>Grad-CAM AI Attention</b>", self.styles['CustomNormal'])]
            ]
            
            image_table = Table(image_data, colWidths=[3.7*inch, 3.7*inch])
            image_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            story.append(image_table)
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
        story.append(Paragraph("Important Disclaimer & System Limitations", self.styles['CustomSubtitle']))
        disclaimer_text = (
            "<b>IMPORTANT LIMITATION:</b> The AI models are highly specialized. The Brain Tumor model is ONLY trained on Brain MRIs, "
            "and the Pneumonia model is ONLY trained on Chest X-rays. Uploading incorrect scan types (e.g., a chest X-ray to the brain model) "
            "will result in forced, inaccurate predictions. <br/><br/>"
            "This report was generated by an AI system and MUST be reviewed by a qualified medical professional. The AI predictions are meant "
            "to assist healthcare providers and should not be used as the sole basis for medical diagnosis or treatment decisions (e.g., prescribing medications). "
            "Always consult with a qualified healthcare provider."
        )
        story.append(Paragraph(disclaimer_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 30))
        
        # Add Signature Section
        story.append(Spacer(1, 40))
        signature_data = [
            [Paragraph("__________________________<br/><b>Medical Professional Signature</b>", self.styles['SignatureStyle']),
             Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}", self.styles['SignatureStyle'])]
        ]
        sig_table = Table(signature_data, colWidths=[4*inch, 3*inch])
        story.append(sig_table)
        story.append(Spacer(1, 30))

        # Add footer
        footer_text = (
            "Generated by MedScan AI | Diagnostic Support Tool | "
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
            if prediction.lower() in ['glioma', 'meningioma', 'pituitary'] or 'tumor' in prediction.lower():
                return (
                    "<b>Recommended Consultations:</b> Neurologist, Neurosurgeon, or Neuro-oncologist.<br/><br/>"
                    "<b>Next Steps:</b><br/>"
                    "1. Immediate neurological evaluation.<br/>"
                    "2. Confirmatory advanced imaging (MRI with contrast, CT scan).<br/>"
                    "3. Possible referral for biopsy.<br/><br/>"
                    "<b>Common Medication (DISCLAIMER: FOR REFERENCE ONLY, DO NOT PRESCRIBE WITHOUT DOCTOR APPROVAL):</b><br/>"
                    "- Corticosteroids (e.g., Dexamethasone) to reduce brain swelling/edema.<br/>"
                    "- Anticonvulsants (e.g., Levetiracetam) if seizures are present."
                )
            else:
                return (
                    "<b>Recommended Consultations:</b> Primary Care Physician or Neurologist for ongoing symptoms.<br/><br/>"
                    "<b>Next Steps:</b><br/>"
                    "1. Routine follow-up.<br/>"
                    "2. Seek medical attention if new neurological symptoms develop (e.g., severe headaches, vision changes)."
                )
        elif scan_type.lower() == 'chest':
            if 'Pneumonia' in prediction:
                return (
                    "<b>Recommended Consultations:</b> Pulmonologist or Infectious Disease Specialist.<br/><br/>"
                    "<b>Next Steps:</b><br/>"
                    "1. Immediate respiratory assessment including SpO2 levels.<br/>"
                    "2. Sputum culture and blood tests to identify the pathogen (bacterial vs viral).<br/><br/>"
                    "<b>Common Medication (DISCLAIMER: FOR REFERENCE ONLY, DO NOT PRESCRIBE WITHOUT DOCTOR APPROVAL):</b><br/>"
                    "- Antibiotics (e.g., Amoxicillin, Azithromycin, or Levofloxacin) for bacterial pneumonia.<br/>"
                    "- Antiviral medications (e.g., Oseltamivir) if viral pneumonia is suspected.<br/>"
                    "- Antipyretics (e.g., Acetaminophen) for fever."
                )
            else:
                return (
                    "<b>Recommended Consultations:</b> Primary Care Physician.<br/><br/>"
                    "<b>Next Steps:</b><br/>"
                    "1. Routine follow-up.<br/>"
                    "2. Monitor for respiratory symptoms like persistent cough, shortness of breath, or fever."
                )
        else:
            return "Consult with a qualified healthcare provider for proper medical evaluation and treatment."
