from cultivation import CultivationSystem
from heart_method import InbornHeartMethod

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = "@"  # 玩家用'@'表示，这是roguelike的传统
        self.color = (255, 255, 255)  # White
        
        # 修为境界 - 默认从九品开始
        self.level = 9  # 9: 淬体, 8: 蕴气, 7: 通脉, 6: 凝罡, 5: 意动, 4: 显形, 3: 师法, 2: 法域, 1: 归真, 0: 洞玄
        
        # Stats
        self.experience = 0
        self.experience_to_level = 100
        self.health = 100
        self.max_health = 100
        self.qi = 50  # 内力
        self.max_qi = 50
        self.attack = 10
        self.defense = 5
        self.speed = 5
        
        # 心法
        self.inborn_heart_method = None  # 先天心法
        self.acquired_heart_methods = []  # 后天心法
        
        # 状态效果
        self.stunned = False  # 眩晕
        self.bleed = 0  # 流血
        self.poison = 0  # 中毒
        
        # Equipment and inventory
        self.weapon = "木剑"
        self.armor = "布衣"
        self.inventory = []
        self.weapon_stats = {"attack": 5}  # 初始武器属性
        self.armor_stats = {"defense": 3}  # 初始护甲属性
        self.max_inventory = 20  # 背包最大容量
        self.money = 0  # 玩家金钱
        
        # Abilities and techniques
        self.abilities = ["基本打击", "气力拳"]
        self.techniques = []  # 招式列表
        
        # Quest related
        self.active_quests = []
        self.completed_quests = []
        
        # 初始化境界属性
        self.cultivation_system = CultivationSystem()
        self.apply_realm_bonuses()
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    
    def gain_experience(self, amount):
        self.experience += amount
        required_exp = self.cultivation_system.requirements_for_next_level(self.level)
        
        if self.experience >= required_exp and self.level > 0:
            self.breakthrough()
    
    def breakthrough(self):
        """突破到下一个境界"""
        if self.cultivation_system.advance_player(self):
            # 获取新境界名称
            new_realm = self.cultivation_system.get_realm(self.level)
            print(f"突破成功！你现在的境界是：{new_realm.name}")
            return True
        return False
    
    def apply_realm_bonuses(self):
        """应用当前境界的属性加成"""
        realm = self.cultivation_system.get_realm(self.level)
        if realm:
            realm.apply_bonuses(self)
    
    def learn_heart_method(self, heart_method):
        """学习心法"""
        if isinstance(heart_method, InbornHeartMethod):
            # 只能有一个先天心法
            self.inborn_heart_method = heart_method
            heart_method.apply_bonuses(self)
            return True
        else:
            # 可以学习多个后天心法
            self.acquired_heart_methods.append(heart_method)
            heart_method.apply_bonuses(self)
            return True
    
    def learn_technique(self, technique):
        """学习招式"""
        if technique not in self.techniques:
            self.techniques.append(technique)
            return True
        return False
    
    def use_ability(self, ability_name):
        # Return the damage and qi cost for the ability
        if ability_name == "基本打击":
            return self.attack, 0
        elif ability_name == "气力拳":
            return int(self.attack * 1.5), 10
        elif ability_name == "旋风斩":
            return int(self.attack * 1.2), 15
        elif ability_name == "飞剑术":
            return int(self.attack * 2), 20
        elif ability_name == "龙拳":
            return int(self.attack * 2.5), 30
        return 0, 0
    
    def restore_health(self, amount):
        self.health = min(self.health + amount, self.max_health)
    
    def restore_qi(self, amount):
        self.qi = min(self.qi + amount, self.max_qi)
    
    def take_damage(self, amount):
        actual_damage = max(1, amount - self.defense)
        self.health -= actual_damage
        return actual_damage
    
    def is_alive(self):
        return self.health > 0
    
    def add_to_inventory(self, item):
        """添加物品到背包，返回添加信息"""
        # 检查背包是否已满
        if len(self.inventory) >= self.max_inventory and not item.stackable:
            return f"无法获得{item.name}，背包已满！"
        
        # 如果是可堆叠物品，尝试与现有物品堆叠
        if item.stackable:
            for inv_item in self.inventory:
                if inv_item.can_stack_with(item):
                    inv_item.stack_count += item.stack_count
                    return f"获得物品：{item.name} x{item.stack_count}"
        
        # 如果不能堆叠或没有找到可堆叠的物品，添加新物品
        if len(self.inventory) < self.max_inventory:
            self.inventory.append(item)
            return f"获得物品：{item.name}" + (f" x{item.stack_count}" if item.stackable and item.stack_count > 1 else "")
        else:
            return f"无法获得{item.name}，背包已满！"
    
    def remove_from_inventory(self, item_index):
        """从背包中移除指定索引的物品"""
        if 0 <= item_index < len(self.inventory):
            item = self.inventory[item_index]
            
            # 如果是堆叠物品且数量大于1，只减少数量
            if item.stackable and item.stack_count > 1:
                item.stack_count -= 1
                return f"使用了1个{item.name}，剩余{item.stack_count}个"
            else:
                # 移除整个物品
                removed_item = self.inventory.pop(item_index)
                return f"移除了物品：{removed_item.name}"
        return "无效的物品索引"
    
    def use_item(self, item_index):
        """使用背包中的物品"""
        if 0 <= item_index < len(self.inventory):
            item = self.inventory[item_index]
            result = item.use(self)
            
            # 如果是消耗品且已用尽，或者是装备且已装备，从背包中移除
            if (hasattr(item, "stack_count") and item.stack_count <= 0) or \
               (hasattr(item, "equipped") and item.equipped):
                self.inventory.pop(item_index)
                
            return result
        return "无效的物品索引"
    
    def get_inventory_by_type(self, item_type=None):
        """获取特定类型的背包物品"""
        if item_type is None:
            return self.inventory
        
        return [item for item in self.inventory if item.item_type == item_type]
    
    def has_item(self, item_name, count=1):
        """检查玩家是否拥有指定物品及数量"""
        total_count = 0
        for item in self.inventory:
            if item.name == item_name:
                if item.stackable:
                    total_count += item.stack_count
                else:
                    total_count += 1
                
                if total_count >= count:
                    return True
                    
        return False
    
    def remove_item_by_name(self, item_name, count=1):
        """移除指定名称和数量的物品"""
        remaining_to_remove = count
        indices_to_remove = []
        
        # 遍历背包，记录要移除的物品
        for i, item in enumerate(self.inventory):
            if item.name == item_name and remaining_to_remove > 0:
                if item.stackable:
                    if item.stack_count <= remaining_to_remove:
                        # 如果物品数量小于或等于要移除的数量，标记整个物品移除
                        indices_to_remove.append(i)
                        remaining_to_remove -= item.stack_count
                    else:
                        # 否则只减少堆叠数量
                        item.stack_count -= remaining_to_remove
                        remaining_to_remove = 0
                else:
                    # 非堆叠物品，直接标记移除
                    indices_to_remove.append(i)
                    remaining_to_remove -= 1
        
        # 从后向前移除物品，避免索引变化问题
        for index in sorted(indices_to_remove, reverse=True):
            self.inventory.pop(index)
            
        return count - remaining_to_remove  # 返回实际移除的数量
    
    def update_status_effects(self):
        """更新状态效果"""
        # 处理流血
        if self.bleed > 0:
            self.health -= self.bleed
            self.bleed -= 1
        
        # 处理中毒
        if self.poison > 0:
            self.health -= self.poison
            self.poison -= 1
        
        # 处理眩晕
        if self.stunned:
            self.stunned = False  # 眩晕只持续一回合
    
    def accept_quest(self, quest):
        self.active_quests.append(quest)
    
    def complete_quest(self, quest):
        if quest in self.active_quests:
            self.active_quests.remove(quest)
            self.completed_quests.append(quest)
            
            # 创建一个记录获得的奖励的字符串
            reward_texts = []
            
            # 获取经验奖励
            if quest.experience_reward > 0:
                self.gain_experience(quest.experience_reward)
                reward_texts.append(f"经验值: {quest.experience_reward}")
            
            # 获取物品奖励
            item_rewards = []
            for item in quest.item_rewards:
                # 添加物品到背包
                self.add_to_inventory(item)
                
                # 根据稀有度添加不同的描述
                rarity_mark = ""
                if item.rarity == "传说":
                    rarity_mark = "【传说】"
                elif item.rarity == "稀有":
                    rarity_mark = "【稀有】"
                elif item.rarity == "优秀":
                    rarity_mark = "【优秀】"
                
                item_description = f"{rarity_mark}{item.name}"
                if item.item_type in ["武器", "护甲"]:
                    item_description += f" (攻击: {item.stats.get('attack', 0)}, 防御: {item.stats.get('defense', 0)})"
                
                item_rewards.append(item_description)
                
            if item_rewards:
                reward_texts.append(f"物品: {', '.join(item_rewards)}")
            
            # 构建完整的奖励文本
            reward_text = f"完成任务「{quest.title}」，获得: {'; '.join(reward_texts)}"
            return True, reward_text
        
        return False, "未找到此任务" 