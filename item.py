import random

class Item:
    """基础物品类"""
    def __init__(self, name, description, item_type, rarity="普通", value=0):
        self.name = name
        self.description = description
        self.item_type = item_type  # 装备、消耗品、材料、任务物品
        self.rarity = rarity  # 普通、优秀、稀有、传说
        self.value = value  # 物品价值
        self.stackable = False  # 默认不可堆叠
        self.stack_count = 1  # 堆叠数量
        
        # 物品图标 - 使用ASCII字符表示
        self.icon = "?"
        if item_type == "武器":
            self.icon = "⚔"
        elif item_type == "护甲":
            self.icon = "🛡"
        elif item_type == "消耗品":
            self.icon = "⚱"
        elif item_type == "材料":
            self.icon = "♦"
        elif item_type == "任务物品":
            self.icon = "!"
    
    def get_display_name(self):
        """获取带有稀有度颜色的显示名称"""
        if self.stack_count > 1:
            return f"{self.name} x{self.stack_count}"
        return self.name
    
    def get_color(self):
        """根据稀有度返回颜色"""
        if self.rarity == "传说":
            return (255, 150, 50)  # 橙色
        elif self.rarity == "稀有":
            return (150, 150, 255)  # 蓝色
        elif self.rarity == "优秀":
            return (150, 255, 150)  # 绿色
        else:
            return (255, 255, 255)  # 白色/普通
    
    def use(self, player):
        """使用物品"""
        return f"你使用了{self.name}，但没有特殊效果。"
    
    def can_stack_with(self, other_item):
        """检查是否可以与另一个物品堆叠"""
        if not self.stackable or not other_item.stackable:
            return False
        return (self.name == other_item.name and 
                self.item_type == other_item.item_type and
                self.rarity == other_item.rarity)

class Equipment(Item):
    """装备类，包括武器和护甲"""
    def __init__(self, name, description, equipment_type, stats, level_req=1, rarity="普通", value=0):
        super().__init__(name, description, equipment_type, rarity, value)
        self.stats = stats  # 字典形式的属性加成，如 {"attack": 5, "defense": 0}
        self.level_req = level_req  # 需要的等级/境界
        self.equipped = False
    
    def can_equip(self, player):
        """检查玩家是否能装备此物品"""
        return player.level >= self.level_req
    
    def equip(self, player):
        """玩家装备此物品"""
        if not self.can_equip(player):
            return f"你的境界不足以装备{self.name}。"
        
        # 根据装备类型装备到不同位置
        if self.item_type == "武器":
            # 先移除旧武器的属性加成
            if player.weapon != "无":
                for stat, value in player.weapon_stats.items():
                    if stat == "attack":
                        player.attack -= value
                    elif stat == "defense":
                        player.defense -= value
                    # 可以添加更多属性
            
            # 记录新武器和其属性
            player.weapon = self.name
            player.weapon_stats = self.stats
            
            # 应用新武器的属性加成
            for stat, value in self.stats.items():
                if stat == "attack":
                    player.attack += value
                elif stat == "defense":
                    player.defense += value
                # 可以添加更多属性
            
            return f"你装备了{self.name}。"
        
        elif self.item_type == "护甲":
            # 先移除旧护甲的属性加成
            if player.armor != "无":
                for stat, value in player.armor_stats.items():
                    if stat == "defense":
                        player.defense -= value
                    elif stat == "attack":
                        player.attack -= value
                    # 可以添加更多属性
            
            # 记录新护甲和其属性
            player.armor = self.name
            player.armor_stats = self.stats
            
            # 应用新护甲的属性加成
            for stat, value in self.stats.items():
                if stat == "defense":
                    player.defense += value
                elif stat == "attack":
                    player.attack += value
                # 可以添加更多属性
            
            return f"你装备了{self.name}。"
        
        return "无法装备此物品。"
    
    def use(self, player):
        """使用装备（装备它）"""
        return self.equip(player)

class Consumable(Item):
    """消耗品类，如药水、食物等"""
    def __init__(self, name, description, effects, rarity="普通", value=0):
        super().__init__(name, description, "消耗品", rarity, value)
        self.effects = effects  # 字典形式的效果，如 {"health": 20, "qi": 10}
        self.stackable = True  # 消耗品一般可堆叠
    
    def use(self, player):
        """使用消耗品，应用效果"""
        if self.stack_count <= 0:
            return "物品已用尽。"
        
        effect_desc = []
        for effect, value in self.effects.items():
            if effect == "health":
                player.restore_health(value)
                effect_desc.append(f"恢复{value}点生命")
            elif effect == "qi":
                player.restore_qi(value)
                effect_desc.append(f"恢复{value}点内力")
            # 可以添加更多效果类型
        
        self.stack_count -= 1
        
        if self.stack_count <= 0:
            # 如果数量为0，需要从玩家背包中移除
            return f"你使用了{self.name}，{', '.join(effect_desc)}。物品已用尽。"
        
        return f"你使用了{self.name}，{', '.join(effect_desc)}。剩余{self.stack_count}个。"

