# Esta clase establece un mapeado entre nombres e ids de la BD original

class Mapping():

    RAZAS = [
        "INDEX0",
        "Humanos",
        "Enanos",
        "Skaven",
        "Orcos",
        "Hombres lagarto",
        "Goblins",
        "Elfos silvanos",
        "Caos",
        "Elfos Oscuros",
        "No muertos",
        "Halflings",
        "Norse",
        "Amazonas",
        "Elfos pro",
        "Altos elfos",
        "Khemri",
        "Nigromantes",
        "Nurgle",
        "Ogros",
        "Vampiros",
        "Enanos del Caos",
        "Inframundo",
        "EQUIPO23",
        "Bretonia",
        "Kislev"
    ]

    @classmethod
    def ids_to_razas(cls, ids):
        return [Mapping.RAZAS[int(id)] for id in ids]

    @classmethod
    def razas_to_ids(cls, razas):
        return [list(Mapping.RAZAS).index(raza) for raza in razas]