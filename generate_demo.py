import subprocess
import time
import os
import sys
from playwright.sync_api import sync_playwright
try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
except ImportError:
    from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import shutil

# Configuration
APP_URL = "http://localhost:8501"
OUTPUT_VIDEO = "OmniIngest_Professional_2026.mp4"
TEMP_VIDEO_DIR = "videos"

def record_demo():
    print("Launching Streamlit App...")
    # Start Streamlit in the background
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true"]
    process = subprocess.Popen(cmd, shell=True)
    time.sleep(5)  # Wait for boot

    try:
        with sync_playwright() as p:
            print("Starting Browser & Recording...")
            # Use light mode context but force 4:5 Mobile Ratio
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                record_video_dir=TEMP_VIDEO_DIR,
                record_video_size={"width": 1080, "height": 1350}, # 4:5 Aspect Ratio
                viewport={"width": 1080, "height": 1350},
                device_scale_factor=2,
                color_scheme='light' # User requested "Medical Light Mode theme" in high contrast
            )
            page = context.new_page()

            # Inject Mouse Trail (Red Dot + Halo)
            page.add_init_script("""
                document.addEventListener('DOMContentLoaded', () => {
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
                            background: rgba(255, 0, 0, 0.8);
                            border: 2px solid white;
                            border-radius: 50%;
                            transform: translate(-50%, -50%);
                            transition: all 0.08s linear;
                            z-index: 10000;
                            box-shadow: 0 0 15px 5px rgba(255, 0, 0, 0.5); /* Halo Effect */
                        }
                    `;
                    document.head.appendChild(style);
                    document.body.appendChild(box);
                    document.addEventListener('mousemove', event => {
                        box.style.left = event.pageX + 'px';
                        box.style.top = event.pageY + 'px';
                        box.style.display = 'block';
                    });
                    document.addEventListener('mouseout', event => {
                        box.style.display = 'none';
                    });
                });
            """)

            # --- STORYBOARD (60s) ---
            print("Action: Ingress Capture (0-15s)")
            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")
            
            # Initial Mouse Movement
            page.mouse.move(540, 675)
            time.sleep(1)
            
            # Manual Entry Tab
            page.get_by_text("Manual Entry").click()
            time.sleep(1)
            
            # Name
            page.get_by_placeholder("e.g. Rahul Verma").click()
            page.keyboard.type("Vikram Malhotra", delay=80) 
            time.sleep(0.5)
            
            # ABHA @sbx
            page.get_by_placeholder("e.g. 91-2345-6789").click()
            page.keyboard.type("vikram.m@sbx", delay=80) # Proving Sandbox Regex
            time.sleep(1)
            
            # Ingest
            page.get_by_role("button", name="Ingest Data").click()
            time.sleep(4) 

            print("Action: Rule 8.2 Demo (15-45s)")
            # Verify processed
            page.mouse.move(200, 300) # Move mouse away
            time.sleep(1)
            
            # Open Compliance Sidebar
            if not page.get_by_text("Field Mapping").is_visible():
                page.get_by_text("Compliance Verification").click()
                time.sleep(1)

            # Purge Flow
            purge_btn = page.get_by_role("button", name="Purge Data (DPDP Rule 8)")
            purge_btn.scroll_into_view_if_needed()
            purge_btn.hover()
            time.sleep(1)
            purge_btn.click()
            
            # Wait for Yellow Warning (Rule 8.2 Notice)
            print("  > Waiting for 48h Notice...")
            page.wait_for_selector("text=DPDP Rule 8.2: Erasure Notice Sent", timeout=5000)
            time.sleep(3) # Ensure visible for 3s
            
            # Override
            override_btn = page.get_by_text("Confirm Immediate Admin Purge")
            override_btn.hover()
            time.sleep(1)
            override_btn.click()
            
            # Wait for Red Banner
            page.wait_for_selector("text=SESSION REVOKED", timeout=5000)
            time.sleep(3)

            print("Action: Compliance Proof (45-60s)")
            # 1. Sidebar X-CM-ID
            # Scroll sidebar if needed
            sb_status = page.get_by_text("X-CM-ID: sbx")
            if sb_status.is_visible():
                sb_status.hover()
                page.mouse.move(sb_status.bounding_box()['x'] + 50, sb_status.bounding_box()['y'] + 10)
                time.sleep(3)
            
            # 2. Hover [DATA PURGED]
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            
            # Look for the red bold text
            purged_cell = page.locator("td").filter(has_text="[DATA PURGED]").first
            if purged_cell.count() > 0:
                purged_cell.scroll_into_view_if_needed()
                purged_cell.hover()
                time.sleep(3)
            
            # Analysis Button Disabled check (Optional visual cue)
            analyze_btn = page.get_by_text("Analyze with AI")
            if analyze_btn.is_visible():
                analyze_btn.scroll_into_view_if_needed()
                analyze_btn.hover(force=True)
            
            print("Action: Holding final state (60s+)")
            time.sleep(5) 

            context.close()
            browser.close()
            
    finally:
        print("Terminating App...")
        process.terminate()
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])

    videos = [f for f in os.listdir(TEMP_VIDEO_DIR) if f.endswith(".webm")]
    if not videos:
        raise Exception("No video recorded!")
    return os.path.join(TEMP_VIDEO_DIR, videos[0])

def add_captions(video_path):
    print("Adding Captions...")
    try:
        clip = VideoFileClip(video_path)
    except Exception as e:
        print(f"Error loading video clip: {e}")
        return

    # Captions Configuration (Bottom Center, White)
    captions = [
        ("Smart Ingress: Verifying @sbx Regex", 0, 15),
        ("DPDP Rule 8.2: 48-Hour Notice Sent", 15, 30),
        ("Override: Hard-Purge Executed", 30, 45),
        ("Compliance Proof: X-CM-ID & Redaction", 45, 60)
    ]
    
    final_clips = [clip]
    
    for text, start, end in captions:
        try:
            # Create text clip
            txt = (TextClip(text, fontsize=50, color='white', font='Arial-Bold', 
                            stroke_color='black', stroke_width=2)
                   .set_position(('center', 'bottom'))
                   .set_start(start)
                   .set_duration(end - start)
                   .margin(bottom=50, opacity=0))
            final_clips.append(txt)
        except Exception as e:
            print(f"Warning: Could not create caption '{text}'. Error: {e}")

    try:
        final = CompositeVideoClip(final_clips)
        final = final.subclip(0, 60)
        final.write_videofile(OUTPUT_VIDEO, codec='libx264', audio_codec='aac', fps=30)
        print(f"Created {OUTPUT_VIDEO}")
    except Exception as e:
        print(f"Error writing final video: {e}")

if __name__ == "__main__":
    if os.path.exists(TEMP_VIDEO_DIR):
        try:
            shutil.rmtree(TEMP_VIDEO_DIR)
        except:
            pass
    
    try:
        raw_video = record_demo()
        add_captions(raw_video)
    except Exception as e:
        print(f"Script failed: {e}")
