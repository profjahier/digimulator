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
            "comout": {"code": 192, "operandCount": 0},
            "comin": {"code": 193, "operandCount": 0},
            "comrdy": {"code": 194, "operandCount": 0},
        }