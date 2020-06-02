python_PYTHON = Build.py leave.py






#config:=default_config.mk
#include $(config)
## Project Setup
#venv_dir = . venv
#src_dir = $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
#python = python3.7
#PY=python -m py_compile
## Declare the tools
#pkgm = install
#venv = virtualenv --no-site-packages --distribute -p /usr/bin/$(python)
#graph = build_graph.py
#lint = pep8
#
## Declare the commands
#venv_cmd = $(venv)
#pkgm_cmd = $(python) -m $(pkgm)
#test_cmd = $(python) -m $(test)
#lint_cmd = $(python) -m $(lint)

# Install the application
#.PHONY: install
#install:
#	$(pkgm_cmd) install $(test)
#	$(pkgm_cmd) install -r requirements.txt
#	$(pkgm_cmd) install -e .

# Run the test suite
#.PHONY: test
#test:
#	$(PY) test.py

# Lint the coding guidelines
#.PHONY: lint
#lint:
#	$(lint_cmd) --max-line-length=120 $(pkg_name)
#
## Clean the directory
#.PHONY: clean
#clean:
#	py3clean $(src_dir)
#	rm -rf $(pkg_name).egg-info
#	rm -rf dist
#	rm -rf $(venv_dir)
#	find $(src_dir) -type d -name 'node_modules'  -exec rm -rf {} +
#	find $(src_dir) -type d -name 'bower_components'  -exec rm -rf {} +
#
## Write the requirements to file
#.PHONY: freeze
#freeze:
#	$(pkgm_cmd) freeze > requirements.txt
#
## Create the virtual environment
#.PHONY: venv
#venv:
#	test -d $(venv_dir) || $(venv_cmd) $(venv_dir)
#	@echo "To activate the virtual environment run following command:"
#	@echo "source $(venv_dir)/bin/activate"
#	@echo "Copying command to clipboard"
#	echo "source $(venv_dir)/bin/activate" | xclip -sel clip
#
## Self-update the Makefile
#MAKE_PATH = https://gist.githubusercontent.com/chaosmail/7d67a998922d3d07686e/raw$(date +%s)
#.PHONY: self-update
#self-update:
#	curl -s -o Makefile.bak $(MAKE_PATH)
#	sed -i '2s/.*/pkg_name = ${pkg_name}/' Makefile.bak
#	rm Makefile
#	mv Makefile.bak Makefile