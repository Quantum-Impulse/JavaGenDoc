import os
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker, Token
from antlr_gen.JavaLexer import JavaLexer
from antlr_gen.JavaParser import JavaParser
from antlr_gen.JavaParserListener import JavaParserListener
from .TreeClassNode import ClassDetails

all_classes = {}


class CustomJavaLexer(JavaLexer):
    def __init__(self, input):
        super().__init__(input)
        self.comments = []
    
    def emitToken(self, token: Token):
        if token.type in [self.COMMENT, self.LINE_COMMENT]:
            self.comments.append((token.text, token.line, token.column))
        super().emitToken(token)

    def reset(self):
        super().reset()
        self._input = JavaLexer.UnicodeBOM + self._input


class CustomJavaParser(JavaParser):
    def __init__(self, lexer):
        super().__init__(input)
        self.current_class = ClassDetails(name="default", kind="class")
        self.lexer = lexer

    def enterClassDeclaration(self, ctx:JavaParser.ClassDeclarationContext):
        self.current_class = ClassDetails(name=ctx.Identifier().getText(), kind="class")
        
        # get implements and extends
        if ctx.typeType() is not None:
            self.current_class.add_inheritance(kind='extends', name=ctx.typeType().getText())
        
        if ctx.typeList() is not None:
            for interface in ctx.typeList().typeType():
                self.current_class.add_inheritance(kind='implements', name=interface.getText())
        
        # get modifiers
        self.get_modifiers(ctx)

        # get comments
        self.current_class.comments = self.get_current_comments(ctx)
        

    def enterInterfaceDeclaration(self, ctx:JavaParser.InterfaceDeclarationContext):
        self.current_class = ClassDetails(name=ctx.Identifier().getText(), kind="interface")
        
        # get extends
        if ctx.typeList() is not None:
            for interface in ctx.typeList().typeType():
                self.current_class.add_inheritance(kind='extends', name=interface.getText())
        
        # get modifiers
        self.get_modifiers(ctx)

        # get comments
        self.current_class.comments = self.get_current_comments(ctx)


    def enterEnumDeclaration(self, ctx:JavaParser.EnumDeclarationContext):
        self.current_class = ClassDetails(name=ctx.Identifier().getText(), kind="enum")
        
        # get implements and extends
        if ctx.typeType() is not None:
            self.current_class.add_inheritance(kind='extends', name=ctx.typeType().getText())

        # get modifiers
        self.get_modifiers(ctx)

        # get comments
        self.current_class.comments = self.get_current_comments(ctx)
    
    def enterEnumConstant(self, ctx:JavaParser.EnumConstantContext):
        self.current_class.add_enum_constant(name=ctx.Identifier().getText(), annotation=ctx.annotation().getText(), arguments=ctx.arguments().getText())

    def enterFieldDeclaration(self, ctx:JavaParser.FieldDeclarationContext):
        modifiers = []
        for modifier in ctx.modifier():
            modifiers.append(modifier.getText())
        self.current_class.add_field(ctx.variableDeclaratorList().getText(), modifiers, ctx.unannType().getText())

    def enterMethodDeclaration(self, ctx:JavaParser.MethodDeclarationContext):
        modifiers = []
        for modifier in ctx.modifier():
            modifiers.append(modifier.getText())
        self.current_class.add_method(ctx.methodHeader().methodDeclarator().Identifier().getText(), modifiers, ctx.methodHeader().result().getText(), ctx.methodHeader().methodDeclarator().formalParameterList().getText())
    
    def get_modifiers(self, ctx):
        # get modifiers for classes and interfaces
        try:
            for mod in ctx.parentCtx.classOrInterfaceModifier():
                if mod.getText()[0] == '@':
                    self.current_class.add_annotation(mod.getText())
                
                if mod.getText() == 'public':
                    self.current_class.is_public = True
                if mod.getText() == 'protected':
                    self.current_class.is_protected = True
                if mod.getText() == 'private':
                    self.current_class.is_private = True
                if mod.getText() == 'static':
                    self.current_class.is_static = True
                if mod.getText() == 'abstract':
                    self.current_class.is_abstract = True
                if mod.getText() == 'final':
                    self.current_class.is_final = True

        except Exception as e:
            print(e)

    def get_current_comments(self, ctx):
        start = ctx.start.start
        end = ctx.stop.stop
        comments = []
        for comment in self.lexer.comments:
            if start <= comment[1] and comment[1] <= end:
                comments.append(comment[0])
        return comments
    
    def exitClassDeclaration(self, ctx:JavaParser.ClassDeclarationContext):
        print(self.current_class.get_dict())

        all_classes[self.current_class.name] = self.current_class
    
    def exitInterfaceDeclaration(self, ctx:JavaParser.InterfaceDeclarationContext):
        print(self.current_class.get_dict())

        all_classes[self.current_class.name] = self.current_class
    
    def exitEnumDeclaration(self, ctx:JavaParser.EnumDeclarationContext):
        print(self.current_class.get_dict())

        all_classes[self.current_class.name] = self.current_class
    

    def get_class(self):
        return self.current_class




class JavaFileParser:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.listener = CustomJavaParser(lexer=None)
        

    
    def parse_files(self):
        for subdir, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(subdir, file)
                    self.parse_file(file_path)

    def parse_file(self, file_path):
        input_stream = FileStream(file_path)
        lexer = CustomJavaLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = CustomJavaParser(stream)
        tree = parser.compilationUnit()
        
        walker = ParseTreeWalker()
        walker.walk(self.listener, tree)

    def get_classes(self):
        return all_classes 
