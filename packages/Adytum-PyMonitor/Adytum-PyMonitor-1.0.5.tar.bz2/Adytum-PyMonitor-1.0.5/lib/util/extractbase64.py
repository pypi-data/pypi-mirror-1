from base64 import decode

filedata = open('b64.txt', 'r')
output = open('spam.zip', 'wb')
decode(filedata, output)
