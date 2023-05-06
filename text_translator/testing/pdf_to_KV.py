import fitz

txt = []


'''
doc = fitz.open("Bhashampally.pdf")            # some existing PDF
page = doc[0]
text = page.get_text("text")
txt = list(text)
# print(text)
text = text.split('\n')
txt = list(text)
# print(txt)
ix = text.index('Prefix')
print(text[ix],": ",end=text[ix+1])
# print(text[ix+18])
'''


'''
doc = fitz.open("Bhashampally.pdf")            # some existing PDF
    
for page_num in range(len(doc.pages)):
    page = doc[page_num]
    text = page.get_text("text")
    # txt = list(text)
    # print(text)
    # text = text.split('\n')
    txt = list(text)
    # print(txt)
    ix = text.index('Prefix')
    print('Prefix',": ",end=text[ix+1])
'''





doc = fitz.open("Bhashampally.pdf")            # some existing PDF

page = doc[0]
words=['Last Name', 'First Name']
text = page.get_text('')
# txt = list(text)
# print(text)
text = text.split('\n')
txt = list(text)
# print(txt)
print('{')
for i in words:
    ix = text.index(i)
    print("\""+text[ix]+"\"",": \"",end=text[ix+1]+"\",\n")
# print(text[ix+18])


page = doc[1]
words=['Program Applying to*', 
        'Semester Applying to*']
text = page.get_text('')
text = text.split('\n')
txt = list(text)
for i in words:
    ix = text.index(i)
    print("\""+text[ix]+"\"",": \"",end=text[ix+1]+"\",\n")
# print(text[ix+18])





page = doc[38]
words=['GRE']
text = page.get_text('')
text = text.split('\n')
txt = list(text)
for i in words:
    ix = text.index(i)
    print("\""+text[ix]+"\"",": \"",end=text[ix+4]+"\n"+text[ix+5]+"\n"+text[ix+6]+"\",\n")
    # print(text[ix],": ",end=text[ix+4]+"\n"+text[ix+5]+"\n"+text[ix+6]+";\n")




page = doc[4]
words=['GPA']
text = page.get_text('')
text = text.split('\n')
txt = list(text)
for i in words:
    ix = text.index(i)
    print("\""+text[ix]+"\"",": \"",end=text[ix+1]+"\"\n")
# print(text[ix+18])


print('}')
