import pygame
import random
import time
from item import generate_monster_drop

class Combat:
    def __init__(self):
        self.combat_log = []
        self.max_log_entries = 5
        self.player_defending = False
        # 添加战斗节奏控制
        self.last_action_time = 0
        self.action_delay = 0.7  # 每个战斗动作之间的延迟(秒)
        self.log_system = None  # 引用游戏中的日志系统
        
        # 自动战斗相关
        self.auto_combat = False  # 是否开启自动战斗
        self.combat_round = 0    # 战斗回合数
        self.auto_combat_delay = 0.8  # 自动战斗每回合延迟(秒)
        self.last_auto_combat_time = 0  # 上次自动战斗时间
    
    def set_log_system(self, log_system):
        """设置日志系统引用"""
        self.log_system = log_system
    
    def add_log(self, message, log_type="combat"):
        """添加战斗日志并同时发送到游戏日志系统"""
        # 添加到本地战斗日志
        self.combat_log.append(message)
        self._trim_combat_log()
        
        # 如果设置了日志系统，也发送到那里
        if self.log_system:
            self.log_system.add(message, log_type)
    
    def start_combat(self, player, monster):
        message = f"开始与{monster.name}战斗！"
        self.combat_log = [message]
        if self.log_system:
            self.log_system.add(message, "combat")
            self.log_system.add("自动战斗按A键开启/关闭", "system")
        self.player_defending = False
        self.last_action_time = time.time()
        self.last_auto_combat_time = time.time()
        self.combat_round = 0
        self.auto_combat = False  # 重置自动战斗状态
    
    def toggle_auto_combat(self):
        """切换自动战斗状态"""
        self.auto_combat = not self.auto_combat
        if self.auto_combat:
            self.add_log("已开启自动战斗", "system")
        else:
            self.add_log("已关闭自动战斗", "system")
        
        # 避免自动战斗开启后立即执行动作
        self.last_auto_combat_time = time.time()
    
    def update_auto_combat(self, player, monster):
        """更新自动战斗状态，如果启用了自动战斗则自动执行战斗动作"""
        if not self.auto_combat or not monster or not player.is_alive() or not monster.is_alive():
            return False
        
        current_time = time.time()
        
        # 检查是否可以执行自动战斗动作
        if current_time - self.last_auto_combat_time < self.auto_combat_delay:
            return False  # 等待延迟
        
        # 增加战斗回合
        self.combat_round += 1
        self.add_log(f"-------- 第{self.combat_round}回合 --------", "system")
        
        # 执行自动战斗逻辑
        # 如果玩家内力不足，使用普通攻击
        if player.qi < 10:
            self.player_attack(player, monster)
        # 如果怪物血量低于一半，使用特殊攻击
        elif monster.health < monster.max_health * 0.5:
            self.player_special_attack(player, monster)
        # 如果玩家血量低于一半，有30%几率防御
        elif player.health < player.max_health * 0.5 and random.random() < 0.3:
            self.player_defend(player)
        # 否则，60%几率普通攻击，40%几率特殊攻击
        else:
            if random.random() < 0.6:
                self.player_attack(player, monster)
            else:
                self.player_special_attack(player, monster)
        
        # 如果怪物还活着，怪物进行反击
        if monster.is_alive():
            self.monster_attack(monster, player)
        
        # 更新自动战斗时间
        self.last_auto_combat_time = current_time
        
        return True  # 表示执行了战斗动作
    
    def player_attack(self, player, monster):
        # 检查是否可以执行动作
        current_time = time.time()
        if not self.auto_combat and current_time - self.last_action_time < self.action_delay:
            return  # 如果时间间隔不够，不执行动作
            
        if not monster or not player.is_alive():
            return
        
        damage, _ = player.use_ability("基本打击")
        actual_damage = monster.take_damage(damage)
        
        message = f"你攻击{monster.name}，造成{actual_damage}点伤害！"
        self.add_log(message)
        
        # Reset defending status
        self.player_defending = False
        self.last_action_time = current_time
    
    def player_special_attack(self, player, monster):
        # 检查是否可以执行动作
        current_time = time.time()
        if not self.auto_combat and current_time - self.last_action_time < self.action_delay:
            return  # 如果时间间隔不够，不执行动作
            
        if not monster or not player.is_alive():
            return
        
        # Choose player's highest ability they have qi for
        ability = "基本打击"  # Default
        for possible_ability in reversed(player.abilities):
            _, qi_cost = player.use_ability(possible_ability)
            if player.qi >= qi_cost:
                ability = possible_ability
                break
        
        damage, qi_cost = player.use_ability(ability)
        
        # Check if player has enough qi
        if player.qi < qi_cost:
            message = f"内力不足，无法使用{ability}！"
            self.add_log(message, "warning")
            # 自动战斗时，如果内力不足，改用普通攻击
            if self.auto_combat:
                self.player_attack(player, monster)
            else:
                self.last_action_time = current_time
            return
        
        # Use qi and deal damage
        player.qi -= qi_cost
        actual_damage = monster.take_damage(damage)
        
        message = f"你使用{ability}，消耗{qi_cost}点内力，造成{actual_damage}点伤害！"
        self.add_log(message)
        
        # Reset defending status
        self.player_defending = False
        self.last_action_time = current_time
    
    def player_defend(self, player):
        # 检查是否可以执行动作
        current_time = time.time()
        if not self.auto_combat and current_time - self.last_action_time < self.action_delay:
            return  # 如果时间间隔不够，不执行动作
            
        self.player_defending = True
        # Restore some qi when defending
        qi_restore = max(5, player.max_qi * 0.1)
        player.restore_qi(qi_restore)
        
        message = f"你进入防御姿态，恢复{int(qi_restore)}点内力！"
        self.add_log(message)
        self.last_action_time = current_time
    
    def monster_attack(self, monster, player):
        # 检查是否可以执行动作
        current_time = time.time()
        if not self.auto_combat and current_time - self.last_action_time < self.action_delay:
            return  # 如果时间间隔不够，不执行动作
            
        if not monster.is_alive() or not player.is_alive():
            return
        
        # 50% chance for monster to attack if player is defending
        if self.player_defending and random.random() < 0.5:
            message = f"{monster.name}的攻击被你格挡了！"
            self.add_log(message)
            self.last_action_time = current_time
            return
        
        # Calculate damage
        base_damage = monster.get_attack_damage()
        
        # Reduce damage by 50% if player is defending
        if self.player_defending:
            base_damage = base_damage // 2
        
        actual_damage = player.take_damage(base_damage)
        
        message = f"{monster.name}攻击你，造成{actual_damage}点伤害！"
        self.add_log(message)
        self.last_action_time = current_time
    
    def render(self, screen, font, player, monster):
        # Draw a combat background
        screen.fill((0, 0, 0))  # Black background
        
        # Draw combat log
        log_y = 400
        for i, entry in enumerate(self.combat_log):
            text_surface = font.render(entry, True, (255, 255, 255))
            screen.blit(text_surface, (50, log_y + i * 25))
        
        # Draw player
        player_text = font.render(player.char, True, (255, 255, 255))
        screen.blit(player_text, (200, 200))
        
        # Draw monster
        if monster:
            monster_text = font.render(monster.char, True, (200, 0, 0))
            screen.blit(monster_text, (600, 200))
            
            # Draw line between player and monster
            pygame.draw.line(screen, (100, 100, 100), (250, 200), (550, 200), 2)
            
        # Draw auto combat status
        auto_combat_text = font.render(f"自动战斗: {'开启' if self.auto_combat else '关闭'}", True, (200, 200, 0))
        screen.blit(auto_combat_text, (600, 400))
    
    def _trim_combat_log(self):
        if len(self.combat_log) > self.max_log_entries:
            self.combat_log = self.combat_log[-self.max_log_entries:] 
    
    def end_combat(self, player, monster, victory=False):
        """结束战斗"""
        self.combat_log = []
        self.in_combat = False
        self.auto_combat = False
        
        if victory:
            # 战利品和经验
            exp_reward = monster.get_exp_reward()
            player.gain_experience(exp_reward)
            message = f"战斗胜利! 你击败了{monster.name}，获得{exp_reward}点经验！"
            self.add_log(message, "success")
            
            # 处理物品掉落
            drops = generate_monster_drop(monster, player.level)
            for item in drops:
                result = player.add_to_inventory(item)
                self.add_log(result, "item")
        else:
            self.add_log("你离开了战斗。", "system") 