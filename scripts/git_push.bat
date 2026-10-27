@echo off
echo ==========================================================
echo  COMMITTING AND PUSHING TO GITHUB
echo  Repo: https://github.com/KarimElwaly/AI-Robotics-Design-Studio
echo ==========================================================
echo.
cd /d "%~dp0\.."

git remote remove origin 2>nul
git remote add origin https://github.com/KarimElwaly/AI-Robotics-Design-Studio.git
echo Adding files to git...
git add .
echo Committing files...
git commit -m "feat: complete AI Robotics Design Studio platform implementation"
echo Setting default branch to main...
git branch -M main
echo Pushing to GitHub repository...
git push -u origin main

echo.
echo ==========================================================
echo  Done!
echo ==========================================================
