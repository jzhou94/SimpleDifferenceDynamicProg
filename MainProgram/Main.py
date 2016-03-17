#!/usr/bin/env python3
# Joe Zhou
# jzhou94@bu.edu
# CS330 HW5
# simpDiff.py
# Utilities

import configparser, sys

def file2string(file):
    "Makes a string consisting of the conntent of the file."
    
    try: 
        fh = open(file)
    except IOError as detail:
        raise Exception("Could not open "+file, detail)
    out = fh.read()
    fh.close()
    return out

# Classes

class Action:
    
    def __init__ (self, name, place, size, content):
        if not ("DEL" == name or "ADD" == name):
            raise Exception("Invalid action name.")
        if ("ADD" == name) and len(content) != size:            
            raise Exception("Action size "+str(size)+" does not match content {"+content+"}")
        self.name = name
        self.place = place
        self.size = size
        self.content = content
                        
    def __str__ (self):
        if "ADD" == self.name:
            contentStr = ' {'+self.content+'}'
        else:
            contentStr = self.content
        return self.name+' '+str(self.place)+' '+str(self.size)+contentStr+'\n'
        
# Functions

def actions2file(actions,file):
    try:
        fh = open(file, "w")
    except IOError as detail:
        raise Exception("Could not open "+file, detail)
    for action in actions:
        fh.write (str(action))
    fh.close()

# My functions start here, rest were given by in class by Professor Gacs of Boston University

def maxtrixInitiate(s1, s2):
    # Creates matrix of right size
    # Generates corresponding characters in s1 and s2 for each element of matrix
    
    matrix = [[0] * (len(s2) + 1) for m in range(len(s1) + 1)]
    matrix[0][0] = ['gap', 'gap', 0, 0, 0]
    for x in range(1, len(s1) + 1):
        matrix[x][0] = [s1[x-1], 'gap', None, x, 0]
        for y in range(1, len(s2) + 1):
            matrix[0][y] = ['gap', s2[y-1], None, 0, y]
            matrix[x][y] = [s1[x-1], s2[y-1], None, x, y]
    a = len(s1)
    b = len(s2)
    grid = gridGenerate(matrix, a, b)  # Generates rest of items in lists for
                                        # each element of the matrix
    actionList = []
    List = actionGenerate(grid[0], a, b, actionList, s2, a-1) # Creates actions from matrix
    actionList = List[3]
    actionList = listConcatenate(actionList, 0)  # Concatenates list to create min number of operations
    return actionList


def gridGenerate(matrix, x, y):
    # Replaces elements in matrix with lists that denote most optimal sequence alignment
    # gap = 1, match = 0, no match = inf
    
    if matrix[x][y][2] == None:  # Checks to see if element doesn't already contain penalty information
        
        diagPath = (matrix, None, None) # Initiates possible path coming from diagonal
        downPath = (matrix, None, None) # Initiates possible path coming from below
        leftPath = (matrix, None, None) # Initiates possible path coming from the left
        
        if x > 0:
            downPath = (matrix, x - 1, y)  # Path from below exists
        if y > 0:
            leftPath = (matrix, x, y - 1)  # Path from left exists
        if x > 0 and y > 0:
            diagPath = (matrix, x - 1, y - 1)  # Diagonal path exists

        # Sequence alignment algorithm to find most optimal sequence alignment
        
        if not diagPath[1] == None: # All 3 paths exists, find min penalty between the 3 paths
            # Recursive calls to generate lists for each element of the matrix that
            #  has a path to the current element of the matrix
            gridGenerate(diagPath[0], diagPath[1], diagPath[2])
            gridGenerate(downPath[0], downPath[1], downPath[2])
            gridGenerate(leftPath[0], leftPath[1], leftPath[2])
            # Calculates min penalty for each path
            diagPenalty = 0
            if not matrix[x][y][0] == matrix[x][y][1]:
                diagPenalty = float('inf')
            diagPenalty = diagPenalty + matrix[x-1][y-1][2]
            downPenalty = matrix[x-1][y][2] + 1
            leftPenalty = matrix[x][y-1][2] + 1

            # Compare penalties
            if diagPenalty < downPenalty and diagPenalty < leftPenalty:
                matrix[x][y][2] = diagPenalty
                matrix[x][y][3] = x - 1
                matrix[x][y][4] = y - 1
                return diagPath
            elif downPenalty < leftPenalty:
                matrix[x][y][2] = downPenalty
                matrix[x][y][3] = x - 1
                matrix[x][y][4] = y
                return downPath
            else:
                matrix[x][y][2] = leftPenalty
                matrix[x][y][3] = x
                matrix[x][y][4] = y - 1
                return leftPath
                
        elif not downPath[1] == None:  # Only path from below exists
            gridGenerate(downPath[0], downPath[1], downPath[2])
            matrix[x][y][2] = matrix[x-1][y][2] + 1
            matrix[x][y][3] = x - 1
            matrix[x][y][4] = y
        else:                          # Only path from left exists
            gridGenerate(leftPath[0], leftPath[1], leftPath[2])
            matrix[x][y][2] = matrix[x][y-1][2] + 1
            matrix[x][y][3] = x
            matrix[x][y][4] = y - 1
    else:
        return (matrix, x, y)

