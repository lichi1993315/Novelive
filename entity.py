class Entity:
    def __init__(self, x, y, char):
        self.x = x
        self.y = y
        self.char = char

class NPC(Entity):
    def __init__(self, x, y, char, greeting):
        super().__init__(x, y, char)
        self.greeting = greeting
        self.dialogs = [greeting]
        self.current_dialog = 0
        self.quests = []
    
    def add_dialog(self, dialog):
        self.dialogs.append(dialog)
    
    def get_next_dialog(self):
        if self.current_dialog < len(self.dialogs):
            dialog = self.dialogs[self.current_dialog]
            self.current_dialog += 1
            return dialog
        return None
    
    def reset_dialog(self):
        self.current_dialog = 0
    
    def add_quest(self, quest):
        self.quests.append(quest)
    
    def get_available_quests(self):
        return [quest for quest in self.quests if not quest.completed]

class Monster(Entity):
    def __init__(self, x, y, char, name, health=100, attack=10, defense=5, experience=50):
        super().__init__(x, y, char)
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.experience = experience
        self.loot = []
    
    def take_damage(self, amount):
        actual_damage = max(1, amount - self.defense)
        self.health -= actual_damage
        return actual_damage
    
    def is_alive(self):
        return self.health > 0
    
    def get_attack_damage(self):
        # Add some randomness to monster attacks
        import random
        variance = 0.2  # 20% variance
        multiplier = 1.0 + random.uniform(-variance, variance)
        return int(self.attack * multiplier)
    
    def add_loot(self, item, drop_chance=1.0):
        # drop_chance is between 0.0 and 1.0
        self.loot.append((item, drop_chance))
    
    def get_loot(self):
        import random
        dropped_items = []
        for item, chance in self.loot:
            if random.random() <= chance:
                dropped_items.append(item)
        return dropped_items

class Item:
    def __init__(self, name, item_type, value, description):
        self.name = name
        self.item_type = item_type  # weapon, armor, potion, quest_item, etc.
        self.value = value
        self.description = description
    
    def use(self, player):
        # Default implementation, to be overridden by subclasses
        pass

class Weapon(Item):
    def __init__(self, name, attack_bonus, value, description):
        super().__init__(name, "weapon", value, description)
        self.attack_bonus = attack_bonus
    
    def use(self, player):
        player.weapon = self.name
        player.attack += self.attack_bonus

class Armor(Item):
    def __init__(self, name, defense_bonus, value, description):
        super().__init__(name, "armor", value, description)
        self.defense_bonus = defense_bonus
    
    def use(self, player):
        player.armor = self.name
        player.defense += self.defense_bonus

class Potion(Item):
    def __init__(self, name, health_restore, qi_restore, value, description):
        super().__init__(name, "potion", value, description)
        self.health_restore = health_restore
        self.qi_restore = qi_restore
    
    def use(self, player):
        player.restore_health(self.health_restore)
        player.restore_qi(self.qi_restore)

class QuestItem(Item):
    def __init__(self, name, quest_id, description):
        super().__init__(name, "quest_item", 0, description)
        self.quest_id = quest_id 