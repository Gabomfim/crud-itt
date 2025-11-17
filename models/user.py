class User:
    def __init__(self, username: str, password: str, age: int, description: str = ""):
        self.username = username
        self.password = password
        self.age = age
        self.description = description
