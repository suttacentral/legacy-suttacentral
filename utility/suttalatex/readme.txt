Convert Suttas in a directory to Latex output including cover

Updated 15th August 2015
--------------------------------------------------------------

To use this module, copy the directory 'English' and give it a new name, preferably the language you want to use but any name will do.

Inside this directory there are 6 files that need to be translated:

1. about.txt - translate this text exactly - it will be used on the last page of the document.
2. bio.txt - write a biography of the author. Do not put the author's name at the bottom or top - this will be done automatically.
3. coverbacktext.txt - write a short text for the back of the cover. An example text is given.
4. preface.txt - write a preface to the document. Again, do not put the author's name at the bottom, this is done automatically.
5. trans.txt - translate all texts behind the '=' exactly according to the instructions in the document. Do not change the names before the '='.
6. vagga.csv - translate the pali headings of the vaggas that you need. It is not necessary to translate all, only the ones you will be using (so no need to translate DN vaggas if you are going to do the MN). Do not change the first 2 columns.

---------------------------------------------------------------
Once you are done translating, you are ready to run the module.
In the terminal, go to where your files are stored and type:
python convertlatex.py

Complete the directory name of where the sutta files are stored (f.i. pt/pi/su/mn/).
Type which suttas you want in this book, the output-name (the output name will become the relevant nikaya+output-name.tex in a directory of the same name) and the directory where you stored your translation files as you made above.

run lualatex on the output.tex file several times and make a note of the total number of pages of the pdf.
or use:
$ latexmk -pdf -pdflatex="lualatex %O %S" foo.tex and it is done automatically.
---------------------------------------------------------------
Now make the covers:
python cover.py

Complete the name of the translation directory as you made above, the number of pages in your pdf and the name of the output file. This program will produce two .tex files: output_paperback.tex and output_hardcover.tex. 

run lualatex on the output files several times or use latexmk as above.

That's it.
--------------------------------------------------------------

Convert Suttas in a directory to Epub output including cover
--------------------------------------------------------------
The cover for the Epub file is made together with the ones for the tex file. You have to convert it from pdf to png with: 

convert -density 300 -quality 100 mn_epub.pdf mn_epub.png

cover-height 7.63 is used as default. Make the cover before creating the epub files, then move it to the respective language folder in templates.

run the module:
python convertepub.py

Complete the directory name of where the sutta files are stored (f.i. pt/pi/su/mn/).
Type which suttas you want in this book, the output-name (the files will be stored in a directory called nikaya+output-name). Also enter again the directory of your translation files and other info.

In the Terminal, go the the just created directory and run (change the relevant sections where needed):
ebook-convert toc.html mn_port.epub --smarten-punctuation --cover mn_epub.png --authors 'Michael Beisert' --publisher 'SuttaCentral' --language 'portuguese' --title 'Majjhima Nikaya' --max-toc-links 54
