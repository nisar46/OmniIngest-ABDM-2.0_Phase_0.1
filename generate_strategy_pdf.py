from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from datetime import datetime

class PDFGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        self.styles = getSampleStyleSheet()
        self.story = []

    def create_styles(self):
        # Custom Styles
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'), # Deep Blue
            alignment=1, # Center
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#424242'),
            alignment=1,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0d47a1'),
            spaceBefore=15,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=4 # Justify
        ))
        
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            backColor=colors.HexColor('#263238'),
            borderPadding=10,
            leading=12,
            spaceBefore=10,
            spaceAfter=10
        ))

    def build_content(self):
        self.create_styles()
        
        # --- Header ---
        self.story.append(Paragraph("BUDGET 2026 STRATEGY BRIEF", self.styles['SubTitle']))
        self.story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        self.story.append(Spacer(1, 20))
        
        self.story.append(Paragraph("AI Governance & The Future of ABDM", self.styles['MainTitle']))
        self.story.append(Paragraph("Prepared by Nisar Ahmed | Health-Tech Product Architect", self.styles['SubTitle']))
        self.story.append(Spacer(1, 20))
        
        # --- Section 1: The Insight ---
        self.story.append(Paragraph("1. The Signal: Governance is the New 'Scale'", self.styles['SectionHeader']))
        text_1 = """
        The <b>Union Budget 2026-27</b> has marked a definitive shift in India's technology roadmap. 
        The focus has moved from "Digital Public Infrastructure" to <b>"AI Public Infrastructure"</b>, 
        with specific mandates for <b>Ethical AI Frameworks</b> and rigorous <b>DPDP Compliance</b>.
        """
        self.story.append(Paragraph(text_1, self.styles['CustomBodyText']))
        self.story.append(Paragraph("<b>The market is underestimating this shift.</b> While others are building faster pipelines, the government is demanding safer ones. The next unicorn will not be the one with the most data, but the one with the most <i>compliant</i> data.", self.styles['CustomBodyText']))
        
        # --- Section 2: The Action ---
        self.story.append(Paragraph("2. Strategic Pivot: 'Compliance by Design'", self.styles['SectionHeader']))
        text_2 = """
        Waiting for frameworks to trickle down is a losing strategy. As a Product Architect, I have 
        proactively updated the <b>OmniIngest</b> architecture to align with these new 2026 mandates 
        <i>today</i>.
        """
        self.story.append(Paragraph(text_2, self.styles['CustomBodyText']))
        
        self.story.append(Paragraph("Technical Implementation (Deployed v0.2):", self.styles['CustomBodyText']))
        
        code_style = """
        <b>Feature 1: The Privacy Mask (Pseudonymization)</b><br/>
        Implements cryptographic hashing for PII (Patient Names/ABHA IDs) to allow 
        population-level analytics without violating Privacy.
        <br/><br/>
        <b>Feature 2: The Audit Ledger (Transparency)</b><br/>
        Immutable logging of every 'Purge' and 'Access' event, directly addressing the 
        Budget's call for 'Auditability in AI Systems'.
        """
        self.story.append(Paragraph(code_style, self.styles['HighlightBox']))
        
        # --- Section 3: The Vision ---
        self.story.append(Paragraph("3. The Road Ahead", self.styles['SectionHeader']))
        text_3 = """
        This is not just code; it is a <b>Governance Framework</b>. By integrating these controls 
        at the ingestion layer, we solve the 'Compliance Debt' problem before it begins. 
        I am building for an India where <b>Biopharma SHAKTI</b> and <b>ABDM</b> can rely on 
        trustworthy, privacy-preserved data layers.
        """
        self.story.append(Paragraph(text_3, self.styles['CustomBodyText']))
        self.story.append(Spacer(1, 30))
        
        # --- Footer ---
        self.story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        self.story.append(Paragraph("<i>Generated via OmniIngest AI | 2026</i>", self.styles['Normal']))

    def save(self):
        self.build_content()
        self.doc.build(self.story)
        print(f"PDF Generated: {self.filename}")

if __name__ == "__main__":
    pdf = PDFGenerator("Budget_2026_Strategy_Nisar_Ahmed.pdf")
    pdf.save()
