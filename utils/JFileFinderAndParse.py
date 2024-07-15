import os
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr_gen.JavaLexer import JavaLexer
from antlr_gen.JavaParser import JavaParser
from antlr_gen.JavaParserListener import JavaParserListener
from .TreeClassNode import ClassDetails

all_classes = {}


class CustomJavaLexer(JavaLexer):
    def __init__(self, input):
        super().__init__(input)
        self.comments = []
    
    def emitToken(self, token):
        if token.type in [self.COMMENT, self.LINE_COMMENT]:
            self.comments.append((token.text, token.tokenIndex))
        super().emitToken(token)


class CustomJavaParser(JavaParserListener):
    def __init__(self, lexer):
        self.current_class = ClassDetails(name="default", kind="class")
        self.lexer = lexer

    def enterClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        self.current_class = ClassDetails(
            name=ctx.identifier().getText(), 
            kind="class"
        )
        
        # get implements and extends
        if ctx.typeType() is not None:
            self.current_class.add_inheritance(
                kind='extends', 
                name=ctx.typeType().getText()
            )
        
        if ctx.typeList() is not None:
            for interface in ctx.typeList():
                self.current_class.add_inheritance(
                    kind='implements', 
                    name=interface.getText()
                )
        
        # get modifiers
        self.get_modifiers(ctx)

        # get comments
        self.current_class.comments = self.get_current_comments(ctx)
        

    def enterInterfaceDeclaration(self, ctx:JavaParser.InterfaceDeclarationContext):
        self.current_class = ClassDetails(
            name=ctx.identifier().getText(), 
            kind="interface"
        )
        
        # get extends
        if ctx.typeList() is not None:
            for interface in ctx.typeList().typeType():
                self.current_class.add_inheritance(
                    kind='extends', 
                    name=interface.getText()
                )
        
        # get modifiers
        self.get_modifiers(ctx)

        # get comments
        self.current_class.comments = self.get_current_comments(ctx)


    def enterEnumDeclaration(self, ctx:JavaParser.EnumDeclarationContext):
        self.current_class = ClassDetails(
            name=ctx.identifier().getText(), 
            kind="enum"
        )
        
        # # get implements and extends
        # if ctx.typeType() is not None:
        #     self.current_class.add_inheritance(
        #         kind='extends', 
        #         name=ctx.typeType().getText()
        #     )

        for enumConstant in ctx.enumConstants().enumConstant():
            self.current_class.add_enum_constant(
                name=enumConstant.identifier().getText(), 
                annotation=enumConstant.annotation().getText(), 
                arguments=enumConstant.arguments().getText()
            )

        # get modifiers
        self.get_modifiers(ctx)

        # get comments
        self.current_class.comments = self.get_current_comments(ctx)
    
    # def enterEnumConstant(self, ctx:JavaParser.EnumConstantContext):
    #     self.current_class.add_enum_constant(
    #         name=ctx.identifier().getText(), 
    #         annotation=ctx.annotation().getText(), 
    #         arguments=ctx.arguments().getText()
    #     )

    def enterClassBodyDeclaration(self, ctx:JavaParser.ClassBodyDeclarationContext):
        # find nested classes
        try:
            if self.current_class.kind == 'class':
                if ctx.memberDeclaration().classDeclaration() is not None:
                    nested_class = ctx.memberDeclaration().classDeclaration()
                    nested_class_name = nested_class.identifier().getText()
                    nested_class = ClassDetails(name=nested_class_name, kind='class')
                    self.current_class.add_nested_class(nested_class)
        except Exception as e:
            print(e, "nested class error")

    def enterFieldDeclaration(self, ctx:JavaParser.FieldDeclarationContext):
        # tries to get class fields information, for all three: class, interface, and enums
        try:
            mods = []
            # 1st parentCtx: memberDeclarationContext, 2nd parentCtx: classBodyDeclarationContext
            for mod in ctx.parentCtx.parentCtx.modifier():
                mods.append(mod.getText())
            
            var_name_and_value = ""
            for name in ctx.variableDeclarators.variableDeclarator():
                var_name_and_value += name.getText() + " "
            
            var_type = ctx.typeType().classOrInterfaceType().typeIdentifier().getText()

            self.current_class.add_field(var_name_and_value, mods, var_type)
        except Exception as e:
            print(e, "field error")
        
        # modifiers = []
        # for modifier in ctx.modifier():
        #     modifiers.append(modifier.getText())
        
        # self.current_class.add_field(
        #     ctx.variableDeclaratorList().getText(), 
        #     modifiers, ctx.unannType().
        #     getText()
        #     )

    def enterMethodDeclaration(self, ctx:JavaParser.MethodDeclarationContext):
        # modifiers = []
        # for modifier in ctx.modifier():
        #     modifiers.append(modifier.getText())
        # self.current_class.add_method(ctx.methodHeader().methodDeclarator().identifier().getText(), modifiers, ctx.methodHeader().result().getText(), ctx.methodHeader().methodDeclarator().formalParameterList().getText())
        
        # for class methods: 
        try:
            name = ctx.identifier().getText()

            mods = []
            for mod in ctx.parentCtx.parentCtx.modifier():
                mods.append(mod.getText())
            
            params = str(ctx.formalParameters().getText())

            return_type = ctx.typeTypeOrVoid().getText()

            self.current_class.add_method(name, mods, return_type, params)
        except Exception as e:
            print(e, "method error") 
    
    def enterInterfaceBodyDeclaration(self, ctx:JavaParser.InterfaceBodyDeclarationContext):
        # find methods in body
        try:
            if self.current_class.kind == 'interface':
                if ctx.interfaceMemberDeclaration().interfaceMethodDeclaration() is not None:
                    method = ctx.interfaceMemberDeclaration().interfaceMethodDeclaration()
                    method_name = method.interfaceCommonBodyDeclaration().identifier().getText()
                    method_params = method.interfaceCommonBodyDeclaration().formalParameterList().getText()
                    method_return_type = method.interfaceCommonBodyDeclaration().typeTypeorVoid().getText()
                    method_mods = []
                    for mod in method.interfaceCommonBodyDeclaration().interfaceMethodModifier():
                        method_mods.append(mod.getText())
                    self.current_class.add_method(method_name, method_mods, method_return_type, method_params)
                    
        except Exception as e:
            print(e, "interface method error")
        
    def enterEnumBodyDeclaration(self, ctx: JavaParser.EnumBodyDeclarationsContext):
        # find methods information in enums
        try:
            name = ctx.classBodyDeclaration().memberDeclaration().getText()

            mods = []
            for mod in ctx.classBodyDeclaration().modifier():
                mods.append(mod.getText())
            
            params = str(ctx.classBodyDeclaration().memberDeclaration().getText())

            return_type = ctx.classBodyDeclaration().memberDeclaration().methodDeclaration().typeTypeOrVoid().getText()

            self.current_class.add_method(name, mods, return_type, params)

        except Exception as e:
            print(e, "nested method in enum error")

    def enterExpression(self, ctx: JavaParser.ExpressionContext):
        try:
            # Capture method calls and variable usages
            if ctx.methodCall() is not None:
                method_call = ctx.methodCall().identifier().getText()
                method_args = ctx.methodCall().expressionList().getText() if ctx.methodCall().expressionList() else ""
                self.current_class.add_usage("method_call", method_call, method_args)
            elif ctx.primary() is not None and ctx.primary().identifier() is not None:
                variable_usage = ctx.primary().identifier().getText()
                self.current_class.add_usage("variable_usage", variable_usage)
        except Exception as e:
            print(e, "expression error")
    
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
    
    def get_current_comments2(self, ctx):
        start_token_index = ctx.start.tokenIndex
        comments =[]
        new_comments = []
        for comment, index in self.lexer.comments:
            if index < start_token_index:
                comments.append(comment)
            else:
                new_comments.append((comment, index))
        self.lexer.comments = new_comments
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
        self.classes = {}

    
    # def parse_files(self):
    #     for subdir, _, files in os.walk(self.root_dir):
    #         for file in files:
    #             if file.endswith('.java'):
    #                 lexer = self.parse_file(os.path.join(subdir, file))
    #     if self.listener:
    #         return self.classes
    #     return {}


    def parse_files(self):
        for subdir, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.java'):
                    print("java file found: ", file)
                    file_path = os.path.join(subdir, file)
                    self.parse_file(file_path)
        if self.listener:
            return self.classes
        return {}

    def parse_file(self, file_path):
        input_stream = FileStream(file_path)
        lexer = CustomJavaLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)
        tree = parser.compilationUnit()
        
        walker = ParseTreeWalker()
        listener = CustomJavaParser(lexer)
        walker.walk(listener, tree)
        return lexer

    def get_classes(self):
        return all_classes 
