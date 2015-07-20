#!/usr/bin/env bash
# (C) 2010 - Pablo Olmos de Aguilera Corradini <pablo{at)glatelier.org>
# Under GPL v3. See http://www.gnu.org/licenses/gpl-3.0.html

# requires html2text.py
wget -q http://www.aaronsw.com/2002/html2text/html2text.py

for file in *.html; do
    name=$(basename $file)
    name=${file%.*}
    python2 html2text.py ${file} > ${name}.txt
done
