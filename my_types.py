"""
Python 3.7
"""
import random
import string
from typing import Union, List, Dict

from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

from setting import QUESTION_ON_ONE_USER

User_id = lambda user_id: str(user_id)


def generate_random_string(length: int):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


def get_point(sum_vote: int, votes: int):
    points = int(round(votes / sum_vote, 2) * 100)
    return points


class User:
    def __init__(self, user_id: User_id):
        self.id: str = user_id
        self.name: str = user_id
        self.points: int = 0
        self.status: str = 'menu'
        self.ready: bool = False
        self.last_question: Question = Question(self, '')


class Question:
    def __init__(self, author: User, text: str):
        self.id: str = author.id
        self.text: str = text
        self.author: User = author
        self.round: Round
        self.views: List[User] = []
        self.appreciated: bool = True
        self.answers: List[Answer] = []
        self.votes: int = 0


class Answer:
    def __init__(self, text: str, author: User, question: Question):
        self.id = id(self)
        self.question = question
        self.text = text
        self.author = author
        self.votes = 0
        self.win_percentage = 0


class Keyboard:
    def __init__(self):
        self.keyboard_inline = InlineKeyboardMarkup(row_width=1)
        self.keyboard_reply = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)

    def game_is_ready(self, server_id: int):
        self.keyboard_inline.add(InlineKeyboardButton('Присоединиться к серверу', callback_data=f'{server_id}'))
        self.keyboard_inline.add(InlineKeyboardButton('Отклонить', callback_data=f'{server_id}'))
        return self.keyboard_inline

    def menu(self):
        self.keyboard_reply.add(KeyboardButton('Начать'))
        self.keyboard_reply.add(KeyboardButton('О игре'))
        return self.keyboard_reply

    def nul(self):
        return self.keyboard_reply

    def answer_question(self, answers: [Answer]):
        for answer in answers:
            self.keyboard_inline.add(InlineKeyboardButton(answer.text, callback_data=f'answer_{answer.id}'))
        return self.keyboard_inline


class Database:
    pass


class Users:
    def __init__(self):
        self.list: List[User] = []

    def add(self, user: Union[User, int, str]):
        if type(user) != User:
            user = User(user_id=user)
        self.list.append(user)

    def delete(self, user: Union[User, int, str]):
        if type(user) != User:
            user = self.get(user)
        self.list.remove(user)

    def get(self, user_id: Union[int, str]) -> User:
        for user in self.list:
            if user.id == user_id:
                return user

        raise NameError(f'User not found [user_id = {user_id}] '
                        )

    def get_list(self):
        return self.list

    def ready_true(self, user_id):
        user = self.get(user_id)
        user.ready = True

    def ready_false(self):
        for user in self.list:
            user.ready = False


