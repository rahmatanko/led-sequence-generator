import pandas
from sympy.logic.boolalg import SOPform, POSform
import re
from itertools import permutations

inputs = ["x", "y", "A", "B", "C", "D"]
nexts = ["*x", "*y", "*A", "*B", "*C", "*D"]

#Example sequence
# 4,2,3,2,0,-,4,2,3,5,2,-

# Use the codes corresponding the symbols according to the 5x3 display adapter (just here, i am using the regular expected codes)
codes = {
    '4': '0100',
    '2': '0010',
    '3': '0011',
    '0': '0000',
    '5': '0101',
    '-': '1010'
}

# Make a dictionary of the positions of each symbol in your sequence
positions = {
    '4': [0, 6],
    '2': [1, 3, 7, 10],
    '3': [2, 8],
    '0': [4],
    '-': [5, 11],
    '5': [9]
}


def build(bits):
    sequence = ['' for i in range(12)]  # Changed from 18 to 12 based on positions

    for symbol, pos in positions.items():
        for i in range(len(pos)):
            sequence[pos[i]] = format(bits[symbol][i], "02b") + codes[symbol]

    return sequence


def fillData(sequence):
    data = {'digit': []}

    for l in inputs + nexts:
        data[l] = []

    for l in inputs:
        data[f"J{l}"] = []
        data[f"K{l}"] = []

    for i in range(64):
        code = format(i, "06b")
        # Check if code exists in sequence (compare full 6-bit code)
        seq_code = next((s for s in sequence if s == code), None)
        data['digit'].append(next((key for key, value in codes.items() if value == code[2:] and seq_code is not None), '~~'))

        for l in data:
            if l != 'digit':
                if l in inputs:
                    data[l].append(code[inputs.index(l)])
                else:
                    if seq_code is None:
                        data[l].append('X')
                    else:
                        n = sequence.index(seq_code)
                        next_index = (n + 1) % len(sequence)  # Handle wrap-around

                        if l in nexts:
                            data[l].append(sequence[next_index][nexts.index(l)])
                        else:
                            j, k = '', ''
                            current_state = sequence[n][inputs.index(l[1])]
                            next_state = sequence[next_index][inputs.index(l[1])]
                            if current_state == '0' and next_state == '0':
                                j, k = ['0', 'X']
                            elif current_state == '0' and next_state == '1':
                                j, k = ['1', 'X']
                            elif current_state == '1' and next_state == '0':
                                j, k = ['X', '1']
                            elif current_state == '1' and next_state == '1':
                                j, k = ['X', '0']

                            if 'J' in l:
                                data[l].append(j)
                            else:
                                data[l].append(k)

    return data


def truthTable(data):
    df = pandas.DataFrame(data)
    df.to_excel('sample.xlsx', index=False)  # Set index=False to exclude row numbers


memory = {}  # Moved memo inside functions to avoid global state issues


def termCost(term, mode):
    memo = {}
    if term in memo:
        return 0

    if term in memory:
        return memory[term]

    size = len(re.findall(r'[A-Dxy]', term))

    if size == 1:
        memo[term] = 0
        memory[term] = 0
        return 0
    else:
        limit = 3 if mode == "NOR" else 2 if mode == "POS" else 4
        extra = size // limit if size > limit else 0
        memo[term] = size + extra
        memory[term] = size + extra
        return size + extra


def expCost(expression, mode):
    memo = {}
    if expression in memo:
        return 0
    if expression in memory:
        return memory[expression]

    # If we only have one term
    if "(" not in expression:
        size = len(re.findall(r'[A-Dxy]', expression))

        # if we only have one literal
        if size == 1:
            memo[expression] = 0
            memory[expression] = 0
            return 0

        else:
            limit = 3 if mode == "NOR" else 2 if "|" in expression else 4
            extra = size // limit if size > limit else 0
            memo[expression] = size + extra
            memory[expression] = size + extra
            return size + extra

    # we have more than 1 term
    terms = expression.split(" | " if mode in ["SOP", "NAND"] else " & ")
    limit = 2 if mode == "SOP" else 3 if mode == "NOR" else 4
    size = len(terms)
    extra = size // limit if size > limit else 0

    # add the no of terms and potential extra gates to the cost
    cost = size + extra

    # add the cost of each term
    for t in terms:
        cost += termCost(t, mode)

    memo[expression] = cost
    memory[expression] = cost
    return cost


def jkExps(data):
    totalCost = {"SOP": 0, "POS": 0}
    for flop in data:
        if 'J' not in flop and 'K' not in flop:
            continue

        print(flop.center(100, '-'))

        minterms, dontcares = [], []
        for t in range(64):
            if data[flop][t] == '1':
                minterms.append(t)
            elif data[flop][t] == 'X':
                dontcares.append(t)

        sop = str(SOPform(inputs, minterms, dontcares))
        sopCost = expCost(sop, "SOP")
        print(f"SOP: {sop}".ljust(60) + f"Cost: {sopCost}")

        pos = str(POSform(inputs, minterms, dontcares))
        posCost = expCost(pos, "POS")
        print(f"POS: {pos}".ljust(60) + f"Cost: {posCost}")

        print(("-"*100) + '\n')
        totalCost["POS"] += posCost
        totalCost["SOP"] += sopCost

    print(" TOTAL COSTS ".center(50, "-"))
    print(f"SOP: {totalCost['SOP']}")  # Fixed quotes here
    print(f"POS: {totalCost['POS']}")  # Fixed quotes here


def findCost(data):
    pos, sop = 0, 0
    for flop in data:
        if 'J' not in flop and 'K' not in flop:
            continue

        minterms, dontcares = [], []
        for t in range(64):
            if data[flop][t] == '1':
                minterms.append(t)
            elif data[flop][t] == 'X':
                dontcares.append(t)

        pos += expCost(str(POSform(inputs, minterms, dontcares)), "POS")
        sop += expCost(str(SOPform(inputs, minterms, dontcares)), "SOP")

    return (pos + sop) / 2


if __name__ == '__main__':
    bits = {}

    # initialize bits
    for symbol in codes:
        bits[symbol] = tuple(range(len(positions[symbol])))

    bestcost = float('inf')  # Better way to initialize
    bestinitial = float('inf')

    # find the optimal solution
    original = tuple(range(4))
    for symbol in codes:
        size = len(positions[symbol])
        # find the best front bits for that number
        bestoption = original[:size]

        # explore the options
        for option in permutations(original, size):
            memory = {}  # Reset memory for each permutation
            bits[symbol] = option
            sequence = build(bits)
            data = fillData(sequence)
            cost = findCost(data)
            if cost < bestcost:
                bestcost = cost
                bestoption = option
                bestinitial = sequence[0].count('1')

            elif cost == bestcost and sequence[0].count('1') < bestinitial:
                bestoption = option
                bestinitial = sequence[0].count('1')

        bits[symbol] = bestoption

    sequence = build(bits)
    data = fillData(sequence)
    truthTable(data)
    jkExps(data)

    print(f"INITIAL STATE: {sequence[0]}")
