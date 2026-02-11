@echo off
echo [OmniIngest] ARCHITECT FORCE-PUSH PROTOCOL...
cd /d "D:\Omnigest_ABDM_2.0"

:: 1. Force the local state to be on 'main' branch, even if it's messy
git checkout -B main

:: 2. Ensure all 84+ files we just created are included
git add .

:: 3. Commit this crystalline state
git commit -m "Final Master Build: OmniIngest Phase 0.3 + ORCHESTRA Platform"

:: 4. FORCE PUSH: Override the website with our computer's truth
echo.
echo [OmniIngest] Overwriting GitHub with local architecture...
git push origin main --force

echo.
echo [OmniIngest] FORCE-PUSH COMPLETE! 
echo Check GitHub now. It MUST be updated.
pause
