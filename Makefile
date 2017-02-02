.PHONY: pep, install, clean

pep:
	pep8 ./ --ignore=E501,E701

install:
	pip install -r requirements.txt

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

deploy:
	python setup.py sdist upload -r mimiron
