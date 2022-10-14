from suffix_tree import Tree
import json

"""
Sovler for https://api.razzlepuzzles.com/wordsearch
"""

class WordGame:
    DIRECTIONS = {
        "H": ("E", "W"),
        "V": ("S", "N"),
        "DL": ("SE", "NW"),
        "DT": ("SE", "NW"),
        "DTB": ("SW", "NE"),
        "DR": ("SW", "NE")
    }

    def __init__(self, board, words):
        self.words = words
        self.board_width = len(board[0])
        self.board_height = len(board)
        self.puzzle_rep = self._build_puzzle_rep(board)
        self.board_tree = Tree(self.puzzle_rep)

    def _build_puzzle_rep(self, board):
        horizontal = {("H", i): word for i, word in enumerate(board)}
        vertical = {("V", i): "".join(word[i] for word in board) for i in range(self.board_width)}
        dl = {("DL", i): "".join(word[j] for j, word in enumerate(board[i:])) for i in range(self.board_height)}
        dt = {("DT", i): "".join(word[i + j] for j, word in enumerate(board[:self.board_width - i])) for i in range(1, self.board_width)}
        dtb = {("DTB", i): "".join(word[i - j] for j, word in enumerate(board[:i + 1])) for i in range(1, self.board_width)}
        dr = {("DR", i): "".join(word[-(j + 1)] for j, word in enumerate(board[i:])) for i in range(1, self.board_height)}

        puzzle_rep = horizontal.copy()
        puzzle_rep.update(vertical)
        puzzle_rep.update(dl)
        puzzle_rep.update(dt)
        puzzle_rep.update(dtb)
        puzzle_rep.update(dr)
        return puzzle_rep

    def find_word(self, word):
        rev = 0
        if not self.board_tree.find(word):
            rev = 1
            word = word[::-1]
        if not self.board_tree.find(word):
            return None

        line, path = self.board_tree.find_all(word)[0]
        wpos = len(self.puzzle_rep[line]) - len(path) + 1
        if rev:
            wpos += len(word) - 1

        line_type = line[0]
        pos = self._linepos_to_xy(line, wpos)
        direction = WordGame.DIRECTIONS[line_type][rev]
        return pos, direction

    def _linepos_to_xy(self, line, pos):
        linepos_to_xy = {
            "H":    lambda l, p: (p, l[1]),
            "V":    lambda l, p: (l[1], p),
            "DL":   lambda l, p: (p, l[1] + p),
            "DT":   lambda l, p: (l[1] + p, p),
            "DTB":  lambda l, p: (l[1] - p, p),
            "DR":   lambda l, p: (self.board_width - p - 1, l[1] + p)
        }

        return linepos_to_xy[line[0]](line, pos)

    def solve(self):
        return {search_word: self.find_word(search_word) for search_word in self.words}

    def create_move_json(self):
        def get_end_coord(w, s):
            (x, y), d = s
            if "N" in d:
                y -= len(w)
            elif "S" in d:
                y += len(w)
            if "E" in d:
                x += len(w)
            elif "W" in d:
                x -= len(w)

            return [x, y]
        return json.dumps([{"word": word, "from": list(sol[0]), "to": get_end_coord(word, sol)} for word, sol in self.solve().items()])

    @classmethod
    def fromJSON(cls, json_str):
        data = json.loads(json_str)

        board = ["".join(row) for row in data["grid"]]
        words = data["words"]

        return cls(board, words)


if __name__ == "__main__":
    while True:
        json_str = input("Enter JSON: ")

        if json_str == "":
            break

        game = WordGame.fromJSON(json_str)
        print(*game.solve().items(), sep="\n")
        print(game.create_move_json())

