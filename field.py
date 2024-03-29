from enum import IntEnum
from itertools import product
from os.path import exists
from random import random, randrange
from tkinter import BOTH, Canvas, Event, Frame


class SquareType(IntEnum):
    FREE = 0
    BLOCKED = 1
    START = 2
    FINISH = 3


class Field(Frame):
    """
    This class provides methods for generating a field and drawing it on the screen.
    :param width: the width of the field in squares.
    :param height: the height of the field in squares.
    :param density: the likelihood of a square to be blocked.
    """
    __padding = 10
    __square_size = 50
    __start_position = (0, 0)
    __finish_position = (0, 0)
    __alt_pressed = False
    __shift_pressed = False

    def __init__(self, width: int = 10, height: int = 10,
                 density: float = 0.5) -> None:
        super().__init__()
        self.__width = width
        self.__height = height
        self.__density = density
        self.__field_data = [[SquareType.FREE for _ in range(width)]
                             for _ in range(height)]
        self.__canvas = Canvas(self)
        self.pack(fill=BOTH, expand=1)
        self.__canvas.pack(fill=BOTH, expand=1)
        self.__add_binds()
        self.generate_random()

    def generate_random(self) -> None:
        """
        This method randomly fills the field.
        :return:
        """
        self.__field_data = [[SquareType.FREE for _ in range(self.__width)]
                             for _ in range(self.__height)]
        for i, j in product(range(self.__height), range(self.__width)):
            if random() < self.__density:
                self.__field_data[i][j] = SquareType.BLOCKED
        start_row = randrange(self.__height)
        start_col = randrange(self.__width)
        self.__start_position = (start_row, start_col)
        self.__field_data[start_row][start_col] = SquareType.START
        finish_row = randrange(self.__height)
        finish_col = randrange(self.__width)
        self.__finish_position = (finish_row, finish_col)
        self.__field_data[finish_row][finish_col] = SquareType.FINISH

    def save(self, file_name: str) -> None:
        """
        This method saves the field to a text file.
        :param file_name: output file name.
        :return:
        """
        with open(file_name, 'w') as file:
            for i in range(self.__height):
                for j in range(self.__width):
                    file.write(f'{int(self.__field_data[i][j])} ')
                file.write('\n')
            file.write(f'{self.__start_position[0]} '
                       f'{self.__start_position[1]}\n')
            file.write(f'{self.__finish_position[0]} '
                       f'{self.__finish_position[1]}\n')

    def load(self, file_name: str) -> None:
        """
        This method loads the field from a text file.
        :param file_name: input file name.
        :return:
        """
        if not exists(file_name):
            print(f'Could not load "{file_name}", file does not exist.')
            return
        with open(file_name, 'r') as file:
            for i in range(self.__height):
                self.__field_data[i] = list(map(lambda x: SquareType(int(x)),
                                                file.readline().split()))
            self.__start_position = tuple(map(int, file.readline().split()))
            self.__finish_position = tuple(map(int, file.readline().split()))

    def draw(self) -> None:
        """
        This method draws the field.
        :return:
        """
        self.__canvas.delete('all')
        for i, j in product(range(self.__height), range(self.__width)):
            self.__draw_square(i, j)

    def __add_binds(self) -> None:
        """
        This method adds binds to this class to process user input.
        :return:
        """
        self.__canvas.bind('<Button>', self.__change_square)
        self.focus_set()
        self.bind('<KeyPress>', self.__process_key_press)
        self.bind('<KeyRelease>', self.__process_key_release)

    def __process_key_press(self, event: Event) -> None:
        """
        This method processes a key press event, it should be used in widget.bind.
        :param event: tkinter event.
        :return:
        """
        key = event.keysym
        if key == 'Alt_L' or key == 'Alt_R':
            self.__alt_pressed = True
        elif key == 'Shift_L' or key == 'Shift_R':
            self.__shift_pressed = True

    def __process_key_release(self, event: Event) -> None:
        """
        This method processes a key release event, it should be used in widget.bind.
        :param event: tkinter event.
        :return:
        """
        key = event.keysym
        if key == 'Alt_L' or key == 'Alt_R':
            self.__alt_pressed = False
        elif key == 'Shift_L' or key == 'Shift_R':
            self.__shift_pressed = False

    def __change_square(self, event: Event) -> None:
        """
        This method changes a square on mouse click, it should be used in widget.bind.
        :param event: tkinter event.
        :return:
        """
        row_index = (event.y - self.__padding) // self.__square_size
        col_index = (event.x - self.__padding) // self.__square_size
        if row_index < 0 or row_index >= self.__height:
            return
        if col_index < 0 or col_index >= self.__width:
            return
        if self.__alt_pressed:
            self.__change_special_square(row_index, col_index,
                                         SquareType.START)
        elif self.__shift_pressed:
            self.__change_special_square(row_index, col_index,
                                         SquareType.FINISH)
        else:
            self.__change_normal_square(row_index, col_index)

    def __change_normal_square(self, row_index: int, col_index: int) -> None:
        """
        This method changes a square from free to blocked and vice versa.
        :param row_index: row index.
        :param col_index: column index.
        :return:
        """
        if self.__field_data[row_index][col_index] == SquareType.BLOCKED:
            self.__field_data[row_index][col_index] = SquareType.FREE
        elif self.__field_data[row_index][col_index] == SquareType.FREE:
            self.__field_data[row_index][col_index] = SquareType.BLOCKED
        self.__draw_square(row_index, col_index)

    def __change_special_square(self, row_index: int, col_index: int,
                                square_type: SquareType) -> None:
        """
        This method changes the position of the start or the finish.
        :param row_index: new row index.
        :param col_index: new column index.
        :param square_type: start or finish.
        :return:
        """
        if self.__field_data[row_index][col_index] == square_type:
            return
        if square_type == SquareType.START:
            old_row = self.__start_position[0]
            old_col = self.__start_position[1]
            self.__start_position = (row_index, col_index)
        elif square_type == SquareType.FINISH:
            old_row = self.__finish_position[0]
            old_col = self.__finish_position[1]
            self.__finish_position = (row_index, col_index)
        else:
            return
        self.__field_data[old_row][old_col] = SquareType.FREE
        self.__field_data[self.__start_position[0]][self.__start_position[1]] \
            = SquareType.START
        self.__field_data[self.__finish_position[0]][self.__finish_position[1]] \
            = SquareType.FINISH
        self.__draw_square(old_row, old_col)
        self.__draw_square(row_index, col_index)

    def __draw_square(self, row_index: int, col_index: int) -> None:
        """
        This method draws a square at given coordinates.
        :param row_index: row index.
        :param col_index: column index.
        :return:
        """
        x0 = self.__padding + col_index * self.__square_size
        x1 = x0 + self.__square_size
        y0 = self.__padding + row_index * self.__square_size
        y1 = y0 + self.__square_size
        square_type = self.__field_data[row_index][col_index]
        color = 'white'
        if square_type == SquareType.FREE:
            color = 'green'
        elif square_type == SquareType.BLOCKED:
            color = 'red'
        elif square_type == SquareType.START:
            color = 'blue'
        elif square_type == SquareType.FINISH:
            color = 'yellow'
        self.__canvas.create_rectangle(x0, y0, x1, y1, fill=color)
