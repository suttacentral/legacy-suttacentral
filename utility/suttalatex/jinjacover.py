import os
import jinja2
import csv

'''
This module creates a cover for a 6x9 inch book with a given number of pages and the user input of the translation texts
that need to be printed on the file.
'''

while True:
    language = input("Enter the directory name where your translation files are stored: ")
    try:
        os.listdir(language)
        break
    except:
        print('Not a valid directory, please try again')
while True:
    pages = input("Enter the number of pages in the book: ")
    try:
        pages_in_file = int(pages)
        break
    except:
        print('This is not an integer, please try again.')

covername = input("Enter the output name for your cover: ")

#sets number of pages to the nearest divisible by 4
if pages_in_file % 4 != 0:
    pages_in_file += 4 - (pages_in_file % 4)

#book dimensions
book_width = 6
book_height = 9

# creates a dictionary of the translated texts in trans.txt
transl_dict = dict()
for rows in csv.reader(open(language+'/trans.txt', mode='r'),delimiter='='):
    transl_dict[rows[0]] = rows[1]

# calculates the measurements used for a paperback book and writes it to jinja2 template
spine_width = round(0.00225 * pages_in_file, 3)
margin_tb = 0.125
margin_lr = 0.125
top_bar = 1.45 + margin_tb
bottom_bar = 1.5 + margin_tb
cover_width = round((book_width * 2) + (margin_lr * 2) + spine_width, 2)
cover_height = book_height + (margin_tb * 2)
text_height = cover_height - top_bar - bottom_bar - 0.05
bottom_colour='dark-pastel-purple'

fileWritePaperback = open(covername+'_paperback.tex', 'w') 

jinja2_environment = jinja2.Environment(autoescape = True, loader = jinja2.FileSystemLoader(os.getcwd()))
template = jinja2_environment.get_template('cover_template.tex')
fileWritePaperback.write(template.render(cover_width=cover_width,cover_height=cover_height,
    spine_width=spine_width,text_height=text_height,top_bar=top_bar,bottom_bar=bottom_bar,
    book_width=book_width,book_height=book_height,margin_tb=margin_tb,margin_lr=margin_lr,transl_dict=transl_dict,
    coverbacktext=language+'/coverbacktext.txt',isbn=transl_dict['isbn_paperback'],bottom_colour=bottom_colour))

fileWritePaperback.close()

# calculates the measurements used for a hardcover book and writes it to jinja2 template
hspine_width = round((0.002 * pages_in_file) + 0.25, 3)
hmargin_tb = 0.125
hmargin_lr = 3.625
htop_bar = 1.245 + hmargin_tb
hbottom_bar = 1.25 + hmargin_tb
hcover_width = round((book_width * 2) + (hmargin_lr * 2) + hspine_width, 2)
hcover_height = book_height + (hmargin_tb * 2)
htext_height = hcover_height - htop_bar - hbottom_bar - 0.05
bottom_colour='dark-pastel-green'

fileWriteHardcover = open(covername+'_hardcover.tex', 'w') 

fileWriteHardcover.write(template.render(cover_width=hcover_width,cover_height=hcover_height,
    spine_width=hspine_width,text_height=htext_height,top_bar=htop_bar,bottom_bar=hbottom_bar,
    book_width=book_width,book_height=book_height,margin_tb=hmargin_tb,margin_lr=hmargin_lr,transl_dict=transl_dict,
    coverbacktext=language+'/coverbacktext.txt',isbn=transl_dict['isbn_hardcover'],bottom_colour=bottom_colour))

fileWriteHardcover.close()
