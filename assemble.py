# Assembler for digirule 2A
# Olivier Lecluse
# Licence CC CC-BY-NC-SA

class Assemble():
    def __init__(self, text):
        self.lines = self.split_lines(text+"\n")
        self.nodes = []

        self.operators_dic = {
                    "halt": { "code": 0, "operandCount": 0 },
                    "nop": { "code": 1, "operandCount": 0},
                    "speed": { "code": 2, "operandCount": 1},
                    "copylr": { "code": 3, "operandCount": 2},
                    "copyla": { "code": 4, "operandCount": 1},
                    "copyar": { "code": 5, "operandCount": 1},
                    "copyra": { "code": 6, "operandCount": 1},
                    "copyrr": { "code": 7, "operandCount": 2},
                    "addla": { "code": 8, "operandCount": 1},
                    "addra": { "code": 9, "operandCount": 1},
                    "subla": { "code": 10, "operandCount": 1},
                    "subra": { "code": 11, "operandCount": 1},
                    "andla": { "code": 12, "operandCount": 1},
                    "andra": { "code": 13, "operandCount": 1},
                    "orla": { "code": 14, "operandCount": 1},
                    "orra": { "code": 15, "operandCount": 1},
                    "xorla": { "code": 16, "operandCount": 1},
                    "xorra": { "code": 17, "operandCount": 1},
                    "decr": { "code": 18, "operandCount": 1},
                    "incr": { "code": 19, "operandCount": 1},
                    "decrjz": { "code": 20, "operandCount": 1},
                    "incrjz": { "code": 21, "operandCount": 1},
                    "shiftrl": { "code": 22, "operandCount": 1},
                    "shiftrr": { "code": 23, "operandCount": 1},
                    "cbr": { "code": 24, "operandCount": 2},
                    "sbr": { "code": 25, "operandCount": 2},
                    "bcrsc": { "code": 26, "operandCount": 2},
                    "bcrss": { "code": 27, "operandCount": 2},
                    "jump": { "code": 28, "operandCount": 1},
                    "call": { "code": 29, "operandCount": 1},
                    "retla": { "code": 30, "operandCount": 1},
                    "return": { "code": 31, "operandCount": 0},
                    "addrpc": { "code": 32, "operandCount": 1},
                    "initsp": { "code": 33, "operandCount": 0},
                    "randa": { "code": 34, "operandCount": 0},
                    "copyli": { "code": 35, "operandCount": 2},
                    "copyai": { "code": 36, "operandCount": 1},
                    "copyia": { "code": 37, "operandCount": 1},
                    "copyii": { "code": 38, "operandCount": 2},
                    "shiftar": { "code": 39, "operandCount": 0},
                    "shiftal": { "code": 40, "operandCount": 0},
                    "jumpi": { "code": 41, "operandCount": 1},
                    "calli": { "code": 42, "operandCount": 1},
                    "push": { "code": 43, "operandCount": 0},
                    "pop": { "code": 44, "operandCount": 0},
                }
        self.labelAddressByName = {}

        self.parse()

    def split_lines(self, text):
        """parses the text and returns a list of lines. A line is a list looking like this :
            ['%define', 'statusregister', '252', 8], ['copylr', '1', 'dataledregister', 10], [':loop', 18] etc..:
            le last element of a line is the line number in the original text file
            coments and empty lines are removed"""    
        def is_space(c):
            return c==" " or c=="\t"
        def is_eol(c):
            return c=="\n"
        def is_comment(c):
            return c==";" or c=="/"
        
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
                    if word : words_list.append(word)
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
            if l==0:
                return (False, "unknown keyword "+msg, l, msg)
            else:
                return (False, msg+" on line "+str(l), l)

        PC = 0
        ram = []

        keywords = dict()   # keywords dictionary (variable definitions and labels)
                            # example of entry (True, value) for a variable definition
                            #                  (False, PC) for a label - PC is the program counter value for the Jump
                            # the key is the variable or the label name

        # Premiere passe
        
        for line in self.lines:
            if PC >=252:
       	        return error("no space left in program memory", line[-1])
            if line[0] == "%define":
                # variable definition
                try:
                    if line[2][0:2]=='0b':
                        keywords[line[1]]=int(line[2],2)
                    else:
                        keywords[line[1]]=int(line[2])
                except:
                    return error("error in keyword definition", line[3])
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
                if nb_par != len(line)-2:
                    return error("bad arguments count for "+word, line[-1])
                code = self.operators_dic[word]["code"]
                # arguments handling
                ram.append(code)
                PC += 1
                for o in line[1:-1]:
                    if o.isdigit():
                        # the operand is a number
                        n = int(o)
                        if not 0<=n<256:
                            return error("too big number "+o, line[-1])
                        ram.append(n)
                    elif o[0:2]=='0b':
                        # the operand is a binary number
                        try:
                            n=int(o,2)
                            if not 0<=n<256:
                                return error("too big number "+o, line[-1])
                        except ValueError:
                            return error("bad argument type "+o, line[-1])
                    else:
                        # the argument is a variable or a label
                        if o in keywords:
                            ram.append(keywords[o])
                        else:
                            ram.append(o)
                        # unknown arguments will be processed during the second pass
                    PC += 1

        # second pass : remaining names processing

        for i,r in enumerate(ram):
            if type(r)==str:
                if r in keywords:
                    ram[i] = keywords[r]
                else:
                    return error(r,0)
        return (True, ram)
