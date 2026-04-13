# levels.py

# Legend:
# '#' = Wall (-1)
# ' ' = Empty (0)
# '.' = Goal (1)
# '$' = Box (2)
# '@' = Player (3)
# '*' = Box on Goal (4)
# '+' = Player on Goal (5)

LEVELS = [
    [
        "  ###  ",
        "  #.#  ",
        "  # #  ",
        "###$###",
        "#.$@$.#",
        "###$###",
        "  # #  ",
        "  #.#  ",
        "  ###  "
    ],
    [
        "#######",
        "#     #",
        "# #.# #",
        "#  $  #",
        "# $.$ #",
        "#  $  #",
        "# .#. #",
        "#  @  #",
        "#######"
    ],
    [
        "  ####  ",
        "###  #  ",
        "#    #  ",
        "# $  ###",
        "###@$  #",
        "  #.#  #",
        "  #..  #",
        "  ######"
    ],
    [
         "####",
         "# .#",
         "#  ###",
         "#*@  #",
         "#  $ #",
         "#  ###",
         "####"
    ]
]

def load_level(level_index):
    if level_index < 0 or level_index >= len(LEVELS):
        return None
    
    raw = LEVELS[level_index]
    max_len = max(len(r) for r in raw) if raw else 0
    padded_raw = [r.ljust(max_len, ' ') for r in raw]
    
    mapping = {
        '#': -1,
        ' ': 0,
        '.': 1,
        '$': 2,
        '@': 3,
        '*': 4,
        '+': 5
    }
    
    matrix = []
    for row in padded_raw:
        matrix_row = []
        for char in row:
            matrix_row.append(mapping.get(char, 0))
        matrix.append(matrix_row)
        
    return matrix

def count_levels():
    return len(LEVELS)
