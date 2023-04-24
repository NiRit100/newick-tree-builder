dist:
	mkdir dist

clean:  dist
	rm -f dist/*
	rm -rf logs/

build:	clean
	python3 -m build

upload:	
	twine upload dist/* --verbose
