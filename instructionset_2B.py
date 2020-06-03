inst_dic = {
            "halt": {"code": 0, "operandCount": 0},
            "nop": {"code": 1, "operandCount": 0},
            "speed": {"code": 2, "operandCount": 1},
            "copylr": {"code": 3, "operandCount": 2},
            "copyla": {"code": 4, "operandCount": 1},
            "copyar": {"code": 5, "operandCount": 1},
            "copyra": {"code": 6, "operandCount": 1},
            "copyrr": {"code": 7, "operandCount": 2},
            "addla": {"code": 8, "operandCount": 1},
            "addra": {"code": 9, "operandCount": 1},
            "subla": {"code": 10, "operandCount": 1},
            "subra": {"code": 11, "operandCount": 1},
            "andla": {"code": 12, "operandCount": 1},
            "andra": {"code": 13, "operandCount": 1},
            "orla": {"code": 14, "operandCount": 1},
            "orra": {"code": 15, "operandCount": 1},
            "xorla": {"code": 16, "operandCount": 1},
            "xorra": {"code": 17, "operandCount": 1},
            "decr": {"code": 18, "operandCount": 1},
            "incr": {"code": 19, "operandCount": 1},
            "decrjz": {"code": 20, "operandCount": 1},
            "incrjz": {"code": 21, "operandCount": 1},
            "shiftrl": {"code": 22, "operandCount": 1},
            "shiftrr": {"code": 23, "operandCount": 1},
            "cbr": {"code": 24, "operandCount": 2},
            "sbr": {"code": 25, "operandCount": 2},
            "bcrsc": {"code": 26, "operandCount": 2},
            "bcrss": {"code": 27, "operandCount": 2},
            "jump": {"code": 28, "operandCount": 1},
            "call": {"code": 29, "operandCount": 1},
            "return": {"code": 30, "operandCount": 0}, # for 2B 2U 
            "retla": {"code": 31, "operandCount": 1},  # RETLA and RETURN swapped
            "addrpc": {"code": 32, "operandCount": 1},
            "initsp": {"code": 33, "operandCount": 0},
            "randa": {"code": 34, "operandCount": 0},
            #
            # Unofficial instructions
            #

            # Indirect copy
            "copyli": {"code": 224, "operandCount": 2},
            "copyai": {"code": 225, "operandCount": 1},
            "copyia": {"code": 226, "operandCount": 1},
            "copyri": {"code": 227, "operandCount": 2},
            "copyir": {"code": 228, "operandCount": 2},
            "copyii": {"code": 229, "operandCount": 2},
            # accumulator shift
            "shiftar": {"code": 230, "operandCount": 0},
            "shiftal": {"code": 231, "operandCount": 0},
            # indirect jump
            "jumpi": {"code": 232, "operandCount": 1},
            "calli": {"code": 233, "operandCount": 1},
            # stack instructions
            "push": {"code": 234, "operandCount": 0},
            "pop": {"code": 235, "operandCount": 0},
            "pushr": {"code": 236, "operandCount": 1},
            "popr": {"code": 237, "operandCount": 1},
            "pushi": {"code": 238, "operandCount": 1},
            "popi": {"code": 239, "operandCount": 1},
            "head": {"code": 240, "operandCount": 0},
            "depth": {"code": 241, "operandCount": 0},
        }