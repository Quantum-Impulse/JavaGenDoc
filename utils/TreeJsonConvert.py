import json

# Convert tree in dictionary formant to json
def covertTreeJson(tree):
    with open('ClassTree.json', 'w') as f:
        json.dump(tree, f, indent=4)