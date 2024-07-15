# this class will be used as nodes in the tree
# the tree will be organized in a way to represent any inheritance, implements, and/or nested classes

class ClassDetails:
    def __init__(self, name, kind, is_abstract=False, is_static=False, is_final=False, is_singleton=False, generics=None) -> None:
        self.name = name
        self.kind = kind # class, interface, enum, annotation, exception
        self.is_abstract = is_abstract
        self.is_static = is_static
        self.is_final = is_final
        self.is_public = False
        self.is_protected = False
        self.is_private = False
        self.is_singleton = is_singleton
        self.generics = generics if generics else []
        self.methods = []
        self.fields = []
        self.enum_constants = []
        self.nested_classes = []
        self.comments = [] # all comments within the files of the related class
        self.annotations = []
        self.inheritance = {'extends': [], 'implements': []}

    def add_field(self, name_and_value, modifiers, var_type=None):
        self.fields.append({
            'name_and_value': name_and_value,
            'modifiers': modifiers,
            'var_type': var_type
        })
    
    def add_method(self, name, modifiers, return_type=None, parameters=None):
        self.methods.append({
            'name': name,
            'modifiers': modifiers,
            'return_type': return_type,
            'parameters': parameters
        })
    
    def add_enum_constant(self, name, annotation=None, arguments=None):
        self.enum_constants.append({
            'name': name,
            'annotation': annotation,
            'arguments': arguments
        })
    
    def add_nested_class(self, nested_class):
        self.nested_classes.append(nested_class)

    def add_comment(self, comment):
        self.comments.append(comment)
    
    def add_annotation(self, annotation):
        self.annotations.append(annotation)
    
    def add_inheritance(self, kind, name):
        self.inheritance[kind].append(name)

    def get_dict(self):
        return {
            'name': self.name,
            'kind': self.kind,
            'is_abstract': self.is_abstract,
            'is_static': self.is_static,
            'is_final': self.is_final,
            'is_public': self.is_public,
            'is_protected': self.is_protected,
            'is_private': self.is_private,
            'is_singleton': self.is_singleton,
            'generics': self.generics,
            'methods': self.methods,
            'fields': self.fields,
            'enum_constants': self.enum_constants,
            'nested_classes': [nested_class.get_dict() for nested_class in self.nested_classes],
            'comment': self.comments,
            'annotations': self.annotations,
            'inheritance': self.inheritance
        }
    
class ClassNode:
    def __init__(self, class_details, parent=None) -> None:
        self.class_details = class_details
        self.parent = parent
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
    

def build_class_tree(classes):
    class_tree = {}
    for name, details in classes.items():
        class_tree[name] = ClassNode(details)
    
    for name, node in class_tree.items():
        for inheritance in node.class_details.inheritance['extends']:
            node.add_child(class_tree[inheritance])
            class_tree[inheritance].parent = node
        for inheritance in node.class_details.inheritance['implements']:
            node.add_child(class_tree[inheritance])
            class_tree[inheritance].parent = node
        for nested_class in node.class_details.nested_classes:
            node.add_child(class_tree[nested_class.name])
            class_tree[nested_class.name].parent = node
    
    return class_tree
    
    
def build_class_tree_dict(classes):
    class_dict = {}
    for name, details in classes.items():
        class_dict[name] = {
            "kind": details.kind,
            "is_abstract": details.is_abstract,
            "is_static": details.is_static,
            "is_final": details.is_final,
            "is_singleton": details.is_singleton,
            "generics": details.generics,
            "methods": details.methods,
            "fields": details.fields,
            "enum_constants": details.enum_constants,
            "nested_classes": [nested_class.get_dict() for nested_class in details.nested_classes],
            "comment": details.comments,
            "annotations": details.annotations,
            "inheritance": details.inheritance
        }
    
    return class_dict
    
    
