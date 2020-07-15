inst_dic = {
            # system control
            "halt":    {"code": 0,  "operandCount": 0},
            "nop":     {"code": 1,  "operandCount": 0},
            "speed":   {"code": 2,  "operandCount": 1},
            "initsp":  {"code": 3,  "operandCount": 0},

            # data movement
            "copyla":  {"code": 4,  "operandCount": 1},
            "copylr":  {"code": 5,  "operandCount": 2},
            "copyli":  {"code": 6,  "operandCount": 2},  # new 2U instructions

            "copyar":  {"code": 7,  "operandCount": 1},
            "copyai":  {"code": 8,  "operandCount": 1},  # new 2U instructions

            "copyra":  {"code": 9,  "operandCount": 1},
            "copyrr":  {"code": 10, "operandCount": 2},
            "copyri":  {"code": 11, "operandCount": 2},  # new 2U instructions

            "copyia":  {"code": 12, "operandCount": 1},  # new 2U instructions
            "copyir":  {"code": 13, "operandCount": 2},  # new 2U instructions
            "copyii":  {"code": 14, "operandCount": 2},  # new 2U instructions

            "swapra":  {"code": 15, "operandCount": 1},  # new 2U instructions
            "swaprr":  {"code": 16, "operandCount": 2},  # new 2U instructions

            # Arithmetic
            "addla":   {"code": 17, "operandCount": 1},
            "addra":   {"code": 18, "operandCount": 1},
            "subla":   {"code": 19, "operandCount": 1},
            "subra":   {"code": 20, "operandCount": 1},
            "mul":     {"code": 21, "operandCount": 2},  # new 2U instructions
            "div":     {"code": 22, "operandCount": 2},  # new 2U instructions

            # Logical
            "andla":   {"code": 23, "operandCount": 1},
            "andra":   {"code": 24, "operandCount": 1},
            "orla":    {"code": 25, "operandCount": 1},
            "orra":    {"code": 26, "operandCount": 1},
            "xorla":   {"code": 27, "operandCount": 1},
            "xorra":   {"code": 28, "operandCount": 1},

            # Increment, decrement
            "decr":    {"code": 29, "operandCount": 1},
            "incr":    {"code": 30, "operandCount": 1},
            "decrjz":  {"code": 31, "operandCount": 1},
            "incrjz":  {"code": 32, "operandCount": 1},

            # shift
            "shiftrl": {"code": 33, "operandCount": 1},
            "shiftrr": {"code": 34, "operandCount": 1},

            # bit manipulation
            "cbr":     {"code": 35, "operandCount": 2},
            "sbr":     {"code": 36, "operandCount": 2},
            "bcrsc":   {"code": 37, "operandCount": 2},
            "bcrss":   {"code": 38, "operandCount": 2},

            # Program comtrol
            "jump":    {"code": 39, "operandCount": 1},
            "jumpi":   {"code": 40, "operandCount": 1},  # new 2U instructions
            "call":    {"code": 41, "operandCount": 1},
            "calli":   {"code": 42, "operandCount": 1},  # new 2U instructions
            "return":  {"code": 43, "operandCount": 0},  
            "retla":   {"code": 44, "operandCount": 1},  
            "addrpc":  {"code": 45, "operandCount": 1},

            # misc
            "randa":   {"code": 46, "operandCount": 0},

            # stack instructions
            "tbr":     {"code": 233, "operandCount": 2},
            "sspush":  {"code": 234, "operandCount": 0}, # new 2B instructions
            "sspop":   {"code": 235, "operandCount": 0}, # new 2B instructions
            "sspushr": {"code": 236, "operandCount": 1}, # new 2B instructions
            "sspopr":  {"code": 237, "operandCount": 1}, # new 2B instructions
            "sspushi": {"code": 238, "operandCount": 1}, # new 2B instructions
            "sspopi":  {"code": 239, "operandCount": 1}, # new 2B instructions
            "sshead":  {"code": 240, "operandCount": 0}, # new 2B instructions
            "ssdepth": {"code": 241, "operandCount": 0}, # new 2B instructions
        }
