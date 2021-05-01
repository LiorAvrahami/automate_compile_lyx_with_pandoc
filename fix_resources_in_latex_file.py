import re

look_for = re.escape("\\includegraphics{") + \
           "(" + \
           re.escape("\\string\"") + \
           ")(" + \
           ".*?" + \
           ")(" + \
           re.escape("\\string\".eps") + \
           ")" + \
           re.escape("}")\

def fix_resources_in_latex_file(target_latex_file):

    with open(target_latex_file, "r") as f:
        file_text = f.read()

    while True:
        match = re.search(look_for, file_text)
        if match is None:
            break
        resource_name = match.group(2)
        file_text = file_text[:match.start(1)] + resource_name + file_text[match.end(3):]

    with open(target_latex_file, "w+") as f:
        f.write(file_text)