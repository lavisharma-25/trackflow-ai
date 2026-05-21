import json

from app.config import file_path

def load_data():
    with open(file_path, "r") as file:
        return json.load(file)

def save_data(data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)