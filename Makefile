init:
	pip install -r requirements.txt

install: init
	python setup.py install

clean:
	rm -r build dist *.egg-info

test:
	nosetests -v tests
