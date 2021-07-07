cfg = open("project.txt")
G = {}
C = {}
start = ""
terminals = []
nonterminals = []
symbols = []
error=0

def parsecfg():
    global G, start, terminals, nonterminals, symbols
    for line in cfg:
        line = " ".join(line.split())
        if line == '\n':
            break
        head = line[:line.index("->")].strip()
        prods = [l.strip().split(' ') for l in ''.join(line[line.index("->") + 2:]).split('|')]
        if not start:
            start = head + "'"
            G[start] = [[head]]
            nonterminals.append(start)
        if head not in G:
            G[head] = []
        if head not in nonterminals:
            nonterminals.append(head)
        for prod in prods:
            G[head].append(prod)
            for char in prod:
                if not char.isupper() and char not in terminals:
                    terminals.append(char)
                elif char.isupper() and char not in nonterminals:
                    nonterminals.append(char)
                    G[char] = []    
    symbols =  nonterminals+terminals
first_seen = []

def FIRST(X):
    global first_seen
    first = []
    first_seen.append(X)
    if X in terminals:  
        first.append(X)
    elif X in nonterminals:
        for prods in G[X]: 
            if prods[0] in terminals and prods[0] not in first:
                first.append(prods[0])
            else:  
                for nonterm in prods:
                    if nonterm not in first_seen:
                        for terms in FIRST(nonterm):
                            if terms not in first:
                                first.append(terms)
    first_seen.remove(X)
    return first


follow_seen = []
def FOLLOW(A):
    global follow_seen
    follow = []
    follow_seen.append(A)
    if A == start:  
        follow.append('$')
    for heads in G.keys():
        for prods in G[heads]:
            follow_head = False
            if A in prods:
                next_symbol_pos = prods.index(A) + 1
                if next_symbol_pos < len(prods):  
                    for terms in FIRST(prods[next_symbol_pos]):
                        if terms not in follow:
                            follow.append(terms)
                else:  
                    follow_head = True
                if follow_head and heads not in follow_seen:
                    for terms in FOLLOW(heads):
                        if terms not in follow:
                            follow.append(terms)
    follow_seen.remove(A)
    return follow

def closure(I):
    J = I
    while True:
        item_len = len(J) + sum(len(v) for v in J.itervalues())
        for heads in J.keys():
            for prods in J[heads]:
                dot_pos = prods.index('.')      
                if dot_pos + 1 < len(prods):
                    prod_after_dot = prods[dot_pos + 1]
                    if prod_after_dot in nonterminals:
                        for prod in G[prod_after_dot]:                   
                            item = ["."] + prod
                            if prod_after_dot not in J.keys():
                                J[prod_after_dot] = [item]
                            elif item not in J[prod_after_dot]:
                                J[prod_after_dot].append(item)
        if item_len == len(J) + sum(len(v) for v in J.itervalues()):
            return J

def GOTO(I, X):
    goto = {}
    for heads in I.keys():
        for prods in I[heads]:
            for i in range(len(prods) - 1):
                if "." == prods[i] and X == prods[i + 1]:
                    temp_prods = prods[:]
                    temp_prods[i], temp_prods[i + 1] = temp_prods[i + 1], temp_prods[i]
                    prod_closure = closure({heads: [temp_prods]})
                    for keys in prod_closure:
                        if keys not in goto.keys():
                            goto[keys] = prod_closure[keys]
                        elif prod_closure[keys] not in goto[keys]:
                            for prod in prod_closure[keys]:
                                goto[keys].append(prod)
    return goto

def items():
    global C
    i = 1
    C = {'I0': closure({start: [['.'] + G[start][0]]})}
    while True:
        item_len = len(C) + sum(len(v) for v in C.itervalues())
        for I in C.keys():
            for X in symbols:
                if GOTO(C[I], X) and GOTO(C[I], X) not in C.values():
                    C['I' + str(i)] = GOTO(C[I], X)
                    i += 1
        if item_len == len(C) + sum(len(v) for v in C.itervalues()):
            return


