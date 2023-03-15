from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot [{self.x}, {self.y}]'


class Ship:
    def __init__(self, head, length, orientation):
        self.head = head
        self.length = length
        self.orientation = orientation
        self.health = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.head.x
            cur_y = self.head.y

            if self.orientation == 0:
                cur_x += i

            elif self.orientation == 1:
                cur_y += i

            elif self.orientation == 2:
                cur_x -= i

            else:
                cur_y -= i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shoot(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [['≋']*size for _ in range(size)]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for dx, dy in near:
                cur = Dot(dot.x + dx, dot.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "⊙"
                    self.busy.append(cur)

    def __str__(self):
        res = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "≋")
        return res

    def out(self, dot):
        return not((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        if dot in self.busy:
            raise BoardUsedException()
        self.busy.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.health -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.health == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен")
                    return False
                else:
                    print("Корабль ранен")
                    return True
        self.field[dot.x][dot.y] = "⊙"
        print("Мимо")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dot.x + 1} {dot.y + 1}")
        return dot


class User(Player):
    def ask(self):
        while True:
            try:
                x, y = map(int, input("Введите две цифры (например: 2 4): ").split())
                break
            except ValueError:
                print("Неправильный ввод.")

        return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True

        self.ai = AI(computer, player)
        self.us = User(player, computer)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts > 3000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 3))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("  Приветствуем вас ")
        print("      в игре       ")
        print("    морской бой    ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()