class Round:
    def __init__(self, users: Users):
        self.users = users
        self.answers: List[Answer] = []
        self.questions: List[Question] = []
        self.result_round: Dict[User, int] = {}
        for user in self.users.list:
            self.result_round.update({user: 0})

    def add_question(self, author_id: User_id, text: str = '') -> None:
        """
        Добовляет вопрос в self раунд
        :param author_id: id автора вопроса
        :param text: текст вопроса
        :return: None
        """
        user = self.users.get(author_id)
        question = Question(author=user, text=text)
        question.round = self
        self.questions.append(question)

    def add_answer(self, text: str, author_id: User_id) -> None:
        """
        Добовляет ответ в self рауд
        :param text: тест ответа
        :param author_id: id автора ответа
        :return: None
        """
        user = self.users.get(author_id)
        question = user.last_question
        answer = Answer(text=text, author=user, question=question)
        self.answers.append(answer)
        question.answers.append(answer)

    def get_question(self, user_id: User_id) -> Union[None, Question]:
        """
        Получить вопрос для указанного пользователя
        :param user_id: id пользователя, для которого нужно получить вопрос
        :return: None, если пользоваетль получил вопросов,
        количество которых меньше и равно настройке QUESTION_ON_ONE_USER;
        объект Question, есди все прошло умпешно
        """
        user = self.users.get(user_id)
        questions_user = [answer.question for answer in self.answers if answer.author == user]

        if len(questions_user) == QUESTION_ON_ONE_USER:
            return

        for question in self.questions:
            if question.author.id != user.id \
                    and len(question.views) != QUESTION_ON_ONE_USER \
                    and user not in question.views \
                    and question not in questions_user:
                question.views.append(user)
                user.last_question = question
                return question

    def get_questions(self) -> List[str]:
        """
        Получить список всех вопросов self раунд
        :return: [str]
        """
        return [question.text for question in self.questions]

    def get_answers_question(self, question_id=None) -> Union[None, List]:
        """
        Получить пару вопрос-ответы
        :param question_id: id вопроса, на который нужно получить список ответов
        :return: Если указан параметр question_id, возвращает лсит:
        [текст вопроса, [текста ответов], [количество очко, полученных за ответ]],
        если параметр question_id не указан, возращает лист:
        [текст вопроса, [текста ответов]],
        и убирает его из дальнешего поиска при вызове данной функции;
        если не найдется не одной доступной пары вопрос-ответы, вернет None
        """
        if question_id is None:
            for question in self.questions:
                if not question.appreciated:
                    question.appreciated = True
                    return [question.text, [answer.text for answer in question.answers]]
                else:
                    return None
        else:
            question = self.__get_obj_question(question_id=question_id)
            sum_votes_answers = sum([answer.votes for answer in question.answers])
            points_result = []
            for answer in question.answers:
                points = get_point(sum_vote=sum_votes_answers, votes=answer.votes)
                if answer.author in self.result_round.keys():
                    value = self.result_round[answer.author]
                    value += points
                    self.result_round.update({answer.author: value})
                points_result.append(points)

            return [question.text, [answer.text for answer in question.answers], points_result]

    def add_vote_answer(self, answer_id) -> None:
        """
        Добовляет голос к вопросу
        :param answer_id: id вопроса
        :return: None
        """
        answer = self.__get_obj_answer(answer_id == answer_id)
        answer.votes += 1

    def add_vote_question(self, question_id) -> None:
        """
        Добовляет голос к ответу
        :param question_id:
        :return: None
        """
        question = self.__get_obj_question(question_id=question_id)
        question.votes += 1

    def get_votes_question(self) -> List:
        """
        Возращает статистику по голосванию за лучщий вопрос
        :return: возвращает лист:
        [[текста вопросов], [количество очков]]
        """
        points_result = []
        sum_votes_questions = sum([question.votes for question in self.questions])

        for question in self.questions:
            points = get_point(sum_vote=sum_votes_questions, votes=question.votes)
            if question.author in self.result_round.keys():
                value = self.result_round[question.author]
                value += points
                self.result_round.update({question.author: value})
            points_result.append(points)

        return [[question.text for question in self.questions], points_result]

    def __get_obj_answer(self, answer_id: int = None, text: str = None) -> Answer:
        """
        Ищет среди self.answers по указанным параметрам
        :param answer_id: id ответа
        :param text: текст ответа
        :return: Возваращает объект класса Answer
        """
        for answer in self.answers:
            if answer.id == answer_id or answer.text == text:
                return answer
        raise NotImplemented(f'Answer not found [answer_id= {answer_id}, text = {text}]')

    def __get_obj_question(self, question_id=None, text: str = '') -> Question:
        """
        Ищет среди self.questions по указанным параметрам
        :param question_id: id вопроса
        :param text: текст вопроса
        :return: Возвращает объект класса Question
        """
        for question in self.questions:
            if question.id == question_id or question.text == text:
                return question

        raise NotImplemented(f'Answer not found [question_id= {question_id}, text = {text}]')

    def end(self):
        for user in self.users.list:
            if user in self.result_round.keys():
                value = self.result_round[user]
                user.points += value


class Game:
    def __init__(self):
        self.rounds: List[Round] = []
        self.users: Users = Users()
        self.round: Round = Round(users=self.users)

    def new_round(self):
        """
        Создает новый раунд
        :return: None
        """
        self.round.end()
        self.rounds.append(self.round)
        self.round = Round(users=self.users)

    def get_stat(self) -> List[List]:
        """
        Получить счет на данный момент
        :return: возврщает лист:
        [[имя пользователей],[количество уже имеюшихся очков],[количество полученных очков за раунд]]
        """
        points_add = []
        for user in self.users.list:
            if user in self.round.result_round.keys():
                points = self.round.result_round[user]
                points_add.append(points)

        return [[user.name for user in self.users.list], [user.points for user in self.users.list], points_add]

# def add_points(self, question_id) -> list:
#     answers = [answer for answer in self.answers_list if answer.question_id == question_id]
#     total_votes = sum([answer.votes for answer in answers])
#     result = {}
#     for answer in answers:
#         percent = (answer.votes * 100) // total_votes
#         points = percent * self.round_now.coefficient
#         user = self.users.get(answer.author_id)
#         result.update({user: points})
#         user.points += points
#     result = result.items()
#     result = sorted(result, key=lambda user: user[1], reverse=True)
#     return result
#
# def check(self):
#     questions = [question for question in self.questions_list if question.round == self.round_now]
#     number_questions_missing = len(self.users_list) - len(questions)
#
#     i = 0
#
#     for i in range(number_questions_missing):
#         questions_ids = [question.id for question in self.questions_list]
#         question = self.get_question_database(questions_ids)
#         self.questions_list.append(question)
#         i += 1
#
#     for question in questions:
#         answer_missing = len(question.views) - len(question.answers)
#
#         i = 0
#         for i in range(answer_missing):
#             answers_ids = [answer.id for answer in self.answers_list]
#             answer = self.get_answer_database(answers_ids)
#             answer.question_id = question.id
#             self.answers_list.append(answer)
#             i += 1
