import pymysql.cursors
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class Restrictions(Enum):
    TRAINER = 0
    ADMIN = 1

@dataclass
class User:
    id: int
    username: str
    email: str
    registered: datetime
    expires: datetime
    restrictions: Restrictions
    locked: bool


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
           user = cursor.fetchone()
           return user['password'] == password

    def getUser(self, id: int) -> User:
        with self.conn.cursor() as cursor:
           cursor.execute(f'SELECT * FROM users WHERE id="{id}";')
           row = cursor.fetchone()
           return User(id, row['username'], row['email'], row['registered'], row['expires'], Restrictions(row['restrictions']), row['locked'])
        return None

    def insertUser(self, username: str, password: str, email:str, restrictions: Restrictions) -> int:
        locked = 0
        with self.conn.cursor() as cursor:
            sql = f"INSERT INTO users (username, password, email, registered, expires, restrictions, locked) VALUES ('{username}', '{password}', '{email}', '{datetime.now()}', '{datetime.now() + timedelta(weeks=300)}', {restrictions.value}, {locked});"
            cnt = cursor.execute(sql)
            if cnt != 1:
                return None
            self.conn.commit()
            return cursor.lastrowid
        return None
    
    def removeUser(self, id: int) -> bool:
        with self.conn.cursor() as cursor:
            sql = f"DELETE FROM `users` WHERE `users`.`id` = {id} ;"
            cnt = cursor.execute(sql)
            return cnt != 0
        return False