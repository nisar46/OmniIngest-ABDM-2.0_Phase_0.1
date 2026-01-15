import asyncio
from playwright.async_api import async_playwright
import os

async def show_overlay(page, text, duration=3, element=None):
    # Sanitize for Windows Console
    safe_console_text = text.encode('ascii', 'ignore').decode('ascii')
    print(f"Overlay: {safe_console_text}")

    # CSS for Arrows and Big Captions
    await page.add_style_tag(content="""
        @keyframes popIn {
            0% { opacity: 0; transform: scale(0.8); }
            100% { opacity: 1; transform: scale(1); }
        }
        .caption-base {
            font-family: 'Segoe UI', sans-serif;
            font-weight: 800; /* Extra Bold */
            color: white;
            background: #0d1117; /* GitHub Dark */
            border: 3px solid #10a37f; /* Streamlit Green */
            box-shadow: 0 8px 24px rgba(0,0,0,0.6);
            border-radius: 12px;
            padding: 20px 30px;
            font-size: 36px; /* BIGGER FONT */
            z-index: 10000;
            animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            max-width: 800px;
            text-align: center;
        }
        /* Fixed Bottom Caption */
        .caption-fixed {
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            border-bottom: 6px solid #10a37f;
        }
        /* Floating Pointer Caption (Above) */
        .caption-float-above {
            position: absolute;
            transform: translate(-50%, -100%); /* Center above element */
        }
        .caption-float-above::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -15px;
            border-width: 15px;
            border-style: solid;
            border-color: #10a37f transparent transparent transparent;
        }

        /* Floating Pointer Caption (Below) */
        .caption-float-below {
            position: absolute;
            transform: translate(-50%, 0); /* Center below element */
        }
        .caption-float-below::after {
            content: '';
            position: absolute;
            bottom: 100%;
            left: 50%;
            margin-left: -15px;
            border-width: 15px;
            border-style: solid;
            border-color: transparent transparent #10a37f transparent;
        }
    """)

    safe_text = text.replace("'", "\\'")
    
    # Logic to position the tooltip
    positioned = False
    if element:
        try:
            # We already have the element locator, just get the box
            box = await element.bounding_box(timeout=2000)
            if box:
                # Calculate position: Center 
                target_x = box["x"] + (box["width"] / 2)
                
                # Check distance from top
                # Assume caption height is max 150px
                if box["y"] < 180:
                    # Too close to top! Put it BELOW.
                    target_y = box["y"] + box["height"] + 20
                    css_classes = 'caption-base caption-float-below'
                else:
                    # Standard ABOVE
                    target_y = box["y"] - 20 
                    css_classes = 'caption-base caption-float-above'

                # Inject Floating Caption with Arrow
                script = f"""
                    const div = document.createElement('div');
                    div.className = '{css_classes}';
                    div.innerHTML = '{safe_text}';
                    div.style.left = '{target_x}px';
                    div.style.top = '{target_y}px';
                    document.body.appendChild(div);
                    setTimeout(() => div.remove(), {duration * 1000});
                """
                await page.evaluate(script)
                positioned = True
            else:
                 print(f"Element found but has no bounding box (hidden?). Falling back.")
        except Exception as e:
             print(f"Error positioning overlay: {e}")

    if not positioned:
        # Standard Bottom Overlay
        script = f"""
            const div = document.createElement('div');
            div.className = 'caption-base caption-fixed';
            div.innerHTML = '{safe_text}';
            document.body.appendChild(div);
            setTimeout(() => div.remove(), {duration * 1000});
        """
        await page.evaluate(script)
    
    await asyncio.sleep(duration)


