@echo off
echo [OmniIngest] Finalizing Phase 0.3...
cd /d "D:\Omnigest_ABDM_2.0"
git add .
git commit -m "Final Release: OmniIngest Phase 0.3 - The Orchestration Foundation for ORCHESTRA"
git push
echo [OmniIngest] Successfully pushed to GitHub!
pause