class Material(Item):
    """材料类，用于合成、任务等"""
    def __init__(self, name, description, source="", rarity="普通", value=0):
        super().__init__(name, description, "材料", rarity, value)
        self.source = source  # 材料来源描述
        self.stackable = True  # 材料一般可堆叠
    
    def use(self, player):
        """使用材料（一般无法直接使用）"""
        return f"{self.name}是一种材料，需要在合适的地方使用。"

class QuestItem(Item):
    """任务物品类，用于任务交互"""
    def __init__(self, name, description, quest_id, rarity="普通"):
        super().__init__(name, description, "任务物品", rarity, 0)
        self.quest_id = quest_id  # 关联的任务ID
        self.stackable = False  # 任务物品通常不可堆叠
    
    def use(self, player):
        """使用任务物品（提示相关任务）"""
        # 查找相关任务
        related_quest = None
        for quest in player.active_quests:
            if quest.id == self.quest_id:
                related_quest = quest
                break
        
        if related_quest:
            return f"{self.name}是任务[{related_quest.title}]需要的物品，找到相关NPC完成任务。"
        return f"{self.name}似乎是某个任务需要的物品。"

def generate_random_weapon(level, quality_modifier=0):
    """生成随机武器"""
    weapon_types = ["剑", "刀", "枪", "锤", "拳套"]
    materials = ["铁", "钢", "青铜", "精钢", "玄铁", "寒铁"]
    prefixes = ["锋利的", "沉重的", "坚固的", "平衡的", "破旧的", "精致的"]
    
    # 根据等级和品质修饰符决定稀有度
    rarity_chance = random.random() + quality_modifier
    if rarity_chance > 0.98:
        rarity = "传说"
        stat_multiplier = 2.5
    elif rarity_chance > 0.9:
        rarity = "稀有"
        stat_multiplier = 1.8
    elif rarity_chance > 0.7:
        rarity = "优秀"
        stat_multiplier = 1.3
    else:
        rarity = "普通"
        stat_multiplier = 1.0
    
    # 随机选择武器类型和材料
    weapon_type = random.choice(weapon_types)
    material = random.choice(materials)
    prefix = random.choice(prefixes)
    
    # 生成武器名称
    name = f"{prefix}{material}{weapon_type}"
    
    # 根据等级和稀有度计算基础属性
    base_attack = int((3 + level * 2) * stat_multiplier)
    stats = {"attack": base_attack}
    
    # 稀有度越高，可能有额外属性
    if rarity in ["稀有", "传说"]:
        stats["speed"] = random.randint(1, 3)
    if rarity == "传说":
        stats["qi_bonus"] = random.randint(5, 15)
    
    # 生成描述
    description = f"一件{rarity}级别的{weapon_type}，由{material}打造而成。"
    
    # 计算价值
    value = base_attack * 10 * (1 + ["普通", "优秀", "稀有", "传说"].index(rarity) * 0.5)
    
    return Equipment(name, description, "武器", stats, level, rarity, int(value))

def generate_random_armor(level, quality_modifier=0):
    """生成随机护甲"""
    armor_types = ["袍", "甲", "衣", "护具", "披风"]
    materials = ["布", "皮革", "锁子", "铁", "精钢", "玄铁"]
    prefixes = ["结实的", "轻盈的", "坚固的", "灵活的", "破旧的", "精致的"]
    
    # 根据等级和品质修饰符决定稀有度
    rarity_chance = random.random() + quality_modifier
    if rarity_chance > 0.98:
        rarity = "传说"
        stat_multiplier = 2.5
    elif rarity_chance > 0.9:
        rarity = "稀有"
        stat_multiplier = 1.8
    elif rarity_chance > 0.7:
        rarity = "优秀"
        stat_multiplier = 1.3
    else:
        rarity = "普通"
        stat_multiplier = 1.0
    
    # 随机选择护甲类型和材料
    armor_type = random.choice(armor_types)
    material = random.choice(materials)
    prefix = random.choice(prefixes)
    
    # 生成护甲名称
    name = f"{prefix}{material}{armor_type}"
    
    # 根据等级和稀有度计算基础属性
    base_defense = int((2 + level * 1.5) * stat_multiplier)
    stats = {"defense": base_defense}
    
    # 稀有度越高，可能有额外属性
    if rarity in ["稀有", "传说"]:
        stats["max_health"] = random.randint(10, 30)
    if rarity == "传说":
        stats["max_qi"] = random.randint(5, 15)
    
    # 生成描述
    description = f"一件{rarity}级别的{armor_type}，由{material}制成。"
    
    # 计算价值
    value = base_defense * 12 * (1 + ["普通", "优秀", "稀有", "传说"].index(rarity) * 0.5)
    
    return Equipment(name, description, "护甲", stats, level, rarity, int(value))

