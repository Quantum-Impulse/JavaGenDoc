from utils.TreeClassNode import build_class_tree_dict
from utils.JFileFinderAndParse import JavaFileParser
from utils.TreeJsonConvert import covertTreeJson



def main(root):
    parser = JavaFileParser(root)
    parser.parse_files()
    classes = parser.get_classes()

    class_tree_dict = build_class_tree_dict(classes)
    covertTreeJson(class_tree_dict)


if __name__ == '__main__':
    # path for my mac: '/Users/apple/Documents/Coding Projects/Temp Java Code/'
    # path for my windows: 
    root = '/Users/apple/Documents/Coding Projects/Temp Java Code/'
    main(root)
