class Base:
    def prnt(self):
        print('Sup')


class Child1(Base):
    pass


class Child2(Base):
    pass


class GrandChild(Child1):
    pass


# Получаем все подклассы класса Base
def get_subclasses(cls):
    subclasses = cls.__subclasses__()
    for subclass in subclasses:
        subclasses.extend(get_subclasses(subclass))
    return subclasses


for subclass in Base.__subclasses__():
    subclass().prnt()
