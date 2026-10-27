import sys
import os
import subprocess

print(f"Python: {sys.version}")
print(f"Current Directory: {os.getcwd()}")

# Check pywin32
try:
    import win32com.client
    import pythoncom
    print("win32com / pythoncom: AVAILABLE")
except ImportError as e:
    print(f"win32com: NOT AVAILABLE ({e})")

# Check SOLIDWORKS COM ProgIDs
for progid in ["SldWorks.Application", "SldWorks.Application.32", "SldWorks.Application.34"]:
    try:
        import win32com.client
        app = win32com.client.GetActiveObject(progid)
        print(f"Active object for {progid}: FOUND ({app.RevisionNumber()})")
    except Exception as e:
        print(f"Active object for {progid}: None or not running ({e})")

# Check running processes for SLDWORKS
try:
    import psutil
    sw_procs = [p for p in psutil.process_iter(['pid', 'name', 'exe']) if 'sldworks' in p.info['name'].lower()]
    print(f"Running SOLIDWORKS processes: {sw_procs}")
except ImportError:
    # Use tasklist
    res = subprocess.run(["tasklist", "/FI", "IMAGENAME eq SLDWORKS.exe"], capture_output=True, text=True)
    print(f"tasklist check:\n{res.stdout}")
