class HeartMethod:
    """
    心法基类，包含所有心法的共同属性和方法
    """
    def __init__(self, name, description, attribute_bonuses=None, qi_attribute=None):
        self.name = name  # 心法名称
        self.description = description  # 心法描述
        self.attribute_bonuses = attribute_bonuses or {}  # 心法带来的属性加成
        self.qi_attribute = qi_attribute or "neutral"  # 内力属性：金、木、水、火、土、混元等
        self.core_abilities = []  # 核心能力列表
    
    def apply_bonuses(self, player):
        """将心法加成应用到玩家属性上"""
        for attr, value in self.attribute_bonuses.items():
            if hasattr(player, attr):
                current = getattr(player, attr)
                if isinstance(current, (int, float)):
                    setattr(player, attr, current + value)
    
    def add_core_ability(self, ability):
        """添加核心能力"""
        self.core_abilities.append(ability)
    
    def get_core_abilities(self):
        """获取所有核心能力"""
        return self.core_abilities


class InbornHeartMethod(HeartMethod):
    """
    先天心法，玩家出生就具备的基本心法
    """
    def __init__(self, name, description, attribute_bonuses=None, qi_attribute=None):
        super().__init__(name, description, attribute_bonuses, qi_attribute)
        self.low_level_core_abilities = []  # 低阶核心能力（任脉）
        self.high_level_core_abilities = []  # 高阶核心能力（督脉）
        self.selected_low_ability = None  # 已选择的低阶核心能力
        self.selected_high_ability = None  # 已选择的高阶核心能力
        self.level = 1  # 心法等级，初始为1级
    
    def add_low_level_ability(self, ability):
        """添加低阶核心能力选项"""
        self.low_level_core_abilities.append(ability)
    
    def add_high_level_ability(self, ability):
        """添加高阶核心能力选项"""
        self.high_level_core_abilities.append(ability)
    
    def select_low_level_ability(self, index, player):
        """选择低阶核心能力"""
        if 0 <= index < len(self.low_level_core_abilities):
            self.selected_low_ability = self.low_level_core_abilities[index]
            # 将能力添加到核心能力列表
            self.add_core_ability(self.selected_low_ability)
            # 应用能力效果
            self.selected_low_ability.apply(player)
            return True
        return False
    
    def select_high_level_ability(self, index, player):
        """选择高阶核心能力"""
        if 0 <= index < len(self.high_level_core_abilities):
            self.selected_high_ability = self.high_level_core_abilities[index]
            # 将能力添加到核心能力列表
            self.add_core_ability(self.selected_high_ability)
            # 应用能力效果
            self.selected_high_ability.apply(player)
            return True
        return False
    
    def can_select_low_ability(self, player):
        """检查是否可以选择低阶能力"""
        # 八品境界（蕴气）解锁低阶能力
        return player.level <= 8 and self.selected_low_ability is None
    
    def can_select_high_ability(self, player):
        """检查是否可以选择高阶能力"""
        # 六品境界（凝罡）解锁高阶能力
        return player.level <= 6 and self.selected_high_ability is None
        
    def increase_level(self):
        """提升心法等级"""
        self.level += 1
        return self.level


class AcquiredHeartMethod(HeartMethod):
    """
    后天心法，通过学习获得的辅助心法
    """
    def __init__(self, name, description, required_level, attribute_bonuses=None, qi_attribute=None):
        super().__init__(name, description, attribute_bonuses, qi_attribute)
        self.required_level = required_level  # 学习所需的境界等级（数字越小境界越高）
        self.level = 1  # 心法等级，初始为1级
    
    def can_learn(self, player):
        """检查玩家是否可以学习此心法"""
        # 五品境界（意动）解锁后天心法
        return player.level <= 5 and player.level <= self.required_level
        
    def increase_level(self):
        """提升心法等级"""
        self.level += 1
        return self.level


class CoreAbility:
    """
    核心能力，心法解锁的特殊能力
    """
    def __init__(self, name, description, effects=None):
        self.name = name  # 能力名称
        self.description = description  # 能力描述
        self.effects = effects or {}  # 能力效果
    
    def apply(self, player):
        """将能力效果应用到玩家身上"""
        for attr, value in self.effects.items():
            if hasattr(player, attr):
                current = getattr(player, attr)
                if isinstance(current, (int, float)):
                    setattr(player, attr, current + value)


