"""
PDF Report Generation Service
Creates professional PDF reports using ReportLab
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from typing import Dict
import os


class PDFService:
    """
    Generates professional PDF reports for asset analysis
    Uses ReportLab Platypus for layout
    """
    
    def __init__(self):
        self.output_dir = "/tmp/stratify_reports"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_report(
        self,
        asset_name: str,
        probabilities: Dict[str, float],
        narratives: Dict[str, str],
        most_likely_scenario: str,
        confidence_level: str,
        macro_summary: str,
        user_email: str
    ) -> str:
        """
        Generate complete PDF report
        
        Args:
            asset_name: Name of analyzed asset
            probabilities: Short, medium, long-term probabilities
            narratives: Explanatory narratives for each horizon
            most_likely_scenario: Overall scenario description
            confidence_level: "High", "Medium", or "Low"
            macro_summary: Summary of current macro conditions
            user_email: User who requested the report
            
        Returns:
            Path to generated PDF file
        """
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stratify_report_{asset_name.replace(' ', '_')}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        # Header
        story.append(Paragraph("STRATIFY AI", title_style))
        story.append(Paragraph("Global Multi-Factor Influence Intelligence", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        metadata = [
            ["Asset Analyzed:", asset_name],
            ["Report Date:", datetime.now().strftime("%B %d, %Y")],
            ["Confidence Level:", confidence_level],
            ["Generated For:", user_email]
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Section 1: Asset Overview
        story.append(Paragraph("1. Asset Overview", heading_style))
        story.append(Paragraph(
            f"This report analyzes <b>{asset_name}</b> using Stratify AI's multi-factor "
            "influence engine. The analysis considers macroeconomic conditions, regulatory "
            "developments, and market dynamics to generate probability-based outlooks across "
            "multiple time horizons.",
            body_style
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Section 2: Current Global Conditions
        story.append(Paragraph("2. Current Global Macro Conditions", heading_style))
        story.append(Paragraph(macro_summary, body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Section 3: Probability Summary
        story.append(Paragraph("3. Probability Summary", heading_style))
        
        prob_data = [
            ["Time Horizon", "Probability Score", "Interpretation"],
            [
                "Short-term (0-4 weeks)",
                f"{probabilities['short_term']:.2f}",
                self._interpret_score(probabilities['short_term'])
            ],
            [
                "Medium-term (1-6 months)",
                f"{probabilities['medium_term']:.2f}",
                self._interpret_score(probabilities['medium_term'])
            ],
            [
                "Long-term (6-24 months)",
                f"{probabilities['long_term']:.2f}",
                self._interpret_score(probabilities['long_term'])
            ]
        ]
        
        prob_table = Table(prob_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        prob_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(prob_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Section 4: Short-term Outlook
        story.append(Paragraph("4. Short-Term Outlook (0-4 weeks)", heading_style))
        story.append(Paragraph(narratives.get('short_term', 'Analysis unavailable'), body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Section 5: Medium-term Outlook
        story.append(Paragraph("5. Medium-Term Outlook (1-6 months)", heading_style))
        story.append(Paragraph(narratives.get('medium_term', 'Analysis unavailable'), body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Section 6: Long-term Outlook
        story.append(Paragraph("6. Long-Term Outlook (6-24 months)", heading_style))
        story.append(Paragraph(narratives.get('long_term', 'Analysis unavailable'), body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Section 7: Most Likely Scenario
        story.append(Paragraph("7. Most Likely Scenario", heading_style))
        story.append(Paragraph(most_likely_scenario, body_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Section 8: Confidence & Limitations
        story.append(Paragraph("8. Confidence Level & Limitations", heading_style))
        
        confidence_text = f"""
        <b>Confidence Level: {confidence_level}</b><br/><br/>
        This analysis is based on publicly available macro data and structured scoring models. 
        Actual market outcomes may differ significantly due to unforeseen events, market sentiment shifts, 
        or factors not captured in the model. This report is for informational purposes only and does not 
        constitute financial advice. Users should conduct their own research and consult financial advisors 
        before making investment decisions.
        """
        
        story.append(Paragraph(confidence_text, body_style))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            f"<i>Report generated by Stratify AI on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _interpret_score(self, score: float) -> str:
        """Convert numerical score to text interpretation"""
        if score > 0.7:
            return "Strongly Positive"
        elif score > 0.6:
            return "Moderately Positive"
        elif score > 0.4:
            return "Neutral"
        elif score > 0.3:
            return "Moderately Negative"
        else:
            return "Strongly Negative"


# Create singleton instance
pdf_service = PDFService()