def actionGenerate(matrix, x, y, actionList, s2, position):
    # Generates list of actions (ADD, DEL, or nothing) by looking at optimal sequence alignment
    # Uses position to determine where in string one the action occurs
    
    minPathX = matrix[x][y][3]  # x coordinate of min path element
    minPathY = matrix[x][y][4]  # y coordinate of min path element
    
    if x == 0 and y == 0:  # Reached beginning of matrix, no more paths exist
        return (matrix, x, y, actionList, s2)
    
    else:  # Recursively travels through matrix down min paths to find actions
        if x > minPathX and y > minPathY:
            # Diagonal path generates no actions
            return actionGenerate(matrix, x-1, y-1, actionList, s2, position-1)
        
        elif x > minPathX:
            # path from below generates DEL action of 1 character
            actionList = [Action('DEL', position, 1, '')] + actionList
            return actionGenerate(matrix, x-1, y, actionList, s2, position-1)
        
        else:
            # path from left generates ADD action of 1 character
            actionList = [Action('ADD', position+1, 1, str(s2[y-1]))] + actionList
            return actionGenerate(matrix, x, y-1, actionList, s2, position)

def listConcatenate(actionList, position):
    # Concatenates list of actions (Since the list only generates ADD and DEL
    # actions of size 1)
    
    newList = []
    
    if position == len(actionList)-1:  # Final action in list, list is concatenated
        return actionList
    
    else:

        # Concatenates actions that matches in position and size with name ADD
        if actionList[position].name == 'ADD' and actionList[position+1].name == 'ADD'\
           and actionList[position].place == actionList[position+1].place:
            newElement = [Action('ADD', actionList[position].place, actionList[position].size+\
                                actionList[position+1].size, (actionList[position].content)+\
                                actionList[position+1].content)]
            newList = actionList[0:position] + newElement + actionList[position+2:]
            return listConcatenate(newList, position)

        # Concatenates actions that matches in position and size with name DEL
        elif actionList[position].name == 'DEL' and actionList[position+1].name == 'DEL'\
        and actionList[position+1].place == actionList[position].place + actionList[position].size:
            newElement = [Action('DEL', actionList[position].place, actionList[position].size+\
                                 actionList[position+1].size, '')]
            newList = actionList[0:position] + newElement + actionList[position+2:]
            return listConcatenate(newList, position)
        
        else:   # Actions don't match, cannot be concatenated
            return listConcatenate(actionList, position+1)

def ListPrint(List):  # Prints lists
    
    for x in range (0, len(List)):
        print(List[x])

def main():
    
    # Read the configuration    
    config = configparser.ConfigParser()
    config.read("config.ini")
    cfg = config["DEFAULT"]

    sandboxDir = cfg["sandbox folder"]
    inFile1 = sandboxDir+"/"+cfg["input file 1"]
    inFile2 = sandboxDir+"/"+cfg["input file 2"]
    actionFile = sandboxDir+"/"+cfg["action file"]

    # Read the input
    s1 = file2string(inFile1)
    s2 = file2string(inFile2)
    # sys.stderr.write("Files read\n")
    
    # The above codes in main where also given by Professor Gacs of Boston University
    
    actions = maxtrixInitiate('name', 'mean')
    
    # Output the result
    
    actions2file(actions, actionFile)

# The executed part

if __name__ == "__main__":
    main()

