from reportlab.lib import pagesizes, colors
from reportlab.lib.pagesizes import landscape, LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class SlideDeckGenerator:
    def __init__(self, filename):
        self.filename = filename
        # Use Landscape letter for a "Slide" feel
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=landscape(LETTER),
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        self.styles = getSampleStyleSheet()
        self.story = []

    def create_styles(self):
        # --- Slide Title (Big, Bold) ---
        self.styles.add(ParagraphStyle(
            name='SlideTitle',
            parent=self.styles['Heading1'],
            fontSize=32,
            leading=38,
            textColor=colors.HexColor('#002147'), # Oxford Blue
            fontName='Helvetica-Bold',
            spaceAfter=30
        ))
        
        # --- Slide Subtitle / Accent ---
        self.styles.add(ParagraphStyle(
            name='SlideSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#E03C31'), # Urgent Red
            fontName='Helvetica',
            spaceAfter=20
        ))

        # --- Body Text (Large for slides) ---
        self.styles.add(ParagraphStyle(
            name='SlideBody',
            parent=self.styles['Normal'],
            fontSize=16,
            leading=24,
            textColor=colors.HexColor('#333333'),
            spaceAfter=15
        ))
        
        # --- Code/Tech Highlight ---
        self.styles.add(ParagraphStyle(
            name='TechBlock',
            parent=self.styles['Normal'],
            fontSize=14,
            leading=18,
            textColor=colors.white,
            backColor=colors.HexColor('#263238'),
            borderPadding=15,
            spaceBefore=20,
            fontName='Courier'
        ))

    def draw_background(self, canvas, doc):
        """Draws a professional footer/header on every slide"""
        canvas.saveState()
        # Footer Bar
        canvas.setFillColor(colors.HexColor('#f5f5f5'))
        canvas.rect(0, 0, landscape(LETTER)[0], 40, fill=1, stroke=0)
        
        # Footer Text
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.grey)
        canvas.drawString(50, 15, "Nisar Ahmed | Health-Tech Product Architect | Budget 2026 Analysis")
        canvas.drawRightString(landscape(LETTER)[0]-50, 15, "OmniIngest v0.2")
        canvas.restoreState()

    def build_content(self):
        self.create_styles()
        
        # --- Slide 1: Title Card ---
        self.story.append(Spacer(1, 60))
        self.story.append(Paragraph("BUDGET 2026 DECODED", self.styles['SlideSubtitle']))
        self.story.append(Paragraph("From 'Digital Infra' to<br/>'AI Governance'", self.styles['SlideTitle']))
        self.story.append(Spacer(1, 20))
        self.story.append(Paragraph("Why the next Health-Tech unicorn will be built on <b>Compliance</b>, not just Code.", self.styles['SlideBody']))
        self.story.append(Paragraph("<b>A Strategy Brief by Nisar Ahmed</b>", self.styles['SlideBody']))
        self.story.append(PageBreak())

        # --- Slide 2: The Signal ---
        self.story.append(Paragraph("THE SIGNAL", self.styles['SlideSubtitle']))
        self.story.append(Paragraph("The Rules Have Changed.", self.styles['SlideTitle']))
        text_2 = """
        The Union Budget 2026 moved the goalposts.
        <br/><br/>
        1. <b>AI Public Infrastructure:</b> It's no longer just about storing data; it's about <i>governing</i> intelligence.
        <br/>
        2. <b>BioPharma SHAKTI:</b> New funds for clinical innovation come with strict data audit requirements.
        <br/>
        3. <b>DPDP Mandate:</b> Compliance is now a <i>funding eligibility</i> criteria.
        """
        self.story.append(Paragraph(text_2, self.styles['SlideBody']))
        self.story.append(PageBreak())

        # --- Slide 3: The Problem ---
        self.story.append(Paragraph("THE PROBLEM", self.styles['SlideSubtitle']))
        self.story.append(Paragraph("Speed vs. Safety", self.styles['SlideTitle']))
        text_3 = """
        Most Health-Tech pipelines are built for speed. They ingest data fast.
        <br/><br/>
        But under the new 2026 rules, <b>fast is dangerous.</b>
        <br/>
        If you cannot trace <i>who</i> touched the data and <i>why</i>, you aren't an asset. You are a liability.
        """
        self.story.append(Paragraph(text_3, self.styles['SlideBody']))
        self.story.append(PageBreak())

        # --- Slide 4: The Solution (Tech) ---
        self.story.append(Paragraph("THE PIVOT", self.styles['SlideSubtitle']))
        self.story.append(Paragraph("OmniIngest v0.2: Governance First", self.styles['SlideTitle']))
        self.story.append(Paragraph("I didn't wait for the whitepaper. I updated the architecture.", self.styles['SlideBody']))
        
        tech_text = """
        [NEW MODULE] Compliance_Engine.py
        ---------------------------------
        + def pseudonymize_pii(data):
            # The Mask: Cryptographic Hashing for Identity
            
        + def audit_transaction(user, action):
            # The Ledger: Immutable logs for Govt Audits
        """
        self.story.append(Paragraph(tech_text, self.styles['TechBlock']))
        self.story.append(PageBreak())

        # --- Slide 5: The Vision ---
        self.story.append(Paragraph("THE VISION", self.styles['SlideSubtitle']))
        self.story.append(Paragraph("Ready for What's Next", self.styles['SlideTitle']))
        text_5 = """
        We don't need more "App Developers". We need <b>System Architects</b>.
        <br/><br/>
        I am building OmniIngest to be the backbone of the <b>ABDM 2.0</b> ecosystem—where data is fluid, but privacy is absolute.
        <br/><br/>
        <b>Let's build the future, responsibly.</b>
        """
        self.story.append(Paragraph(text_5, self.styles['SlideBody']))
        self.story.append(Spacer(1, 20))
        self.story.append(Paragraph("<i>- Nisar Ahmed</i>", self.styles['SlideBody']))

    def save(self):
        self.build_content()
        # Add the 'onPage' callback to draw the background
        self.doc.build(self.story, onFirstPage=self.draw_background, onLaterPages=self.draw_background)
        print(f"Slide Deck Generated: {self.filename}")

if __name__ == "__main__":
    generator = SlideDeckGenerator("Budget_2026_Analysis_Slides.pdf")
    generator.save()
