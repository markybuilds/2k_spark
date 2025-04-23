@echo off
echo Setting up Git repository for 2K_Spark...

rem Initialize Git repository
git init

rem Add remote origin
git remote add origin https://github.com/markybuilds/2K_Spark.git

rem Add all files to staging
git add .

rem Commit changes
git commit -m "Initial commit"

echo Repository setup complete!
echo.
echo To push to GitHub, run:
echo git push -u origin main
echo.
echo Note: You'll need to create the repository on GitHub first at:
echo https://github.com/markybuilds/2K_Spark
