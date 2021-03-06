## Hearthstone Deck Generator
CircleCI Status: [![CircleCI](https://circleci.com/gh/buckley-w-david/hs_markov.svg?style=svg&circle-token=44fd8d959ae07d5868395c75be199d4d050c5b47)](https://circleci.com/gh/buckley-w-david/hs_markov)

### Installation

#### Python 3.6

Hearthstone Deck Generator is tested to run on Python 3.6. To begin, you will need to have Python 3.6 installed.

We recommend `pyenv` as an easy way to easily install and switch between any versions of Python that you need.

See https://github.com/pyenv/pyenv#installation for pyenv installation instructions.

#### Virtualenv

Installing Python applications in a `virtualenv` is considered best practice. To do so, run:
```
python3 -m venv env
source env/bin/activate
```
This will create a new virtualenv in a  folder called `env`, and activate the virutalenv. To deactivate the virtualenv, run `deactivate`

#### Installing the app

Inside an activated virtualenv, and from the python folder of the project, run:
```
pip install -r requirements.txt
pip install -e .
```

#### Running the app

#### Running tests locally

Many of the tests require a running local MongoDB server. It will attempt to connect using the environment variable values, if they are set, or the defaults if they are not.

To run the tests, run:
```
pytest tests
```

To run the linter, run:
```
pylint src tests
```

To run the mypy type checker, run:
```
mypy src tests --ignore-missing-imports
```

#### Automated Testing

This repo is connected to CircleCI, and all tests, linters, and static type checking must pass before merging to master.
