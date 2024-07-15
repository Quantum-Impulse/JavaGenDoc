# Java Code Parser and Documentation Generator

This project parses a Java codebase to generate an Abstract Syntax Tree (AST) and uses the AST to generate basic documentation for the codebase. It then uses langchain to use AI(RAG) to prompt a genAI model to suggest code for implementing new features along with creating documentation.

## Prerequisites
Technolgies:
- Python 3.x
- Java Development Kit (JDK)
- `pip` (Python package installer)
    - antlr4
    - langchain
- openai api key

Permissions:
- [developer restriction policy]()

## Setup Instructions

### Generate files from .g4
Generate the lexer, parser, and parserListerner files from [.g4 files](https://github.com/antlr/grammars-v4/tree/master/java/java) 

Primary way to generate:
```sh
antlr4 -Dlanguage=Python3 JavaLexer.g4
antlr4 -Dlanguage=Python3 JavaParser.g4
```
Or \
Jar file should be download within the local enviroment packages
```sh
java -jar antlr-4.8-complete.jar -Dlanguage=Python3 JavaLexer.g4
java -jar antlr-4.8-complete.jar -Dlanguage=Python3 JavaParser.g4
```
### Venv and installing packages
Then create venv(make sure to have permission to do so) and install packages. Run powershell command for windows before activating venv.

```sh
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
Windows admin powershell:  Set-ExecutionPolicy Unrestricted -Force
```
### Setup OpenAI key
In the utils folder using the constants.py.default as a template, create a copy of it and rename it to constants.py. Put key in there.

## Running The Script
```sh
python main.py
```