class Realm:
    """
    境界类，表示武侠世界中的修为境界
    """
    def __init__(self, level, name, description, attribute_bonuses=None):
        self.level = level  # 境界等级，数字越小境界越高
        self.name = name  # 境界名称
        self.description = description  # 境界描述
        self.attribute_bonuses = attribute_bonuses or {}  # 境界带来的属性加成
    
    def apply_bonuses(self, player):
        """将境界加成应用到玩家属性上"""
        for attr, value in self.attribute_bonuses.items():
            if hasattr(player, attr):
                current = getattr(player, attr)
                if isinstance(current, (int, float)):
                    setattr(player, attr, current + value)
                else:
                    # 如果属性不是数值类型，则直接设置
                    setattr(player, attr, value)


class CultivationSystem:
    """
    修为境界系统，管理所有境界及其进阶关系
    """
    def __init__(self):
        self.realms = self._initialize_realms()
    
    def _initialize_realms(self):
        """初始化所有境界"""
        realms = {}
        
        # 九品：淬体
        realms[9] = Realm(9, "淬体：凡躯极限", 
                        "通过艰苦锻炼和特定方法打熬肉身，突破凡人极限。",
                        {"max_health": 100, "attack": 10, "defense": 5, "speed": 5})
        
        # 八品：蕴气
        realms[8] = Realm(8, "蕴气：内息初生", 
                        "成功在丹田凝聚第一缕内息，并掌握粗浅的搬运法门。",
                        {"max_health": 150, "max_qi": 50, "attack": 15, "defense": 8, "speed": 6})
        
        # 七品：通脉
        realms[7] = Realm(7, "通脉：气行周天", 
                        "打通体内主要的奇经八脉，内息运行畅通无阻，形成完整周天循环。",
                        {"max_health": 200, "max_qi": 100, "attack": 20, "defense": 12, "speed": 8})
        
        # 六品：凝罡
        realms[6] = Realm(6, "凝罡：内气化罡", 
                        '内力经过高度压缩与提纯，由无形气态向更凝练、坚韧的"罡气"形态转化。',
                        {"max_health": 300, "max_qi": 150, "attack": 30, "defense": 18, "speed": 10})
        
        # 五品：意动
        realms[5] = Realm(5, "意动：心意相合", 
                        '精神力量开始觉醒，能够以"意"引导内力/罡气，使其运用更加精妙随心。',
                        {"max_health": 450, "max_qi": 200, "attack": 45, "defense": 25, "speed": 12})
        
        # 四品：显形
        realms[4] = Realm(4, "显形：意到形随", 
                        "内力/罡气与精神意念深度结合，能够依据心意短暂凝聚成相对稳定的外部形态。",
                        {"max_health": 600, "max_qi": 300, "attack": 60, "defense": 35, "speed": 15})
        
        # 三品：师法
        realms[3] = Realm(3, "师法：法效天地", 
                        "心神与自然产生共鸣，开始理解并模仿天地间某些规律，将其融入武学理念与内力特性中。",
                        {"max_health": 800, "max_qi": 450, "attack": 80, "defense": 50, "speed": 18})
        
        # 二品：法域
        realms[2] = Realm(2, "法域：意展成界", 
                        '以自身强大的意志与精纯的能量，向外辐射形成一个有限范围的"领域"或"气场"。',
                        {"max_health": 1000, "max_qi": 600, "attack": 100, "defense": 70, "speed": 22})
        
        # 一品：归真
        realms[1] = Realm(1, "归真：返璞归元", 
                        "精气神三者高度凝练统一，对自身力量和天地规则的理解达到返璞归真的境界。",
                        {"max_health": 1500, "max_qi": 800, "attack": 150, "defense": 100, "speed": 25})
        
        # 洞玄：窥道之境
        realms[0] = Realm(0, "洞玄：窥道之境", 
                        '超越了对"力"的追求，达到了对世界本源"道"的深刻理解和部分感悟。',
                        {"max_health": 2000, "max_qi": 1000, "attack": 200, "defense": 150, "speed": 30})
        
        return realms
    
    def get_realm(self, level):
        """获取指定等级的境界"""
        if level in self.realms:
            return self.realms[level]
        return None
    
    def get_next_realm(self, current_level):
        """获取下一个境界"""
        if current_level > 0:  # 如果不是最高境界
            return self.realms.get(current_level - 1)
        return None
    
    def requirements_for_next_level(self, current_level):
        """获取晋升到下一个境界的要求"""
        # 这里简化为只返回需要的经验值
        base_exp = 100
        # 每提升一个境界，所需经验翻倍
        return base_exp * (2 ** (9 - current_level))
    
    def can_advance_to_next_level(self, player):
        """检查玩家是否满足晋升到下一个境界的条件"""
        if player.level > 0:  # 如果不是最高境界
            required_exp = self.requirements_for_next_level(player.level)
            return player.experience >= required_exp
        return False
    
    def advance_player(self, player):
        """将玩家晋升到下一个境界"""
        if self.can_advance_to_next_level(player):
            # 扣除经验
            player.experience -= self.requirements_for_next_level(player.level)
            # 提升境界
            player.level -= 1
            # 应用新境界加成
            new_realm = self.get_realm(player.level)
            new_realm.apply_bonuses(player)
            return True
        return False
    
    def get_experience_for_next_level(self, current_level):
        """获取晋升到下一个境界所需的经验值，用于UI显示"""
        return self.requirements_for_next_level(current_level) 