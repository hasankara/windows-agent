import subprocess,sys,os

psxmlgen = subprocess.Popen([r'powershell.exe',
                             '-ExecutionPolicy',
                             'Unrestricted',
                             'C:\\Users\\hasan\\Desktop\\first_script.ps1'], cwd=os.getcwd())
result = psxmlgen.wait()

