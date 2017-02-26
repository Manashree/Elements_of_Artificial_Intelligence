import gamePlay
from copy import deepcopy
from getAllPossibleMoves import getAllPossibleMoves

colour = ""

def evaluation(board, color):
    opponentColor = gamePlay.getOpponentColor(color)
    pieceValue = 0
    kingValue = 0
    defenceValue = 0

    for piece in range(1, 33):
        xy = gamePlay.serialToGrid(piece)
        x = xy[0]
        y = xy[1]
        if board[x][y].upper() == color.upper():
            pieceValue += 1
        elif board[x][y].upper() == opponentColor.upper():
            pieceValue -= 1

        if board[x][y] == color.upper():
            kingValue += 1
        elif board[x][y] == opponentColor.upper():
            kingValue -= 1

        if board[x][y] == color and (x == 0 or y == 0 or x == 7 or y == 7):
            defenceValue += 1
        elif board[x][y] == opponentColor and (x == 0 or y == 0 or x == 7 or y == 7):
            defenceValue -= 1

    return pieceValue + defenceValue + kingValue


def nextMove(board, color, time, movesRemaining):
    global colour
    colour = color
    moves = getAllPossibleMoves(board, colour)
    values = []
    for index, move in enumerate(moves):
        values.append(minimax(board, move))
    return moves[values.index(max(values))]


def minimax(board, move, depth=4, alpha=-1, beta=99999, maximizer=True):
    global colour
    if depth == 0:
        return evaluation(board, colour)
    else:
        if maximizer:
            newBoard = deepcopy(board)
            gamePlay.doMove(newBoard, move)
            moves = getAllPossibleMoves(newBoard, gamePlay.getOpponentColor(colour))
            for m in moves:
                alpha = max(alpha, minimax(newBoard, m, depth - 1, alpha, beta, False))
                if alpha >= beta:
                    break
            return alpha
        else:
            newBoard = deepcopy(board)
            gamePlay.doMove(newBoard, move)
            moves = getAllPossibleMoves(newBoard, colour)
            for m in moves:
                beta = min(beta, minimax(newBoard, m, depth - 1, alpha, beta, True))
                if alpha >= beta:
                    break
            return beta