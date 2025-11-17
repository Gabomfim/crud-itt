from models.user import User

# Initialize users
lavinia = User(username="lavinia", password="1234", age=16, description="Odeio sushi")
gabriel = User(
    username="gabriel", password="5678", age=26, description="Gosto de morango"
)

lista_de_usuarios = [lavinia, gabriel]