class HeartMethodSystem:
    """
    心法系统，管理所有心法
    """
    def __init__(self):
        self.inborn_heart_methods = self._initialize_inborn_heart_methods()
        self.acquired_heart_methods = self._initialize_acquired_heart_methods()
    
    def _initialize_inborn_heart_methods(self):
        """初始化所有先天心法"""
        heart_methods = {}
        
        # 太极心法
        taiji = InbornHeartMethod(
            "太极心法", 
            "源自武当派的内家拳法根基，讲究以柔克刚，以静制动，阴阳相济。",
            {"max_qi": 20, "defense": 5, "qi_recovery": 2},
            "neutral"
        )
        
        # 太极心法的低阶核心能力（任脉）
        taiji.add_low_level_ability(CoreAbility(
            "化劲", 
            "能够将敌人的攻击力转化为己用，增加防御能力。",
            {"defense_bonus": 10, "counter_chance": 0.2}
        ))
        taiji.add_low_level_ability(CoreAbility(
            "太极气旋", 
            "形成气旋护体，提高闪避能力和移动速度。",
            {"dodge_chance": 0.15, "speed": 3}
        ))
        taiji.add_low_level_ability(CoreAbility(
            "气沉丹田", 
            "内力更加凝练，提高内力上限和恢复速度。",
            {"max_qi": 30, "qi_recovery": 3}
        ))
        
        # 太极心法的高阶核心能力（督脉）
        taiji.add_high_level_ability(CoreAbility(
            "阴阳调和", 
            "平衡阴阳之力，使所有属性得到全面提升。",
            {"attack": 10, "defense": 10, "speed": 5, "max_health": 50, "max_qi": 50}
        ))
        taiji.add_high_level_ability(CoreAbility(
            "四两拨千斤", 
            "以巧劲卸力，极大提升防御能力，并有几率反弹伤害。",
            {"defense": 20, "reflect_damage_chance": 0.3, "reflect_damage_percent": 0.5}
        ))
        taiji.add_high_level_ability(CoreAbility(
            "太极无极", 
            "达到太极拳法的至高境界，攻防一体，使攻击力基于防御力获得额外加成。",
            {"attack_from_defense_ratio": 0.5}  # 攻击力额外获得防御力的50%加成
        ))
        
        heart_methods["taiji"] = taiji
        
        # 少林心法
        shaolin = InbornHeartMethod(
            "少林心法", 
            "少林寺独传内功，注重内外兼修，刚柔并济，以禅入武。",
            {"max_health": 30, "attack": 8},
            "earth"
        )
        
        # 少林心法的低阶核心能力
        shaolin.add_low_level_ability(CoreAbility(
            "金钟罩", 
            "修炼全身气血，大幅提高生命上限和防御力。",
            {"max_health": 80, "defense": 8}
        ))
        shaolin.add_low_level_ability(CoreAbility(
            "易筋经", 
            "改变筋骨结构，提高攻击力和暴击率。",
            {"attack": 15, "critical_chance": 0.1}
        ))
        shaolin.add_low_level_ability(CoreAbility(
            "洗髓经", 
            "净化全身精元，提高内力上限和各种抗性。",
            {"max_qi": 40, "all_resistance": 10}
        ))
        
        # 少林心法的高阶核心能力
        shaolin.add_high_level_ability(CoreAbility(
            "拈花指", 
            "以禅入武的点穴绝技，增加攻击的穿透力和命中要害的几率。",
            {"armor_penetration": 20, "vital_hit_chance": 0.2}
        ))
        shaolin.add_high_level_ability(CoreAbility(
            "大力金刚指", 
            "刚猛无比的指力，极大提升攻击力和破防能力。",
            {"attack": 25, "defense_break": 15}
        ))
        shaolin.add_high_level_ability(CoreAbility(
            "达摩一苇", 
            "传说中达摩祖师渡江的绝学，提高闪避能力和移动速度。",
            {"dodge_chance": 0.2, "speed": 8, "counterattack_chance": 0.15}
        ))
        
        heart_methods["shaolin"] = shaolin
        
        return heart_methods
    
    def _initialize_acquired_heart_methods(self):
        """初始化所有后天心法"""
        heart_methods = {}
        
        # 九阳神功
        jiuyang = AcquiredHeartMethod(
            "九阳神功", 
            "明教至高无上的内功心法，阳刚至极，能化解百毒，增强体质。",
            5,  # 需要五品境界（意动）
            {"max_health": 100, "qi_recovery": 5, "poison_resistance": 0.8},
            "fire"
        )
        
        # 九阳神功的核心能力
        jiuyang.add_core_ability(CoreAbility(
            "九阳护体", 
            "运转九阳真气护体，获得持续的生命恢复效果。",
            {"health_regeneration": 5}
        ))
        jiuyang.add_core_ability(CoreAbility(
            "阳炎爆", 
            "引爆体内阳气，对周围敌人造成火属性伤害。",
            {"fire_damage_bonus": 0.3, "area_damage": 15}
        ))
        
        heart_methods["jiuyang"] = jiuyang
        
        # 北冥神功
        beiming = AcquiredHeartMethod(
            "北冥神功", 
            "逍遥派独门绝学，能吸收他人内力为己用，化为己身内力。",
            4,  # 需要四品境界（显形）
            {"max_qi": 120, "energy_absorb": 0.2},
            "water"
        )
        
        # 北冥神功的核心能力
        beiming.add_core_ability(CoreAbility(
            "吸星大法", 
            "能够吸收敌人的内力恢复自身内力。",
            {"qi_steal_per_hit": 5}
        ))
        beiming.add_core_ability(CoreAbility(
            "寒冰真气", 
            "运转寒冰真气，攻击附带冰冻效果。",
            {"freeze_chance": 0.15, "freeze_duration": 2}
        ))
        
        heart_methods["beiming"] = beiming
        
        return heart_methods
    
    def get_inborn_heart_method(self, key):
        """获取指定的先天心法"""
        return self.inborn_heart_methods.get(key)
    
    def get_acquired_heart_method(self, key):
        """获取指定的后天心法"""
        return self.acquired_heart_methods.get(key)
    
    def get_all_inborn_heart_methods(self):
        """获取所有先天心法"""
        return list(self.inborn_heart_methods.values())
    
    def get_available_acquired_heart_methods(self, player):
        """获取玩家当前可学习的后天心法"""
        available = []
        for heart_method in self.acquired_heart_methods.values():
            if heart_method.can_learn(player):
                available.append(heart_method)
        return available 