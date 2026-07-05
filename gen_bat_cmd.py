import base64,json
# Read the bat file
data=open('/home/ubuntu/.openclaw/workspace/一键远程.bat','rb').read().replace(b'\n',b'\r\n')
b64=base64.b64encode(data).decode()
# Split into 2 lines for cmd echo
n=len(b64)//2+1
part1=b64[:n]
part2=b64[n:]
# Generate commands
print(f'REM Write this to Windows Desktop:')
print(f'echo {part1}> p1.txt')
print(f'echo {part2}> p2.txt')
print(f'echo copy /b p1.txt+p2.txt yyb64.txt | find "copied"')