def ACTION(i, a):
    global error
    for heads in C['I' + str(i)]:
        for prods in C['I' + str(i)][heads]:
            for j in range(len(prods) - 1):
                if prods[j] == '.' and prods[j + 1] == a:
                    for k in range(len(C)):
                        if GOTO(C['I' + str(i)], a) == C['I' + str(k)]:
                            if a in terminals:
                                if "r" in parse_table[i][terminals.index(a)]:
                                    if error!=1:
                                        print "ERROR: Shift-Reduce Conflict at State " + str(i) + ", Symbol \'" + str(terminals.index(a))+"\'"
                                    error=1
                                    if "s"+str(k) not in parse_table[i][terminals.index(a)]:
                                        parse_table[i][terminals.index(a)] = parse_table[i][terminals.index(a)]+ "/s" + str(k)
                                    return parse_table[i][terminals.index(a)]
                                else:
                                    parse_table[i][terminals.index(a)] = "s" + str(k)
                            else:
                                parse_table[i][len(terminals) + nonterminals.index(a)] = str(k)
                            return "s" + str(k)
    for heads in C['I' + str(i)]:
        if heads != start:
            for prods in C['I' + str(i)][heads]:
                if prods[-1] == '.':
                    k = 0
                    for head in G.keys():
                        for Gprods in G[head]:
                            if head == heads and (Gprods == prods[:-1] ) and (a in terminals or a == '$'):
                                for terms in FOLLOW(heads):
                                    if terms == '$':
                                        index = len(terminals)
                                    else:
                                        index = terminals.index(terms)
                                    if "s" in parse_table[i][index]:
                                        if error!=1:
                                            print "ERROR: Shift-Reduce Conflict at State " + str(i) + ", Symbol \'" + str(terms)+"\'"
                                        error=1
                                        if "r"+str(k) not in parse_table[i][index]:
                                            parse_table[i][index] = parse_table[i][index]+ "/r" + str(k)
                                        return parse_table[i][index]
                                    elif parse_table[i][index] and parse_table[i][index] != "r" + str(k):
                                        if error!=1:
                                            print "ERROR: Reduce-Reduce Conflict at State " + str(i) + ", Symbol \'" + str(terms)+"\'"
                                        error=1
                                        if "r"+str(k) not in parse_table[i][index]:
                                                parse_table[i][index] = parse_table[i][index]+ "/r" + str(k)
                                        return parse_table[i][index]                                
                                    else:
                                        parse_table[i][index] = "r" + str(k)
                                return "r" + str(k)
                            k += 1
    if start in C['I' + str(i)] and G[start][0] + ['.'] in C['I' + str(i)][start]:
        parse_table[i][len(terminals)] = "acc"
        return "acc"
    return ""
    

def process_input():
    get_input = raw_input("\nEnter Input: ")
    to_parse = " ".join((get_input + " $").split()).split(" ")
    pointer = 0
    stack = ['0']

    print "\n+--------+----------------------------+----------------------------+----------------------------+"
    print "|{:^8}|{:^28}|{:^28}|{:^28}|".format("STEP", "STACK", "INPUT", "ACTION")
    print "+--------+----------------------------+----------------------------+----------------------------+"

    step = 1
    while True:
        curr_symbol = to_parse[pointer]
        top_stack = int(stack[-1])
        stack_content = ""
        input_content = ""

        print "|{:^8}|".format(step),
        for i in stack:
            stack_content += i
        print "{:27}|".format(stack_content),
        i = pointer
        while i < len(to_parse):
            input_content += to_parse[i]
            i += 1
        print "{:>26} | ".format(input_content),

        step += 1
        get_action = ACTION(top_stack, curr_symbol)
        if "/" in get_action:
            print "{:^26}|".format(get_action+". So conflict")
            break
        if "s" in get_action:
            print "{:^26}|".format(get_action)
            stack.append(curr_symbol)
            stack.append(get_action[1:])
            pointer += 1
        elif "r" in get_action:
            print "{:^26}|".format(get_action)
            i = 0
            for head in G.keys():
                for prods in G[head]:
                    if i == int(get_action[1:]):
                        for j in range(2 * len(prods)):
                            stack.pop()
                        state = stack[-1]
                        stack.append(head)
                        stack.append(parse_table[int(state)][len(terminals) + nonterminals.index(head)])
                    i += 1
        elif get_action == "acc":
            print "{:^26}|".format("ACCEPTED")
            break
        else:
            print "ERROR: Unrecognized symbol", curr_symbol, "|"
            break
    print "+--------+----------------------------+----------------------------+----------------------------+"

ch=1 
parsecfg()
items()
global parse_table
parse_table = [["" for c in range(len(terminals) + len(nonterminals) + 1)] for r in range(len(C))]
for i in range(len(parse_table)):       
    for j in symbols:
        ACTION(i, j)
print "PARSING TABLE:"
print "+" + "--------+" * (len(terminals) + len(nonterminals) + 1)
print "|{:^8}|".format('STATE'),
for terms in terminals:
    print "{:^7}|".format(terms),
print "{:^7}|".format("$"),
for nonterms in nonterminals:
    if nonterms == start:
        continue
    print "{:^7}|".format(nonterms),
print "\n+" + "--------+" * (len(terminals) + len(nonterminals) + 1)
for i in range(len(parse_table)):
    print "|{:^8}|".format(i),
    for j in range(len(parse_table[i]) - 1):
        print "{:^7}|".format(parse_table[i][j]),
    print
print "+" + "--------+" * (len(terminals) + len(nonterminals) + 1)
while(ch):
    process_input()
    choice=raw_input("Do you wish to continue?(Y/N): ")
    if(choice=="N" or choice=="n"):
        ch=0