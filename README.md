# Shopping Made Easy (SME)
This repository contains the source code for both the front-end and back-end of the shopping made easy (SME) application.

## Running the Server Locally
```sh
uvicorn main:app --reload
```

## Linting
The following command lints all python files.

```sh
pylint --jobs=0 $(git ls-files '*.py')
```
