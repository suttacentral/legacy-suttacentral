all:
	./pass1.py
	./pass2.py
	./pass3.py
	./dn.py
	./mn.py

clean:
	rm -rf tmp output

assets:
	cp tmp/sc.css output/mn
	cp tmp/sc.css output/dn
	cp tmp/sc.css output/sn
	cp ../../static/fonts/tharlon-regular-1.ttf output/mn
	cp ../../static/fonts/tharlon-regular-1.ttf output/dn
	cp ../../static/fonts/tharlon-regular-1.ttf output/sn

copy:
	mkdir -p ../../data/text/my/pi/dn
	mkdir -p ../../data/text/my/pi/mn
	cp output/dn/dn*.html ../../data/text/my/pi/dn
	cp output/mn/mn*.html ../../data/text/my/pi/mn

snpatch:
	diff -ur tmp/bakpass3 tmp/pass3 > sn.patch
