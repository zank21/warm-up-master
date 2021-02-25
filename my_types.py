# version Alpha 1.1
from typing import Union, Any, Optional, List
import string
import random
import shelve
import socket
from setting import DISTRIBUTOR_SERVER_PORT
from setting import QUESTION_ON_ONE_USER, ANSWER_ON_ONE_QUESTION
from telebot.types import ReplyKeyboardMarkup


class KeyboardTelegram:
    def __init__(self):
        self.keyboard = ReplyKeyboardMarkup()

    def assessment(self, question_text: str, answers: List[str]):
        self.keyboard.row('Вопрос:' + question_text)
        for answer in answers:
            self.keyboard.row('1. ' + answer)

        return self.keyboard

    def nul(self):
        return self.keyboard


def server_send(text: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
    sock.connect(('localhost', DISTRIBUTOR_SERVER_PORT))  # подключемся к серверному сокету
    sock.send(bytes(text, encoding='UTF-8'))  # отправляем сообщение
    data = sock.recv(1024)  # читаем ответ от серверного сокета
    sock.close()  # закрываем соединение
    return data


def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


class User:
    def __init__(self, user_id: int, name: str, platform: str):
        self.id = str(platform + '_' + str(user_id))
        self.name = name
        self.questions_list = []
        self.question_responded = []
        self.points = 0
        self.last_command = None
        self.answers_list = []

    def add_last_command(self, text: str):
        with shelve.open('last_command') as user:
            user[self.id] = text

    def get_last_command(self):
        with shelve.open('last_command') as user:
            last_command = user.get(self.id)
        return last_command


class Question:
    def __init__(self, author_id: str, text: str):
        self.id = id(self)
        self.text = text
        self.author_id = author_id
        self.round = None
        self.users_saw = []
        self.is_activate = True
        self.answers = []

    def get_data(self):
        answers = [answer.text for answer in self.answers]
        return self.text, answers


class Answer:
    def __init__(self, text: str, author_id: str):
        self.id = id(self)
        self.question = None
        self.text = text
        self.author_id = author_id
        self.round = None
        self.votes = 0
        self.win_percentage = 0


class Round:
    def __init__(self, number_round: int, name: str = 'round', coefficient: int = 1):
        self.name = name
        self.number_round = number_round
        self.coefficient = coefficient
        self.score = []


class Game:
    def __init__(self):
        self.rounds_list = []
        self.users_list = []
        self.questions_list = []
        self.answers_list = []
        self.number_round = 0
        self.round_now = Round(0)

    def __get_obj_user(self, user_id: str) -> User:
        for user in self.users_list:
            if user.id == user_id:
                return user

    def __get_obj_answer(self, answer_id: int, text: str = '') -> Answer:
        for answer in self.answers_list:
            if answer.id == answer_id or answer.text == text:
                return answer

    def __get_obj_question(self, question_id: int = -1, text: str = '') -> Question:
        for question in self.questions_list:
            if question.id == question_id or question.text == text:
                return question

    @staticmethod
    def get_question_database(questions_ids: list[int]):
        database: list[Question] = [
            Question('p', '111111'),
            Question('p', '222222'),
            Question('p', '333333'),
            Question('p', '444444'),
            Question('p', '555555'),
        ]
        result = [question for question in database if question.id not in questions_ids]
        return random.choice(result)

    @staticmethod
    def get_answer_database(answers_ids: list[int]):
        database: list[Answer] = [
            Answer('11111111111', 'p'),
            Answer('2222222222', 'p'),
            Answer('3333333333', 'p'),
            Answer('4444444444', 'p'),
            Answer('5555555555', 'p')
        ]
        result = [answer for answer in database if answer.id not in answers_ids]
        return random.choice(result)

    def add_user(self, user_id: int, name: str, platform: str):
        user = User(user_id=user_id, name=name, platform=platform)
        self.users_list.append(user)

    def delete_user(self, user_id: str):
        user_delete = self.__get_obj_user(user_id)
        for user in self.users_list:
            if user == user_delete:
                self.users_list.remove(user)

    def get_score(self) -> list:
        pass
        # Вычитание очков если пользователь не написал вопроса

    def new_round(self, round: Round):
        self.rounds_list.append(round)
        self.round_now = round

    def add_question(self, author_id: str, text: str):
        question = Question(author_id=author_id, text=text)
        question.round = self.round_now
        self.questions_list.append(question)

    def add_answer(self, text: str, author_id: str, question_id: int):
        question = self.__get_obj_question(question_id=question_id)
        answer = Answer(text=text, author_id=author_id)
        answer.question = question
        answer.round = self.round_now

        user = self.__get_obj_user(author_id)
        user.answers_list.append(answer)
        self.answers_list.append(answer)
        question.answers.append(answer)

    def get_question(self, user_id: str) -> Union[Optional[Question], Any]:
        user = self.__get_obj_user(user_id)
        questions_user = [question for question in user.question_responded if question.round == self.round_now]
        if len(questions_user) == QUESTION_ON_ONE_USER:
            return None

        for question in self.questions_list:
            if question.round == self.round_now \
                    and question.author_id != user.id \
                    and len(question.users_saw) != QUESTION_ON_ONE_USER \
                    and user not in question.users_saw \
                    and question not in user.question_responded:
                user.question_responded.append(question)
                question.users_saw.append(user)
                return question

    def get_answer_question(self) -> Union[tuple[Any, list], list]:
        for question in self.questions_list:
            if question.is_activate and question.round == self.round_now:
                question.is_activate = False
                answers = [answer for answer in self.answers_list if answer.question == question]
                return question, answers

        return []

    def add_vote_to_answer(self, answer_id):
        answer = self.__get_obj_answer(answer_id)
        answer.votes += 1

    def add_points(self, question_id: int) -> list:
        answers = [answer for answer in self.answers_list if answer.question_id == question_id]
        total_votes = sum([answer.votes for answer in answers])
        result = {}
        for answer in answers:
            percent = (answer.votes * 100) // total_votes
            points = percent * self.round_now.coefficient
            user = self.__get_obj_user(answer.author_id)
            result.update({user: points})
            user.points += points
        result = result.items()
        result = sorted(result, key=lambda user: user[1], reverse=True)
        return result

    def add_vote(self, answer_id: int):
        answer = self.__get_obj_answer(answer_id)
        answer.votes += 1

    def check(self):
        questions = [question for question in self.questions_list if question.round == self.round_now]
        number_questions_missing = len(self.users_list) - len(questions)

        i = 0

        for i in range(number_questions_missing):
            questions_ids = [question.id for question in self.questions_list]
            question = self.get_question_database(questions_ids)
            self.questions_list.append(question)
            i += 1

        for question in questions:
            answer_missing = len(question.users_saw) - len(question.answers)

            i = 0
            for i in range(answer_missing):
                answers_ids = [answer.id for answer in self.answers_list]
                answer = self.get_answer_database(answers_ids)
                answer.question_id = question.id
                self.answers_list.append(answer)
                i += 1
