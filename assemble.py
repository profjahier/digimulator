# Assembler for digirule 2A
# Ronan Jahier
# Olivier Lécluse
# Thomas Lécluse
# Licence GNU General Public License v3.0

class Assemble:
    def __init__(self, text, inst_dic):
        self.lines = self.split_lines(text + "\n")
        self.nodes = []

        self.operators_dic = inst_dic
        self.labelAddressByName = {}

        self.parse()

    def split_lines(self, text):
        """parses the text and returns a list of lines. A line is a list looking like this :
            ['%define', 'statusregister', '252', 8], ['copylr', '1', 'dataledregister', 10], [':loop', 18] etc..:
            le last element of a line is the line number in the original text file
            coments and empty lines are removed"""

        def is_space(c):
            return c == " " or c == "\t"

        def is_eol(c):
            return c == "\n"

        def is_comment(c):
            return c == ";" or c == "/"

        comment_mode = False
        lines_list = []
        words_list = []
        word = ""
        line_number = 0

        for c in text:
            if is_eol(c):
                line_number += 1
                if word: words_list.append(word)
                if words_list:
                    words_list.append(line_number)
                    lines_list.append(words_list)
                words_list = []
                word = ""
                comment_mode = False
            elif not comment_mode:
                if is_space(c):
                    if word: words_list.append(word)
                    word = ""
                elif is_comment(c):
                    comment_mode = True
                else:
                    word += c.lower()
        return lines_list

    def parse(self):
        """converts the lines into machine code
        returns (True, list of bytes) if the compilation succeeds
                (False, error message, line of error) if it fails"""

        def error(msg, l):
            if l == 0:
                return (False, "unknown keyword " + msg, l, msg)
            else:
                return (False, msg + " on line " + str(l), l)

        PC = 0
        ram = []

        keywords = dict()  # keywords dictionary (variable definitions and labels)
        # example of entry (True, value) for a variable definition
        #                  (False, PC) for a label - PC is the program counter value for the Jump
        # the key is the variable or the label name

        # Premiere passe
        for line in self.lines:
            if PC >= 252:
                return error("no space left in program memory", line[-1])
            if line[0] == "%define":
                # variable definition
                try:
                    if line[2][0:2] == '0b':
                        keywords[line[1]] = int(line[2], 2)
                    elif line[2][0:2] == '0x':
                        keywords[line[1]] = int(line[2], 16)
                    else:
                        keywords[line[1]] = int(line[2])
                except:
                    return error("error in keyword definition", line[3])
            elif line[0] == "%data":
                # Data definitions
                keywords[line[1]] = PC
                for d in line[2:-1]:
                    try:
                        if d[0:2] == '0b':
                            code = int(d, 2)
                        elif d[0:2] == '0x':
                            code = int(d, 16)
                        else:
                            code = int(d)
                    except:
                        return error("error in data definition", line[-1])
                    ram.append(code)
                    PC += 1
            elif line[0][0] == ":":
                # label definition
                try:
                    keywords[line[0][1:]] = PC
                except:
                    return error("error in label definition", line[1])
            else:
                # command analysis
                word = line[0]
                # name checking
                if word not in self.operators_dic:
                    return error("unkwown command : " + word, line[-1])
                # number of arguments checking
                nb_par = self.operators_dic[word]["operandCount"]
                if nb_par != len(line) - 2:
                    return error("bad arguments count for " + word, line[-1])
                code = self.operators_dic[word]["code"]
                # arguments handling
                ram.append(code)
                PC += 1
                for o in line[1:-1]:
                    if o.isdigit():
                        # the operand is a number
                        n = int(o)
                        if not 0 <= n < 256:
                            return error("too big number " + o, line[-1])
                        ram.append(n)
                    elif o[0:2] == '0b':
                        # the operand is a binary number
                        try:
                            n = int(o, 2)
                            if not 0 <= n < 256:
                                return error("too big number " + o, line[-1])
                            ram.append(n)
                        except ValueError:
                            return error("bad argument type " + o, line[-1])
                    elif o[0:2] == '0x':
                        # the operand is a binary number
                        try:
                            n = int(o, 16)
                            if not 0 <= n < 256:
                                return error("too big number " + o, line[-1])
                            ram.append(n)
                        except ValueError:
                            return error("bad argument type " + o, line[-1])
                    else:
                        # the argument is an offset, a variable or a label
                        # it will be handled in the second pass
                        ram.append(o)
                        # unknown arguments will be processed during the second pass
                    PC += 1

        # second pass : remaining names processing

        for i, r in enumerate(ram):
            if type(r) == str:
                if '+' in r:
                    # offset type
                    arg1, arg2 = r.split('+')
                    try:
                        ram[i] = keywords[arg1] + int(arg2)
                    except:
                        return error(r, 0)
                elif r in keywords:
                    ram[i] = keywords[r]
                else:
                    return error(r, 0)
        return (True, ram)