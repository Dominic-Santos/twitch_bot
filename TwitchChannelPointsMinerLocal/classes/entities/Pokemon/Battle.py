import jwt
import json
from .Utils import check_output_folder, save_to_file

WEAKNESS_CHART = {
    "Normal": {"Fighting": 2, "Ghost": 0},
    "Fire": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Ice": 0.5, "Ground": 2, "Bug": 0.5, "Rock": 2, "Steel": 0.5, "Fairy": 0.5},
    "Water": {"Fire": 0.5, "Water": 0.5, "Electric": 2, "Grass": 2, "Ice": 0.5, "Steel": 0.5},
    "Electric": {"Electric": 0.5, "Ground": 2, "Flying": 0.5, "Steel": 0.5},
    "Grass": {"Fire": 2, "Water": 0.5, "Electric": 0.5, "Grass": 0.5, "Ice": 2, "Poison": 2, "Ground": 0.5, "Flying": 2, "Bug": 2},
    "Ice": {"Fire": 2, "Ice": 0.5, "Fighting": 2, "Rock": 2, "Steel": 2},
    "Fighting": {"Flying": 2, "Psychic": 2, "Bug": 0.5, "Rock": 0.5, "Dark": 0.5, "Fairy": 2},
    "Poison": {"Grass": 0.5, "Fighting": 0.5, "Poison": 0.5, "Ground": 2, "Psychic": 2, "Bug": 0.5, "Fairy": 0.5},
    "Ground": {"Water": 2, "Electric": 0, "Grass": 2, "Ice": 2, "Poison": 0.5, "Rock": 0.5},
    "Flying": {"Electric": 2, "Grass": 0.5, "Ice": 2, "Fighting": 0.5, "Ground": 0, "Bug": 0.5, "Rock": 2},
    "Psychic": {"Fighting": 0.5, "Psychic": 0.5, "Bug": 2, "Ghost": 2, "Dark": 2},
    "Bug": {"Fire": 2, "Grass": 0.5, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Rock": 2},
    "Rock": {"Normal": 0.5, "Fire": 0.5, "Water": 2, "Grass": 2, "Fighting": 2, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Steel": 2},
    "Ghost": {"Normal": 0, "Fighting": 0, "Poison": 0.5, "Bug": 0.5, "Ghost": 2, "Dark": 2},
    "Dragon": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Grass": 0.5, "Ice": 2, "Dragon": 2, "Fairy": 2},
    "Dark": {"Fighting": 2, "Psychic": 0, "Bug": 2, "Ghost": 0.5, "Dark": 0.5, "Fairy": 2},
    "Steel": {"Normal": 0.5, "Fire": 2, "Grass": 0.5, "Ice": 0.5, "Fighting": 2, "Poison": 0, "Ground": 2, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 0.5, "Dragon": 0.5, "Steel": 0.5, "Fairy": 0.5},
    "Fairy": {"Fighting": 0.5, "Poison": 2, "Bug": 0.5, "Dragon": 0, "Dark": 0.5, "Steel": 2}
}


def decode(data):
    try:
        decoded = jwt.decode(data, options={"verify_signature": False})
        return json.loads(decoded["content"])
    except Exception as e:
        print(e)
    return None


def weakness_resistance(attack_type, defender_types):
    effective = 1
    for def_type in defender_types:
        effective = effective * WEAKNESS_CHART[def_type].get(attack_type, 1)

    return effective


class Battle():
    def __init__(self):
        self.team = {}
        self.enemy_team = {}
        self.action = 0
        self.battle_id = 0
        self.player_id = 0
        self.battle_key = ""
        self.state = "continue"
        self.log = []
        self.result = None
        self.rewards = ""

    def save_log(self):
        check_output_folder(f"battles/{self.battle_id}_{self.battle_key}")
        with open(f"battles/{self.battle_id}_{self.battle_key}/log.txt", "w") as f:
            for line in self.log:
                f.write(line + "\n")

    def set_battle(self, battle_id, player_id, unique_battle_key):
        self.battle_id = battle_id
        self.player_id = player_id
        self.battle_key = unique_battle_key

    def save_action(self, data):
        check_output_folder(f"battles/{self.battle_id}_{self.battle_key}")
        save_to_file(f"battles/{self.battle_id}_{self.battle_key}/{self.action}.json", data)

    def run_action(self, data):
        self.state = "continue"

        if "data" in data:
            data["decoded"] = decode(data["data"])

        action = data["action"]

        if action in ["INIT", "RE_INIT"]:
            self.action_init(data["decoded"])
        elif action == "AWAITING_NEXT_MOVE":
            # wait for player to use an attack or switch (or quit)
            self.state = "move"
        elif action == "AWAITING_NEXT_POKEMON":
            # player pokemon died, must switch
            self.state = "switch"
        elif action == "START_LOG":
            # clears the app text, does nothing
            self.log.append("")
        elif action == "LOG":
            # could be many things
            result = self.action_log(data["decoded"])
            if result is False:
                self.log.append(f"Unknown LOG action {data['decoded']['type']} ({self.action})")
                self.save_action(data)
        elif action == "ANIMATION":
            # animations do nothing
            pass
        elif action == "DAMAGE":
            # damage is delt
            self.action_damage(data["decoded"])
        elif action == "END":
            # battle ended
            self.action_end(data["decoded"])
        elif action == "KO":
            # pokemon ko'ed
            self.action_ko(data["decoded"])
        elif action == "WAIT":
            self.state = "switch"
        else:
            self.log.append(f"Unknown action {action} ({self.action})")
            self.save_action(data)

        self.action = self.action + 1
        # maybe remove this if all goes well with testing
        self.save_log()

    def action_ko(self, data):
        if self.team["current_pokemon"] == data["pokemon"]:
            prefix, pokemon = self._get_pokemon(self.player_id, data["pokemon"])
            self.team["pokemon"][str(data["pokemon"])]["hp"] = 0
        else:
            prefix, pokemon = self._get_pokemon(0, data["pokemon"])
            self.enemy_team["pokemon"][str(data["pokemon"])]["hp"] = 0
        self.log.append(f"{prefix} {pokemon['name']} fainted")

    def action_end(self, data):
        self.state = "end"
        self.result = True if data["loser"] != self.player_id else False
        prefix = "winner" if self.result else "loser"
        xp = data[prefix + "_xp"]
        cash = data[prefix + "_cash"]
        self.rewards = f"{xp}Exp and {cash}$"
        self.log.append(f"\nYou are the {prefix}!\nYou got {self.rewards}")
        self.save_log()

    def action_damage(self, data):
        self._apply_damage(data["player"], data["pokemon"], data["damage"])
        prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])

        self.log.append(f"{prefix} {pokemon['name']} took {data['damage']} damage")
        self.log.append(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")

    def _get_pokemon(self, player, pokemon):
        if player == self.player_id:
            prefix = "My"
            pokemon = self.team["pokemon"][str(pokemon)]
        else:
            prefix = "Enemy"
            pokemon = self.enemy_team["pokemon"][str(pokemon)]

        return prefix, pokemon

    def _apply_damage(self, player, pokemon, damage):
        if player == self.player_id:
            self.team["pokemon"][str(pokemon)]["hp"] = self.team["pokemon"][str(pokemon)]["hp"] - damage
        else:
            self.enemy_team["pokemon"][str(pokemon)]["hp"] = self.enemy_team["pokemon"][str(pokemon)]["hp"] - damage

    def _use_move(self, player, pokemon, move):
        if player == self.player_id:
            self.team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] = self.team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] - 1
            return self.team["pokemon"][str(pokemon)]["moves"][str(move)]["name"]
        else:
            self.enemy_team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] = self.enemy_team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] - 1
            return self.enemy_team["pokemon"][str(pokemon)]["moves"][str(move)]["name"]

    def action_log(self, data):
        if "player" in data and "pokemon" in data:
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])

        typ = data["type"]

        if typ == "ATTACK_MISSED":
            self.log.append(f"Attack missed")
        elif typ == "BURN_APPLIED":
            self.log.append(f"{prefix} {pokemon['name']} was burned")
        elif typ == "BURN_DAMAGE":
            self._apply_damage(data["player"], data["pokemon"], data["damage"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log.append(f"{prefix} {pokemon['name']} took {data['damage']} burn damage")
            self.log.append(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ == "CONFUSED":
            self.log.append(f"{prefix} {pokemon['name']} is confused")
        elif typ == "CONFUSION_APPLIED":
            self.log.append(f"{prefix} {pokemon['name']} was confused")
        elif typ == "CRITICAL_HIT":
            self.log.append("Critical Hit")
        elif typ == "END_CONFUSION":
            self.log.append(f"{prefix} {pokemon['name']} is not confused anymore")
        elif typ == "END_MAGNET_RISE":
            self.log.append(f"{prefix} {pokemon['name']} magnet rise ended")
        elif typ == "FLINCHED":
            self.log.append(f"{prefix} {pokemon['name']} flinched")
        elif typ == "FREEZE_APPLIED":
            self.log.append(f"{prefix} {pokemon['name']} was frozen")
        elif typ == "HAZE_USED":
            self.log.append("Haze used")
        elif typ == "HEALED":
            self._apply_damage(data["player"], data["pokemon"], 0 - data["heal"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log.append(f"{prefix} {pokemon['name']} healed {data['heal']} damage")
            self.log.append(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ == "IS_FROZEN":
            self.log.append(f"{prefix} {pokemon['name']} is frozen")
        elif typ == "IS_PARALYZED":
            self.log.append(f"{prefix} {pokemon['name']} can't attack due to paralysis")
        elif typ == "IS_SLEEPING":
            self.log.append(f"{prefix} {pokemon['name']} is asleep")
        elif typ == "MOVE_EFFECTIVE":
            self.log.append(f"Effective x{data['factor']}")
        elif typ == "MOVE_FAILED":
            self.log.append("Move Failed")
        elif typ == "MOVE_USED":
            move_name = self._use_move(data["player"], data["pokemon"], data["move"])
            self.log.append(f"{prefix} {pokemon['name']} used {move_name}")
        elif typ == "MOVE_USED_NAME":
            self.log.append(f"{prefix} {pokemon['name']} used {data['move']}")
        elif typ == "MULTIPLE_HITS":
            self.log.append(f"Attack hit {data['amount']} times")
        elif typ == "PARALYSIS_APPLIED":
            self.log.append(f"{prefix} {pokemon['name']} was paralyzed")
        elif typ == "POISON_APPLIED":
            self.log.append(f"{prefix} {pokemon['name']} was poisoned")
        elif typ == "POISON_DAMAGE":
            self._apply_damage(data["player"], data["pokemon"], data["damage"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log.append(f"{prefix} {pokemon['name']} took {data['damage']} poison damage")
            self.log.append(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ == "POKEMON_CHANGED":
            if self.team["current_pokemon"] == data["last_pokemon"]:
                prefix, last = self._get_pokemon(self.player_id, data["last_pokemon"])
                prefix, current = self._get_pokemon(self.player_id, data["current_pokemon"])
                self.team["current_pokemon"] = data["current_pokemon"]
            else:
                prefix, last = self._get_pokemon(0, data["last_pokemon"])
                prefix, current = self._get_pokemon(0, data["current_pokemon"])
                self.enemy_team["current_pokemon"] = data["current_pokemon"]
            self.log.append(f"Switched {prefix} {last['name']} for {current['name']}")
            self.log.append(f"Current HP {current['hp']}/{current['max_hp']}")
        elif typ == "RECOIL_APPLIED":
            self.log.append("Hurt by recoil")
        elif typ == "SANDSTORM_STARTED":
            self.log.append("Sandstorm started")
        elif typ == "SLEEP_APPLIED":
            self.log.append(f"{prefix} {pokemon['name']} fell asleep")
        elif typ == "STAT_CHANGED":
            self.log.append(f"{prefix} {pokemon['name']} {data['stat']} changed by {data['change_by']}")
        elif typ == "TOXIC_APPLIED":
            self.log.append(f"{prefix} {pokemon['name']} was badly poisoned")
        elif typ == "TRICK_ROOM_STARTED":
            self.log.append("Trick room started")
        elif typ == "TRICK_ROOM_END":
            self.log.append("Trick room ended")
        elif typ == "UNTHAWED":
            self.log.append(f"{prefix} {pokemon['name']} unthawed")
        elif typ == "WOKE_UP":
            self.log.append(f"{prefix} {pokemon['name']} woke up")
        else:
            return False
        return True

    def action_init(self, data):
        if "actionNo" in data:
            self.action = data["actionNo"] - 1
            self.log.append("Reconnected to Battle\n")
        else:
            self.log.append("Connected to Battle\n")

        for player in data["players"]:
            if player == str(self.player_id):
                self.team = data["players"][player]
            else:
                self.enemy_team = data["players"][player]

        for team in [self.team, self.enemy_team]:
            for pokemon_id in team["pokemon"]:
                pokemon_data = team["pokemon"][pokemon_id]
                self.log.append(f"{pokemon_data['name']} {pokemon_data['hp']}/{pokemon_data['max_hp']}")
            self.log.append("")
