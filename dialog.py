import pygame
from util import load_chinese_font  # 从util导入中文字体加载函数

class DialogSystem:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font  # 使用传入的字体
        self.width, self.height = screen.get_size()
        self.current_npc = None
        self.dialog_finished = True
        self.text_color = (255, 255, 255)
        self.ui_bg_color = (20, 20, 20)
        self.ui_border_color = (100, 100, 100)
        self.quest_system = None  # 保存对任务系统的引用
        self.player = None  # 保存对玩家的引用
        self.log_system = None  # 保存对日志系统的引用
        self.show_quest_options = False  # 是否显示任务选项
        self.current_quest = None  # 当前选中的任务
        self.option_selected = None  # 当前选中的选项
    
    def set_references(self, quest_system, player, log_system=None):
        """设置对任务系统和玩家的引用"""
        self.quest_system = quest_system
        self.player = player
        if log_system:
            self.log_system = log_system
    
    def start_dialog(self, npc):
        """开始与NPC的对话"""
        self.current_npc = npc
        self.dialog_finished = False
        self.show_quest_options = False
        self.current_quest = None
        self.option_selected = None
        npc.reset_dialog()
    
    def advance_dialog(self):
        """推进对话到下一条"""
        if not self.current_npc:
            self.dialog_finished = True
            return
        
        # 如果显示任务选项，则根据选项进行处理
        if self.show_quest_options:
            if self.option_selected == "accept":
                # 接受任务
                if self.current_quest and self.player:
                    self.player.accept_quest(self.current_quest)
                    self.show_quest_options = False
                    # 添加接受任务后的对话
                    self.current_npc.add_temp_dialog(f"很好，请完成任务后回来找我。")
                    # 重置当前任务，防止重复提供
                    already_accepted_quest = self.current_quest
                    self.current_quest = None
                    # 不要return，继续执行下面的对话获取逻辑，立即显示临时对话
                    self.option_selected = None
                else:
                    self.option_selected = None
                    return
            elif self.option_selected == "decline":
                # 拒绝任务
                self.show_quest_options = False
                # 添加拒绝任务后的对话
                self.current_npc.add_temp_dialog("我理解，如果你改变主意了再来找我。")
                # 重置当前任务，防止重复提供
                self.current_quest = None
                # 不要return，继续执行下面的对话获取逻辑
                self.option_selected = None
            elif self.option_selected == "complete":
                # 完成任务
                if self.current_quest and self.player:
                    if self.current_quest in self.player.active_quests and self.current_quest.check_completion(self.player):
                        # 完成任务并获取详细的奖励信息
                        success, reward_text = self.player.complete_quest(self.current_quest)
                        self.show_quest_options = False
                        
                        # 添加完成任务后的对话，包括详细的奖励信息
                        self.current_npc.add_temp_dialog(f"你做得很好！{reward_text}")
                        
                        # 如果有日志系统，记录奖励信息
                        if hasattr(self, 'log_system') and self.log_system:
                            self.log_system.add(reward_text, "success")
                        
                        # 重置当前任务，防止重复提供
                        self.current_quest = None
                        # 不要return，继续执行下面的对话获取逻辑
                        self.option_selected = None
                    else:
                        self.show_quest_options = False
                        # 添加任务未完成的对话
                        self.current_npc.add_temp_dialog("你还没有完成任务的所有目标，请继续努力。")
                        # 重置当前任务，防止重复提供
                        self.current_quest = None
                        # 不要return，继续执行下面的对话获取逻辑
                        self.option_selected = None
                else:
                    self.option_selected = None
                    return
            else:
                self.option_selected = None
                return
        
        # 检查是否有更多对话
        dialog = self.current_npc.get_next_dialog()
        if dialog is None:
            # 对话结束，检查是否有任务可以提供
            if self.quest_system and self.player:
                available_quests = self.quest_system.get_available_quests_for_npc(self.current_npc.char)
                
                # 过滤掉已经接受的任务
                available_quests = [quest for quest in available_quests 
                                   if quest not in self.player.active_quests]
                
                # 检查是否有可完成的任务
                completable_quests = []
                for quest in self.player.active_quests:
                    if quest.npc_id == self.current_npc.char and quest.check_completion(self.player):
                        completable_quests.append(quest)
                
                if completable_quests:
                    # 显示可完成的任务
                    self.current_quest = completable_quests[0]  # 简化：只处理第一个可完成的任务
                    self.show_quest_options = True
                    self.option_selected = None
                    return
                elif available_quests:
                    # 显示可接的任务
                    self.current_quest = available_quests[0]  # 简化：只处理第一个可用任务
                    self.show_quest_options = True
                    self.option_selected = None
                    # 添加任务介绍对话
                    self.current_npc.add_temp_dialog(f"我有一个任务给你: {self.current_quest.title}。{self.current_quest.description}")
                    return
            
            # 如果没有任务，结束对话
            self.dialog_finished = True
    
    def handle_input(self, event):
        """处理任务对话的键盘输入"""
        if not self.show_quest_options:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if self.current_quest in self.player.active_quests:
                    self.option_selected = "complete"
                else:
                    self.option_selected = "accept"
                    if hasattr(self, 'log_system') and self.log_system:
                        self.log_system.add(f"您已接受「{self.current_quest.title}」任务", "quest")
                return True
            elif event.key == pygame.K_2:
                self.option_selected = "decline"
                return True
        
        return False
    
    def is_dialog_finished(self):
        """检查对话是否已结束"""
        return self.dialog_finished
    
    def render(self):
        """渲染对话框"""
        if not self.current_npc or self.dialog_finished:
            return
        
        width, height = self.screen.get_size()
        
        # 对话框设置
        box_width = width - 100
        box_height = 150
        box_x = 50
        box_y = height - box_height - 120  # 调整位置以避免与状态栏重叠
        
        # 绘制对话框背景
        pygame.draw.rect(self.screen, self.ui_bg_color, 
                        (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, self.ui_border_color, 
                        (box_x, box_y, box_width, box_height), 2)
        
        # NPC名称框
        name_box_width = len(self.current_npc.char) * 15 + 20
        pygame.draw.rect(self.screen, self.ui_bg_color, 
                        (box_x + 10, box_y - 15, name_box_width, 30))
        pygame.draw.rect(self.screen, self.ui_border_color, 
                        (box_x + 10, box_y - 15, name_box_width, 30), 2)
        self.render_text(self.current_npc.char, box_x + 20, box_y - 10)
        
        # 如果显示任务选项
        if self.show_quest_options and self.current_quest:
            # 任务标题
            title_text = f"任务: {self.current_quest.title}"
            self.render_text(title_text, box_x + 20, box_y + 20, (255, 215, 0))
            
            # 任务描述
            desc_text = self.current_quest.description
            self.render_wrapped_text(desc_text, box_x + 20, box_y + 45, box_width - 40)
            
            # 任务目标
            objectives_y = box_y + 75
            self.render_text("目标:", box_x + 20, objectives_y, (200, 200, 200))
            objectives_y += 25
            
            for i, (desc, completed) in enumerate(self.current_quest.get_objective_status()):
                status = "✓" if completed else "□"
                color = (100, 255, 100) if completed else (200, 200, 200)
                self.render_text(f"{status} {desc}", box_x + 40, objectives_y + i * 20, color)
                
            # 显示任务奖励信息
            rewards_y = objectives_y + len(self.current_quest.get_objective_status()) * 20 + 10
            self.render_text("奖励:", box_x + 20, rewards_y, (255, 215, 0))
            
            # 经验奖励
            if self.current_quest.experience_reward > 0:
                exp_text = f"经验: {self.current_quest.experience_reward}"
                self.render_text(exp_text, box_x + 40, rewards_y + 20, (200, 200, 200))
            
            # 物品奖励
            if self.current_quest.item_rewards:
                for i, item in enumerate(self.current_quest.item_rewards):
                    # 根据稀有度设置颜色
                    item_color = (255, 255, 255)  # 默认白色
                    if item.rarity == "传说":
                        item_color = (255, 150, 50)  # 橙色
                    elif item.rarity == "稀有":
                        item_color = (150, 150, 255)  # 蓝色
                    elif item.rarity == "优秀":
                        item_color = (150, 255, 150)  # 绿色
                    
                    # 构建显示文本
                    item_text = f"{item.name} ({item.rarity})"
                    # 如果是装备类物品，显示属性加成
                    if hasattr(item, 'stats') and item.stats:
                        stats_text = ""
                        if "attack" in item.stats:
                            stats_text += f"攻击+{item.stats['attack']} "
                        if "defense" in item.stats:
                            stats_text += f"防御+{item.stats['defense']} "
                        if "speed" in item.stats:
                            stats_text += f"速度+{item.stats['speed']} "
                        if "max_health" in item.stats:
                            stats_text += f"生命+{item.stats['max_health']} "
                        if "max_qi" in item.stats:
                            stats_text += f"内力+{item.stats['max_qi']} "
                        
                        if stats_text:
                            item_text += f" [{stats_text.strip()}]"
                    
                    # 渲染物品信息
                    self.render_text(item_text, box_x + 40, rewards_y + 20 + (i+1) * 20, item_color)
            
            # 选项 - 移动到对话框外部，放在游戏窗口底部中间
            option_panel_width = 300
            option_panel_height = 40
            option_panel_x = (width - option_panel_width) // 2
            option_panel_y = height - 50  # 距离底部50像素
            
            # 绘制选项背景
            pygame.draw.rect(self.screen, (0, 0, 0, 180), 
                            (option_panel_x, option_panel_y, option_panel_width, option_panel_height))
            pygame.draw.rect(self.screen, (100, 100, 150), 
                            (option_panel_x, option_panel_y, option_panel_width, option_panel_height), 2)
            
            # 居中显示选项文本
            if self.current_quest in self.player.active_quests:
                complete_text = self.font.render("1. 完成任务", True, (100, 255, 100))
                not_ready_text = self.font.render("2. 我还没准备好", True, (255, 150, 150))
                
                option1_x = option_panel_x + 20
                option2_x = option_panel_x + option_panel_width - not_ready_text.get_width() - 20
                option_y = option_panel_y + (option_panel_height - complete_text.get_height()) // 2
                
                self.screen.blit(complete_text, (option1_x, option_y))
                self.screen.blit(not_ready_text, (option2_x, option_y))
            else:
                accept_text = self.font.render("1. 接受任务", True, (100, 255, 100))
                decline_text = self.font.render("2. 拒绝任务", True, (255, 150, 150))
                
                option1_x = option_panel_x + 40
                option2_x = option_panel_x + option_panel_width - decline_text.get_width() - 40
                option_y = option_panel_y + (option_panel_height - accept_text.get_height()) // 2
                
                self.screen.blit(accept_text, (option1_x, option_y))
                self.screen.blit(decline_text, (option2_x, option_y))
        else:
            # 显示普通对话
            dialog_index = self.current_npc.current_dialog - 1
            if dialog_index >= 0 and dialog_index < len(self.current_npc.dialogs):
                text = self.current_npc.dialogs[dialog_index]
                # 绘制对话文本
                self.render_wrapped_text(text, box_x + 20, box_y + 20, box_width - 40)
            
            # 提示
            self.render_text("按空格或回车继续...", box_x + box_width - 250, box_y + box_height - 30)
    
    def render_text(self, text, x, y, color=None):
        """渲染文本"""
        if color is None:
            color = self.text_color
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def render_wrapped_text(self, text, x, y, max_width):
        """渲染自动换行的文本，支持中文"""
        # 中文文本不需要按空格分词，需要逐字检查宽度
        if any('\u4e00' <= char <= '\u9fff' for char in text):  # 检测是否包含中文字符
            words = list(text)  # 中文按字符分
            current_line = words[0] if words else ""
            
            for char in words[1:]:
                test_line = current_line + char
                test_width = self.font.size(test_line)[0]
                if test_width < max_width:
                    current_line = test_line
                else:
                    self.render_text(current_line, x, y)
                    y += self.font.get_height()
                    current_line = char
            
            # 渲染最后一行
            if current_line:
                self.render_text(current_line, x, y)
        else:
            # 英文文本按空格分词
            words = text.split(' ')
            lines = []
            current_line = words[0] if words else ""
            
            for word in words[1:]:
                test_line = current_line + ' ' + word
                test_width = self.font.size(test_line)[0]
                if test_width < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            
            lines.append(current_line)
            
            # 渲染文本行
            line_height = self.font.get_height()
            for i, line in enumerate(lines):
                self.render_text(line, x, y + i * line_height) 