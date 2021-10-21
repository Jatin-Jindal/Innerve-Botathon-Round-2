equipments = {
    "🔪": {'name': "Knife",
           'desc': ("Knife! Melee Weapon that hits its mark almost every time!, but deals low damage!"
                    "\nChance to hit  :  **90%**\nDamage Dealt :  **10 - 20**")},
    "🏹": {'name': "Bow and Arrow",
           'desc': ("Bow and Arrow! Ranged Weapon that has a mediocre chance to hit, and deals mediocre damage!"
                    "\nChance to hit  :  **60%**\nDamage Dealt :  **40 - 50**")},
    "🔫": {'name': "Gun",
           'desc': ("Gun! Ranged Weapon that has the highest damage, but recoil makes it miss a few times!"
                    "\nChance to hit  :  **20%**\nDamage Dealt :  **90 - 100**")},
    # "🛡": {'name': "Shield",
    #        'desc': ("Shield! Protects you from enemies attack, but damages you if enemy's attack doesnt hit!"
    #                 "\nChance to activate  :  **Guaranteed if enemy attack connects**\nDamage Dealt :  **30-40**")},
    "🏥": {'name': "Potion",
           'desc': "Potion! Heals you a little. Limited Uses only"
                   "\nHP Healed  :  **20-30**\nMax. Uses :  **3**"}
}

starters = {
    "Kanto": {
        "fire": "Charmander",
        "water": "Squirtle",
        "grass": "Bulbasaur",
    },
    "Johto": {
        "fire": "Cyndaquil",
        "water": "Totodile",
        "grass": "Chikorita",
    },
    "Hoenn": {
        "fire": "Torchic",
        "water": "Mudkip",
        "grass": "Treecko",
    },
    "Sinnoh": {
        "fire": "Chimchar",
        "water": "Piplup",
        "grass": "Turtwig",
    },
    "Unova": {
        "fire": "Tepig",
        "water": "Oshawott",
        "grass": "Snivy",
    },
    "Kalos": {
        "fire": "Fennekin",
        "water": "Froakie",
        "grass": "Chespin",
    },
    "Alola": {
        "fire": "Litten",
        "water": "Popplio",
        "grass": "Rowlet",
    }
}

starterNames = set()
for i in starters.values():
    for j in i.values():
        starterNames.add(j.lower())


class pokedex:
    def __init__(self, user):
        self.pokedex = {}
        self.user = user
        self.length = 0

    def addEntry(self, catchName, catchImg):
        self.length += 1
        self.pokedex[self.length] = {'name': catchName, 'image': catchImg}


class Pokemon:
    def __init__(self, pokeNum, name, level, image, stats, types):
        self.id = pokeNum
        self.name = name
        self.level = level
        self.image = image
        self.stats = stats
        self.types = types

    def typeString(self) -> str:
        return '/'.join(i.capitalize() for i in self.types)
