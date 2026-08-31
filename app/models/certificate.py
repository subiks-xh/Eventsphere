"""
EventSphere - Certificate Model
"""

from datetime import datetime
import uuid
import os
from app import db


class Certificate(db.Model):
    """Certificate model representing participation certificates."""
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), unique=True, nullable=False)
    certificate_id = db.Column(db.String(50), unique=True, nullable=False)
    participant_name = db.Column(db.String(200), nullable=False)
    event_name = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    organizer_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(256))
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, registration, **kwargs):
        """
        Initialize a new certificate for a registration.
        
        Args:
            registration: Registration object
            **kwargs: Additional certificate attributes
        """
        super().__init__(**kwargs)
        self.registration_id = registration.id
        self.certificate_id = f"CERT-{str(uuid.uuid4())[:8].upper()}"
        self.participant_name = registration.user.full_name
        self.event_name = registration.event.name
        self.event_date = registration.event.date
        self.organizer_name = registration.event.organizer.full_name

    def generate_pdf(self, save_path=None):
        """
        Generate PDF certificate.
        
        Args:
            save_path: Optional path to save the PDF
        
        Returns:
            bytes: PDF data
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import io

        # Create PDF buffer
        buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=15,
            textColor=colors.darkblue
        )
        center_style = ParagraphStyle(
            'CustomCenter',
            parent=styles['Normal'],
            fontSize=14,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            leading=16,
            spaceAfter=8
        )
        footer_style = ParagraphStyle(
            'CustomFooter',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            spaceAfter=5,
            textColor=colors.grey
        )

        # Story (content)
        story = []

        # Title
        story.append(Paragraph("CERTIFICATE OF PARTICIPATION", title_style))

        # Subtitle
        story.append(Paragraph("This certifies that", center_style))

        # Participant name
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(self.participant_name.upper(), ParagraphStyle(
            'NameStyle',
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )))

        # Event details
        story.append(Paragraph("has successfully participated in", center_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(self.event_name, ParagraphStyle(
            'EventStyle',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=15,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )))

        # Date
        story.append(Paragraph(f"held on {self.event_date.strftime('%B %d, %Y')}", center_style))

        # Organizer
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(f"Organized by: {self.organizer_name}", normal_style))

        # Certificate ID
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(f"Certificate ID: {self.certificate_id}", ParagraphStyle(
            'IDStyle',
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.grey
        )))

        # Signature area
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("_________________________", ParagraphStyle(
            'SignatureStyle',
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=5
        )))
        story.append(Paragraph("Organizer's Signature", ParagraphStyle(
            'SignatureLabel',
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        )))

        # Footer
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("EventSphere - Event Management System", footer_style))
        story.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%B %d, %Y')}", footer_style))

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        # Save to file if path provided
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(buffer.getvalue())
            self.file_path = os.path.relpath(save_path, 'app/static')
            db.session.commit()

        return buffer.getvalue()

    def get_file_url(self):
        """Get URL for certificate file."""
        if self.file_path:
            return f"/static/{self.file_path}"
        return None

    def __repr__(self):
        return f"<Certificate {self.certificate_id} for {self.participant_name}>"
