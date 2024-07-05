from utils.TreeClassNode import ClassDetails, build_class_tree_dict
from utils.JFileFinderAndParse import JavaFileParser
from utils.TreeJsonConvert import covertTreeJson

def main(root_dir):
    parser = JavaFileParser(root_dir)
    parser.parse_files()
    all_classes = parser.get_classes()
    class_tree = build_class_tree_dict(all_classes)

    


if __name__ == "__main__":
    root_dir = "test"
    main(root_dir)