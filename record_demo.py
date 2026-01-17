import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        
        # Create context with video recording
        context = await browser.new_context(
            record_video_dir=".",
            record_video_size={"width": 1080, "height": 1350},
            viewport={"width": 1080, "height": 1350}
        )
        
        # Injection of "Waterabloons" (Visual Effects)
        await context.add_init_script("""
            window.addEventListener('DOMContentLoaded', () => {
                // 1. Red Halo Cursor
                const box = document.createElement('div');
                box.classList.add('mouse-helper');
                const style = document.createElement('style');
                style.innerHTML = `
                    .mouse-helper {
                        pointer-events: none;
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 20px;
                        height: 20px;
                        background: rgba(255, 0, 0, 0.4);
                        border: 1px solid red;
                        border-radius: 50%;
                        margin-left: -10px;
                        margin-top: -10px;
                        transition: background .2s, border-radius .2s, border-color .2s;
                        z-index: 999999;
                        box-shadow: 0 0 10px rgba(255,0,0,0.5);
                    }
                    .mouse-helper.button-hover {
                        background: rgba(255, 0, 0, 0.7);
                        width: 30px;
                        height: 30px;
                        margin-left: -15px;
                        margin-top: -15px;
                    }
                    .caption-box {
                        position: fixed;
                        bottom: 50px;
                        left: 50%;
                        transform: translateX(-50%);
                        background: rgba(0, 0, 0, 0.8);
                        color: white;
                        padding: 10px 20px;
                        border-radius: 30px;
                        font-family: sans-serif;
                        font-weight: bold;
                        font-size: 24px;
                        z-index: 999999;
                        display: none;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                    }
                `;
                document.head.appendChild(style);
                document.body.appendChild(box);
                
                // 2. Caption Container
                const caption = document.createElement('div');
                caption.classList.add('caption-box');
                caption.id = 'demo-caption';
                document.body.appendChild(caption);

                document.addEventListener('mousemove', event => {
                    box.style.left = event.pageX + 'px';
                    box.style.top = event.pageY + 'px';
                    
                    // Hover effect logic
                    let target = document.elementFromPoint(event.clientX, event.clientY);
                    if (target && (target.tagName === 'BUTTON' || target.closest('button'))) {
                        box.classList.add('button-hover');
                    } else {
                        box.classList.remove('button-hover');
                    }
                }, true);
            });
            
            window.showCaption = (text) => {
                const c = document.getElementById('demo-caption');
                if (c) {
                    c.innerText = text;
                    c.style.display = 'block';
                }
            };
            window.hideCaption = () => {
                const c = document.getElementById('demo-caption');
                if (c) c.style.display = 'none';
            };
        """)

        page = await context.new_page()
        
        print("Starting Recording...")
        
        # 1. Navigate to App (Assume running on localhost:8501)
        await page.goto("http://localhost:8501")
        
        # Wait for app to load completely
        await page.wait_for_selector("text=OmniIngest ABDM 2.0", timeout=10000)
        
        # Wait a brief moment for "Intro" (0:00-0:02)
        await page.wait_for_timeout(2000)
        
        # 2. FAST INGESTION (Replacing the slow manual part)
        print("Performing Fast Ingestion...")
        await page.evaluate("window.showCaption('PHASE 1: INSTANT AI INGESTION')")
        
        # Upload file instantly
        await page.locator('input[type="file"]').set_input_files('raw_data.csv')
        
        # Wait for "Smart Ingestion Discovery" or "Analytics Dashboard"
        # If the file is recognized perfectly it goes to Dashboard, but if not it asks for mapping.
        # Based on app.py, if mapping_confirmed is False, it shows Discovery.
        # Let's assume we need to click "Use Auto-Fill Fallback" for speed.
        
        # Check if we need to map - Wait up to 15s (Mandatory Step)
        await page.wait_for_selector("text=Smart Ingestion Discovery", timeout=15000)
        print("Handling Smart Ingestion UI...")
        
        # Check for Auto-Fill (Missing Fields) OR Analyze (Success)
        fallback_btn = page.locator("button:has-text('Use Auto-Fill Fallback')")
        analyze_btn = page.locator("button:has-text('Analyze with AI')")
        
        if await fallback_btn.is_visible(timeout=3000):
            await fallback_btn.scroll_into_view_if_needed()
            await fallback_btn.click()
            print("Clicked Auto-Fill button.")
        elif await analyze_btn.is_visible(timeout=3000):
                await analyze_btn.scroll_into_view_if_needed()
                await analyze_btn.click()
                print("Clicked Analyze button.")

        # Wait for processing to finish (look for "Analytics Dashboard")
        print("Waiting for Dashboard...")
        try:
            await page.wait_for_selector("text=Analytics Dashboard", timeout=30000)
            await page.evaluate("window.showCaption('ANALYZING CLINICAL PAYLOAD...')")
        except Exception as e:
            print("TIMEOUT waiting for Dashboard. Saving debug screenshot.")
            await page.screenshot(path="debug_failed.png")
            raise e
        
        await page.wait_for_timeout(1000)
        await page.evaluate("window.hideCaption()")
        
        # 3. FAST PURGE TRANSITION
        print("Triggering Kill Switch...")
        await page.evaluate("window.showCaption('PHASE 2: COMPLIANCE KILL SWITCH')")
        
        # Scroll to bottom or ensure button is visible
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Click "Purge Data"
        await page.click("text=Purge Data (DPDP Rule 8)")
        
        # Wait for Warning Banner (very short wait now)
        await page.wait_for_selector("text=DPDP Rule 8.2: Erasure Notice Sent", timeout=2000)
        await page.evaluate("window.showCaption('⚠️ DPDP Rule 8.2 NOTICE SENT')")
        await page.wait_for_timeout(500) # Quick glance
        
        # Click Confirm Override
        await page.click("text=Confirm Immediate Admin Purge")
        
        # 4. CAPTURE THE ANIMATION (The App has its own 3s delay, we catch that)
        # Wait for "System Locked" or "SESSION REVOKED"
        await page.wait_for_selector("text=SESSION REVOKED", timeout=10000)
        await page.evaluate("window.showCaption('🔒 CRYPTOGRAPHIC SHREDDING COMPLETE')")
        
        # Hold on result for 2s
        await page.wait_for_timeout(2000)
        
        print("Recording Complete.")
        
        await context.close()
        await browser.close()
        
        # Rename video
        # Find the latest .webm file
        import glob
        list_of_files = glob.glob('*.webm') 
        latest_file = max(list_of_files, key=os.path.getctime)
        if os.path.exists("OmniIngest_Fast_Demo.webm"):
            os.remove("OmniIngest_Fast_Demo.webm")
        os.rename(latest_file, "OmniIngest_Fast_Demo.webm")
        print(f"Video saved as: OmniIngest_Fast_Demo.webm")

if __name__ == "__main__":
    asyncio.run(run())
