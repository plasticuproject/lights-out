"""lights_out.py"""
import socketserver
import socket
import random


def generate_random_board(n: int) -> list[int]:
    """
    Generate a random n x n Lights Out board.

    Args:
        n (int): The size of the board (n x n).

    Returns:
        list[int]: A list representing the board, where each element
                     is either 0 (off) or 1 (on).
    """
    board = [random.randint(0, 1) for _ in range(n * n)]
    return board


def create_vector_representations(n: int) -> list[list[int]]:
    """
    Create vector representations for each position on the n x n board.

    Args:
        n (int): The size of the board (n x n).

    Returns:
        list[list[int]]: A list of vectors representing the effect of
                           toggling each light.
    """
    vectors = []
    for i in range(n * n):
        vector = [0] * (n * n)
        vector[i] = 1
        if i % n != 0:
            vector[i - 1] = 1  # left
        if i % n != n - 1:
            vector[i + 1] = 1  # right
        if i >= n:
            vector[i - n] = 1  # up
        if i < n * (n - 1):
            vector[i + n] = 1  # down
        vectors.append(vector)
    return vectors


def create_augmented_matrix(vectors: list[list[int]],
                            board: list[int]) -> list[list[int]]:
    """
    Create an augmented matrix from the vectors and board state.

    Args:
        vectors (list[list[int]]): The vector representations.
        board (list[int]): The current state of the board.

    Returns:
        list[list[int]]: The augmented matrix.
    """
    matrix = [vec + [board[i]] for i, vec in enumerate(vectors)]
    return matrix


def print_board(board: list[int], n: int) -> str:
    """
    Generate a string representation of the n x n board.

    Args:
        board (list[int]): The board state.
        n (int): The size of the board (n x n).

    Returns:
        str: The string representation of the board.
    """
    board_string = ""
    for i in range(n):
        row = ""
        for j in range(n):
            row += "#" if board[i * n + j] else "."
        board_string += row + "\n"
    return board_string


def gauss_jordan_elimination(matrix: list[list[int]]) -> list[list[int]]:
    """
    Perform Gauss-Jordan elimination on the given matrix to produce its
    Reduced Row Echelon Form (RREF).

    Args:
        matrix (list[list[int]]): The matrix to be reduced.

    Returns:
        list[list[int]]: The matrix in RREF.
    """
    rows, cols = len(matrix), len(matrix[0])
    r = 0
    for c in range(cols - 1):
        if r >= rows:
            break
        pivot = None
        for i in range(r, rows):
            if matrix[i][c] == 1:
                pivot = i
                break
        if pivot is None:
            continue
        if r != pivot:
            matrix[r], matrix[pivot] = matrix[pivot], matrix[r]
        for i in range(rows):
            if i != r and matrix[i][c] == 1:
                for j in range(cols):
                    matrix[i][j] ^= matrix[r][j]
        r += 1
    return matrix


def is_solvable(matrix: list[list[int]]) -> bool:
    """
    Check if the given augmented matrix represents a solvable system.

    Args:
        matrix (list[list[int]]): The augmented matrix.

    Returns:
        bool: True if the system is solvable, False otherwise.
    """
    rref = gauss_jordan_elimination(matrix)
    for row in rref:
        if row[-1] == 1 and all(val == 0 for val in row[:-1]):
            return False
    return True


def get_solution(board: list[int], n: int) -> list[int] | None:
    """
    Get a solution for the Lights Out board if it exists.

    Args:
        board (list[int]): The current state of the board.
        n (int): The size of the board (n x n).

    Returns:
        list[int] | None: A list representing the solution, or None
                            if no solution exists.
    """
    vectors = create_vector_representations(n)
    matrix = create_augmented_matrix(vectors, board)
    if not is_solvable(matrix):
        return None
    rref_matrix = gauss_jordan_elimination(matrix)
    # DEBUG
    # x = [row[-1] for row in rref_matrix[:n * n]]
    # xx = ""
    # for i in x:
    #     xx += "#" if i else "."
    # print(xx)
    # END DEBUG
    return [row[-1] for row in rref_matrix[:n * n]]


def check_solution(board: list[int], solution: list[int], n: int) -> bool:
    """
    Check if the given solution solves the Lights Out board.

    Args:
        board (list[int]): The current state of the board.
        solution (list[int]): The proposed solution.
        n (int): The size of the board (n x n).

    Returns:
        bool: True if the solution is correct, False otherwise.
    """
    for i in range(n * n):
        if solution[i] == 1:
            board[i] ^= 1
            if i % n != 0:
                board[i - 1] ^= 1  # left
            if i % n != n - 1:
                board[i + 1] ^= 1  # right
            if i >= n:
                board[i - n] ^= 1  # up
            if i < n * (n - 1):
                board[i + n] ^= 1  # down
    return all(val == 0 for val in board)


class LightsOutHandler(socketserver.BaseRequestHandler):
    """
    Request handler for the Lights Out game server.

    Handles incoming TCP requests, generates Lights Out boards,
    and checks user solutions.
    """

    def handle(self) -> None:
        """
        Handle an incoming TCP request.

        Generates a Lights Out board, sends it to the client,
        and checks the client's solution.
        """
        self.request.sendall(
            b"\nWelcome to Lights Out!\n"
            b"\nThe goal of the game is to turn off all the lights on "
            b"the board.\n"
            b"You can toggle any light by entering its position in "
            b"a string format,\n"
            b"where # represents ON and . represents OFF.\n"
            b"Each toggle will also flip the state of its adjacent "
            b"lights (above, below, left, right).\n"
            b"Try to turn off all the lights to win!\n"
            b"\nEnter your solution as a string of #s and .s "
            b"for ALL board positions, read "
            b"from left to right, top to bottom (e.g., ..##...#.)\n"
            b"\nEXAMPLE\n"
            b"To solve the board:\n\n"
            b"\t###\n\t#.#\n\t.##\n\n"
            b"Your solution would be: ..##...#.\n\n\n")

        while True:
            n = random.randint(15, 25)
            board = generate_random_board(n)
            solution = get_solution(board, n)
            if solution is None:
                continue
            self.request.sendall(b"\nLights Out Board:\n\n")
            self.request.sendall(print_board(board, n).encode("utf-8"))
            self.request.sendall(b"\nYour Solution: ")
            self.request.settimeout(10)
            try:
                user_input = self.request.recv(1024).strip().decode(
                    "utf-8")
            except socket.timeout:
                self.request.sendall(
                    b"\n\nTime out. Generating a new board...\n")
                continue

            user_solution = [1 if c == "#" else 0 for c in user_input]
            if len(user_solution) == n * n and check_solution(
                    board[:], user_solution, n):
                self.request.sendall(b"\ncorctf{freshman_math"
                                     b"_class_throwback}\n")
                break
            self.request.sendall(
                b"\n\nIncorrect solution. Generating a new board...\n")


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 1337

    with socketserver.TCPServer((HOST, PORT), LightsOutHandler) as server:
        print(f"Server started at {HOST}:{PORT}")
        server.serve_forever()
