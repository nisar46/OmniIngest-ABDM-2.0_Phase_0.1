@echo off
echo [OmniIngest] ARCHITECT FINAL SYNC: Fixing the Root README...
cd /d "D:\Omnigest_ABDM_2.0"

:: 1. Force branch identity
git checkout main

:: 2. Ensure the ROOT README is staged
git add README.md
git add .

:: 3. Final Commit
git commit -m "Architect Fix: Ensuring root README reflects ORCHESTRA Gateway vision"

:: 4. Force Push to finalize UI
git push origin main --force

echo.
echo [OmniIngest] VISUAL SYNC COMPLETE!
echo Refresh your GitHub main page now. The ORCHESTRA branding will be there.
pause
