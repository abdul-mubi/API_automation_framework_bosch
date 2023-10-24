
import os
import glob
import logging
cur_path = os.path.dirname(__file__)
os.chdir(cur_path + "\\..\\")

func = "def step_impl"
bdd_line_no = 0
functions = []
bdd_lines = []
comment_lines = []


def split_bdd(lines, line_no):
    line = str(lines[line_no])
    keyword = ""
    while "@" in line:
        keyword += line[line.index("@")+1:line.index("('")]
        frm = line.index("('") + 2
        to = line.index("')", frm)
        keyword += ": " + line[frm:to] + " \n    "
        line_no -= 1
        line = str(lines[line_no])
    return keyword[:-5]


def split_cmnt(lines, line_no):
    text = ""
    line = lines[line_no]
    frm = line.index('"""') + 3
    line = line[frm:]
    frm = 0
    while '"""' not in line:
        text += line
        line_no += 1
        line = lines[line_no]

    to = line.index('"""')
    text += line[:to]
    return text


def print_target(lines):
    global func, bdd_lines, functions, bdd_line_no, comment_lines
    line_no = -1
    for line in lines:
        line_no += 1
        if func in line:
            bdd_line_no += 1
            functions.append(line)
            bdd_lines.append(lines[line_no-1])
            comment_lines.append(lines[line_no+1])
            logging.info(f"{str(bdd_line_no)} ) {str(split_bdd(lines, line_no-1))}")
            logging.info('\t' + split_cmnt(lines, line_no+1) + '\n\n')


for file_name in glob.glob("*.py"):
    file = open(file_name, "r")
    lines = file.readlines()
    logging.info("*" + file_name + "*" + "\n")
    print_target(lines)
