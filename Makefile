clean:
	mv -f dist/* dist-old/

build:	clean
	python3 -m build

upload:	
	twine upload dist/* --verbose