def generate_random_consumable(level):
    """生成随机消耗品"""
    consumable_types = [
        {"name": "回血丹", "effects": {"health": 20 + level * 10}},
        {"name": "气回丹", "effects": {"qi": 15 + level * 8}},
        {"name": "混元丹", "effects": {"health": 10 + level * 5, "qi": 10 + level * 5}},
        {"name": "小还丹", "effects": {"health": 30 + level * 15}}
    ]
    
    # 随机选择消耗品类型
    consumable = random.choice(consumable_types)
    
    # 根据等级决定稀有度
    if level >= 8:
        rarity = "稀有"
    elif level >= 4:
        rarity = "优秀"
    else:
        rarity = "普通"
    
    # 计算价值
    total_effect = sum(consumable["effects"].values())
    value = total_effect * (1 + ["普通", "优秀", "稀有"].index(rarity) * 0.3)
    
    # 生成描述
    effects_desc = []
    for effect, value in consumable["effects"].items():
        if effect == "health":
            effects_desc.append(f"恢复{value}点生命")
        elif effect == "qi":
            effects_desc.append(f"恢复{value}点内力")
    
    description = f"{rarity}级别的丹药，使用后可{', '.join(effects_desc)}。"
    
    # 创建消耗品对象
    item = Consumable(consumable["name"], description, consumable["effects"], rarity, int(value))
    
    # 随机设置堆叠数量
    item.stack_count = random.randint(1, 3)
    
    return item

def generate_random_material(monster_type=None):
    """生成随机材料，可以根据怪物类型生成特定材料"""
    if monster_type:
        if "狼" in monster_type:
            return Material("狼皮", "一张完整的狼皮，可以用来制作护具。", f"由{monster_type}身上获得", "普通", 15)
        elif "虎" in monster_type:
            return Material("虎骨", "珍贵的虎骨，是制作丹药的重要材料。", f"由{monster_type}身上获得", "优秀", 50)
        elif "蛇" in monster_type:
            return Material("蛇胆", "蛇胆，含有剧毒，也是珍贵的药材。", f"由{monster_type}身上获得", "普通", 25)
        elif "熊" in monster_type:
            return Material("熊掌", "珍贵的熊掌，是名贵的食材。", f"由{monster_type}身上获得", "优秀", 60)
        elif "山贼" in monster_type or "强盗" in monster_type:
            return Material("布料", "一些粗糙的布料，可用于制作简单的衣物。", f"由{monster_type}身上获得", "普通", 10)
    
    # 通用材料
    materials = [
        Material("草药", "常见的草药，可用于制作简单的药物。", "野外采集", "普通", 5),
        Material("兽皮", "一块普通的兽皮，可以用来制作简单的护具。", "由野兽身上获得", "普通", 12),
        Material("铁矿石", "一块含铁量较高的矿石，可以提炼出铁。", "矿洞中开采", "普通", 20),
        Material("木材", "一段结实的木材，可用于制作武器或建筑。", "森林中获取", "普通", 8)
    ]
    
    material = random.choice(materials)
    material.stack_count = random.randint(1, 5)
    return material

def generate_monster_drop(monster, player_level):
    """根据怪物生成掉落物品"""
    drops = []
    drop_chance = random.random()
    
    # 必定掉落的材料
    if hasattr(monster, "name"):
        material = generate_random_material(monster.name)
        material.stack_count = random.randint(1, 2)
        drops.append(material)
    
    # 概率掉落装备
    if drop_chance < 0.2:  # 20%几率掉落武器
        weapon = generate_random_weapon(player_level, quality_modifier=-0.2)
        drops.append(weapon)
    elif drop_chance < 0.35:  # 15%几率掉落护甲
        armor = generate_random_armor(player_level, quality_modifier=-0.2)
        drops.append(armor)
    
    # 概率掉落消耗品
    if random.random() < 0.4:  # 40%几率掉落消耗品
        consumable = generate_random_consumable(player_level)
        drops.append(consumable)
    
    return drops 