.DEFAULT_GOAL := help

help: ## Shows this help message
	@printf "\033[1m%s\033[36m %s\033[32m %s\033[0m \n\n" "Development environment for" "aioskybellgen" "";
	@awk 'BEGIN {FS = ":.*##";} /^[a-zA-Z_-]+:.*?##/ { printf " \033[36m make %-25s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST);
	@echo

requirements: ## Install requirements
	@python3 -m pip --disable-pip-version-check install -r requirements_test.txt

lint: ## Lint all files
	@python3 -m isort .
	@python3 -m black --fast custom_components/skybellgen tests
	@python3 -m pylint custom_components/skybellgen tests
	@python3 -m flake8 --max-line-length=88 custom_components/skybellgen tests
	@python3 -m mypy custom_components/skybellgen

coverage: ## Check the coverage of the package
	@python3 -m pytest tests

build: ## Build the package
	@python3 -m build