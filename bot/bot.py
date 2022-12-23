from telebot.async_telebot import AsyncTeleBot
from sudoku_py import SudokuGenerator
from telebot import types
import query
import asyncio

bot = AsyncTeleBot('5879745106:AAFs66VmDwMYGTWhAcGmH0nySUuipagCaAU') # Это секретная информация! Не смотрите сюда, пожалуйста (◕‿◕)
board = []
now_x = 0
now_y = 0
saved_message = 0
square_x = 0
square_y = 0

def generate_string(board):
    board_string = ""
    for i in range(9):
        for j in range(9):
            board_string += str(board[i][j])
            board_string += '  '
            if j == 2 or j == 5:
                board_string += '|  '
        board_string += '\n'
        if i == 2 or i == 5:
            for j in range(34):
                if j == 10:
                    board_string += '+'
                elif j == 22:
                    board_string += '+'
                else:
                    board_string += '-'
            board_string += '\n'
    return board_string

@bot.message_handler(commands=['start'])
async def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    generate_button = types.KeyboardButton("/generate")
    print_button = types.KeyboardButton("/print")
    help_button = types.KeyboardButton("/help")
    about_button = types.KeyboardButton("/about")
    rules_button = types.KeyboardButton("/rules")
    question_button = types.KeyboardButton("/question")
    
    markup.add(generate_button, print_button, help_button, about_button, rules_button, question_button)
    await bot.send_message(message.chat.id, text="Этот бот позволит вам поиграть в судоку прямо в чате! Напишите /help для списка команд".format(message.from_user), reply_markup=markup)

@bot.message_handler(commands=['generate'])
async def generate(message):
    global board, wait_coords, wait_number
    sudokuGenerator = SudokuGenerator(board_size=9)
    sudokuGenerator.generate(cells_to_remove=50, symmetry_removal=True)
    sudokuGenerator.board_exchange_values({'a': 9, 'b': 8, 'c': 7, 'd': 6, 'e': 5, 'f': 4, 'g': 3, 'h': 2, 'i': 1})
    board = sudokuGenerator.board
    wait_coords = False
    wait_number = False
    await bot.send_message(message.from_user.id, "Новое судоку сгенерировано!")

@bot.callback_query_handler(func=lambda call: call.data[:5] == "paste")
async def callback_query_paste(call):
    global board, saved_message
    y = int(call.data.split()[1])
    x = int(call.data.split()[2])
    number = int(call.data.split()[3])
    for i in range(9):
        if board[i][x] == number:
            await bot.answer_callback_query(call.id, "No.")
            return
    for i in range(9):
        if board[y][i] == number:
            await bot.answer_callback_query(call.id, "No.")
            return
    board[y][x] = number
    board_string = generate_string(board)
    markup = types.InlineKeyboardMarkup()
    place_button = types.InlineKeyboardButton("Добавить цифру", callback_data="place")
    markup.add(place_button)
    await bot.send_message(saved_message.from_user.id, board_string, reply_markup=markup)
    n = 0
    for i in range(9):
        for j in range(9):
            if board[i][j] != 0:
                n += 1
    if n == 81:
        await bot.send_message(saved_message.from_user.id, "Поздравляю, вы решили судоку!")

async def paste_number(message, y, x):
    global board
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    for i in range(3):
        f_data = "paste" + ' ' + str(y) + ' '  + str(x) + ' ' + str(i * 3 + 1)
        s_data = "paste" + ' ' + str(y) + ' '  + str(x) + ' ' + str(i * 3 + 2)
        t_data = "paste" + ' ' + str(y) + ' '  + str(x) + ' ' + str(i * 3 + 3)
        markup.add(types.InlineKeyboardButton(str(i * 3 + 1), callback_data=f_data), types.InlineKeyboardButton(str(i * 3 + 2), callback_data=s_data), types.InlineKeyboardButton(str(i * 3 + 3), callback_data=t_data))
    await bot.send_message(saved_message.from_user.id, "Выберите число:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data[:6] == "square")
async def callback_query_square(call):
    await paste_number(call.message, int(call.data.split()[1]), int(call.data.split()[2]))

async def choose_square(message, y, x):
    global board
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    for i in range(3):
        f_data = "square" + ' ' + str(y * 3 + i) + ' ' + str(x * 3)
        s_data = "square" + ' ' + str(y * 3 + i) + ' ' + str(x * 3 + 1)
        t_data = "square" + ' ' + str(y * 3 + i) + ' ' + str(x * 3 + 2)
        markup.add(types.InlineKeyboardButton(str(board[y * 3 + i][x * 3]), callback_data=f_data), types.InlineKeyboardButton(str(board[y * 3 + i][x * 3 + 1]), callback_data=s_data), types.InlineKeyboardButton(str(board[y * 3 + i][x * 3 + 2]), callback_data=t_data))
    await bot.send_message(saved_message.from_user.id, "Выберите ячейку:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data[:5] == "click")
async def callback_query_click(call):
    await choose_square(call.message, int(call.data.split()[1]), int(call.data.split()[2]))

async def place(message):
    global board
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    saved_message = message
    for i in range(3):
        f_data = "click" + ' ' + str(i) + ' ' + '0'
        s_data = "click" + ' ' + str(i) + ' ' + '1'
        t_data = "click" + ' ' + str(i) + ' ' + '2'
        markup.add(types.InlineKeyboardButton("o", callback_data=f_data), types.InlineKeyboardButton("o", callback_data=s_data), types.InlineKeyboardButton("o", callback_data=t_data))
    await bot.send_message(message.from_user.id, "Выберите квадрат", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "place")
async def callback_query_place(call):
    global saved_message
    await place(saved_message)

@bot.message_handler(commands=['print'])
async def print_board(message):
    global saved_message
    board_string = generate_string(board)
    markup = types.InlineKeyboardMarkup()
    saved_message = message
    place_button = types.InlineKeyboardButton("Добавить цифру", callback_data="place")
    markup.add(place_button)
    await bot.send_message(message.from_user.id, board_string, reply_markup=markup)

@bot.message_handler(commands=['help'])
async def about(message):
    ans = 'У бота есть 6 команд:\n /start - запустить бота\n /generate - сгенерировать новое судоку\n /print - вывести текущее судоку\n /help - список команд\n /about - о боте\n /rules - правила судоку\n /question - что это?..'
    await bot.send_message(message.from_user.id, ans)

@bot.message_handler(commands=['about'])
async def about(message):
    ans = 'Этот бот позволит вам играть в судоку через кнопочный интерфейс. Для начала игры напечатайте (или воспользуйтесь кнопками) /generate, а потом /print'
    await bot.send_message(message.from_user.id, ans)

@bot.message_handler(commands=['rules'])
async def rules(message):
    ans = 'Правила судоку:\n У нас есть поле 9х9, в каждой клетке может находиться цфира. Наша цель так расставить цифры по клеточкам, чтобы в каждой вертикальной, горизонатальной линии и квадрате 3х3 не было одинаковых цифр'
    await bot.send_message(message.from_user.id, ans)

@bot.message_handler(commands=['question'])
async def question(message):
    ans = 'Почему же бот называется семафором?...\n . \n . \n . \n Хороший вопрос.'
    await bot.send_message(message.from_user.id, ans)
    ans = '(тут должен был быть тот самый стикер, который дал название боту, но он nsfw, но мб в ботах моих одногруппников его можно найти...)'
    await bot.send_message(message.from_user.id, ans)

while True:
    try:
        asyncio.run(bot.polling())
    except Exception as e:
        print(e)
