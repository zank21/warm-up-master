# version Alpha 1.1
from typing import Union, Any
import string
import random

ANSWER_ON_ONE_QUESTION = 2


def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


class User:
    def __init__(self, user_id: int, name: str):
        self.id = user_id
        self.name = name
        self.questions_list = []
        self.question_responded = []
        self.points = 0
        self.last_command = 'None'
        self.answers_list = []


class Question:
    def __init__(self, author_id: int, text: str):
        self.id = id(self)
        self.text = text
        self.author_id = author_id
        self.round = None
        self.users_saw = 0
        self.is_activate = True


class Answer:
    def __init__(self, question_id: int, text: str, author_id: int):
        self.id = id(self)
        self.question_id = question_id
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
        self.QUESTIONS_DATABASE: list[Question] = [
            Question(0, '111111'),
            Question(0, '222222'),
            Question(0, '333333'),
            Question(0, '444444'),
            Question(0, '555555'),
        ]

    def add_user(self, user: User):
        self.users_list.append(user)

    def get_score(self) -> list:
        pass

    # Вычитание очков если пользователь не написал вопроса

    def new_round(self, round: Round):
        self.rounds_list.append(round)
        self.round_now = round

    def add_question(self, question: Question):
        question.round = self.round_now
        self.questions_list.append(question)

    def add_answer(self, answer: Answer):
        answer.round = self.round_now
        user_id = answer.author_id
        user = self.__get_obj_user(user_id)
        user.answers_list.append(answer)
        self.answers_list.append(answer)

    def get_question(self, user_id: int) -> Question:
        user = self.__get_obj_user(user_id)
        for question in self.questions_list:
            if question.round == self.round_now \
                    and question.author_id != user.id \
                    and question.users_saw != ANSWER_ON_ONE_QUESTION \
                    and question not in user.question_responded:
                user.question_responded.append(question)
                question.users_saw += 1
                return question
        return Question(text='<none>', author_id=0)

    def get_answer_question(self) -> Union[tuple[Any, list], list]:
        for question in self.questions_list:
            if question.is_activate and question.round == self.round_now:
                question.is_activate = False
                answers = [answer for answer in self.answers_list if answer.question_id == question.id]
                return question, answers

        return []

    def __get_obj_user(self, user_id: int) -> User:
        for user in self.users_list:
            if user.id == user_id:
                return user

    def __get_obj_answer(self, answer_id) -> Answer:
        for answer in self.users_list:
            if answer.id == answer_id:
                return answer

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

    def __get_question_database(self):
        for question in self.QUESTIONS_DATABASE:
            if question.is_activate:
                question.is_activate = False
                return question
        raise Exception('Кончились вопросы в базе данных')

    def check(self):
        questions = [question for question in self.questions_list if question.round == self.round_now]
        number_questions_missing = len(self.users_list) * ANSWER_ON_ONE_QUESTION - len(questions)
        for i in range(number_questions_missing):
            question = self.__get_question_database()
            self.questions_list.append(question)
