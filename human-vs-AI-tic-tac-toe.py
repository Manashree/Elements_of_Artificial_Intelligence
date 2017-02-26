import random

# Randomly choose the first player

def first_player():
    if random.randint(0, 1) == 0:
        print "Computer goes first"
        return 'computer'
    else:
        print "Human goes first"
        return 'human'


#AI Move 1 :: If center block is empty return co-ordinates. Else check for an empty edge.

def first_move():
    if checkIfEmpty(1,1):
        return [1,1]
    else:
        for i in corners:
            a,b = (int(x) for x in i)
            if checkIfEmpty(a,b):
                return list(i)

#Input: Co-ordinates of cell
#Output: Boolean value indicating "True" if empty and "False" otherwise
#Function: Checks if a cell is empty or not

def checkIfEmpty(i,j):
    if board[i][j] == " ":
        return True
    else:
        return False

#Returns a dictionary object for a paticular set of co-ordinates alongwith the status of the cell

def set_dict(state,x,y):
    return {'state': state, 'x-co-ordinate':x,'y-co-ordinate':y}

#Input: String to compare with if a row if occupied. String is required to see if cell is occupied with the calling player's symbol or with symbol or other player.
#Output: Returns a dictionary object with the status as True, and coordinates if cell is empty
#        If row is occupied,sends status as False with dummy co-ordinates

def check_horizontally(strComp):
    #print "check horizontally %s" %strComp
    dict_variable={'state': False, 'x-co-ordinate':0,'y-co-ordinate':0}
    for i in rangeof3:
        if board[i][0]==board[i][1]== strComp !=" " and board[i][2]==" ":
            return set_dict(True,2,i)
        if board[i][1]==board[i][2]==strComp!=" " and board[i][0]==" ":
            return set_dict(True,0,i)
        if board[i][0]==board[i][2]==strComp!=" " and board[i][1]==" ":
           return set_dict(True,1,i)

    return dict_variable

#Input: String to compare with if a column if occupied. String is required to see if cell is occupied with the calling player's symbol or with symbol or other player.
#Output: Returns a dictionary object with the status as True, and coordinates if cell is empty
#        If column is occupied,sends status as False with dummy co-ordinates

def check_vertically(strComp):
    #print "check vertically %s" %strComp
    dict_variable={'state': False, 'x-co-ordinate':0,'y-co-ordinate':0}
    for j in rangeof3:
        if board[0][j]==board[1][j]==strComp!=" " and board[2][j]==" ":
            return set_dict(True,j,2)
        if board[2][j]==board[1][j]==strComp!=" " and board[0][j]==" ":
           return set_dict(True,j,0)
        if board[2][j]==board[0][j]==strComp!=" " and board[1][j]==" ":
            return set_dict(True,j,1)
    return dict_variable

#Input: String to compare with if a diagonal if occupied. String is required to see if cell is occupied with the calling player's symbol or with symbol or other player.
#Output: Returns a dictionary object with the status as True, and coordinates if cell is empty
#        If diagonal is occupied,sends status as False with dummy co-ordinates

def check_diagonally(strComp):
    #print "check diagonally %s" %strComp
    dict_variable={'state': False, 'x-co-ordinate':0,'y-co-ordinate':0}
    if board[0][0] == board[1][1]==strComp != " " and board[2][2] == " ":
        return set_dict(True,2,2)
    if board[2][2] == board[1][1]==strComp != " " and board[0][0] == " ":
        return set_dict(True,0,0)
    if board[2][2] == board[0][0]==strComp != " " and board[1][1] == " ":
        return set_dict(True,1,1)
    if board[0][2] == board[1][1]==strComp != " " and board[2][0] == " ":
        return set_dict(True,0,2)
    if board[0][2] == board[2][0]==strComp != " " and board[1][1] == " ":
        return set_dict(True,1,1)
    if board[1][1] == board[2][0]==strComp != " " and board[0][2] == " ":
        return set_dict(True,2,0)
    return dict_variable

#Function: Checks randomly for an empty block.
#Output: Returns co-ordinates of an empty cell if present with status as True
#        If no cell is empty returns status as False

def check_randomly():
     #print "check randomly %s" %strComp
    dict_variable={'state': False, 'x-co-ordinate':0,'y-co-ordinate':0}
    for i in rangeof3:
        for j in rangeof3:
            if board[i][j]==" ":
                return set_dict(True,j,i)
    return dict_variable

#Function: Checks all corner cell for an empty block.
#Output: Returns co-ordinates of an empty cell if present with status as True
#        If no cell is empty returns status as False

def check_fork(strComp):
    dict_variable={'state': False, 'x-co-ordinate':0,'y-co-ordinate':0}
    for i in corners:
        a,b = (int(x) for x in i)
        if checkIfEmpty(a,b):
            return set_dict(True,b,a)
    return dict_variable


