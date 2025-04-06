import random

class Technique:
    """
    武学招式基类
    """
    def __init__(self, name, description, damage_base, qi_cost, cooldown=0, requirements=None):
        self.name = name  # 招式名称
        self.description = description  # 招式描述
        self.damage_base = damage_base  # 基础伤害
        self.qi_cost = qi_cost  # 内力消耗
        self.cooldown = cooldown  # 冷却时间（回合数）
        self.current_cooldown = 0  # 当前冷却状态
        self.requirements = requirements or {}  # 使用要求（境界、心法、属性等）
    
    def can_use(self, player):
        """检查是否能够使用该招式"""
        # 检查冷却
        if self.current_cooldown > 0:
            return False
        
        # 检查内力
        if player.qi < self.qi_cost:
            return False
        
        # 检查要求
        for attr, value in self.requirements.items():
            if attr == "level":
                # 境界要求，数字越小境界越高
                if player.level > value:
                    return False
            elif attr == "heart_method":
                # 心法要求
                if not hasattr(player, "heart_method") or player.heart_method.name != value:
                    return False
            elif hasattr(player, attr):
                # 属性要求
                player_value = getattr(player, attr)
                if player_value < value:
                    return False
        
        return True
    
    def use(self, user, target):
        """使用招式"""
        if not self.can_use(user):
            return 0, "不能使用该招式"
        
        # 消耗内力
        user.qi -= self.qi_cost
        
        # 计算伤害
        damage = self.calculate_damage(user, target)
        
        # 应用伤害
        actual_damage = target.take_damage(damage)
        
        # 设置冷却
        self.current_cooldown = self.cooldown
        
        # 应用额外效果
        effect_description = self.apply_effects(user, target)
        
        return actual_damage, effect_description
    
    def calculate_damage(self, user, target):
        """计算伤害"""
        # 基础伤害 + 用户攻击力 * 攻击系数
        base_damage = self.damage_base + user.attack
        
        # 考虑目标防御
        damage = max(1, base_damage - target.defense // 2)
        
        return damage
    
    def apply_effects(self, user, target):
        """应用额外效果，由子类实现"""
        return ""
    
    def update_cooldown(self):
        """更新冷却时间"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class BasicTechnique(Technique):
    """
    基础招式，不消耗内力的普通攻击
    """
    def __init__(self):
        super().__init__(
            "普通攻击", 
            "最基本的攻击方式，不消耗内力。", 
            5,  # 基础伤害
            0,  # 内力消耗
            0   # 无冷却
        )
    
    def calculate_damage(self, user, target):
        # 普通攻击只考虑基础攻击力
        return max(1, user.attack - target.defense // 2)


class MartialArtTechnique(Technique):
    """
    武学招式，有特殊效果的攻击
    """
    def __init__(self, name, description, damage_base, qi_cost, cooldown=0, 
                 effects=None, requirements=None):
        super().__init__(name, description, damage_base, qi_cost, cooldown, requirements)
        self.effects = effects or {}  # 额外效果
    
    def apply_effects(self, user, target):
        """应用额外效果"""
        effect_description = []
        
        for effect_type, value in self.effects.items():
            if effect_type == "stun":
                # 眩晕效果
                if random.random() < value:
                    target.stunned = True
                    effect_description.append("目标被眩晕")
            elif effect_type == "bleed":
                # 流血效果
                if random.random() < value[0]:
                    if not hasattr(target, "bleed"):
                        target.bleed = 0
                    target.bleed += value[1]
                    effect_description.append(f"目标受到{value[1]}点流血伤害")
            elif effect_type == "qi_damage":
                # 内力伤害
                if hasattr(target, "qi"):
                    target.qi = max(0, target.qi - value)
                    effect_description.append(f"目标损失{value}点内力")
            elif effect_type == "heal":
                # 治疗效果
                heal_amount = value if isinstance(value, int) else int(user.max_health * value)
                user.health = min(user.max_health, user.health + heal_amount)
                effect_description.append(f"恢复{heal_amount}点生命")
            elif effect_type == "qi_restore":
                # 内力恢复
                restore_amount = value if isinstance(value, int) else int(user.max_qi * value)
                user.qi = min(user.max_qi, user.qi + restore_amount)
                effect_description.append(f"恢复{restore_amount}点内力")
        
        return ", ".join(effect_description)


class TechniqueSystem:
    """
    招式系统，管理所有招式
    """
    def __init__(self):
        self.basic_techniques = [BasicTechnique()]
        self.martial_art_techniques = self._initialize_martial_arts()
    
    def _initialize_martial_arts(self):
        """初始化所有武学招式"""
        import random  # 为了随机效果
        
        techniques = []
        
        # 太极系列招式
        taiji_palm = MartialArtTechnique(
            "太极掌", 
            "以柔克刚的太极掌法，能够借力打力。", 
            15,  # 基础伤害
            10,  # 内力消耗
            2,   # 冷却回合
            {"counter_damage": 0.5},  # 反弹敌人50%的攻击力
            {"level": 8, "heart_method": "太极心法"}  # 要求八品境界以上，太极心法
        )
        
        taiji_fist = MartialArtTechnique(
            "太极拳", 
            "刚柔并济的太极拳法，讲究借力打力。", 
            20,  # 基础伤害
            15,  # 内力消耗
            3,   # 冷却回合
            {"stun": 0.2},  # 20%几率眩晕
            {"level": 7, "heart_method": "太极心法"}  # 要求七品境界以上，太极心法
        )
        
        techniques.extend([taiji_palm, taiji_fist])
        
        # 少林系列招式
        shaolin_fist = MartialArtTechnique(
            "少林伏虎拳", 
            "刚猛有力的少林拳法，以刚克刚。", 
            25,  # 基础伤害
            20,  # 内力消耗
            2,   # 冷却回合
            {"stun": 0.3},  # 30%几率眩晕
            {"level": 7, "heart_method": "少林心法"}  # 要求七品境界以上，少林心法
        )
        
        finger_jab = MartialArtTechnique(
            "一指禅", 
            "少林点穴绝技，消耗对手内力。", 
            15,  # 基础伤害
            30,  # 内力消耗
            4,   # 冷却回合
            {"qi_damage": 30},  # 消耗30点内力
            {"level": 6, "heart_method": "少林心法"}  # 要求六品境界以上，少林心法
        )
        
        techniques.extend([shaolin_fist, finger_jab])
        
        # 高级武学
        dragon_tiger = MartialArtTechnique(
            "龙虎八卦掌", 
            "结合刚柔变化，威力强大的八卦掌法。", 
            40,  # 基础伤害
            40,  # 内力消耗
            5,   # 冷却回合
            {"bleed": [0.5, 10]},  # 50%几率造成10点流血
            {"level": 5}  # 要求五品境界以上
        )
        
        nine_sun = MartialArtTechnique(
            "九阳神掌", 
            "明教绝学，阳刚至极的掌法。", 
            50,  # 基础伤害
            50,  # 内力消耗
            6,   # 冷却回合
            {"heal": 20},  # 恢复20点生命
            {"level": 4, "heart_method": "九阳神功"}  # 要求四品境界以上，九阳神功
        )
        
        absorb_qi = MartialArtTechnique(
            "吸星大法", 
            "逍遥派绝学，能吸收对方内力为己用。", 
            30,  # 基础伤害
            45,  # 内力消耗
            5,   # 冷却回合
            {"qi_damage": 40, "qi_restore": 30},  # 消耗40点内力，恢复30点内力
            {"level": 4, "heart_method": "北冥神功"}  # 要求四品境界以上，北冥神功
        )
        
        techniques.extend([dragon_tiger, nine_sun, absorb_qi])
        
        return techniques
    
    def get_basic_techniques(self):
        """获取基础招式"""
        return self.basic_techniques
    
    def get_available_techniques(self, player):
        """获取玩家可用的招式"""
        available = []
        # 基础招式总是可用的
        available.extend(self.basic_techniques)
        
        # 检查每个武学招式是否可用
        for technique in self.martial_art_techniques:
            if technique.can_use(player):
                available.append(technique)
        
        return available
    
    def update_cooldowns(self, techniques):
        """更新所有招式的冷却时间"""
        for technique in techniques:
            technique.update_cooldown() 