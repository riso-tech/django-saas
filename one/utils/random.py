import random
import string


def generate_random_string(length=16):
    characters = string.ascii_letters + string.digits  # You can add more characters if needed
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string
