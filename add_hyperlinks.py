
import PyPDF2

def add_link():
    input_pdf = "OmniIngest_Launch_2026.pdf"
    output_pdf = "OmniIngest_Launch_2026_Interactive.pdf"
    
    reader = PyPDF2.PdfReader(input_pdf)
    writer = PyPDF2.PdfWriter()
    
    # Copy all pages
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        writer.add_page(page)
        
    print(f"Loaded {len(reader.pages)} pages.")
    
    # Page 10 (Index 9) - Add Link
    # Coordinates calculation:
    # Image Size: 1080 x 1350
    # PDF UserUnits might map 1:1 if PIL saved default dpi (72).
    # PIL defaults: 72 DPI. 1080px = 15 inches? 
    # Wait, PDF coordinates depend on MediaBox.
    
    page = writer.pages[9]
    mediabox = page.mediabox
    width = float(mediabox.width)
    height = float(mediabox.height)
    print(f"Page Dimensions: {width} x {height}")
    
    # Target visual coordinates from generate_carousel.py:
    # Width: 1080 px -> Mapped to PDF width
    # URL Y pos: ~960px from top
    # URL X pos: Centered at 540px
    
    # Coordinate Transform
    # pdf_y = height - (pixel_y / pixel_height * height)
    # But if PIL saved 1:1, width=1080. Let's assume proportional.
    
    scale_y = height / 1350.0
    scale_x = width / 1080.0
    
    # URL Area
    # Y=960 (top of text) to Y=1000 (bottom of text) approximately
    # X=200 to X=880 (wide enough to cover URL)
    
    # Expanded Clickable Area for maximum usability
    # Covering the Button, QR Code, and URL text
    # PDF Coordinates (Bottom-Left Origin)
    # y_ll = 100 points (near bottom)
    # y_ur = 450 points (middle of page) -> Top of link area
    # x_ll = 50 points
    # x_ur = width - 50 points
    
    rect = [
        50, 
        100, 
        width - 50, 
        450
    ]
    
    # Manual Annotation Injection with Visible Border for Debugging
    # Link: https://www.linkedin.com/in/nisar-ahmed-8440763a3
    
    from PyPDF2.generic import DictionaryObject, NumberObject, FloatObject, NameObject, TextStringObject, ArrayObject

    link_url = "https://www.linkedin.com/in/nisar-ahmed-8440763a3"

    # Create the annotation object
    link_annotation = DictionaryObject()
    link_annotation.update({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Link"),
        NameObject("/Rect"): ArrayObject([
            FloatObject(rect[0]), FloatObject(rect[1]), FloatObject(rect[2]), FloatObject(rect[3])
        ]),
        NameObject("/Border"): ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0)]), # Invisible Border
        # NameObject("/C"): ArrayObject([FloatObject(1), FloatObject(0), FloatObject(0)]), # Color removed
        NameObject("/A"): DictionaryObject({
            NameObject("/S"): NameObject("/URI"),
            NameObject("/URI"): TextStringObject(link_url)
        })
    })

    # Add to page
    if "/Annots" not in page:
        page[NameObject("/Annots")] = ArrayObject()
        
    page["/Annots"].append(link_annotation)
    
    # writer.add_uri is skipped in favor of this manual injection
    
    with open(output_pdf, "wb") as f:
        writer.write(f)
        
    print(f"Created {output_pdf} with clickable link on Slide 10.")

if __name__ == "__main__":
    add_link()
