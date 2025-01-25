from dataclasses import asdict
import math
from typing import Union
from fastapi import FastAPI, HTTPException, Path
from models.pokemon import Pokemon
import json

# ouverture et chargement de la liste des pokemons
with open("pokemons.json", "r") as f:
    pokemons_list = json.load(f)
list_pokemons: dict[int, any] = {
    key + 1: value for key, value in enumerate(pokemons_list)
}


# ---------------------DEFINITION DE L'APPLICATION----------------------------------

app = FastAPI(title="Api de pokemons")


# récupération du nombre total de pokemons
@app.get("/total_pokemons")
def get_total_pokemons() -> dict:
    return {"total": len(list_pokemons)}


# liste des pokemons
@app.get("/pokemons")
def get_all_pokemons() -> list[Pokemon]:
    response = [Pokemon(**list_pokemons[id]) for id in list_pokemons]
    return response


# pokemons avec une pagination
@app.get("/pokemons2/")
def get_all_pokemons(page: int = 1, items: int = 10) -> list[Pokemon]:
    items = min(items, 20)  # pas plus de 20 pokemons par page et pas moins de 10
    max_page = math.ceil(len(list_pokemons) / items)
    current_page = min(page, max_page)
    start = (current_page - 1) * items
    stop = start + items if start + items <= len(list_pokemons) else len(list_pokemons)
    sublist = (list(list_pokemons))[start:stop]

    response = []

    for id in sublist:
        response.append(Pokemon(**list_pokemons[id]))
    return response


# optenir un pokemons en particulier
@app.get("/pokemon/{id}")
def get_pokemons_by_id(id: int = Path(ge=1)) -> Pokemon:
    if id not in list_pokemons:
        raise HTTPException(status_code=404, detail="Ce pokemons n'exste pas ")

    return Pokemon(**list_pokemons[id])


# ajout d'un pokemons
@app.post("/pokemon/")
def create_pokemon(pokemon: Pokemon) -> Pokemon:
    if pokemon.id in list_pokemons:
        raise HTTPException(
            status_code=404, detail=f"Le pokemons {pokemon.id} existe déja"
        )
    list_pokemons[pokemon.id] = asdict(pokemon)
    return pokemon


# modification d'un pokemon
@app.put("/pokemon/{id}")
def update_pokemon(pokemon: Pokemon, id: int = Path(ge=1)) -> Pokemon:
    if id not in list_pokemons:
        raise HTTPException(status_code=404, detail="Ce pokemons n'exste pas ")
    list_pokemons[id] = asdict(pokemon)
    return pokemon


# suppression d'un pokemon
@app.delete("/pokemon/{id}")
def delete_pokemin(id: int = Path(ge=1)) -> Pokemon:
    if id not in list_pokemons:
        raise HTTPException(status_code=404, detail="Ce pokemons n'exste pas ")
    pokemon = Pokemon(**list_pokemons[id])
    del list_pokemons[id]
    return pokemon


# types de pokemons
#  TODO: faire la liste des type des pokemons


# recherche sur les pokemons
@app.get("/pokemons/search/")
def search_pokemons(
    types: Union[str, None] = None,
    evo: Union[str, None] = None,
    totalgt: Union[int, None] = None,
    totallt: Union[int, None] = None,
    sortby: Union[str, None] = None,
    order: Union[str, None] = None,
) -> Union[list[Pokemon], None]:
    filtered_list = []
    response = []

    # filtre sur les types
    if type is not None:
        for pokemon in pokemons_list:
            if set(types.split(",")).issubset(
                pokemon["types"]
            ):  # issubset test si un ensemble est dans l'autre
                filtered_list.append(pokemon)

    # on trie su rles ebolutions
    if evo is not None:
        tmp = filtered_list if filtered_list else pokemons_list
        new = []
        for pokemon in tmp:
            if evo == "true" and "evolution_id" in pokemon:
                new.append(pokemon)
            if evo == "false" and "evolution_id" not in pokemon:
                new.append(pokemon)
        filtered_list = new

    # on filtre sur greater than total

    if totalgt is not None:
        tmp = filtered_list if filtered_list else pokemons_list
        new = []
        for pokemon in tmp:
            if pokemon["total"] > totalgt:
                new.append(pokemon)
        filtered_list = new

    # on filtre sur le less yhan total
    if totallt is not None:
        tmp = filtered_list if filtered_list else pokemons_list
        new = []
        for pokemon in tmp:
            if pokemon["total"] < totallt:
                new.append(pokemon)
        filtered_list = new
    # on gere le trie
    if sortby is not None and sortby in ["id", "name", "total"]:
        filtered_list = filtered_list if filtered_list else pokemons_list
        sorting_order = False
        if order == "asc":
            sorting_order = False
        if order == "desc":
            sorting_order = True
        filtered_list = sorted(
            filtered_list, key=lambda d: d[sortby], reverse=sorting_order
        )

    # Reponse
    if filtered_list:
        for pokemon in filtered_list:
            response.append(Pokemon(**pokemon))
        return response
    raise HTTPException(
        status_code=404, detail="Aucun pokemins ne répond aux critères de recherche"
    )
