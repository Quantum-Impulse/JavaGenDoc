# This file gives context of the project,
# and it is used to import the generated files from the antlr_gen folder.
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from antlr_gen.JavaLexer import JavaLexer
from antlr_gen.JavaParser import JavaParser
from antlr_gen.JavaParserListener import JavaParserListener
