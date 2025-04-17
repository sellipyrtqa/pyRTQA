import os
import subprocess

# Check if requirements.txt exists, otherwise generate it
if not os.path.exists("requirements.txt"):
    subprocess.run(["pipreqs", ".", "--force"])

# Read dependencies
with open("requirements.txt", "r", encoding="utf-8") as req_file:
    dependencies = req_file.readlines()

# Write formatted credits to CREDITS.md
with open("CREDITS.md", "w", encoding="utf-8") as credits_file:
    credits_file.write("# 🎉 Credits\n\n")
    credits_file.write("This software is powered by amazing open-source libraries:\n\n")

    for dep in dependencies:
        package_name = dep.split("==")[0]  # Extract package name
        homepage = f"https://pypi.org/project/{package_name}/"
        credits_file.write(f"- **[{package_name}]({homepage})**\n")

print("✅ Fancy CREDITS.md file created!")
