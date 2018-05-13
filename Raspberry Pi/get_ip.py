import subprocess

process = subprocess.Popen(["hostname", "-I"], stdout=subprocess.PIPE)
text = process.communicate()[0][:-1].decode('utf-8')
print(text)