async def record_demo():
    async with async_playwright() as p:
        # Launching with a specific window size that accommodates 1080p
        browser = await p.chromium.launch(headless=False, args=["--window-size=1920,1080"])
        
        # 1920x1080 resolution
        context = await browser.new_context(
            record_video_dir=".",
            record_video_size={"width": 1920, "height": 1080},
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            color_scheme='dark'
        )
        page = await context.new_page()
        
        # Force Dark Background via CSS globally
        await page.add_style_tag(content="""
            html, body, [data-testid="stAppViewContainer"] {
                background-color: #0d1117 !important;
            }
        """)

        print("Action! 90-Second Demo Started...")

        # --- 0s-15s: PREP & WATERMARK HOVER ---
        print("Segment 1: Prep (0-15s)")
        await page.goto("http://localhost:8501")
        # Enhance visual vibe
        await show_overlay(page, "<b>OmniIngest ABDM 2.0</b><br>Enterprise-Grade Compliance Engine.", duration=2)
        
        # Hover over Safety Rails/Watermark (Sidebar)
        try:
            watermark = page.locator("div").filter(has_text="System Status: DPDP Rule 8.3 Active").first
            await watermark.wait_for()
            await watermark.hover()
            await show_overlay(page, "<b>Safety Rails Active</b><br>Retention Protocol enforce by default.", duration=2, element=watermark)
        except:
            print("Watermark not found, skipping hover.")
        
        await asyncio.sleep(3) # Fill time to 15s

        # --- 15s-35s: SMART INGRESS ---
        print("Segment 2: Ingress (15-35s)")
        file_path = os.path.abspath("demo_sample.csv")
        async with page.expect_file_chooser() as fc_info:
            await page.get_by_text("Browse files").click()
        file_chooser = await fc_info.value
        await file_chooser.set_files(file_path)
        
        # Wait for "Analyzed" or file name
        await page.wait_for_selector("text=demo_sample.csv")
        
        # Wait for "Analyze with AI" or generic success
        try:
            analyze_btn = page.get_by_text("Analyze with AI").first
            await analyze_btn.wait_for(state="visible", timeout=5000)
            await analyze_btn.click()
            await show_overlay(page, "<b>[SUCCESS]</b><br>Smart Ingress Auto-Mapped Patient Data.", duration=2)
        except:
             # Logic if mapping needed
             try:
                 apply = page.get_by_text("Apply Mapping")
                 await apply.click()
             except:
                 pass
        
        await asyncio.sleep(2)

        # --- 35s-70s: KILL SWITCH & ZOOM ---
        print("Segment 3: Kill Switch (35-70s)")
        # Make sure logs are visible
        # Check detected format just to be sure we are in dashboard
        await page.wait_for_selector("text=Analytics Dashboard", timeout=15000)

        kill_switch = page.get_by_text("Purge Data (DPDP Rule 8)")
        await kill_switch.scroll_into_view_if_needed()
        await kill_switch.click()
        await asyncio.sleep(1)
        
        confirm_btn = page.get_by_text("Confirm Immediate Admin Purge (Override)")
        await confirm_btn.wait_for()
        
        # Trigger automation
        await confirm_btn.click()
        
        # Watch the logs (Log is in sidebar, make sure it's visible)
        # We need to ensure we are looking at the sidebar
        # Or wait for the 3-step animation (approx 3 * 0.9s + overhead = ~4s)
        await asyncio.sleep(2) 
        
        # Now ZOOM on [DATA PURGED]
        try:
            # Wait for reload
            await page.wait_for_selector("td:has-text('[DATA PURGED]')", timeout=10000)
            purged_el = page.locator("td").filter(has_text="[DATA PURGED]").first
            await purged_el.scroll_into_view_if_needed()
            
            # CSS Zoom Effect
            await page.evaluate("document.body.style.transition = 'zoom 2s'; document.body.style.zoom = '1.25';")
            await show_overlay(page, "<b>CRYPTOGRAPHIC SHRED COMPLETE</b><br>Data is irretrievable.", duration=2, element=purged_el)
            await asyncio.sleep(1)
            # Zoom back
            await page.evaluate("document.body.style.zoom = '1.0';")
        except Exception as e:
            print(f"Zoom failed: {e}")

        await asyncio.sleep(4) # Fill time

        # --- 70s-90s: EXPORT FHIR ---
        print("Segment 4: Export (70-90s)")
        fhir_btn = page.get_by_text("FHIR Bundle")
        await fhir_btn.scroll_into_view_if_needed()
        await fhir_btn.click() # Downloads file usually
        
        # Show structure overlay instead of opening file (hard in generic browser recording)
        await show_overlay(page, "<b>INTEROPERABILITY READY</b><br>FHIR R5 Compliant JSON Generated.", duration=2)
        
        await asyncio.sleep(2)
        
        # Outro
        await show_overlay(page, "<b>OmniIngest Phase 0.1</b><br>Building a Safer Digital Health Future.", duration=2)

        print("Cut!")
        await context.close()
        await browser.close()
        
        # Cleanup and rename
        files = [f for f in os.listdir(".") if f.endswith(".webm")]
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        if files:
            latest_video = files[0]
            target_name = "OmniIngest_Demo_2026.webm" 
            if os.path.exists(target_name):
                os.remove(target_name)
            os.rename(latest_video, target_name)
            print(f"Saved: {os.path.abspath(target_name)}")

if __name__ == "__main__":
    asyncio.run(record_demo())
