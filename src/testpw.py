import subprocess
import sys

# process = subprocess.Popen([r'powershell.exe',
#                              '-ExecutionPolicy',
#                              'Unrestricted',
#                              'C:\\Users\\hasan\\Desktop\\first_script.ps1lllll11'],  stderr=subprocess.PIPE, stdout=subprocess.PIPE)

# filePath = 'C:\\Users\\hasan\\Desktop\\test_param.ps1'
# process = subprocess.Popen([r'powershell.exe',
#                             '-ExecutionPolicy',
#                             'Unrestricted', filePath, '"hasan" "dsa"'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
# # stdout=subprocess.PIPE
# # stdout=sys.stdout
#
# result_code = process.wait()
# p_out = process.stdout.read().decode("unicode_escape")
# p_err = process.stderr.read().decode("unicode_escape")
#
# print(result_code)
# print(p_out)
# print(p_err)


process = subprocess.Popen("wmic baseboard get manufacturer", stdout=subprocess.PIPE, shell=True)
# print(p.stdout.read())

p_out = process.stdout.read()
print("----->>" + str(p_out))
p_out = process.stdout.read().decode("ascii")
print("----->>" + p_out)