import requests
import json
import os
import csv

from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS

from Mapping import Mapping

# aplicacion
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def index():
    return redirect(url_for("indice"))

@app.route("/indice")
def indice():
    data = []
    with open("clasificacion-circuito.csv") as fichero:
        lector = csv.DictReader(fichero)
        for indice, fila in enumerate(lector):
            if indice < 8:
                fila.update({"status": "clasificado"})
            data.append(fila)

    return json.dumps(data)

@app.route('/clasificacion-ccl/<idtournament>', methods=["GET"])
def clasificacion_ccl(idtournament):
    if request.method == "GET":
        compStandings = {
            "id": "compStandings",
            "idmap" : {
                "idcompetition": idtournament
            }
        }

        req = {
            "compStandings": {
                "id": "compStandings",
                "idmap": {
                    "idcompetition": idtournament,
                },
                "filters": {
                    "team_name": "[PI]",
                    "active": 1,
                },
                "ordercol": "sorting",
                "order": "desc",
                "limit": 256,
                "from": 0
            }
        }

        req = requests.get(f'https://www.mordrek.com:666/api/v1/queries?req={req}', verify=False)
        req = req.json()
        req = req["response"]["compStandings"]["result"]["rows"]
        lista_datos = [{
            "position": indice+1,
            "coach_name": fila[27],
            "team_name": fila[22],
            "race_name": Mapping.ids_to_razas([fila[21]])[0],
            "wins": fila[6],
            "draws": fila[7],
            "losses": fila[8],
            "ranking": fila[2],
            "td": fila[9],
            "cas": fila[12],
            "idteam": fila[20]
        } for indice, fila in enumerate(req)]

        colorear_clasificacion(lista_datos)

        return json.dumps(lista_datos)

def colorear_clasificacion(equipos) -> list:
        tama??o_top = 14
        tama??o_top_stunty = 1
        equipos_maximos_raza = 2

        equipos_super_clasificados = []
        equipos_clasificados = []
        equipos_no_clasificados = []

        indice = 0
        # Coloreo los super clasificados
        while indice < len(equipos):
            equipo = equipos[indice]
            if float(equipo["ranking"]) >= 75.00:
                equipo.update({"status": "super_clasificado"})
                equipos_super_clasificados.append(equipo)
                indice += 1
            else:
                break

        # Coloreo los equipos clasificados y los que lo estar??an pero no cumplen alg??n requisito
        while indice < len(equipos) and len(equipos_clasificados) < tama??o_top:
            equipo = equipos[indice]
            equipos_misma_raza = 0
            repetido = False
            for mejor_equipo in equipos_clasificados:
                if mejor_equipo["coach_name"] == equipo["coach_name"] or int(equipo["wins"]) + int(equipo["draws"]) + int(equipo["losses"]) > 40:
                    repetido = True
                    break
                if mejor_equipo["race_name"] == equipo["race_name"]:
                    equipos_misma_raza += 1
                if equipos_misma_raza >= equipos_maximos_raza:
                    break
            
            if equipos_misma_raza < 2 and not repetido:
                equipo.update({"status": "clasificado"})
                equipos_clasificados.append(equipo)
            else:
                equipo = equipo.update({"status": "no_clasificado"})
                equipos_no_clasificados.append(equipo)
            
            indice += 1

        # Cojo todos los equipos stunty
        ids_razas_stunty = Mapping.razas_to_ids(["Goblins", "Halflings", "Ogros"])
        equipos_stunty = list(filter(lambda equipo: equipo["race_name"] in ids_razas_stunty, equipos))

        # Quito los stunty que se han clasificado en intervalo verde
        ids_equipos_clasificados = [equipo["idteam"] for equipo in equipos_clasificados]
        equipos_stunty = list(filter(lambda equipo: equipo["idteam"] not in ids_equipos_clasificados, equipos_stunty))

        # Quito a los entrenadores en verde con stunty clasificado
        entrenadores_clasificados = [equipo["coach_name"] for equipo in equipos_clasificados]
        equipos_stunty = list(filter(lambda equipo: equipo["coach_name"] not in entrenadores_clasificados, equipos_stunty))

        # Si hay alg??n equipo stunty, asigno el top reservado a los stunties
        if equipos_stunty:
            for index in range(tama??o_top_stunty):
                top_stunty = equipos_stunty.pop(index)
                # Como est?? en el top, es verde
                top_stunty.update({"status": "clasificado"})
                equipos_clasificados.append(top_stunty)

                # Si el equipo estuviese en el grupo azul, ahora est?? en el verde, as?? que lo quito del azul
                if top_stunty in equipos_no_clasificados:
                    equipos_no_clasificados.remove(top_stunty)

        # Uno todos los resultados
        equipos_super_clasificados.extend(equipos_clasificados)
        equipos_super_clasificados.extend(equipos_no_clasificados)
        return equipos_super_clasificados

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 30504)), debug=True)