.PHONY: lint
lint:
	@pipenv run lint
	@pipenv run sast
	@pipenv run imports
	@pipenv run issues

.PHONY: metrics
metrics:
	$(info computing Halstead complexity metrics...)
	@pipenv run hal-metrics
	$(info computing McCabe/cyclomatic complexity...)
	@pipenv run cc-metrics
	$(info computing maintainability index score...)
	@pipenv run mi-metrics

.PHONY: test
test:
	@pipenv run test

.PHONY: coverage
coverage:
	-@pipenv run coverage

.PHONY: build
build: clean
	pipenv run build

.PHONY: clean
clean:
	pipenv run clean

.PHONY: install
install:
	@mkdir -p .venv
	pipenv install -d

.PHONY: test-publish
test-publish:
	pipenv run python -m twine upload --repository testpypi dist/*

.PHONY: test-install
test-install:
	python -m pip install --index-url https://test.pypi.org/simple/ --no-deps dotctl
.PHONY: local-install
local-install: build
	python3 -m pip install --use-feature=in-tree-build .
.PHONY: local-dotfiles-install
local-dotfiles-install:
	@/usr/local/Cellar/python@3.9/3.9.1/Frameworks/Python.framework/Versions/3.9/bin/dotfiles install
.PHONY: local-dotfiles-setup
local-dotfiles-setup:
	@/usr/local/Cellar/python@3.9/3.9.1/Frameworks/Python.framework/Versions/3.9/bin/dotfiles setup

image:
	@docker build -t dotctl:test -f Dockerfile .

sh-image: ARGS=ash
sh-image: run-image

test-image: ARGS=pipenv run test
test-image: run-image

coverage-image: ARGS=pipenv run coverage
coverage-image: run-image

run-image:
	@touch coverage.xml
	@touch test-report.xml
	@docker run \
		--rm \
		-it \
		-v ${PWD}/.env:/home/dotctl/.env \
		-v ${PWD}/.env.test:/home/dotctl/.env.test \
		-v ${PWD}/src:/home/dotctl/src \
		-v ${PWD}/tests:/home/dotctl/tests \
		-v ${PWD}/coverage.xml:/home/dotctl/coverage.xml \
		-v ${PWD}/test-report.xml:/home/dotctl/test-report.xml \
		dotctl:test \
		${ARGS}
