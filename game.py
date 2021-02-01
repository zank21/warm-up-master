import random


class Game:
    def __init__(self):
        self.rounds_list = []
        self.users_list = []
        self.number_round = 0
        self.round_now = Round('start', 0)
        self.score = Score()

    def add_user(self, user_id, name):
        user = User(user_id, name)
        self.users_list.append(user)
        self.score.add_user(user)

    # def get_difference_scores(self):
    #     new_score = Score()
    #     new_score.add_users(self.users_list)
    #     difference = new_score - self.score
    #     return difference
    #
    # def get_score(self):
    #     new_score = Score()
    #     new_score.add_users(self.users_list)

    def new_round(self):
        number_round = self.number_round + 1
        name = 'round' + str(number_round)
        new_round = Round(name, number_round)
        self.users_list.append(new_round)
        self.round_now = new_round

    def add_question(self, question_text, question_author):
        question = Question(question_text, question_author, self.round_now)
        self.round_now.questions_list.append(question)
        user = self.__get_obj_user(question_author)
        user.question_list.append(question)

    def add_answer(self, question_id, answer_text, answer_author):
        answer = Answer(question_id, answer_text, answer_author, self.round_now)
        self.round_now.answers_list.append(answer)
        user = self.__get_obj_user(answer_author)
        user.question_list.append(answer)

    def get_question(self, user_id):
        user = self.__get_obj_user(user_id)
        questions = [question for question in self.round_now.questions_list if question not in user.question_list]
        question = random.choice(questions)
        user.question_list.append(question)
        return question

    def __get_obj_user(self, user_id):
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


class Round:
    def __init__(self, name, number_round):
        self.name = str(name)
        self.number_round = number_round
        self.questions_list = []
        self.answers_list = []
        self.answer_question_list = []

    def create_answer_question_list(self):
        for question in self.questions_list:
            answer_question = AnswerQuestion(question)
            question_id = question.id
            for answer in self.answers_list:
                if answer.question_id == question_id:
                    answer_question.add_answer(answer)
            self.answer_question_list.append(answer_question)


class Question:
    def __init__(self, question_text, question_author, round_object):
        self.id = id(self)
        self.text = question_text
        self.author = question_author
        self.round = round_object


class Answer:
    def __init__(self, question_id, answer_text, answer_author, round_object):
        self.id = id(self)
        self.question_id = question_id
        self.text = str(answer_text)
        self.author = answer_author
        self.round = round_object
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


class User:
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name
        self.question_list = []
        self.answer_list = []
        self.score = 0
        self.last_command = 'None'

    def question_count_in_round(self, round_obj):
        question = [question for question in self.question_list if question.round is round_obj]
        return len(question)


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
