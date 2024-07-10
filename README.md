# Java Code Parser and Documentation Generator

This project parses a Java codebase to generate an Abstract Syntax Tree (AST) and uses the AST to generate basic documentation for the codebase.

## Prerequisites

- Python 3.x
- Java Development Kit (JDK)
- `pip` (Python package installer)

## Setup Instructions
java -jar antlr-4.8-complete.jar -Dlanguage=Python3 JavaLexer.g4
java -jar antlr-4.8-complete.jar -Dlanguage=Python3 JavaParser.g4
or 
antlr4 -Dlanguage=Python3 JavaLexer.g4
antlr4 -Dlanguage=Python3 JavaParser.g4


python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
Windows admin powershell:  Set-ExecutionPolicy Unrestricted -Force

### 1. Clone the Repository

First, clone the repository to your local machine. If you haven't created a repository yet, initialize a new one and clone it:

```sh
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
