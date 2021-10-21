import requests as r


def fetch_data(pokeNumber):
    response = r.get(f"https://pokeapi.co/api/v2/pokemon/{pokeNumber}/")
    data = response.json()

    pokeNum = data["id"]
    name = data["name"]
    image = data["sprites"]["other"]["official-artwork"]["front_default"]
    types = [i["type"]["name"] for i in data["types"] if type(i) == dict]

    return {"id": pokeNum, "name": name, "image": image, "types": types}


def fetch_data_by_name(name):
    response = r.get(f"https://pokeapi.co/api/v2/pokemon/{name}/")
    data = response.json()

    pokeNum = data["id"]
    name = data["name"]
    image = data["sprites"]["other"]["official-artwork"]["front_default"]
    types = [i["type"]["name"] for i in data["types"] if type(i) == dict]

    return {"id": pokeNum, "name": name, "image": image, "types": types}
