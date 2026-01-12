from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os

# --- PATHS ---
BRAIN_DIR = r"C:\Users\nisar\.gemini\antigravity\brain\e7ede31d-7ab4-4866-ac58-968d93681823"
BANNER_BG = os.path.join(BRAIN_DIR, "linkedin_banner_clean_bg_png_1768155017141.png")
OLD_BRAIN_DIR = r"C:\Users\nisar\.gemini\antigravity\brain\5a48e18f-cd66-4818-8128-dd4b025b4ff4"
SLIDE_1_BG = os.path.join(OLD_BRAIN_DIR, "linkedin_slide_1_background_1768148702510.png")
OUTPUT_BANNER = os.path.abspath("final_linkedin_banner.png")
OUTPUT_CAROUSEL_PREFIX = os.path.abspath("carousel_slide_")

# Font settings (fallback to Arial)
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"

def create_banner():
    print("Generating Optimized Banner...")
    # LinkedIn Recommended dimensions
    BANNER_WIDTH = 1584
    BANNER_HEIGHT = 396
    
    img_orig = Image.open(BANNER_BG)
    
    # Resize and crop background to fit 1584x396
    scale = max(BANNER_WIDTH / img_orig.width, BANNER_HEIGHT / img_orig.height)
    new_size = (int(img_orig.width * scale), int(img_orig.height * scale))
    img_resized = img_orig.resize(new_size, Image.Resampling.LANCZOS)
    
    # Center crop
    left = (img_resized.width - BANNER_WIDTH) / 2
    top = (img_resized.height - BANNER_HEIGHT) / 2
    right = (img_resized.width + BANNER_WIDTH) / 2
    bottom = (img_resized.height + BANNER_HEIGHT) / 2
    img = img_resized.crop((left, top, right, bottom))
    
    # --- REDUCE BRIGHTNESS FOR READABILITY ---
    enhancer = ImageEnhance.Brightness(img)
    # 0.7 makes it 30% darker
    img = enhancer.enhance(0.7)
    
    draw = ImageDraw.Draw(img)
    
    # Text content
    title_line1 = "Building 'Privacy-By-Design'"
    title_line2 = "for India's Health Revolution"
    subtitle = "Health Ops Veteran | Regulatory Engineering | Gen AI Architect"
    
    # Fonts - Bold titles, Regular subtitle
    title_font = ImageFont.truetype(FONT_BOLD, 44)
    # Reduced size to 24 to fit at the further right position (x=780)
    sub_font = ImageFont.truetype(FONT_REGULAR, 24)
    
    # Position (Right-aligned Safe Zone)
    # x=780 is further right as requested, font reduced to ensure no cutoff
    x_pos = 780
    
    # Draw Titles
    draw.text((x_pos, 100), title_line1, font=title_font, fill="white")
    draw.text((x_pos, 160), title_line2, font=title_font, fill="white")
    
    # Draw Subtitle with a subtle shadow for better readability
    shadow_offset = 1
    draw.text((x_pos + shadow_offset, 240 + shadow_offset), subtitle, font=sub_font, fill="black")
    draw.text((x_pos, 240), subtitle, font=sub_font, fill="white")
    
    img.save(OUTPUT_BANNER)
    print(f"SUCCESS: Optimized Banner saved to {OUTPUT_BANNER}")

def create_carousel():
    print("Generating Carousel Slides...")
    slides_text = [
        {
            "headline": "India is moving to ABDM 2.0. \nIs your data ready for the DPDP Act?",
            "body": "India’s healthcare is going digital, but most hospitals are \nsitting on 'Compliance Time-Bombs.'",
            "is_hook": True
        },
        {
            "headline": "The 'Messy Middle' of Healthcare Data",
            "body": "❌ Inconsistent headers (Name vs pt_name)\n❌ PII leaks (Exposing patient IDs in dashboards)\n❌ Deletion compliance (DPDP Rule 8.3 risks)",
            "footer": "These aren't just IT issues; they are legal risks."
        },
        {
            "headline": "Solving the 'Techno-Legal' Puzzle",
            "body": "To solve this, you need a different perspective:\n- 10 Years of Health Ops: Hospital experience.\n- IIT Medical Law: Regulatory understanding.\n- GenAI & Python: High-speed development."
        },
        {
            "headline": "Privacy-By-Design: Zero PII Exposure",
            "body": "Most dashboards leak patient data by default.\nMy Solution: Universal UI masking. Data is private until \nit is legally necessary to see it."
        },
        {
            "headline": "Compliance with DPDP Rule 8.3",
            "body": "How do you delete data but keep audit logs?\nOmniIngest implements automated Rule 8.3 'Hard-Purge' \nlogic to ensure your system stays legal."
        },
        {
            "headline": "Smart Ingress (Polars Powered)",
            "body": "No More Typos. No More Failed Uploads.\nUsing Polars (High-Speed Data Engine), OmniIngest \nautomatically maps messy headers (e.g., pt_name -> PatientName)."
        },
        {
            "headline": "Built with 'Vibe-Coding'",
            "body": "Leveraging Agentic AI (GenAI), I built this healthcare-grade \nsolution in record time, focusing on medical-legal compliance."
        },
        {
            "headline": "Let's Secure India's Digital Health Stack.",
            "body": "I am building the tools for the next era of Bharat's HealthTech.\n\nCheck the GitHub Repo or Connect today!\ngithub.com/nisar46/OmniIngest-ABDM-2.0_Phase_0.1"
        }
    ]

    images = []
    for i, slide in enumerate(slides_text):
        if slide.get("is_hook"):
            img = Image.open(SLIDE_1_BG)
        else:
            # Generic medical dark blue background
            img = Image.new('RGB', (1080, 1350), color='#1A365D')
        
        draw = ImageDraw.Draw(img)
        h_font = ImageFont.truetype(FONT_BOLD, 60)
        b_font = ImageFont.truetype(FONT_REGULAR, 40)
        
        # Draw Headline
        draw.text((100, 300), slide["headline"], font=h_font, fill="white")
        
        # Draw Body
        draw.text((100, 600), slide["body"], font=b_font, fill="#cbd5e0")
        
        if "footer" in slide:
            f_font = ImageFont.truetype(FONT_BOLD, 30)
            draw.text((100, 1100), slide["footer"], font=f_font, fill="#63b3ed")
            
        temp_path = f"{OUTPUT_CAROUSEL_PREFIX}{i}.png"
        img.save(temp_path)
        images.append(img.convert('RGB'))
        print(f"Slide {i+1} generated.")

    # Save as PDF
    pdf_path = os.path.abspath("final_carousel_slides.pdf")
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    print(f"SUCCESS: Carousel PDF saved to {pdf_path}")

if __name__ == "__main__":
    create_banner()
    create_carousel()
