from pydantic import BaseModel, validator
from typing import List, Dict, Tuple, Optional
from random import randint

from datetime import date, datetime

def clamp(low, x, high):
    if x < low:
        return low
    if x > high:
        return high
    return x


class ClampedNumber():
    def __init__(self, lowest: int, highest: int, init: int = None):
        self.lowest = lowest
        self.highest = highest
        self.__value = clamp(lowest, init if init is not None else lowest, highest)
    
    def __call__(self) -> int:
        return self.value
    
    @property
    def value(self) -> int:
        return self.__value
    @value.setter
    def value(self, new_value):
        self.__value = clamp(self.lowest, new_value, self.highest)
    
    def can_increase(self) -> bool:
        return self.value < self.highest
    
    def can_decrease(self) -> bool:
        return self.value > self.lowest
    
    def increase(self) -> bool:
        success = self.can_increase()
        if success:
            self.value += 1
        return success
    
    def decrease(self) -> bool:
        success = self.can_decrease()
        if success:
            self.value -= 1
        return success
    
    def crease(self, change_type) -> Tuple[bool, int]:
        if change_type == '+':
            return self.increase(), self.value
        elif change_type == '-':
            return self.decrease(), self.value
        else:
            raise ValueError(f'Unknown crease: {change_type} (has to be "+" or "-")')
    
    def to_dict(self) -> dict:
        return {
            'lowest': self.lowest,
            'highest': self.highest,
            'value': self.__value
        }
    
    @classmethod
    def from_dict(cls, basket):
        return cls(
            lowest=basket['lowest'],
            highest=basket['highest'],
            init=basket['value']
        )


class CharacterModel(BaseModel):
    name: str
    health: int
    mental: int

    @validator('health', 'mental')
    def params_validator(cls, value):
        return clamp(0, value, 5)


class Character:
    preset_names = [
        'Аманда Шарп',
        'Боб Дженкинс',
        'Винсент Ли',
        'Глория Голдберг',
        'Даррел Симонс',
        'Декстер Дрейк',
        'Дженни Барнс',
        'Джо Даймонд'
    ]

    def __init__(self, name):
        self.name = name
        self.health = ClampedNumber(0, 5, init=5)
        self.mental = ClampedNumber(0, 5, init=5)

    def to_dict(self):
        return {
            'name': self.name,
            'health': self.health.to_dict(),
            'mental': self.mental.to_dict()
        }
    
    @classmethod
    def from_dict(cls, basket):
        self = cls("")

        self.name = basket['name']
        self.health = ClampedNumber.from_dict(basket['health'])
        self.mental = ClampedNumber.from_dict(basket['mental'])

        return self
    
    @classmethod
    def from_model(cls, model: CharacterModel):
        obj = cls(model.name)
        obj.health.value = model.health
        obj.mental.value = model.mental
        return obj


class ChangeModel(BaseModel):
    who: str
    what: str
    where: str
    extra: Optional[Dict[str, str]]

class RoomParamsModel(BaseModel):
    characters: List[CharacterModel]
    despair_limit: int
    ancient: str
    author: str

    @validator('despair_limit')
    def despair_limit_validator(cls, value):
        return clamp(10, value, 14)

    
