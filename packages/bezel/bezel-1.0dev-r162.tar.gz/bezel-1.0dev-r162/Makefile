all: docs

clean: doxygen-clean pylint-clean code-clean

code-clean:
	@find -name '*.pyc' -delete
	@find -name '*~' -delete
	@python setup.py clean
	@echo "Cleaned source directory."

# create Doxygen API documentation.
doxygen:
	doxygen docs/Doxyfile
	@echo "Doxygen API documentation created.."

# clean Doxygen API documentation.
doxygen-clean:
	@rm -rf docs/html
	@echo "Cleaned Doxygen API documentation."

# create pylint report.
pylint:
	@pylint --rcfile=docs/pylintrc `find bezel -name '*.py'` > docs/pylint.html
	@echo "Pylint report generated."

#clean pylint report.
pylint-clean:
	rm -f docs/pylint.html
	@echo "Cleaned Pylint report."

