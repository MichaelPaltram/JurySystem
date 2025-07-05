import pymysql.cursors
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List

class Restrictions(Enum):
    TRAINER = 0
    ADMIN = 1
    
class Gender(Enum):
    MALE = 0
    FEMALE = 1

@dataclass
class User:
    id: int
    username: str
    email: str
    team: str
    registered: datetime
    expires: datetime
    restrictions: Restrictions
    locked: bool
    
    def valid(self) -> bool:
        return datetime.now() < self.expires and not self.locked
    
    @staticmethod
    def fromRow(row):
        return User(row['id'], row['username'], row['email'], row['team'], row['registered'], row['expires'], Restrictions(row['restrictions']), row['locked'] != 0)


@dataclass
class Athlete:
    id: int
    givenname: str
    surname: str
    userId: int
    birth: datetime
    gender: Gender
    
    @staticmethod
    def fromRow(row):
        return Athlete(row['id'], row['givenname'], row['surname'], row['userId'], row['birth'], Gender(row['gender']))

class JuryDatabase:
    def __init__(self, host: str):
        self.conn = pymysql.connect(host=host,
                            user='JurySystem',
                            password='asdfuas347lkasudhr',
                            database='JurySystem',
                            cursorclass=pymysql.cursors.DictCursor)
    
    def validateUser(self, username, password):
        with self.conn.cursor() as cursor:
           if cursor.execute(f'SELECT * FROM users WHERE username="{username}";') != 1:
               return False
           row = cursor.fetchone()
           user = User.fromRow(row)
           return row['password'] == password and user.valid()

    def getUser(self, userId: int) -> User:
        with self.conn.cursor() as cursor:
            sql = f'SELECT * FROM users WHERE id="{userId}";'
            cursor.execute(sql)
            return User.fromRow(cursor.fetchone())
        return None

    def insertUser(self, username: str, password: str, email:str, team:str, restrictions: Restrictions) -> int:
        locked = 0
        with self.conn.cursor() as cursor:
            sql = f"INSERT INTO users (username, password, email, team, registered, expires, restrictions, locked) VALUES ('{username}', '{password}', '{email}','{team}', '{datetime.now()}', '{datetime.now() + timedelta(weeks=300)}', {restrictions.value}, {locked});"
            cnt = cursor.execute(sql)
            if cnt != 1:
                return None
            self.conn.commit()
            return cursor.lastrowid
        return None
    
    def removeUser(self, userId: int) -> bool:
        with self.conn.cursor() as cursor:
            sql = f"DELETE FROM `users` WHERE `users`.`id` = {userId} ;"
            cnt = cursor.execute(sql)
            self.conn.commit()
            return cnt != 0
        return False
    
    def updateUser(self, userId: int, username: str, email: str, team: str, expires: datetime, restrictions: Restrictions, locked: bool):
        with self.conn.cursor() as cursor:
            sql = f"UPDATE `users` SET `username` = '{username}', `email` = '{email}', `team` = '{team}', `expires` = '{expires}',`restrictions` = '{restrictions.value}', `locked` = '{1 if locked else 0}' WHERE `users`.`id` = {userId};"
            print(sql)
            cnt = cursor.execute(sql)
            self.conn.commit()
            return cnt != 0
        return False
    
    def getAllUsers(self) -> List[User]:
        users = []
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users;')
            for row in cursor.fetchall():
                users.append(User.fromRow(row))
        return users
    
    def getAthletes(self, userId: int) -> List[Athlete]:
        athletes = []
        with self.conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM athletes WHERE userId = {userId};')
            for row in cursor.fetchall():
                athletes.append(Athlete.fromRow(row))
        return athletes
    
    def getAthlete(self, athleteId: int) -> Athlete:
        with self.conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM athletes WHERE id = {athleteId};')
            return Athlete.fromRow(cursor.fetchone())
        return None
    
    def insertAthlete(self, givenname: str, surname: str, userId: int, birth: datetime, gender: Gender):
        with self.conn.cursor() as cursor:
            sql = f"INSERT INTO athletes (givenname, surname, userId, birth, gender) VALUES ('{givenname}', '{surname}', '{userId}','{birth}', {gender.value});"
            cnt = cursor.execute(sql)
            if cnt != 1:
                return None
            self.conn.commit()
            return cursor.lastrowid
        return None