class Room:
    def __init__(self):
        self.id: int = randint(1, 1 << 31 - 1)
        self.start_date: datetime = None
        
        self.characters: List[Character] = None
        self.despair_limit: int = None
        self.ancient: str = None
        self.room_author: str = None

        self.portal_limit: int = None
        
        self.despair: ClampedNumber = None
        self.portals: ClampedNumber = None

        self.terror: ClampedNumber = None
        
        self.monsters: List[int] = None
        self.monster_cap: int = None

        self.outskirts: ClampedNumber = None

        self.complete: bool = False
        self.victory: bool = None

        self.action_log: List[Dict] = None

        self.notifications: List[str] = None

        pass
    
    @classmethod
    def from_params(cls, params: RoomParamsModel):
        self = cls()

        self.start_date = datetime.now()

        self.characters = [Character.from_model(character_model) for character_model in params.characters]
        self.despair_limit = params.despair_limit
        self.ancient = params.ancient
        self.room_author = params.author

        self.portal_limit = 9 - (len(self.characters) + 1) // 2

        self.despair = ClampedNumber(0, self.despair_limit)
        self.portals = ClampedNumber(0, self.portal_limit)

        self.terror = ClampedNumber(1, 10)

        self.monsters = []
        self.monster_cap = len(self.characters) + 3

        self.outskirts = ClampedNumber(0, len(self.characters))

        self.complete = False
        self.victory = None

        self.action_log = []
        self.notifications = []

        return self


    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'start_date': self.start_date.timestamp(),
            'characters': [
                character.to_dict() for character in self.characters
            ],
            'ancient': self.ancient,
            'room_author': self.room_author,
            'despair': self.despair.to_dict(),
            'portals': self.portals.to_dict(),
            'terror': self.terror.to_dict(),
            'monsters': self.monsters[:],
            'monster_cap': self.monster_cap,
            'outskirts': self.outskirts.to_dict(),
            'complete': self.complete,
            'victory': self.victory,
            'action_log': self.action_log[:],
            'notifications': self.notifications[:]
        }
    
    @classmethod
    def from_dict(cls, basket):
        self = cls()

        self.id = basket['id']
        self.start_date = datetime.fromtimestamp(basket['start_date'])

        self.characters = [Character.from_dict(character) for character in basket['characters']]
        self.ancient = basket['ancient']
        self.room_author = basket['room_author']

        self.despair = ClampedNumber.from_dict(basket['despair'])
        self.portals = ClampedNumber.from_dict(basket['portals'])
        self.terror = ClampedNumber.from_dict(basket['terror'])

        self.monsters = basket['monsters'][:]
        self.monster_cap = basket['monster_cap']

        self.outskirts = ClampedNumber.from_dict(basket['outskirts'])

        self.complete = basket['complete']
        self.victory = basket['victory']

        self.action_log = basket['action_log']
        self.notifications = basket['notifications']

        return self

    verbs = {
        'health': 'здоровье',
        'mental': 'рассудок',
        'despair': 'безысходность',
        'portals': 'порталы',
        'terror': 'ужас',
        'monsters': 'монстра в город',
        'outskirts': 'окраины',
        '+': 'увеличивает',
        '-': 'уменьшает',
        'new': 'добавляет',
        'remove': 'удаляет',
    }

    @staticmethod
    def make_action_record(who: str, what: str) -> dict:
        return {
            'date': datetime.now().timestamp(),
            'user': who,
            'text': what
        }
    
    def notice(self, text) -> None:
        self.notifications.append(text)

    def log(self, who, message) -> None:
        action = self.make_action_record(who, message)
        self.action_log.append(action)

    def set_gameover(self, victory: bool):
        if not self.complete:
            self.complete = True
            self.victory = victory
            if victory:
                self.notifications.append('Вы выиграли!')
            else:
                self.notifications.append('Вы проиграли!')


    def make_change(self, who: str, what: str, where: str, extra: dict = None) -> bool:
        action = ''
        v = self.verbs

        # where == 'character 0 health'; what == '+'
        if where.startswith('character'):
            where = where.split(' ')

            index = int(where[1])
            character = self.characters[index]

            where = where[2]
            if where == 'health':
                success, new_value = character.health.crease(what)
            elif where == 'mental':
                success, new_value = character.mental.crease(what)
            
            if success:
                self.log(who, f'{v[what]} {v[where]} сыщика {character.name} (теперь {new_value})')
            
            return success
        
        elif where == 'despair':
            success, new_value = self.despair.crease(what)

            if success:
                self.log(who, f'{v[what]} {v[where]} (теперь {new_value})')

                if not self.despair.can_increase():
                    self.set_gameover(victory=False)

            return success

        elif where == 'portals':
            success, new_value = self.portals.crease(what)

            if success:
                self.log(who, f'{v[what]} {v[where]} (теперь {new_value})')

                if not self.portals.can_increase():
                    self.set_gameover(victory=False)
                else:
                    self.make_change(who, '+', 'despair')
            
            return success
        
        elif where == 'terror':
            success, new_value = self.terror.crease(what)

            if success:
                self.log(who, f'{v[what]} {v[where]} (теперь {new_value})')

                if not self.terror.can_increase():
                    self.set_gameover(victory=False)
                
                if self.terror() == 3:
                    self.notice('Магазин закрывается!')
                elif self.terror() == 6:
                    self.notice('Лавка древностей закрывается!')
                elif self.terror() == 9:
                    self.notice('Ye Olde Magick Shoppe закрывается!')

            return success
        
        elif where == 'outskirts':
            success, new_value = self.outskirts.crease(what)

            if success:
                self.log(who, f'{v[what]} {v[where]} (теперь {new_value})')

                if not self.outskirts.can_increase():
                    self.outskirts.value = 0
                    self.log('Система', f'Окраины переполнились и сброшены (теперь {self.outskirts()})')
                    self.notice('Окраины переполнены!')
                    self.make_change('Система', '+', 'terror')
                
            return success
        
        elif where == 'monsters':
            type = int(extra['type'])

            if type not in [1, 2, 3]:
                return False

            if what == 'new':
                if len(self.monsters) >= self.monster_cap:
                    self.log(who, f'попытался добавить {v[what]}, но город заполнен')
                    return self.make_change(who, '+', 'outskirts')
                
                self.monsters.append(type)
                new_value = len(self.monsters)
                self.log(who, f'{v[what]} {v[where]} (теперь монстр{"" if new_value == 1 else "ов"} {new_value})')
                return True
            elif what == 'remove':
                if type not in self.monsters:
                    return False
                
                self.monsters.remove(type)
                new_value = len(self.monsters)
                self.log(who, f'{v[what]} {v[where]} (теперь монстр{"" if new_value == 1 else "ов"} {new_value})')
                return True
        
        elif where == 'victory':
            victory = what == '+'
            if victory:
                self.log(who, f'завершает игру победой')
            else:
                self.log(who, f'завершает игру поражением')
            self.set_gameover(victory=victory)
            return True

        return False

