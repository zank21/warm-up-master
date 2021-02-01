import random
from pprint import pprint

class User:
    def __init__(self, user_id: int, name: str):
        self.id = user_id
        self.name = name
        self.questions_list = []
        self.answers_list = []
        self.points = 0
        self.last_command = 'None'

    def add_point(self, number_point: int):
        self.points = + number_point


class Question:
    def __init__(self, text: str, author_id: int):
        self.id = id(self)
        self.text = text
        self.author_id = author_id
        self.round = None
        self.is_got = False


class Answer:
    def __init__(self, question_id: int, text: str, author_id: int):
        self.id = id(self)
        self.question_id = question_id
        self.text = text
        self.author_id = author_id
        self.round = None
        self.votes = 0
        self.win_percentage = 0

    def add_vote(self):
        self.votes += 1


class AnswerQuestion:
    def __init__(self, question_object):
        self.id = id(self)
        self.question_id = question_object.id
        self.question_text = question_object.text
        self.question_author = question_object.author
        self.answer_count = 0
        self.answers_list = []
        self.round_name = question_object.round_name

    def add_answer(self, answer):
        self.answers_list.append(answer)
        self.answer_count += 1

    def generate_win_percentage(self):
        total_votes = sum(answer.votes for answer in self.answers_list)
        for answer in self.answers_list:
            percentage = int(round(answer.votes / total_votes, 2) * 100)
            answer.win_percentage = percentage


class Score:
    def __init__(self):
        self.dict = {}
        self.str = ''

    def __sub__(self, other):
        new_score = Score()
        for key in self.dict:
            score_1 = self.dict.get(key)
            score_2 = other.dict.get(key, 0)
            difference = score_1 - score_2
            new_score.dict.update({
                key: difference
            })
            new_score.str += f'{key} - {difference} \n'
        return new_score

    def add_users(self, users_list):
        for user in users_list:
            self.dict.update({
                user.id: user.score
            })
            self.str += f'{user.name} - {user.score} \n'

    def add_user(self, user):
        self.dict.update({
            user.id: user.score
        })
        self.str += f'{user.name} - {user.score} \n'


class Round:
    def __init__(self, name: str, number_round: int):
        self.name = name
        self.number_round = number_round


class Game:
    def __init__(self):
        self.rounds_list = []
        self.users_list = []
        self.questions_list = []
        self.answers_list = []
        self.number_round = 0
        self.round_now = Round('start', 0)
        self.score = Score()

    def add_user(self, user: User):
        self.users_list.append(user)

    def get_score(self):
        score = sorted(self.users_list, key=lambda user: user.points)
        return score

    def new_round(self, round: Round):
        self.rounds_list.append(round)
        self.round_now = round

    def add_question(self, question: Question):
        question.round = self.round_now
        self.questions_list.append(question)

    def add_answer(self, answer: Answer):
        answer.round = self.round_now
        self.answers_list.append(answer)

    def get_question(self, user_id: int):
        user = self.__get_obj_user(user_id)
        for question in self.questions_list:
            if question.round == self.round_now and question.author_id != user.id and not question.is_got:
                question.is_got = True
                return question

    def __get_obj_user(self, user_id: int):
        for user in self.users_list:
            if user.id == user_id:
                return user

    def __get_obj_answer(self, answer_id):
        for answer in self.users_list:
            if answer.id == answer_id:
                return answer

    def add_vote_to_answer(self, answer_id):
        answer = self.__get_obj_answer(answer_id)
        answer.add_vote()
