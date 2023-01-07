import random
from enum import Enum
from collections import namedtuple

import pygame

Size = namedtuple("Size", "width height")
Block = namedtuple("Block", "position player isEmpty")
Position = namedtuple("Position", "x y")

WIN_SIZE = 600
ROWS_NUM = 3
MARK_SIZE = WIN_SIZE // ROWS_NUM * 0.8
LINE_THICKNESS = 10


class Player(Enum):
    X = "x"
    O = "o"


class Colours(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)


def is_within_block(mouse_position, block_position):
    block_side_size = WIN_SIZE // ROWS_NUM
    return (block_position.x < mouse_position.x < block_position.x + block_side_size and
            block_position.y < mouse_position.y < block_position.y + block_side_size)


class TicTacToe:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TicTacToe")

        # if player_turn = True then it's the 1st players turn, otherwise the 2nds
        self._player_turn = bool(random.randint(0, 1))
        self._running = True
        # 3x3
        self._game_board = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.size = Size(WIN_SIZE, WIN_SIZE)
        self.font = pygame.font.SysFont("arial", 40)
        self._display_surface = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.assets = {
            Player.X: pygame.transform.scale(pygame.image.load("x.png"), (MARK_SIZE, MARK_SIZE)),
            Player.O: pygame.transform.scale(pygame.image.load("o.png"), (MARK_SIZE, MARK_SIZE))
        }

    def _init_board(self):
        lines_gap = self.size.width // ROWS_NUM
        # Fill in the game_board with the top left point of each block and other metadata
        for i in range(len(self._game_board)):
            for j in range(len(self._game_board[i])):
                x = lines_gap * j
                y = lines_gap * i
                self._game_board[i][j] = Block(Position(x, y), "", True)

    def _handle_events(self, event):
        """
        Event's handler
        - Mouse clicks
        - Quiting the game
        - Restarting the game
        """
        match event.type:
            case pygame.QUIT:
                self._running = False
            case pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down()
            case pygame.KEYDOWN:
                self._handle_key_down(event)
            case _:
                pass

    def _game_logic(self):
        """
        Check winning/draw conditions
        """
        game_won = False
        winning_player = ""

        board = self._game_board
        # Check rows and columns
        for i in range(len(self._game_board)):
            if board[i][0].player == board[i][1].player == board[i][2].player and board[i][2].player != "":
                game_won = True
                winning_player = board[i][0].player
            if board[0][i].player == board[1][i].player == board[2][i].player and board[2][i].player != "":
                game_won = True
                winning_player = board[0][i].player

        # Check diagonal
        if board[0][0].player != "" and board[1][1] == board[2][2].player == board[0][0].player:
            game_won = True
            winning_player = board[0][0].player

        # Check reverse diagonal
        if board[0][2].player != "" and board[1][1] == board[2][0].player == board[0][2].player:
            game_won = True
            winning_player = board[0][2].player

        if self._game_draw():
            self._display_message("It's a draw!")
            self._init_board()

        if game_won:
            self._display_message(f"{winning_player} has won!")
            self._init_board()


    def _display_message(self, content):
        pygame.time.delay(500)
        self._display_surface.fill(Colours.WHITE.value)
        end_text = self.font.render(content, True, Colours.BLACK.value)
        self._display_surface.blit(
            end_text, ((WIN_SIZE - end_text.get_width()) // 2, (WIN_SIZE - end_text.get_height()) // 2)
        )
        pygame.display.update()
        pygame.time.delay(3000)

    def _game_draw(self):
        for i in range(len(self._game_board)):
            for j in range(len(self._game_board[i])):
                if self._game_board[i][j].player == "":
                    return False
        return True

    def _render(self):
        """
        Render the screen
        """
        self._display_surface.fill(Colours.WHITE.value)
        self._draw_grid()
        self._draw_moves()
        pygame.display.update()

    @staticmethod
    def _cleanup():
        pygame.quit()

    def start(self):
        """
        Game loop
        """
        self._init_board()

        while self._running:
            for event in pygame.event.get():
                self._handle_events(event)
            self._render()
            self._game_logic()

        self._cleanup()

    def _handle_mouse_down(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for i in range(len(self._game_board)):
            for j in range(len(self._game_board[i])):
                current_block = self._game_board[i][j]
                # Debugging TODO: Remove
                if is_within_block(Position(mouse_x, mouse_y), current_block.position):
                    print(
                        f"Clicked inside: {current_block}, Players turn: {self._player_turn}")
                if is_within_block(Position(mouse_x, mouse_y), current_block.position) and current_block.isEmpty:
                    player = Player.X.value if self._player_turn else Player.O.value
                    self._game_board[i][j] = Block(current_block.position, player, False)
                    self._player_turn = not self._player_turn
                    print(f"Updated block: {self._game_board[i][j]}")  # Debugging TODO: Remove

    def _draw_grid(self):
        """
        Draws the tic-tac-toe board
        """
        lines_gap = self.size.width // ROWS_NUM
        for i in range(ROWS_NUM):
            line_x_pos = i * lines_gap

            pygame.draw.line(
                self._display_surface,
                Colours.GRAY.value,
                (line_x_pos, 0),
                (line_x_pos, self.size.width),
                LINE_THICKNESS
            )
            pygame.draw.line(
                self._display_surface,
                Colours.GRAY.value,
                (0, line_x_pos),
                (self.size.width, line_x_pos),
                LINE_THICKNESS
            )

    def _draw_moves(self):
        block_half_distance = WIN_SIZE // ROWS_NUM // 2

        for i in range(len(self._game_board)):
            for j in range(len(self._game_board[i])):
                current_block = self._game_board[i][j]
                if current_block.isEmpty:
                    continue

                asset = self.assets[Player.X if current_block.player == Player.X.value else Player.O]
                if asset:
                    self._display_surface.blit(
                        asset,
                        (current_block.position.x + block_half_distance - asset.get_width() // 2,
                         current_block.position.y + block_half_distance - asset.get_height() // 2)
                    )

    def _handle_key_down(self, event):
        match event.key:
            case pygame.K_r:
                self._init_board()
            case pygame.K_ESCAPE:
                self._running = False


if __name__ == "__main__":
    game = TicTacToe()
    game.start()