#Function: Takes input from human player and depending on position selected return the co-ordinates to calling function

def human_player():
    print "Please select position by typing in a number between 1 and 9. Use the below figure for reference.."
    print "7|8|9"
    print "4|5|6"
    print "1|2|3"
    print

    try:
        pos = input("Select: ")
        if pos <=9 and pos >=1:
            Y = pos/3
            X = pos%3
            if X != 0:
                X -=1
            else:
                 X = 2
                 Y -=1
        return [X,Y]
    except:
        print "You need to add a numeric value"

#Input: The current symbol or "turn" variable which helps in deciding if the row is occupied with self's symbol or not
#Function: Plays a move with priority to win followed by block followed by trying to occupy corners and lastly tries to occupy central edges
#Output: Returns a valid set of co-ordinates

def ai_player(turn):
    pos_fixed=False
    global Move1
    if Move1:
        #print "Computer starts"
        first_coords = first_move()
        X=first_coords[0]
        Y=first_coords[1]
        Move1=False
        pos_fixed=True
    else:
        local_dict_state= {'state': False, 'x-co-ordinate':0,'y-co-ordinate':0}
        checkTowin=True
        #print "checktowin %s" %(checkTowin)
        while not pos_fixed:
            if checkTowin:
                strComp=turn
                #print "check to win %s" %strComp
                local_dict_state = check_horizontally(strComp);
                if local_dict_state['state']:
                    pos_fixed= local_dict_state['state']
                    break

                local_dict_state = check_vertically(strComp);
                if local_dict_state['state']:
                    pos_fixed= local_dict_state['state']
                    break

                local_dict_state = check_diagonally(strComp);
                if local_dict_state['state']:
                    pos_fixed= local_dict_state['state']
                    break

                checkTowin=False
            else:
                if turn == "X":
                    strComp = "O"
                else:
                    strComp = "X"
                #print "check to block %s" %strComp

                local_dict_state = check_horizontally(strComp);
                if local_dict_state['state']:
                    pos_fixed= local_dict_state['state']
                    break

                local_dict_state = check_vertically(strComp);
                if local_dict_state['state']:
                    pos_fixed= local_dict_state['state']
                    break

                local_dict_state = check_diagonally(strComp);
                if local_dict_state['state']:
                    pos_fixed= local_dict_state['state']
                    break

                local_dict_state = check_fork(strComp);
                if local_dict_state['state']:
                    pos_fixed= local_dict_state['state']
                    break

                local_dict_state = check_randomly();
                if local_dict_state['state']:
                    pos_fixed= local_dict_state['state']
                    break
                checkTowin= True
        X=local_dict_state['x-co-ordinate']
        Y=local_dict_state['y-co-ordinate']

    return [X,Y]

#Prints the board
#Original Code
def print_board():
    for i in range(0,3):
        for j in range(0,3):
            print board[2-i][j],
            if j != 2:
                print "|",
        print ""


#Checks if the game is over.
#Output: Printd the board and Returns true if game is over else returns False
#Original code with print statements edited
def check_done():
    global player_curr
    for i in range(0,3):
        if board[i][0] == board[i][1] == board[i][2] != " " or board[0][i] == board[1][i] == board[2][i] != " ":
            print player_curr, " won!!!"
            print_board()
            return True

        elif board[0][0] == board[1][1] == board[2][2] != " " or board[0][2] == board[1][1] == board[2][0] != " ":
            print player_curr, " won!!!"
            print_board()
            return True

        elif " " not in board[0] and " " not in board[1] and " " not in board[2]:
            print "Match drawn"
            print_board()
            return True

    return False


#Variable Initializations
Move1 = True
turn="X"
done = False
board = [[" "," "," "],
       [" "," "," "],
       [" "," "," "]]
rangeof3 = range(0,3)
corners = [[0,0],[0,2],[2,0],[2,2]]
player_curr= first_player()

#Function: While loop switches between human and computer player until game is over and only accepts valid inputs from user.
#Original code but edited to include randomized first player
while done != True:
    print_board()
    curr_coords=[]
    print player_curr, " player's move with symbol: %s" %turn
    print

    moved = False
    while moved != True:
        if player_curr == "human":
            curr_coords=human_player()
        else:
            curr_coords=ai_player(turn)

        X=curr_coords[0]
        Y=curr_coords[1]

        if board[Y][X] == " ":
            board[Y][X] = turn
            moved = True
            done = check_done()

            if done == False:
                if turn == "X":
                    turn = "O"
                else:
                    turn = "X"

                if player_curr=="computer":
                    player_curr="human"
                else:
                    player_curr="computer"
        else:
            print "Please enter a valid move in an empty cell"
