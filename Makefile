PHONY: help, setup, install

# ---------------------------------------------------------------------------- #

python_version = 3.12.2
python_env = filtering_interface_poc

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------- #
# developer python setup
# ---------------------------------------------------------------------------- #

pyenv-setup:   ## setup python virtual environment
	pyenv install --skip-existing $(python_version) &&\
	pyenv uninstall -f $(python_env) &&\
	pyenv virtualenv --force $(python_version) $(python_env) &&\
	pyenv local $(python_env) &&\
	pip install --upgrade pip &&\
	pip install -r requirements.txt 

pyenv-install:   ## install/reinstall python requirements into virtual env
	pip install --upgrade pip &&\
	pip install -r requirements.txt

pyenv-upgrade:   ## install/reinstall python requirements into virtual env
	pip install --upgrade pip &&\
	pip install --upgrade -r requirements.txt
