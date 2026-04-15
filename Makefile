.DEFAULT_GOAL := help

help: ## Shows this help message
	@printf "\033[1m%s\033[36m %s\033[32m %s\033[0m \n\n" "Development environment for" "SkyBellgen" "";
	@awk 'BEGIN {FS = ":.*##";} /^[a-zA-Z_-]+:.*?##/ { printf " \033[36m make %-25s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST);
	@echo

requirements: ## Install requirements
	@python3 -m pip --disable-pip-version-check install -r requirements_test.txt

lint: ## Lint all files
	@pre-commit run --all-files

coverage: ## Check the coverage of the package
	@python3 -m pytest tests

build: ## Build the package
	@python3 -m build
