# version Alpha 1.0 (No tests)
class User:
    def __init__(self, user_id: int, name: str):
        self.id = user_id
        self.name = name
        self.questions_list = []
        self.answers_list = []
        self.points = 0
        self.last_command = 'None'


class Question:
    def __init__(self, author_id: int, text: str):
        self.id = id(self)
        self.text = text
        self.author_id = author_id
        self.round = None
        self.is_got = False
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

    def add_user(self, user: User):
        self.users_list.append(user)

    def get_score(self) -> list:
        score = sorted(self.users_list, key=lambda user: user.points)
        self.round_now.score = score
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

    def get_question(self, user_id: int) -> Question:
        user = self.__get_obj_user(user_id)
        for question in self.questions_list:
            if question.round == self.round_now and question.author_id != user.id and not question.is_got:
                question.is_got = True
                return question
            else:
                return Question(text='<none>', author_id=0)

    def get_answer_question(self) -> list:
        for question in self.questions_list:
            if question.is_activate and question.round == self.round_now:
                question.is_activate = False
                return [question, [answer for answer in self.answers_list if answer.question_id == question.id]]

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
