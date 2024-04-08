class FClass(object):
    def __init__(self):
        self.age = 0

    def fangfa(self, age):
        self.age += age
        print(f'小王子的年龄是{self.age}')


class Dclass(FClass):
    pass


kkk = Dclass()
kkk.fangfa(30)
