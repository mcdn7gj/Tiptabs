# Simple makefile for tiptabs

# Create the environment directory and install all requirements
env:
	virtualenv env
	./env/bin/pip install -r requirements.txt

# Build the docker image
docker:
	docker build --tag tiptabs-app:3.9.0 .

# Install the project
install:
	pip install .

# Install the project on the command line
devel:
	pip install -e .

test:
	python -m unittest discover -s tests -p 'test_*.py'

# Run tests with coverage
coverage:
	python -m coverage run -m unittest discover -s tests -p 'test_*.py'
	python -m coverage report --fail-under=90

# Run tests with coverage and generate HTML report
coverage-html:
	python -m coverage run -m unittest discover -s tests -p 'test_*.py'
	python -m coverage html -d htmlcov

# Check per-file coverage minimums
coverage-check:
	python -m coverage run -m unittest discover -s tests -p 'test_*.py'
	python -c "
import coverage
import sys
cov = coverage.Coverage()
cov.load()
failed = False
for filename, analysis in cov.get_analysis_results():
    if 'Tiptabs' in filename and '__pycache__' not in filename:
        stmts = len(analysis[1])
        miss = len(analysis[2])
        if stmts > 0:
            pct = 100 * (stmts - miss) / stmts
            if pct < 90:
                print(f'FAIL: {filename} coverage {pct:.1f}% < 90%')
                failed = True
if failed:
    sys.exit(1)
print('All Tiptabs modules >= 90%')
"

clean:
	find ./tests/__pycache__ -type f -name '*.pyc' -exec /bin/rm {} \;

.PHONY: env docker install devel test coverage coverage-html coverage-check clean