import pygame
from player import Player
from world import World
from ui import UI
from combat import Combat
from quest import QuestSystem
from dialog import DialogSystem
from cultivation import CultivationSystem
from heart_method import HeartMethodSystem
from technique import TechniqueSystem
from log import LogSystem
from util import get_font
import os
import time
import random
import sys
from npc import NPC
from item import generate_monster_drop  # 导入物品掉落函数

class Game:
    def __init__(self):
        self.width, self.height = 900, 530
        # 设置窗口为可调整大小
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Novelive - 让小说活过来")
        
        # 加载支持中文和ASCII的字体，减小字体以美化UI
        self.chinese_font = get_font(is_ascii=False, size=20)
        self.ascii_font = get_font(is_ascii=True, size=20)
        
        # 状态界面标识
        self.show_stats_screen = False
        # 状态界面滚动偏移量
        self.stats_scroll_offset = 0
        # 最大滚动偏移量
        self.max_scroll_offset = 200
        
        # 初始化日志系统（先初始化，后面其他系统需要用到）
        self.log_system = LogSystem(max_logs=8)  # 最多显示8条日志
        
        # Set up game systems
        self.world = World(40, 25)  # 40x25 grid for the game world
        self.player = Player(20, 12)  # Start player in the middle
        self.ui = UI(self.screen, self.chinese_font)
        self.combat = Combat()
        self.combat.set_log_system(self.log_system)  # 将日志系统传递给战斗系统
        self.quest_system = QuestSystem()
        self.quest_system.set_log_system(self.log_system)  # 将日志系统传递给任务系统
        self.dialog_system = DialogSystem(self.screen, self.chinese_font)
        # 设置对话系统的引用
        self.dialog_system.set_references(self.quest_system, self.player, self.log_system)
        
        # 新增系统
        self.cultivation_system = CultivationSystem()
        self.heart_method_system = HeartMethodSystem()
        self.technique_system = TechniqueSystem()
        
        # 给玩家一个初始的先天心法
        default_heart_method = self.heart_method_system.get_inborn_heart_method("taiji")
        if default_heart_method and hasattr(self.player, "learn_heart_method"):
            self.player.learn_heart_method(default_heart_method)
            self.log_system.add("你已习得太极心法", "success")
        
        # Game state
        self.state = "EXPLORATION"  # EXPLORATION, DIALOG, COMBAT, BREAKTHROUGH, HEART_METHOD_SELECTION
        self.current_npc = None
        self.current_monster = None
        
        # 控制游戏更新速度
        self.last_monster_move_time = time.time()
        self.monster_move_delay = 0.5  # 怪物AI行动间隔(秒)
        
        # 系统启动日志
        self.log_system.add("欢迎来到Novelive - 让小说活过来", "system")
        self.log_system.add("使用WASD键移动，E键交互", "system")
        self.log_system.add("窗口大小可调整，使用+/-按键或直接拖拽窗口边缘", "system")
        
        # 添加背包界面相关状态
        self.show_inventory = False
        
        # 鼠标点击位置指示器
        self.clicked_position = None
        self.click_indicator_timer = 0
        
    def handle_input(self, event):
        # 处理窗口调整事件
        if event.type == pygame.QUIT:
            self.running = False
        
        if self.state == "EXPLORATION":
            if event.type == pygame.KEYDOWN:
                # Movement controls
                if event.key == pygame.K_w:
                    self.try_move(0, -1)
                elif event.key == pygame.K_s:
                    self.try_move(0, 1)
                elif event.key == pygame.K_a:
                    self.try_move(-1, 0)
                elif event.key == pygame.K_d:
                    self.try_move(1, 0)
                # Interaction
                elif event.key == pygame.K_e:
                    self.interact()
                # 突破境界
                elif event.key == pygame.K_b:
                    self.attempt_breakthrough()
                # 查看状态 - 切换显示/隐藏状态界面
                elif event.key == pygame.K_c:
                    self.show_stats_screen = not self.show_stats_screen
                    if self.show_stats_screen:
                        self.log_system.add("显示角色状态界面，按C键关闭", "system")
                    else:
                        self.log_system.add("关闭角色状态界面", "system")
                # 日志面板宽度调整
                elif event.key == pygame.K_SLASH:  # 增加宽度
                    self.ui.adjust_log_width(20)
                elif event.key == pygame.K_PERIOD:  # 减少宽度
                    self.ui.adjust_log_width(-20)
                # 日志面板高度调整
                elif event.key == pygame.K_SEMICOLON:  # 增加高度
                    self.ui.adjust_log_height(20)
                elif event.key == pygame.K_QUOTE:  # 减少高度
                    self.ui.adjust_log_height(-20)
                # 窗口大小调整快捷键
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # 增大窗口
                    self.resize_window((self.width + 100, self.height + 75))
                elif event.key == pygame.K_MINUS:  # 缩小窗口
                    self.resize_window((max(800, self.width - 100), max(600, self.height - 75)))
                # 重置窗口大小
                elif event.key == pygame.K_0:
                    self.resize_window((900, 530))  # 重置为默认大小
            
            # 添加鼠标点击移动支持
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self.handle_mouse_movement(event.pos)
        
        elif self.state == "DIALOG":
            if event.type == pygame.KEYDOWN:
                # 先检查是否处理任务对话选项
                if self.dialog_system.handle_input(event):
                    self.dialog_system.advance_dialog()
                    if self.dialog_system.is_dialog_finished():
                        self.state = "EXPLORATION"
                        self.current_npc = None
                        self.log_system.add("对话结束", "info")
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.dialog_system.advance_dialog()
                    if self.dialog_system.is_dialog_finished():
                        self.state = "EXPLORATION"
                        self.current_npc = None
                        self.log_system.add("对话结束", "info")
        
        elif self.state == "COMBAT":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Basic attack
                    self.combat.player_attack(self.player, self.current_monster)
                elif event.key == pygame.K_2:  # Special attack
                    self.combat.player_special_attack(self.player, self.current_monster)
                elif event.key == pygame.K_3:  # Defend
                    self.combat.player_defend(self.player)
                elif event.key == pygame.K_a:  # 切换自动战斗
                    self.combat.toggle_auto_combat()
                    
                self.check_combat_state()
                    
        elif self.state == "BREAKTHROUGH":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.state = "EXPLORATION"
        
        elif self.state == "HEART_METHOD_SELECTION":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and len(self.heart_method_system.get_all_inborn_heart_methods()) >= 1:
                    # 选择太极心法
                    heart_method = self.heart_method_system.get_inborn_heart_method("taiji")
                    if heart_method:
                        self.player.learn_heart_method(heart_method)
                        self.state = "EXPLORATION"
                elif event.key == pygame.K_2 and len(self.heart_method_system.get_all_inborn_heart_methods()) >= 2:
                    # 选择少林心法
                    heart_method = self.heart_method_system.get_inborn_heart_method("shaolin")
                    if heart_method:
                        self.player.learn_heart_method(heart_method)
                        self.state = "EXPLORATION"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "EXPLORATION"
        
        # 在状态界面时，按C键关闭状态界面，上下键滚动
        elif self.state == "STATS":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c or event.key == pygame.K_ESCAPE:
                    self.show_stats_screen = False
                    self.state = "EXPLORATION"
                    self.log_system.add("关闭角色状态界面", "system")
                # 添加滚动控制
                elif event.key == pygame.K_UP:
                    self.stats_scroll_offset = max(0, self.stats_scroll_offset - 30)
                elif event.key == pygame.K_DOWN:
                    self.stats_scroll_offset = min(self.max_scroll_offset, self.stats_scroll_offset + 30)
        
        # 背包界面的专用处理
        if self.show_inventory:
            if event.type == pygame.KEYDOWN:
                # 关闭背包
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    self.show_inventory = False
                    return
                
                # 切换标签页
                elif event.key == pygame.K_1:
                    self.ui.inventory_active_tab = "全部"
                    self.ui.selected_item_index = -1
                elif event.key == pygame.K_2:
                    self.ui.inventory_active_tab = "武器"
                    self.ui.selected_item_index = -1
                elif event.key == pygame.K_3:
                    self.ui.inventory_active_tab = "护甲"
                    self.ui.selected_item_index = -1
                elif event.key == pygame.K_4:
                    self.ui.inventory_active_tab = "消耗品"
                    self.ui.selected_item_index = -1
                elif event.key == pygame.K_5:
                    self.ui.inventory_active_tab = "材料"
                    self.ui.selected_item_index = -1
                elif event.key == pygame.K_6:
                    self.ui.inventory_active_tab = "任务"
                    self.ui.selected_item_index = -1
                
                # 背包滚动和物品选择
                elif event.key == pygame.K_UP:
                    self.ui.selected_item_index = max(0, self.ui.selected_item_index - 4)
                    self._update_inventory_scroll()
                elif event.key == pygame.K_DOWN:
                    # 根据当前分类获取物品列表
                    filtered_items = self._get_filtered_inventory_items()
                    max_index = len(filtered_items) - 1
                    self.ui.selected_item_index = min(max_index, self.ui.selected_item_index + 4)
                    self._update_inventory_scroll()
                elif event.key == pygame.K_LEFT:
                    if self.ui.selected_item_index > 0:
                        self.ui.selected_item_index -= 1
                elif event.key == pygame.K_RIGHT:
                    filtered_items = self._get_filtered_inventory_items()
                    if self.ui.selected_item_index < len(filtered_items) - 1:
                        self.ui.selected_item_index += 1
                
                # 使用/装备物品
                elif event.key == pygame.K_e:
                    self._use_selected_item()
                
                # 丢弃物品
                elif event.key == pygame.K_d:
                    self._drop_selected_item()
                
                # 鼠标滚轮滚动
                elif event.key == pygame.K_PAGEUP:
                    self.ui.inventory_scroll = max(0, self.ui.inventory_scroll - 80)
                elif event.key == pygame.K_PAGEDOWN:
                    max_scroll = self._calculate_max_scroll()
                    self.ui.inventory_scroll = min(max_scroll, self.ui.inventory_scroll + 80)
            
            # 鼠标事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self._handle_inventory_click(event.pos)
                elif event.button == 4:  # 滚轮上滚
                    self.ui.inventory_scroll = max(0, self.ui.inventory_scroll - 40)
                elif event.button == 5:  # 滚轮下滚
                    max_scroll = self._calculate_max_scroll()
                    self.ui.inventory_scroll = min(max_scroll, self.ui.inventory_scroll + 40)
            
            # 鼠标移动事件 - 更新提示框
            elif event.type == pygame.MOUSEMOTION:
                self._handle_inventory_hover(event.pos)
                
            return
        
        keys = pygame.key.get_pressed()
        
        # 打开背包界面
        if keys[pygame.K_i]:
            self.show_inventory = True
            return
    
    def handle_inventory_input(self):
        """处理背包界面的输入 - 这个方法已废弃，逻辑已移至handle_input方法中"""
        pass
    
    def _get_filtered_inventory_items(self):
        """获取当前标签页下的物品列表"""
        if self.ui.inventory_active_tab == "全部":
            return self.player.inventory
        else:
            item_type_map = {
                "武器": "武器",
                "护甲": "护甲",
                "消耗品": "消耗品",
                "材料": "材料",
                "任务": "任务物品"
            }
            item_type = item_type_map.get(self.ui.inventory_active_tab)
            if item_type:
                return [item for item in self.player.inventory if item.item_type == item_type]
            return []
    
    def _update_inventory_scroll(self):
        """根据选中的物品更新滚动位置"""
        filtered_items = self._get_filtered_inventory_items()
        if not filtered_items or self.ui.selected_item_index < 0:
            return
        
        items_per_row = 4
        row = self.ui.selected_item_index // items_per_row
        item_height = 80
        
        # 获取物品区域高度
        panel_width = int(self.screen.get_width() * 0.8)
        panel_height = int(self.screen.get_height() * 0.8)
        panel_y = (self.screen.get_height() - panel_height) // 2
        items_area_y = panel_y + 50 + 30 + 10  # 标题高度 + 标签高度 + 间距
        items_area_height = panel_height - (50 + 30 + 10 + 60)  # 减去顶部和底部的空间
        
        visible_rows = items_area_height // item_height
        
        # 如果选中的行在可视区域上方，向上滚动
        if row * item_height < self.ui.inventory_scroll:
            self.ui.inventory_scroll = row * item_height
        
        # 如果选中的行在可视区域下方，向下滚动
        elif (row + 1) * item_height > self.ui.inventory_scroll + visible_rows * item_height:
            self.ui.inventory_scroll = (row + 1) * item_height - visible_rows * item_height
    
    def _calculate_max_scroll(self):
        """计算最大滚动位置"""
        filtered_items = self._get_filtered_inventory_items()
        items_per_row = 4
        item_height = 80
        
        total_rows = (len(filtered_items) + items_per_row - 1) // items_per_row  # 向上取整
        content_height = total_rows * item_height
        
        # 获取物品区域高度
        panel_width = int(self.screen.get_width() * 0.8)
        panel_height = int(self.screen.get_height() * 0.8)
        items_area_height = panel_height - (50 + 30 + 10 + 60)  # 减去顶部和底部的空间
        
        max_scroll = max(0, content_height - items_area_height)
        return max_scroll
    
    def _handle_inventory_click(self, pos):
        """处理物品栏点击"""
        # 获取面板尺寸和位置
        panel_width = int(self.screen.get_width() * 0.8)
        panel_height = int(self.screen.get_height() * 0.8)
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        # 检查标签点击
        tabs = ["全部", "武器", "护甲", "消耗品", "材料", "任务"]
        left_width = int(panel_width * 0.25)
        right_x = panel_x + left_width + 10
        right_width = panel_width - left_width - 20
        tab_width = right_width // len(tabs)
        tab_area_y = panel_y + 50
        
        for i, tab in enumerate(tabs):
            tab_x = right_x + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_area_y, tab_width, 30)
            if tab_rect.collidepoint(pos):
                self.ui.inventory_active_tab = tab
                self.ui.selected_item_index = -1
                return
        
        # 检查物品点击
        items_area_y = panel_y + 50 + 30 + 10
        items_area_height = panel_height - (50 + 30 + 10 + 60)
        items_area_rect = pygame.Rect(right_x, items_area_y, right_width, items_area_height)
        
        if items_area_rect.collidepoint(pos):
            filtered_items = self._get_filtered_inventory_items()
            if not filtered_items:
                return
            
            items_per_row = 4
            item_width = right_width // items_per_row
            item_height = 80
            
            # 计算点击的网格位置
            rel_x = pos[0] - right_x
            rel_y = pos[1] - items_area_y + self.ui.inventory_scroll
            
            col = rel_x // item_width
            row = rel_y // item_height
            
            item_index = row * items_per_row + col
            if 0 <= item_index < len(filtered_items):
                self.ui.selected_item_index = item_index
    
    def _handle_inventory_hover(self, pos):
        """处理鼠标悬停在物品上的事件，显示提示信息"""
        # 获取面板尺寸和位置
        panel_width = int(self.screen.get_width() * 0.8)
        panel_height = int(self.screen.get_height() * 0.8)
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        # 物品区域
        left_width = int(panel_width * 0.25)
        right_x = panel_x + left_width + 10
        right_width = panel_width - left_width - 20
        items_area_y = panel_y + 50 + 30 + 10
        items_area_height = panel_height - (50 + 30 + 10 + 60)
        items_area_rect = pygame.Rect(right_x, items_area_y, right_width, items_area_height)
        
        if items_area_rect.collidepoint(pos):
            filtered_items = self._get_filtered_inventory_items()
            if not filtered_items:
                self.ui.item_tooltip_active = False
                return
            
            items_per_row = 4
            item_width = right_width // items_per_row
            item_height = 80
            
            # 计算鼠标悬停的网格位置
            rel_x = pos[0] - right_x
            rel_y = pos[1] - items_area_y + self.ui.inventory_scroll
            
            col = rel_x // item_width
            row = rel_y // item_height
            
            item_index = row * items_per_row + col
            if 0 <= item_index < len(filtered_items):
                self.ui.item_tooltip_active = True
                self.ui.tooltip_item = filtered_items[item_index]
            else:
                self.ui.item_tooltip_active = False
        else:
            self.ui.item_tooltip_active = False
    
    def _use_selected_item(self):
        """使用或装备选中的物品"""
        filtered_items = self._get_filtered_inventory_items()
        if not filtered_items or self.ui.selected_item_index < 0 or self.ui.selected_item_index >= len(filtered_items):
            return
        
        # 获取选中的物品
        selected_item = filtered_items[self.ui.selected_item_index]
        
        # 获取物品在玩家背包中的实际索引
        actual_index = self.player.inventory.index(selected_item)
        
        # 使用物品
        result = self.player.use_item(actual_index)
        
        # 添加使用结果到日志
        self.log_system.add(result, "item")
    
    def _drop_selected_item(self):
        """丢弃选中的物品"""
        filtered_items = self._get_filtered_inventory_items()
        if not filtered_items or self.ui.selected_item_index < 0 or self.ui.selected_item_index >= len(filtered_items):
            return
        
        # 获取选中的物品
        selected_item = filtered_items[self.ui.selected_item_index]
        
        # 获取物品在玩家背包中的实际索引
        actual_index = self.player.inventory.index(selected_item)
        
        # 移除物品
        result = self.player.remove_from_inventory(actual_index)
        
        # 重置选中的物品索引
        self.ui.selected_item_index = -1
        
        # 添加丢弃结果到日志
        self.log_system.add(result, "item")
    
    def try_move(self, dx, dy):
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        # 检查新位置是否有效
        valid, reason = self.world.is_position_valid(new_x, new_y)
        
        if valid:
            # 检查是否有怪物在新位置
            monster = self.world.get_monster_at(new_x, new_y)
            if monster:
                self.start_combat(monster)
                self.log_system.add(f"你遇到了{monster.name}！", "combat")
            else:
                # 移动玩家
                self.player.move(dx, dy)
                
                # 检查是否踩到传送门
                portal = self.world.check_portal(new_x, new_y)
                if portal:
                    self.change_area(portal)
                    area_name = self.world.area_info.get(portal, {}).get('name', portal)
                    self.log_system.add(f"你进入了{area_name}", "system")
                
                # 移动后检查是否有相邻的怪物
                self.check_adjacent_monsters()
        else:
            # 如果新位置无效，检查那个位置是否有怪物
            monster = self.world.get_monster_at(new_x, new_y)
            if monster:
                # 与怪物战斗而不是移动
                self.start_combat(monster)
                self.log_system.add(f"你发现了{monster.name}并开始战斗！", "combat")
            else:
                # 无法移动，添加原因到日志
                self.log_system.add(reason, "warning")
    
    def check_adjacent_monsters(self):
        """检查玩家周围是否有怪物，有则触发战斗"""
        adjacent_positions = [
            (self.player.x+1, self.player.y),
            (self.player.x-1, self.player.y),
            (self.player.x, self.player.y+1),
            (self.player.x, self.player.y-1)
        ]
        
        for x, y in adjacent_positions:
            monster = self.world.get_monster_at(x, y)
            if monster:
                self.start_combat(monster)
                self.log_system.add(f"你遇到了相邻的{monster.name}并开始战斗！", "combat")
                break
    
    def interact(self):
        # Check for NPCs in adjacent tiles
        adjacent_positions = [
            (self.player.x+1, self.player.y),
            (self.player.x-1, self.player.y),
            (self.player.x, self.player.y+1),
            (self.player.x, self.player.y-1)
        ]
        
        interaction_found = False
        for x, y in adjacent_positions:
            npc = self.world.get_npc_at(x, y)
            if npc:
                self.start_dialog(npc)
                self.log_system.add(f"你与{npc.char}交谈", "info")
                interaction_found = True
                break
                
        if not interaction_found:
            self.log_system.add("附近没有可交互的对象", "info")
    
    def start_dialog(self, npc):
        self.current_npc = npc
        self.dialog_system.start_dialog(npc)
        self.state = "DIALOG"
    
    def start_combat(self, monster):
        """开始战斗"""
        self.current_monster = monster
        self.state = "COMBAT"
        self.combat.start_combat(self.player, monster)
        self.log_system.add(f"与{monster.name}战斗开始！1-普通攻击 2-特殊攻击 3-防御 A-自动战斗", "combat")
    
    def attempt_breakthrough(self):
        """尝试突破到下一个境界"""
        current_realm = self.cultivation_system.get_realm(self.player.level)
        next_realm = self.cultivation_system.get_next_realm(self.player.level)
        
        if next_realm and self.cultivation_system.can_advance_to_next_level(self.player):
            success = self.player.breakthrough()
            if success:
                self.state = "BREAKTHROUGH"
                self.log_system.add(f"恭喜！你成功突破到了{next_realm.name}境界", "success")
                
                # 更新等级相关的任务目标
                self.quest_system.update_level_objectives(self.player, self.player.level)
                
                return True
            else:
                self.log_system.add("突破失败，需要更多修炼", "warning")
        else:
            self.log_system.add("当前无法突破，需要积累更多经验", "warning")
        
        return False
    
    def show_character_info(self):
        """显示角色状态界面"""
        # 如果已经显示状态界面，则关闭
        if self.state == "STATS":
            self.show_stats_screen = False
            self.state = "EXPLORATION"
            self.log_system.add("关闭角色状态界面", "system")
        else:
            # 显示状态界面
            self.show_stats_screen = True
            self.state = "STATS"
            self.log_system.add("显示角色状态界面，按C键关闭", "system")
            
            # 这部分留下用于Debug信息打印
            realm = self.cultivation_system.get_realm(self.player.level)
            print(f"境界: {realm.name}")
            print(f"生命: {self.player.health}/{self.player.max_health}")
            print(f"内力: {self.player.qi}/{self.player.max_qi}")
            print(f"攻击: {self.player.attack}")
            print(f"防御: {self.player.defense}")
            print(f"速度: {self.player.speed}")
            print(f"经验: {self.player.experience}")
            if self.player.inborn_heart_method:
                print(f"先天心法: {self.player.inborn_heart_method.name}")
    
    def change_area(self, area_name):
        """切换游戏区域"""
        self.world.change_area(area_name)
        
        # 更新探索任务目标
        if self.player and self.quest_system:
            # 检查是否有特殊区域的探索任务
            if area_name == "cave" and self.player.x > 30 and self.player.y > 20:
                # 假设坐标(30,20)以上区域是洞窟深处的BOSS房间
                self.quest_system.update_explore_objectives(self.player, "cave_boss_room")
            # 可以添加更多特殊区域的判断
    
    def update(self):
        current_time = time.time()
        
        # 更新玩家状态效果
        self.player.update_status_effects()
        
        # 更新鼠标点击指示器计时器
        if self.click_indicator_timer > 0:
            self.click_indicator_timer -= 1
        
        if self.state == "EXPLORATION":
            # Only update monster movement after delay has passed
            if current_time - self.last_monster_move_time >= self.monster_move_delay:
                # Random monster movement or other world updates
                self.world.update()
                self.last_monster_move_time = current_time
                
        elif self.state == "COMBAT":
            # 处理自动战斗
            if self.current_monster and self.combat.auto_combat:
                combat_action_performed = self.combat.update_auto_combat(self.player, self.current_monster)
                if combat_action_performed:
                    self.check_combat_state()
            
            # 怪物反击 - 仅在非自动战斗模式下，自动战斗已在update_auto_combat中处理
            elif self.current_monster and self.current_monster.health > 0 and not self.combat.auto_combat:
                self.combat.monster_attack(self.current_monster, self.player)
                
                # 更新招式冷却时间
                if hasattr(self.player, "techniques"):
                    self.technique_system.update_cooldowns(self.player.techniques)
                
                # 检查玩家是否阵亡
                self.check_player_death()
    
    def check_combat_state(self):
        """检查战斗状态，处理战斗结束等情况"""
        if not self.current_monster:
            return
            
        # 检查怪物是否被击败
        if self.current_monster.health <= 0:
            # 战斗胜利，获得经验和物品
            exp_gained = self.current_monster.experience
            self.player.gain_experience(exp_gained)
            self.log_system.add(f"你击败了{self.current_monster.name}，获得{exp_gained}点经验", "success")
            
            # 处理战利品
            loot = getattr(self.current_monster, 'get_loot', lambda: [])()
            if loot:
                for item in loot:
                    info = self.player.add_to_inventory(item)
                    self.log_system.add(info, "item")
                    # 更新收集任务目标
                    self.quest_system.update_collect_objectives(self.player, item.name)
            
            # 更新击杀任务目标
            self.quest_system.update_kill_objectives(self.player, self.current_monster.name)
            
            # 更新世界中的怪物状态
            self.world.update_monster(self.current_monster)
            
            self.current_monster = None
            self.state = "EXPLORATION"
        else:
            # 战斗还在继续，更新怪物状态
            self.world.update_monster(self.current_monster)
    
    def check_player_death(self):
        """检查玩家是否阵亡，并处理死亡后果"""
        if self.player.health <= 0:
            # Game over handling
            self.log_system.add("你被击败了，生命值已耗尽！", "combat")
            self.log_system.add("你被救助回逍遥阁，恢复了一半生命值", "system")
            self.player.health = self.player.max_health // 2  # Revive with half health
            self.state = "EXPLORATION"
            self.current_monster = None
            # 传送回逍遥阁
            self.change_area("xiaoyao")
    
    def render(self):
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.state == "EXPLORATION":
            # 设置开始渲染的位置，确保玩家在视图中间
            view_x = max(0, min(self.player.x - 15, self.world.width - 30))
            view_y = max(0, min(self.player.y - 10, self.world.height - 20))
            
            # 渲染世界
            self.world.render(self.screen, self.chinese_font, view_x, view_y, self.player.x, self.player.y)
            
            # 渲染鼠标点击位置指示器
            if self.clicked_position and self.click_indicator_timer > 0:
                grid_x, grid_y = self.clicked_position
                # 转换为屏幕坐标
                if view_x <= grid_x < view_x + 30 and view_y <= grid_y < view_y + 20:
                    screen_x = (grid_x - view_x) * 20 + 20 // 2
                    screen_y = (grid_y - view_y) * 20 + 20 // 2
                    
                    # 绘制指示器
                    indicator_color = (255, 255, 0, min(255, self.click_indicator_timer * 25))  # 黄色，随时间淡出
                    indicator_radius = 10
                    
                    # 创建一个临时的Surface来绘制半透明圆
                    temp_surface = pygame.Surface((indicator_radius*2, indicator_radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surface, indicator_color, (indicator_radius, indicator_radius), indicator_radius)
                    self.screen.blit(temp_surface, (screen_x - indicator_radius, screen_y - indicator_radius))
            
            # 渲染UI
            self.ui.render(self.player, self.log_system.get_recent_logs())
            
            # 如果状态界面标志为True，渲染状态界面并将状态设为STATS
            if self.show_stats_screen:
                self.state = "STATS"
                self.render_character_stats()
        
        elif self.state == "DIALOG":
            # 仍然在背景中渲染世界
            view_x = max(0, min(self.player.x - 15, self.world.width - 30))
            view_y = max(0, min(self.player.y - 10, self.world.height - 20))
            self.world.render(self.screen, self.chinese_font, view_x, view_y, self.player.x, self.player.y)
            
            # 渲染鼠标点击位置指示器 - 在对话模式下也显示
            if self.clicked_position and self.click_indicator_timer > 0:
                grid_x, grid_y = self.clicked_position
                # 转换为屏幕坐标
                if view_x <= grid_x < view_x + 30 and view_y <= grid_y < view_y + 20:
                    screen_x = (grid_x - view_x) * 20 + 20 // 2
                    screen_y = (grid_y - view_y) * 20 + 20 // 2
                    
                    # 绘制指示器
                    indicator_color = (255, 255, 0, min(255, self.click_indicator_timer * 25))  # 黄色，随时间淡出
                    indicator_radius = 10
                    
                    # 创建一个临时的Surface来绘制半透明圆
                    temp_surface = pygame.Surface((indicator_radius*2, indicator_radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surface, indicator_color, (indicator_radius, indicator_radius), indicator_radius)
                    self.screen.blit(temp_surface, (screen_x - indicator_radius, screen_y - indicator_radius))
            
            # 渲染对话框
            self.dialog_system.render()
        
        elif self.state == "COMBAT":
            # 渲染战斗界面
            if self.current_monster:
                # 绘制战斗背景
                pygame.draw.rect(self.screen, (20, 20, 40), (50, 50, 700, 400))
                
                # 绘制玩家和怪物信息
                player_info = f"玩家 - HP:{self.player.health}/{self.player.max_health} 内力:{self.player.qi}/{self.player.max_qi}"
                monster_info = f"{self.current_monster.name} - HP:{self.current_monster.health}/{self.current_monster.max_health}"
                
                player_text = self.chinese_font.render(player_info, True, (255, 255, 255))
                monster_text = self.chinese_font.render(monster_info, True, (255, 100, 100))
                
                self.screen.blit(player_text, (100, 100))
                self.screen.blit(monster_text, (100, 150))
                
                # 绘制操作提示
                controls_text = self.chinese_font.render("1-普通攻击 2-特殊攻击 3-防御", True, (200, 200, 0))
                self.screen.blit(controls_text, (100, 400))
                
                # 绘制战斗日志
                for i, log in enumerate(self.combat.combat_log[-5:]):
                    log_text = self.chinese_font.render(log, True, (200, 200, 200))
                    self.screen.blit(log_text, (100, 200 + i * 30))
            
            # 渲染UI (只显示日志部分)
            self.ui.render_logs(self.log_system.get_recent_logs())
        
        elif self.state == "BREAKTHROUGH":
            self.render_breakthrough_screen()
        
        elif self.state == "HEART_METHOD_SELECTION":
            self.render_heart_method_selection()
        
        elif self.state == "STATS":
            # 先渲染背景世界（半透明显示）
            view_x = max(0, min(self.player.x - 15, self.world.width - 30))
            view_y = max(0, min(self.player.y - 10, self.world.height - 20))
            self.world.render(self.screen, self.chinese_font, view_x, view_y, self.player.x, self.player.y)
            
            # 然后渲染角色状态界面
            self.render_character_stats()
        
        # 如果显示背包界面，渲染背包
        if self.show_inventory:
            self.ui.render_inventory(self.player)
        
        # 刷新屏幕
        pygame.display.flip()
    
    def render_breakthrough_screen(self):
        """渲染突破境界的画面"""
        # 获取当前境界
        realm = self.cultivation_system.get_realm(self.player.level)
        
        # 清空屏幕
        self.screen.fill((0, 0, 0))
        
        # 显示突破成功信息
        title_text = self.chinese_font.render(f"突破成功！", True, (255, 215, 0))  # 金色
        realm_text = self.chinese_font.render(f"你已经突破到：{realm.name}", True, (255, 255, 255))
        desc_text = self.chinese_font.render(f"{realm.description}", True, (200, 200, 200))
        continue_text = self.chinese_font.render("按空格键或回车键继续", True, (150, 150, 150))
        
        # 计算文本位置
        title_x = (self.width - title_text.get_width()) // 2
        realm_x = (self.width - realm_text.get_width()) // 2
        desc_x = (self.width - desc_text.get_width()) // 2
        continue_x = (self.width - continue_text.get_width()) // 2
        
        # 显示文本
        self.screen.blit(title_text, (title_x, 200))
        self.screen.blit(realm_text, (realm_x, 250))
        self.screen.blit(desc_text, (desc_x, 300))
        self.screen.blit(continue_text, (continue_x, 400))
    
    def render_heart_method_selection(self):
        """渲染心法选择画面"""
        # 清空屏幕
        self.screen.fill((0, 0, 0))
        
        # 显示选择心法的标题
        title_text = self.chinese_font.render("选择你的先天心法", True, (255, 215, 0))
        self.screen.blit(title_text, ((self.width - title_text.get_width()) // 2, 100))
        
        # 获取所有可选的先天心法
        heart_methods = self.heart_method_system.get_all_inborn_heart_methods()
        
        # 显示心法选项
        y_pos = 180
        for i, method in enumerate(heart_methods):
            option_text = self.chinese_font.render(f"{i+1}. {method.name}", True, (255, 255, 255))
            self.screen.blit(option_text, ((self.width - option_text.get_width()) // 2, y_pos))
            
            desc_text = self.chinese_font.render(method.description, True, (200, 200, 200))
            self.screen.blit(desc_text, ((self.width - desc_text.get_width()) // 2, y_pos + 30))
            
            y_pos += 80
        
        # 显示提示
        hint_text = self.chinese_font.render("按数字键选择，或按ESC取消", True, (150, 150, 150))
        self.screen.blit(hint_text, ((self.width - hint_text.get_width()) // 2, 500))
    
    def resize_window(self, size):
        """处理窗口大小调整"""
        self.width, self.height = size
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        
        # 更新UI组件尺寸
        self.ui.update_screen_size(self.width, self.height)
        
        # 添加日志
        self.log_system.add(f"窗口大小已调整为 {self.width}x{self.height}", "system")
    
    def render_character_stats(self):
        """渲染全屏角色状态界面"""
        # 创建半透明黑色背景
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # 黑色半透明背景
        self.screen.blit(overlay, (0, 0))
        
        # 获取当前境界
        realm = self.cultivation_system.get_realm(self.player.level)
        
        # 标题和角色基本信息
        title_text = self.chinese_font.render("角色状态", True, (255, 215, 0))
        name_text = self.chinese_font.render(f"姓名: 侠客", True, (255, 255, 255))
        level_text = self.chinese_font.render(f"境界: {realm.name}", True, (255, 255, 255))
        
        # 创建角色状态面板 - 基本属性部分
        panel_width = 700
        panel_height = 400
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        # 绘制面板主背景 - 增加渐变效果
        for i in range(panel_height):
            alpha = 150 + (i / panel_height) * 80  # 从上到下渐变
            color = (20 + i/10, 20 + i/15, 40 + i/8, alpha)
            pygame.draw.line(self.screen, color, 
                            (panel_x, panel_y + i), 
                            (panel_x + panel_width, panel_y + i))
        
        # 绘制面板边框 - 使用更美观的边框
        pygame.draw.rect(self.screen, (120, 120, 180), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # 裁剪区域 - 确保内容不会溢出面板
        panel_rect = pygame.Rect(panel_x, panel_y + 50, panel_width, panel_height - 50)
        self.screen.set_clip(panel_rect)
        
        # 边框装饰 - 四角
        corner_size = 10
        # 左上角
        pygame.draw.line(self.screen, (200, 200, 255), 
                        (panel_x, panel_y), (panel_x + corner_size, panel_y), 2)
        pygame.draw.line(self.screen, (200, 200, 255), 
                        (panel_x, panel_y), (panel_x, panel_y + corner_size), 2)
        # 右上角
        pygame.draw.line(self.screen, (200, 200, 255), 
                        (panel_x + panel_width, panel_y), (panel_x + panel_width - corner_size, panel_y), 2)
        pygame.draw.line(self.screen, (200, 200, 255), 
                        (panel_x + panel_width, panel_y), (panel_x + panel_width, panel_y + corner_size), 2)
        # 左下角
        pygame.draw.line(self.screen, (200, 200, 255), 
                        (panel_x, panel_y + panel_height), (panel_x + corner_size, panel_y + panel_height), 2)
        pygame.draw.line(self.screen, (200, 200, 255), 
                        (panel_x, panel_y + panel_height), (panel_x, panel_y + panel_height - corner_size), 2)
        # 右下角
        pygame.draw.line(self.screen, (200, 200, 255), 
                        (panel_x + panel_width, panel_y + panel_height), (panel_x + panel_width - corner_size, panel_y + panel_height), 2)
        pygame.draw.line(self.screen, (200, 200, 255), 
                        (panel_x + panel_width, panel_y + panel_height), (panel_x + panel_width, panel_y + panel_height - corner_size), 2)
        
        # 内部分割线
        pygame.draw.line(self.screen, (120, 120, 180), 
                        (panel_x, panel_y + 50), (panel_x + panel_width, panel_y + 50), 2)
        pygame.draw.line(self.screen, (120, 120, 180), 
                        (panel_x + 350, panel_y + 50), (panel_x + 350, panel_y + panel_height), 2)
        
        # 重置裁剪区域以绘制标题
        self.screen.set_clip(None)
        
        # 显示标题 - 添加发光效果
        title_shadow = self.chinese_font.render("角色状态", True, (100, 80, 0))
        self.screen.blit(title_shadow, (panel_x + (panel_width - title_text.get_width()) // 2 + 2, panel_y + 15 + 2))
        self.screen.blit(title_text, (panel_x + (panel_width - title_text.get_width()) // 2, panel_y + 15))
        
        # 设置裁剪区域 - 左侧面板
        left_panel_rect = pygame.Rect(panel_x, panel_y + 50, 350, panel_height - 50)
        self.screen.set_clip(left_panel_rect)
        
        # 应用滚动偏移
        scroll_y = -self.stats_scroll_offset
        
        # 显示角色基本信息
        self.screen.blit(name_text, (panel_x + 30, panel_y + 70 + scroll_y))
        self.screen.blit(level_text, (panel_x + 30, panel_y + 100 + scroll_y))
        
        # 计算生命、内力条的百分比
        hp_percent = self.player.health / self.player.max_health
        qi_percent = self.player.qi / self.player.max_qi
        exp_required = self.cultivation_system.get_experience_for_next_level(self.player.level)
        exp_percent = min(1.0, self.player.experience / exp_required) if exp_required > 0 else 1.0
        
        # 绘制生命、内力和经验条
        # 生命条
        self.render_stat_bar(
            panel_x + 30, panel_y + 130 + scroll_y, 
            300, 20, 
            (150, 0, 0), (255, 50, 50), 
            hp_percent, 
            f"生命: {self.player.health}/{self.player.max_health}"
        )
        
        # 内力条
        self.render_stat_bar(
            panel_x + 30, panel_y + 160 + scroll_y, 
            300, 20, 
            (0, 0, 150), (50, 50, 255), 
            qi_percent, 
            f"内力: {self.player.qi}/{self.player.max_qi}"
        )
        
        # 经验条
        self.render_stat_bar(
            panel_x + 30, panel_y + 190 + scroll_y, 
            300, 20, 
            (50, 100, 0), (100, 200, 0), 
            exp_percent, 
            f"经验: {self.player.experience}/{exp_required}"
        )
        
        # 基本属性
        attributes = [
            f"攻击: {self.player.attack}",
            f"防御: {self.player.defense}",
            f"速度: {self.player.speed}"
        ]
        
        for i, attr in enumerate(attributes):
            attr_text = self.chinese_font.render(attr, True, (200, 200, 200))
            self.screen.blit(attr_text, (panel_x + 30, panel_y + 230 + i * 30 + scroll_y))
        
        # 设置裁剪区域 - 右侧面板
        right_panel_rect = pygame.Rect(panel_x + 350, panel_y + 50, panel_width - 350, panel_height - 50)
        self.screen.set_clip(right_panel_rect)
        
        # 右侧面板 - 心法和装备信息
        right_panel_x = panel_x + 370
        
        # 心法标题 - 美化
        heart_method_title = self.chinese_font.render("心法", True, (220, 200, 100))
        title_width = heart_method_title.get_width()
        # 标题下划线
        pygame.draw.line(self.screen, (180, 160, 80), 
                        (right_panel_x, panel_y + 90 + scroll_y), 
                        (right_panel_x + title_width + 20, panel_y + 90 + scroll_y), 2)
        self.screen.blit(heart_method_title, (right_panel_x, panel_y + 70 + scroll_y))
        
        # 心法内容区域宽度
        heart_content_width = panel_width - 370 - 30
        
        if hasattr(self.player, "inborn_heart_method") and self.player.inborn_heart_method:
            heart_method = self.player.inborn_heart_method
            heart_text = self.chinese_font.render(f"{heart_method.name}", True, (180, 180, 255))
            
            # 文本自动换行处理
            description = heart_method.description
            words_per_line = int(heart_content_width / 20)  # 估计每行可以容纳多少个字符
            
            # 将长描述分割成多行
            desc_lines = []
            for i in range(0, len(description), words_per_line):
                if i + words_per_line < len(description):
                    desc_lines.append(description[i:i+words_per_line])
                else:
                    desc_lines.append(description[i:])
            
            self.screen.blit(heart_text, (right_panel_x + 20, panel_y + 100 + scroll_y))
            
            # 逐行渲染描述文本
            for i, line in enumerate(desc_lines):
                if i < 3:  # 限制最多显示三行描述
                    desc_text = self.chinese_font.render(f"描述: {line}" if i == 0 else line, True, (150, 150, 200))
                    self.screen.blit(desc_text, (right_panel_x + 20, panel_y + 130 + i * 25 + scroll_y))
            
            # 心法效果
            effects_title = self.chinese_font.render("效果:", True, (180, 180, 200))
            self.screen.blit(effects_title, (right_panel_x + 20, panel_y + 210 + scroll_y))
            
            # 从attribute_bonuses字典中获取值，如果不存在则默认为0
            attack_bonus = heart_method.attribute_bonuses.get('attack', 0)
            defense_bonus = heart_method.attribute_bonuses.get('defense', 0)
            qi_bonus = heart_method.attribute_bonuses.get('max_qi', 0)
            
            # 渲染心法效果，确保文本不重叠
            attack_effect = f"攻击 +{attack_bonus}" if attack_bonus != 0 else "攻击 +0"
            defense_effect = f"防御 +{defense_bonus}" if defense_bonus != 0 else "防御 +0"
            qi_effect = f"内力 +{qi_bonus}" if qi_bonus != 0 else "内力 +0"
            
            effect_texts = [attack_effect, defense_effect, qi_effect]
            for i, effect in enumerate(effect_texts):
                effect_text = self.chinese_font.render(effect, True, (150, 150, 180))
                self.screen.blit(effect_text, (right_panel_x + 40, panel_y + 240 + i * 25 + scroll_y))
        else:
            no_heart_text = self.chinese_font.render("未学习心法", True, (150, 150, 150))
            self.screen.blit(no_heart_text, (right_panel_x + 20, panel_y + 100 + scroll_y))
        
        # 装备与武学信息 - 添加更多分类
        # 装备标题 - 美化
        equipment_title = self.chinese_font.render("装备", True, (220, 200, 100))
        title_width = equipment_title.get_width()
        # 标题下划线
        pygame.draw.line(self.screen, (180, 160, 80), 
                        (right_panel_x, panel_y + 320 + scroll_y), 
                        (right_panel_x + title_width + 20, panel_y + 320 + scroll_y), 2)
        self.screen.blit(equipment_title, (right_panel_x, panel_y + 300 + scroll_y))
        
        # 渲染装备信息，确保文本不重叠
        equip_texts = [
            f"武器: {self.player.weapon}",
            f"护甲: {self.player.armor}"
        ]
        
        for i, equip in enumerate(equip_texts):
            equip_text = self.chinese_font.render(equip, True, (180, 180, 200))
            self.screen.blit(equip_text, (right_panel_x + 20, panel_y + 330 + i * 30 + scroll_y))
        
        # 武学招式部分
        techniques_title = self.chinese_font.render("武学招式", True, (220, 200, 100))
        title_width = techniques_title.get_width()
        # 标题下划线
        pygame.draw.line(self.screen, (180, 160, 80), 
                        (right_panel_x, panel_y + 400 + scroll_y), 
                        (right_panel_x + title_width + 20, panel_y + 400 + scroll_y), 2)
        self.screen.blit(techniques_title, (right_panel_x, panel_y + 380 + scroll_y))
        
        # 检查玩家是否有招式
        if hasattr(self.player, "techniques") and self.player.techniques:
            for i, technique in enumerate(self.player.techniques[:3]):  # 最多显示前三个招式
                tech_text = self.chinese_font.render(f"{technique.name}", True, (180, 180, 255))
                cooldown = f"冷却: {technique.cooldown}" if technique.cooldown > 0 else "可用"
                cooldown_color = (255, 100, 100) if technique.cooldown > 0 else (100, 255, 100)
                cooldown_text = self.chinese_font.render(cooldown, True, cooldown_color)
                
                self.screen.blit(tech_text, (right_panel_x + 20, panel_y + 410 + i * 30 + scroll_y))
                self.screen.blit(cooldown_text, (right_panel_x + 150, panel_y + 410 + i * 30 + scroll_y))
        else:
            no_tech_text = self.chinese_font.render("尚未学会武学招式", True, (150, 150, 150))
            self.screen.blit(no_tech_text, (right_panel_x + 20, panel_y + 410 + scroll_y))
        
        # 额外信息部分（如果需要滚动显示的更多内容）
        additional_info_y = panel_y + 490 + scroll_y
        if hasattr(self.player, "status_effects") and self.player.status_effects:
            status_title = self.chinese_font.render("状态效果", True, (220, 200, 100))
            title_width = status_title.get_width()
            # 标题下划线
            pygame.draw.line(self.screen, (180, 160, 80), 
                            (right_panel_x, additional_info_y + 20), 
                            (right_panel_x + title_width + 20, additional_info_y + 20), 2)
            self.screen.blit(status_title, (right_panel_x, additional_info_y))
            
            for i, effect in enumerate(self.player.status_effects):
                effect_text = self.chinese_font.render(f"{effect.name}: {effect.duration}回合", True, (180, 180, 200))
                self.screen.blit(effect_text, (right_panel_x + 20, additional_info_y + 30 + i * 25))
        
        # 重置裁剪区域
        self.screen.set_clip(None)
        
        # 添加滚动提示
        if self.stats_scroll_offset > 0:
            up_arrow = self.chinese_font.render("▲", True, (150, 150, 150))
            self.screen.blit(up_arrow, (panel_x + panel_width // 2, panel_y + 55))
        
        if self.stats_scroll_offset < self.max_scroll_offset:
            down_arrow = self.chinese_font.render("▼", True, (150, 150, 150))
            self.screen.blit(down_arrow, (panel_x + panel_width // 2, panel_y + panel_height - 20))
        
        # 底部操作提示 - 移动到屏幕底部
        hint_text = self.chinese_font.render("按 C 键或 ESC 键返回游戏，↑↓键滚动", True, (150, 150, 150))
        hint_text_x = (self.width - hint_text.get_width()) // 2
        hint_text_y = self.height - 30  # 距离屏幕底部30像素
        self.screen.blit(hint_text, (hint_text_x, hint_text_y))
    
    def render_stat_bar(self, x, y, width, height, bg_color, fill_color, percentage, label_text):
        """渲染属性条（生命、内力、经验等）"""
        # 绘制背景
        pygame.draw.rect(self.screen, bg_color, (x, y, width, height))
        
        # 绘制填充部分 - 添加渐变效果
        fill_width = int(width * percentage)
        if fill_width > 0:  # 避免百分比为0时的问题
            for i in range(fill_width):
                # 从左到右渐变
                r, g, b = fill_color
                gradient_factor = 0.7 + (i / fill_width) * 0.3
                color = (int(r * gradient_factor), int(g * gradient_factor), int(b * gradient_factor))
                pygame.draw.line(self.screen, color, (x + i, y), (x + i, y + height))
        
        # 绘制边框
        pygame.draw.rect(self.screen, (150, 150, 150), (x, y, width, height), 1)
        
        # 绘制文本标签
        label = self.chinese_font.render(label_text, True, (255, 255, 255))
        text_x = x + (width - label.get_width()) // 2
        text_y = y + (height - label.get_height()) // 2
        self.screen.blit(label, (text_x, text_y))
    
    def handle_mouse_movement(self, pos):
        """将鼠标点击转换为玩家移动"""
        # 计算网格大小
        grid_size = 20
        
        # 获取可见区域的起始坐标（世界坐标系）
        view_x = max(0, min(self.player.x - 15, self.world.width - 30))
        view_y = max(0, min(self.player.y - 10, self.world.height - 20))
        
        # 将屏幕坐标转换为世界坐标
        mouse_x, mouse_y = pos
        grid_x = view_x + mouse_x // grid_size
        grid_y = view_y + mouse_y // grid_size
        
        # 限制坐标在地图范围内
        grid_x = max(0, min(grid_x, self.world.width - 1))
        grid_y = max(0, min(grid_y, self.world.height - 1))
        
        # 设置点击位置指示器
        self.clicked_position = (grid_x, grid_y)
        self.click_indicator_timer = 10  # 显示10帧
        
        # 计算移动方向
        dx = 0
        dy = 0
        
        # 水平方向
        if grid_x > self.player.x:
            dx = 1
        elif grid_x < self.player.x:
            dx = -1
            
        # 垂直方向
        if grid_y > self.player.y:
            dy = 1
        elif grid_y < self.player.y:
            dy = -1
        
        # 优先选择离目标更近的方向移动（先水平移动还是先垂直移动）
        if dx != 0 and dy != 0:
            x_distance = abs(grid_x - self.player.x)
            y_distance = abs(grid_y - self.player.y)
            
            if x_distance > y_distance:
                # 水平距离更大，优先水平移动
                self.try_move(dx, 0)
            else:
                # 垂直距离更大，优先垂直移动
                self.try_move(0, dy)
        else:
            # 只有一个方向需要移动
            self.try_move(dx, dy) 