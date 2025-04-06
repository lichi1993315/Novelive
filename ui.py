import pygame

class UI:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.width, self.height = screen.get_size()
        self.text_color = (255, 255, 255)
        self.ui_bg_color = (20, 20, 30)  # 改为深蓝色基调
        self.ui_border_color = (100, 100, 150)  # 改为蓝紫色边框
        
        # 日志面板参数 - 设为属性以便动态调整
        self.log_width = 250
        self.log_height = 300
        # 注意: 实际的log_x和log_y会在render_logs中计算
        # 这里只是初始默认值
        self.log_x = self.width - self.log_width - 10
        self.log_y = 300  # 默认值，实际会根据任务面板高度自动调整
        
        # 设置统一的UI样式
        self.panel_alpha = 200  # 半透明度
        self.title_bg_color = (60, 60, 90, 230)  # 标题背景颜色
        self.title_color = (255, 215, 0)  # 金色标题文字
        
        # 玩家状态面板高度
        self.player_stats_height = 110
        
        # 背包UI相关参数
        self.inventory_active_tab = "全部"  # 当前激活的标签
        self.inventory_scroll = 0  # 背包滚动位置
        self.selected_item_index = -1  # 当前选中的物品索引
        self.item_tooltip_active = False  # 是否显示物品提示
        self.tooltip_item = None  # 当前提示的物品
    
    def adjust_log_width(self, amount):
        """调整日志面板宽度"""
        self.log_width = max(150, min(350, self.log_width + amount))
        self.log_x = self.width - self.log_width - 10
    
    def adjust_log_height(self, amount):
        """调整日志面板高度"""
        self.log_height = max(150, min(400, self.log_height + amount))
    
    def render_text(self, text, x, y, color=None):
        if color is None:
            color = self.text_color
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def render_player_stats(self, player):
        # 创建一个底部状态面板
        panel_height = self.player_stats_height
        panel_y = self.height - panel_height
        
        # 绘制半透明背景而不是完全不透明
        s = pygame.Surface((self.width, panel_height), pygame.SRCALPHA)
        s.fill((*self.ui_bg_color, self.panel_alpha))  # 使用与其他面板相同的半透明背景
        self.screen.blit(s, (0, panel_y))
        
        # 绘制顶部边框
        pygame.draw.line(self.screen, self.ui_border_color, 
                         (0, panel_y), (self.width, panel_y), 2)
        
        # 获取境界名称
        realm_name = "未知"
        if hasattr(player, "cultivation_system") and player.cultivation_system:
            realm = player.cultivation_system.get_realm(player.level)
            if realm:
                realm_name = realm.name
        
        # 计算所有文本位置以适应不同宽度
        left_column_x = 15
        right_column_x = min(420, self.width // 2 + 20)
        bar_width = min(180, (self.width // 2) - 50)
        bar_start_x = 170  # 调整进度条起始位置，避免与文本重叠
        
        # 行距设置
        line_height = 24  # 增加行距
        
        # Basic info - 加入境界信息
        self.render_text(f"境界: {realm_name}  经验: {player.experience}", left_column_x, panel_y + 12)
        
        # Health bar
        health_percent = player.health / player.max_health
        self.render_text(f"生命: {player.health}/{player.max_health}", left_column_x, panel_y + 12 + line_height)
        pygame.draw.rect(self.screen, (50, 0, 0), (bar_start_x, panel_y + 16 + line_height, bar_width, 12))
        pygame.draw.rect(self.screen, (200, 0, 0), (bar_start_x, panel_y + 16 + line_height, int(bar_width * health_percent), 12))
        
        # Qi bar
        qi_percent = player.qi / player.max_qi
        self.render_text(f"内力: {player.qi}/{player.max_qi}", left_column_x, panel_y + 12 + line_height * 2)
        pygame.draw.rect(self.screen, (0, 0, 50), (bar_start_x, panel_y + 16 + line_height * 2, bar_width, 12))
        pygame.draw.rect(self.screen, (0, 0, 200), (bar_start_x, panel_y + 16 + line_height * 2, int(bar_width * qi_percent), 12))
        
        # Equipment
        self.render_text(f"武器: {player.weapon}  护甲: {player.armor}", right_column_x, panel_y + 12)
        self.render_text(f"攻击: {player.attack}  防御: {player.defense}  速度: {player.speed}", right_column_x, panel_y + 12 + line_height)
        
        # 心法信息
        heart_method_text = "心法: 无"
        if hasattr(player, "inborn_heart_method") and player.inborn_heart_method:
            heart_method_text = f"心法: {player.inborn_heart_method.name}"
        self.render_text(heart_method_text, right_column_x, panel_y + 12 + line_height * 2)
        
        # 状态效果信息
        status_effects = []
        if hasattr(player, "stunned") and player.stunned:
            status_effects.append("眩晕")
        if hasattr(player, "bleed") and player.bleed > 0:
            status_effects.append(f"流血({player.bleed})")
        if hasattr(player, "poison") and player.poison > 0:
            status_effects.append(f"中毒({player.poison})")
        
        if status_effects:
            self.render_text(f"状态: {', '.join(status_effects)}", right_column_x, panel_y + 12 + line_height * 3, (255, 150, 0))
        
        # 操作提示信息（包含窗口调整快捷键）
        controls_text = "WASD-移动 E-交互 B-突破 C-状态 +/-/0-窗口大小"
        self.render_text(controls_text, 15, panel_y + panel_height - 22, (150, 150, 150))
    
    def render_combat_options(self):
        # Create a combat panel at the bottom right
        panel_width = 250
        panel_height = 160  # 增加高度以提供更好的间距
        panel_x = self.width - panel_width - 10
        panel_y = self.height - panel_height - 120
        
        # 半透明背景
        bg_color = (*self.ui_bg_color[:3], 220)  # 添加透明度
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill(bg_color)
        self.screen.blit(s, (panel_x, panel_y))
        
        # 绘制边框
        pygame.draw.rect(self.screen, self.ui_border_color, 
                         (panel_x, panel_y, panel_width, panel_height), 2)
        
        # 行距设置
        line_height = 26  # 增加行距
        
        # 标题 - 稍微增加字体大小和颜色
        title_color = (220, 180, 60)  # 金色标题
        title_surface = self.font.render("战斗选项", True, title_color)
        self.screen.blit(title_surface, (panel_x + 15, panel_y + 14))
        
        # 战斗选项
        self.render_text("1. 普通攻击", panel_x + 22, panel_y + 14 + line_height, (200, 200, 200))
        self.render_text("2. 特殊攻击", panel_x + 22, panel_y + 14 + line_height * 2, (200, 200, 200))
        self.render_text("3. 防御", panel_x + 22, panel_y + 14 + line_height * 3, (200, 200, 200))
        self.render_text("4. 使用招式", panel_x + 22, panel_y + 14 + line_height * 4, (200, 200, 200))
        
        # 添加分隔线
        line_y = panel_y + 14 + line_height * 5 - 5
        pygame.draw.line(self.screen, (100, 100, 100), 
                         (panel_x + 15, line_y), (panel_x + panel_width - 15, line_y), 1)
        
        # 小提示
        self.render_text("* 特殊攻击消耗内力", panel_x + 22, panel_y + 14 + line_height * 5 + 5, (150, 150, 200))
        self.render_text("A - 开启/关闭自动战斗", panel_x + 22, panel_y + 14 + line_height * 6 + 2, (150, 150, 200))
    
    def render_monster_stats(self, monster):
        # Create a monster stat panel at the top right
        panel_width = 250
        panel_height = 110  # 增加高度以提供更好的间距
        panel_x = self.width - panel_width - 10
        panel_y = 10
        
        # Draw panel background
        pygame.draw.rect(self.screen, self.ui_bg_color, 
                         (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.ui_border_color, 
                         (panel_x, panel_y, panel_width, panel_height), 2)
        
        # 行距设置
        line_height = 24  # 统一行距
        
        # Monster info - 怪物名称
        self.render_text(f"{monster.name}", panel_x + 15, panel_y + 14, (255, 200, 100))
        
        # Health bar
        health_percent = monster.health / monster.max_health
        self.render_text(f"生命: {monster.health}/{monster.max_health}", panel_x + 15, panel_y + 14 + line_height)
        
        # 调整进度条位置和尺寸
        bar_start_x = panel_x + 120
        bar_width = 120
        pygame.draw.rect(self.screen, (50, 0, 0), (bar_start_x, panel_y + 18 + line_height, bar_width, 12))
        pygame.draw.rect(self.screen, (200, 0, 0), (bar_start_x, panel_y + 18 + line_height, int(bar_width * health_percent), 12))
        
        # Stats
        self.render_text(f"攻击: {monster.attack}  防御: {monster.defense}", panel_x + 15, panel_y + 14 + line_height * 2)
        
        # 状态效果
        status_effects = []
        if hasattr(monster, "stunned") and monster.stunned:
            status_effects.append("眩晕")
        if hasattr(monster, "bleed") and monster.bleed > 0:
            status_effects.append(f"流血({monster.bleed})")
        if hasattr(monster, "poison") and monster.poison > 0:
            status_effects.append(f"中毒({monster.poison})")
        
        if status_effects:
            self.render_text(f"状态: {', '.join(status_effects)}", panel_x + 15, panel_y + 14 + line_height * 3, (255, 150, 0))
    
    def render_dialog_box(self, text, npc_name):
        # Create a dialog box at the bottom of the screen
        box_width = self.width - 100
        box_height = 150
        box_x = 50
        box_y = self.height - box_height - 120  # 调整位置以避免与状态栏重叠
        
        # Draw box background
        pygame.draw.rect(self.screen, self.ui_bg_color, 
                         (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, self.ui_border_color, 
                         (box_x, box_y, box_width, box_height), 2)
        
        # NPC name
        name_box_width = len(npc_name) * 15 + 20
        pygame.draw.rect(self.screen, self.ui_bg_color, 
                         (box_x + 10, box_y - 15, name_box_width, 30))
        pygame.draw.rect(self.screen, self.ui_border_color, 
                         (box_x + 10, box_y - 15, name_box_width, 30), 2)
        self.render_text(npc_name, box_x + 20, box_y - 10)
        
        # Dialog text - word wrap implementation
        max_width = box_width - 40
        words = text.split(' ')
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + ' ' + word
            test_width = self.font.size(test_line)[0]
            if test_width < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        
        # Render text lines
        line_height = self.font.get_height()
        for i, line in enumerate(lines):
            self.render_text(line, box_x + 20, box_y + 20 + i * line_height)
        
        # Prompt
        self.render_text("按空格键或回车键继续...", box_x + box_width - 230, box_y + box_height - 30)
    
    def render_technique_selection(self, techniques):
        """渲染招式选择界面"""
        # 创建招式选择面板
        panel_width = 300
        panel_height = 300
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        # 绘制面板背景
        pygame.draw.rect(self.screen, self.ui_bg_color, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.ui_border_color, 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # 标题
        self.render_text("选择招式:", panel_x + 10, panel_y + 10, (255, 215, 0))
        
        # 列出招式
        y_offset = 40
        for i, technique in enumerate(techniques):
            # 招式名称
            self.render_text(f"{i+1}. {technique.name}", panel_x + 20, panel_y + y_offset)
            
            # 描述
            self.render_text(f"   {technique.description[:40]}...", panel_x + 20, panel_y + y_offset + 20, (200, 200, 200))
            
            # 内力消耗与冷却
            qi_color = (150, 150, 255) if technique.qi_cost > 0 else (150, 150, 150)
            cooldown_color = (255, 150, 150) if technique.cooldown > 0 else (150, 150, 150)
            self.render_text(f"   内力: {technique.qi_cost}", panel_x + 20, panel_y + y_offset + 40, qi_color)
            self.render_text(f"   冷却: {technique.cooldown}", panel_x + 150, panel_y + y_offset + 40, cooldown_color)
            
            y_offset += 60
            
            # 最多显示4个招式
            if i >= 3:
                break
        
        # 提示
        self.render_text("按数字键选择，按ESC取消", panel_x + 20, panel_y + panel_height - 30, (150, 150, 150))
    
    def render_stats(self, player, cultivation_system):
        """渲染玩家状态栏"""
        # 背景
        stats_rect = pygame.Rect(10, 10, 780, 30)
        pygame.draw.rect(self.screen, self.ui_bg_color, stats_rect)
        pygame.draw.rect(self.screen, self.ui_border_color, stats_rect, 2)
        
        # 获取玩家的境界
        realm = cultivation_system.get_realm(player.level)
        realm_name = realm.name if realm else "无境界"
        
        # 显示玩家信息
        stats_text = f"境界: {realm_name} | 生命: {player.health}/{player.max_health} | 内力: {player.qi}/{player.max_qi} | 经验: {player.experience}"
        self.render_text(stats_text, 20, 20)
    
    def render_combat_ui(self, player, monster):
        """渲染战斗界面"""
        # 战斗信息面板背景
        combat_rect = pygame.Rect(10, self.height - 100, self.width - 20, 90)
        pygame.draw.rect(self.screen, self.ui_bg_color, combat_rect)
        pygame.draw.rect(self.screen, self.ui_border_color, combat_rect, 2)
        
        # 显示敌人信息
        monster_info = f"敌人: {monster.name} | 生命: {monster.health}/{monster.max_health}"
        self.render_text(monster_info, 20, self.height - 90)
        
        # 显示可用操作
        actions_text = "战斗操作: [1] 基本攻击  |  [2] 特殊攻击  |  [3] 防御"
        self.render_text(actions_text, 20, self.height - 60)
        
        # 如果玩家有招式，显示它们
        if hasattr(player, "techniques") and player.techniques:
            techniques_text = "武学招式:"
            y_pos = self.height - 30
            for i, technique in enumerate(player.techniques):
                cooldown_info = f" (冷却中: {technique.cooldown}回合)" if technique.cooldown > 0 else ""
                tech_text = f"[{i+4}] {technique.name}{cooldown_info}"
                techniques_text += f" | {tech_text}"
            self.render_text(techniques_text, 20, y_pos)
    
    def render_game_over(self):
        """渲染游戏结束画面"""
        self.screen.fill((0, 0, 0))
        
        # 游戏结束文字
        game_over_text = "游戏结束"
        text_surface = self.font.render(game_over_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(text_surface, text_rect)
        
        # 重新开始提示
        restart_text = "按任意键重新开始"
        text_surface = self.font.render(restart_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
    
    def render_prompt(self, message):
        """渲染提示消息"""
        prompt_rect = pygame.Rect(10, self.height - 40, self.width - 20, 30)
        pygame.draw.rect(self.screen, self.ui_bg_color, prompt_rect)
        pygame.draw.rect(self.screen, self.ui_border_color, prompt_rect, 2)
        self.render_text(message, 20, self.height - 30)
    
    def render(self, player, logs):
        """主游戏UI渲染方法"""
        # 渲染玩家状态界面
        self.render_player_stats(player)
        
        # 先渲染任务面板
        quest_panel_height = 0
        if hasattr(player, "active_quests") and player.active_quests:
            quest_panel_height = self.render_quest_tracker(player.active_quests)
            if quest_panel_height is None:  # 防止返回None
                quest_panel_height = 0
        
        # 渲染日志面板 - 传入任务面板高度以正确定位
        self.render_logs(logs, quest_panel_height)
    
    def render_logs(self, logs, quest_panel_height=0):
        """渲染日志部分，显示在窗口右侧，任务窗口下方，并自动调整高度避免与底部状态栏重叠"""
        # 使用类属性而不是局部变量
        log_width = self.log_width
        
        # 根据任务面板高度调整日志面板的位置
        log_x = self.width - log_width - 10
        
        # 日志窗口y位置：如果有任务面板，则在其下方；否则在顶部
        if quest_panel_height and quest_panel_height > 0:
            log_y = 10 + quest_panel_height + 10  # 在任务窗口下方10像素的位置
        else:
            log_y = 10  # 如果没有任务窗口，直接在顶部
        
        # 动态调整日志窗口高度，确保不会与底部状态栏重叠
        max_height = self.height - log_y - self.player_stats_height - 20  # 减去底部状态栏高度和额外间距
        log_height = min(self.log_height, max_height)  # 确保不超过最大可用高度
        
        # 保存当前计算的位置到类属性，以便其他方法可以使用
        self.log_x = log_x
        self.log_y = log_y
        
        # 绘制半透明背景 - 使用与任务追踪相同的风格
        s = pygame.Surface((log_width, log_height), pygame.SRCALPHA)
        s.fill((*self.ui_bg_color, self.panel_alpha))  # 使用统一的半透明背景色
        self.screen.blit(s, (log_x, log_y))
        
        # 绘制边框和标题背景
        pygame.draw.rect(self.screen, self.ui_border_color, 
                         (log_x, log_y, log_width, log_height), 2)
        
        # 添加标题背景 - 与任务追踪相同的样式
        title_bg = pygame.Surface((log_width, 30), pygame.SRCALPHA)
        title_bg.fill(self.title_bg_color)
        self.screen.blit(title_bg, (log_x, log_y))
        
        # 显示日志标题
        title_text = self.font.render("日志:", True, self.title_color)
        self.screen.blit(title_text, (log_x + 10, log_y + 5))
        
        # 显示调整提示
        adjust_text = self.font.render("[ / ] - 宽度  [ ; ' ] - 高度", True, (150, 150, 150))
        self.screen.blit(adjust_text, (log_x + log_width - 180, log_y + 5))
        
        # 显示最近的日志消息
        if logs:
            line_height = 20  # 每行高度
            line_spacing = 4  # 行间距
            entry_spacing = 8  # 条目间距
            y_offset = 35  # 日志开始的y偏移
            
            # 计算可显示的日志条目数，基于可用高度
            visible_log_area = log_height - 40  # 减去标题和边距
            
            # 计算日志区域内部可用宽度（减去左右边距和滚动条区域）
            usable_width = log_width - 25
            
            # 计算每个字符的平均宽度（考虑中文和英文混合情况）
            # 注意：实际渲染时每个字符宽度不同，这里取一个近似值
            test_str = "测试中文abcABC123"
            avg_char_width = self.font.size(test_str)[0] / len(test_str) * 0.95  # 乘以0.95作为安全系数
            
            # 估算每行可容纳的最大字符数
            max_chars_per_line = int(usable_width / avg_char_width)
            
            # 处理并渲染日志条目
            rendered_entries = 0
            current_y = log_y + y_offset
            
            # 从最新的日志开始渲染，直到填满可见区域
            for log_entry in reversed(logs):
                message = log_entry["message"]
                msg_type = log_entry["type"]
                
                # 根据日志类型选择颜色
                color = (255, 255, 255)  # 默认白色
                if msg_type == "combat":
                    color = (255, 100, 100)  # 战斗日志红色
                elif msg_type == "success":
                    color = (100, 255, 100)  # 成功消息绿色
                elif msg_type == "warning":
                    color = (255, 255, 0)  # 警告黄色
                elif msg_type == "system":
                    color = (100, 100, 255)  # 系统消息蓝色
                elif msg_type == "item":
                    color = (255, 165, 0)  # 物品消息橙色
                elif msg_type == "quest":
                    color = (255, 215, 0)  # 任务消息金色
                
                # 处理文本换行 - 使用更精确的方法
                lines = []
                remaining_text = message
                
                while remaining_text:
                    # 尝试找到合适的断行点
                    line_text = remaining_text
                    test_width = self.font.size(line_text)[0]
                    
                    # 如果当前文本适合在一行内，直接添加
                    if test_width <= usable_width:
                        lines.append(line_text)
                        break
                    
                    # 否则，需要寻找合适的断行点
                    cutoff = len(line_text)
                    while cutoff > 0 and self.font.size(line_text[:cutoff])[0] > usable_width:
                        cutoff -= 1
                    
                    # 找到最后一个空格作为断点（除非是中文文本）
                    if " " in line_text[:cutoff]:
                        # 对于包含英文的文本，尝试在空格处断行
                        last_space = line_text[:cutoff].rstrip().rfind(" ")
                        if last_space > 0:
                            cutoff = last_space + 1  # +1 to include the space
                    
                    # 添加当前行并更新剩余文本
                    lines.append(line_text[:cutoff])
                    remaining_text = remaining_text[cutoff:].lstrip()
                
                # 计算此条目总共需要的高度
                entry_height = len(lines) * line_height + (len(lines) - 1) * line_spacing
                
                # 检查是否还有足够空间显示这条日志
                if current_y + entry_height > log_y + log_height - 10:
                    break
                
                # 渲染每一行
                for i, line in enumerate(lines):
                    line_y = current_y + i * (line_height + line_spacing)
                    # 确保文本不超出日志窗口底部
                    if line_y < log_y + log_height - 15:
                        self.render_text(line, log_x + 15, line_y, color)
                
                # 更新垂直位置和计数
                current_y += entry_height + entry_spacing
                rendered_entries += 1
                
                # 如果已经渲染了足够多的条目，就停止
                if rendered_entries >= 8:  # 最多显示8条日志
                    break
                    
        return log_height  # 返回实际使用的日志高度

    def update_screen_size(self, width, height):
        """更新UI组件以适应新的屏幕尺寸"""
        self.width = width
        self.height = height
        
        # 重新计算日志面板位置的x坐标
        # 注意：y坐标将在渲染时根据任务面板的存在与否动态计算
        self.log_x = self.width - self.log_width - 10
        
        # 检查日志面板是否超出屏幕
        if self.log_x < 400:  # 确保留出至少400像素给游戏区域
            self.log_width = self.width - 410
            self.log_x = self.width - self.log_width - 10
        
        # 确保日志高度不超过屏幕高度
        if self.log_height > self.height - 120:  # 保留底部空间给状态栏
            self.log_height = self.height - 120
    
    def render_quest_tracker(self, active_quests):
        """渲染任务追踪器，并返回面板高度"""
        if not active_quests:
            return 0
            
        # 计算任务和目标的总数，用于动态调整高度
        total_objectives = 0
        for quest in active_quests[:3]:  # 最多考虑3个任务
            total_objectives += len(quest.objectives)
        
        # 任务面板设置
        panel_width = 250
        # 根据任务和目标数量动态调整高度
        base_height = 60  # 基础高度（标题和边距）
        quest_title_height = 25  # 每个任务标题高度
        quest_margin = 20  # 任务之间的间距
        objective_height = 25  # 每个目标的基础高度
        
        # 计算动态面板高度
        panel_height = base_height + (quest_title_height + quest_margin) * min(3, len(active_quests)) + objective_height * total_objectives
        panel_height = min(350, panel_height)  # 设置最大高度上限
        
        panel_x = self.width - panel_width - 10  # 放置在右上角
        panel_y = 10
        
        # 绘制半透明背景
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill((*self.ui_bg_color, self.panel_alpha))  # 使用统一的半透明背景色
        self.screen.blit(s, (panel_x, panel_y))
        
        # 绘制边框和标题背景
        pygame.draw.rect(self.screen, self.ui_border_color, 
                         (panel_x, panel_y, panel_width, panel_height), 2)
        
        # 渲染标题
        title_bg = pygame.Surface((panel_width, 30), pygame.SRCALPHA)
        title_bg.fill(self.title_bg_color)
        self.screen.blit(title_bg, (panel_x, panel_y))
        
        title_text = self.font.render("任务追踪", True, self.title_color)
        self.screen.blit(title_text, (panel_x + 10, panel_y + 5))
        
        # 渲染任务列表
        y_offset = panel_y + 35
        for i, quest in enumerate(active_quests[:3]):  # 最多显示3个任务
            # 任务标题
            quest_title = self.font.render(quest.title, True, (200, 200, 255))
            self.screen.blit(quest_title, (panel_x + 10, y_offset))
            
            # 任务目标
            objective_y = y_offset + 25
            for obj_desc, completed in quest.get_objective_status():
                # 目标描述截断 - 保留进度指示器部分
                progress_part = ""
                if "(" in obj_desc and ")" in obj_desc:
                    main_text, progress_part = obj_desc.rsplit("(", 1)
                    progress_part = "(" + progress_part
                    main_text = main_text.strip()
                    
                    # 如果主文本太长，截断它
                    if len(main_text) > 18:
                        main_text = main_text[:15] + "..."
                        
                    # 重新组合文本
                    obj_desc = f"{main_text} {progress_part}"
                elif len(obj_desc) > 25:
                    obj_desc = obj_desc[:22] + "..."
                
                # 目标完成状态指示
                status_mark = "✓" if completed else "□"
                status_color = (100, 255, 100) if completed else (200, 200, 200)
                
                # 进度指示器颜色变化
                if not completed and progress_part:
                    # 计算进度百分比用于颜色渐变
                    try:
                        current, total = progress_part.strip("()").split("/")
                        progress_pct = int(current) / int(total)
                        # 从红到绿的颜色渐变
                        r = int(255 * (1 - progress_pct))
                        g = int(200 * progress_pct)
                        b = 50
                        status_color = (r, g, b)
                    except:
                        pass
                
                # 使用_render_wrapped_text渲染目标文本，确保自动换行
                height_used = self._render_wrapped_text(
                    f"{status_mark} {obj_desc}", 
                    panel_x + 20, 
                    objective_y,
                    panel_width - 30,  # 减去边距
                    status_color
                )
                
                objective_y += height_used + 5  # 添加额外间距
            
            # 添加任务间分隔线
            if i < len(active_quests) - 1:
                line_y = objective_y + 5  # 在最后一个目标下方添加分隔线
                pygame.draw.line(self.screen, self.ui_border_color, 
                              (panel_x + 10, line_y), 
                              (panel_x + panel_width - 10, line_y), 1)
                y_offset = line_y + 10  # 下一个任务从分隔线下方开始
            else:
                # 如果是最后一个任务，更新y_offset为最后一个目标的位置
                y_offset = objective_y
        
        # 如果有更多任务
        if len(active_quests) > 3:
            more_text = self.font.render(f"...还有{len(active_quests)-3}个任务", True, (150, 150, 150))
            self.screen.blit(more_text, (panel_x + 10, panel_y + panel_height - 25))
            
        # 返回面板高度，以便日志窗口定位
        return panel_height

    def render_inventory(self, player):
        """渲染背包界面 - 风格与角色信息界面一致"""
        # 创建半透明背景覆盖游戏区域，但保留底部状态栏
        bg = pygame.Surface((self.width, self.height - self.player_stats_height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))  # 半透明黑色背景
        self.screen.blit(bg, (0, 0))
        
        # 背包主面板 - 调整为不覆盖底部状态栏
        panel_width = int(self.width * 0.8)
        panel_height = int(self.height * 0.8) - self.player_stats_height
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - self.player_stats_height - panel_height) // 2
        
        # 绘制背包主面板背景
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((*self.ui_bg_color, self.panel_alpha))  # 使用与其他面板相同的半透明背景
        self.screen.blit(panel_bg, (panel_x, panel_y))
        
        # 绘制边框
        pygame.draw.rect(self.screen, self.ui_border_color, 
                         (panel_x, panel_y, panel_width, panel_height), 2)
        
        # 标题区域 - 使用与其他面板相同的标题样式
        title_bg = pygame.Surface((panel_width, 30), pygame.SRCALPHA)
        title_bg.fill(self.title_bg_color)
        self.screen.blit(title_bg, (panel_x, panel_y))
        
        title_text = self.font.render("背包", True, self.title_color)
        self.screen.blit(title_text, (panel_x + 20, panel_y + 5))
        
        # 背包信息
        info_text = self.font.render(f"已使用: {len(player.inventory)}/{player.max_inventory}", True, (200, 200, 200))
        self.screen.blit(info_text, (panel_x + panel_width - 150, panel_y + 5))
        
        # 分隔线
        pygame.draw.line(self.screen, self.ui_border_color, 
                         (panel_x, panel_y + 30), (panel_x + panel_width, panel_y + 30), 1)
        
        # 左侧分区 - 装备和角色
        left_width = int(panel_width * 0.25)
        character_section_height = 80
        equipment_section_height = 180  # 减小高度以适应新布局
        
        # 角色信息区
        char_section_y = panel_y + 40
        char_bg = pygame.Surface((left_width - 10, character_section_height), pygame.SRCALPHA)
        char_bg.fill((30, 30, 40, 200))
        self.screen.blit(char_bg, (panel_x + 10, char_section_y))
        
        # 显示角色信息
        self.render_text(f"角色: 修真者", panel_x + 20, char_section_y + 10, (200, 200, 255))
        self.render_text(f"境界: {self._get_realm_name(player)}", panel_x + 20, char_section_y + 30, (200, 200, 255))
        self.render_text(f"银两: {player.money}", panel_x + 20, char_section_y + 50, (255, 215, 0))
        
        # 装备区域
        equip_section_y = char_section_y + character_section_height + 10
        equip_bg = pygame.Surface((left_width - 10, equipment_section_height), pygame.SRCALPHA)
        equip_bg.fill((30, 30, 40, 200))
        self.screen.blit(equip_bg, (panel_x + 10, equip_section_y))
        
        # 装备区标题
        equip_title = self.font.render("装备", True, (200, 200, 255))
        self.screen.blit(equip_title, (panel_x + 20, equip_section_y + 10))
        
        # 装备槽位
        slot_height = 40
        slot_y = equip_section_y + 40
        
        # 武器槽
        pygame.draw.rect(self.screen, (50, 50, 60), 
                         (panel_x + 20, slot_y, left_width - 40, slot_height), 0)
        pygame.draw.rect(self.screen, (100, 100, 120), 
                         (panel_x + 20, slot_y, left_width - 40, slot_height), 1)
        
        weapon_icon = self.font.render("⚔", True, (255, 255, 255))
        self.screen.blit(weapon_icon, (panel_x + 30, slot_y + 10))
        self.render_text(f"武器: {player.weapon}", panel_x + 60, slot_y + 12, (255, 255, 255))
        
        # 护甲槽
        slot_y += slot_height + 10
        pygame.draw.rect(self.screen, (50, 50, 60), 
                         (panel_x + 20, slot_y, left_width - 40, slot_height), 0)
        pygame.draw.rect(self.screen, (100, 100, 120), 
                         (panel_x + 20, slot_y, left_width - 40, slot_height), 1)
        
        armor_icon = self.font.render("🛡", True, (255, 255, 255))
        self.screen.blit(armor_icon, (panel_x + 30, slot_y + 10))
        self.render_text(f"护甲: {player.armor}", panel_x + 60, slot_y + 12, (255, 255, 255))
        
        # 右侧物品区域
        right_x = panel_x + left_width + 10
        right_width = panel_width - left_width - 20
        
        # 标签页
        tabs = ["全部", "武器", "护甲", "消耗品", "材料", "任务"]
        tab_width = right_width // len(tabs)
        tab_height = 30
        
        for i, tab in enumerate(tabs):
            tab_x = right_x + i * tab_width
            # 绘制标签背景 - 当前激活标签使用不同颜色
            tab_bg_color = (60, 60, 90) if tab == self.inventory_active_tab else (40, 40, 60)
            pygame.draw.rect(self.screen, tab_bg_color, 
                             (tab_x, panel_y + 40, tab_width, tab_height), 0)
            pygame.draw.rect(self.screen, self.ui_border_color, 
                             (tab_x, panel_y + 40, tab_width, tab_height), 1)
            
            # 标签文字 - 添加数字提示
            tab_text = self.font.render(f"{i+1}:{tab}", True, (255, 255, 255))
            text_rect = tab_text.get_rect(center=(tab_x + tab_width//2, panel_y + 40 + tab_height//2))
            self.screen.blit(tab_text, text_rect)
        
        # 物品区域 - 调整高度以适应新布局
        items_area_y = panel_y + 40 + tab_height + 10
        items_area_height = panel_height - (40 + tab_height + 10 + 20)  # 减去顶部和底部的空间
        
        # 物品区域背景
        items_bg = pygame.Surface((right_width, items_area_height), pygame.SRCALPHA)
        items_bg.fill((30, 30, 40, 200))
        self.screen.blit(items_bg, (right_x, items_area_y))
        
        # 过滤当前标签对应的物品
        filtered_items = []
        if self.inventory_active_tab == "全部":
            filtered_items = player.inventory
        elif self.inventory_active_tab == "武器":
            filtered_items = [item for item in player.inventory if item.item_type == "武器"]
        elif self.inventory_active_tab == "护甲":
            filtered_items = [item for item in player.inventory if item.item_type == "护甲"]
        elif self.inventory_active_tab == "消耗品":
            filtered_items = [item for item in player.inventory if item.item_type == "消耗品"]
        elif self.inventory_active_tab == "材料":
            filtered_items = [item for item in player.inventory if item.item_type == "材料"]
        elif self.inventory_active_tab == "任务":
            filtered_items = [item for item in player.inventory if item.item_type == "任务物品"]
        
        # 显示物品
        if filtered_items:
            # 计算网格布局
            items_per_row = 4
            item_width = right_width // items_per_row
            item_height = 80
            
            # 显示物品
            for i, item in enumerate(filtered_items):
                # 计算物品网格位置
                row = i // items_per_row
                col = i % items_per_row
                
                # 检查是否在可见范围内
                if row < self.inventory_scroll // item_height:
                    continue
                
                if row > self.inventory_scroll // item_height + items_area_height // item_height:
                    continue
                
                item_x = right_x + col * item_width
                item_y = items_area_y + (row * item_height) - self.inventory_scroll
                
                # 物品背景 - 选中项使用不同颜色
                item_bg_color = (60, 60, 100) if i == self.selected_item_index else (50, 50, 70)
                pygame.draw.rect(self.screen, item_bg_color, 
                                 (item_x + 5, item_y + 5, item_width - 10, item_height - 10), 0)
                pygame.draw.rect(self.screen, (100, 100, 150), 
                                 (item_x + 5, item_y + 5, item_width - 10, item_height - 10), 1)
                
                # 物品图标
                icon_color = item.get_color()
                icon_text = self.font.render(item.icon, True, icon_color)
                self.screen.blit(icon_text, (item_x + 15, item_y + 15))
                
                # 物品名称 - 稀有度使用不同颜色
                name_text = self.font.render(item.get_display_name(), True, icon_color)
                self.screen.blit(name_text, (item_x + 40, item_y + 15))
                
                # 物品类型
                type_text = self.font.render(item.item_type, True, (200, 200, 200))
                self.screen.blit(type_text, (item_x + 40, item_y + 35))
                
                # 物品稀有度
                rarity_text = self.font.render(item.rarity, True, icon_color)
                self.screen.blit(rarity_text, (item_x + 40, item_y + 55))
        else:
            # 显示无物品提示
            no_items_text = self.font.render("当前分类没有物品", True, (200, 200, 200))
            text_rect = no_items_text.get_rect(center=(right_x + right_width//2, items_area_y + items_area_height//2))
            self.screen.blit(no_items_text, text_rect)
        
        # 如果物品过多，显示滚动条
        if filtered_items and len(filtered_items) > (items_area_height // 80) * 4:
            scroll_height = items_area_height
            content_height = (len(filtered_items) // 4 + (1 if len(filtered_items) % 4 > 0 else 0)) * 80
            
            # 滚动条背景
            pygame.draw.rect(self.screen, (40, 40, 50), 
                             (right_x + right_width - 15, items_area_y, 10, scroll_height), 0)
            
            # 滚动条滑块
            slider_ratio = items_area_height / content_height
            slider_height = max(30, int(scroll_height * slider_ratio))
            slider_pos = int(self.inventory_scroll / content_height * scroll_height)
            pygame.draw.rect(self.screen, (100, 100, 150), 
                             (right_x + right_width - 15, items_area_y + slider_pos, 10, slider_height), 0)
        
        # 在底部状态栏上方渲染操作提示，与角色信息UI一致
        panel_y_bottom = self.height - self.player_stats_height - 22
        controls_text = "方向键:选择物品 | 数字键1-6:切换分类 | I/ESC:关闭背包 | E:使用/装备 | D:丢弃"
        self.render_text(controls_text, 15, panel_y_bottom, (150, 150, 150))
        
        # 物品提示
        if self.item_tooltip_active and self.tooltip_item:
            self._render_item_tooltip(self.tooltip_item)
    
    def _render_item_tooltip(self, item):
        """渲染物品详细提示"""
        tooltip_width = 300
        tooltip_height = 200
        
        # 根据鼠标位置确定提示框位置，避免超出屏幕
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tooltip_x = min(mouse_x + 20, self.width - tooltip_width - 10)
        tooltip_y = min(mouse_y + 20, self.height - tooltip_height - 10)
        
        # 提示框背景
        tooltip_bg = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        tooltip_bg.fill((30, 30, 50, 240))
        self.screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
        
        # 提示框边框
        pygame.draw.rect(self.screen, (100, 100, 150), 
                         (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)
        
        # 物品名称
        name_color = item.get_color()
        name_text = self.font.render(item.get_display_name(), True, name_color)
        self.screen.blit(name_text, (tooltip_x + 15, tooltip_y + 15))
        
        # 物品类型和稀有度
        type_text = self.font.render(f"{item.item_type} · {item.rarity}", True, (200, 200, 200))
        self.screen.blit(type_text, (tooltip_x + 15, tooltip_y + 40))
        
        # 分隔线
        pygame.draw.line(self.screen, (100, 100, 150), 
                         (tooltip_x + 15, tooltip_y + 60), (tooltip_x + tooltip_width - 15, tooltip_y + 60), 1)
        
        # 物品描述
        self._render_wrapped_text(item.description, tooltip_x + 15, tooltip_y + 70, tooltip_width - 30, (200, 200, 200))
        
        # 物品属性（如果是装备）
        if hasattr(item, "stats") and item.stats:
            attr_y = tooltip_y + 120
            attr_text = self.font.render("属性:", True, (255, 215, 0))
            self.screen.blit(attr_text, (tooltip_x + 15, attr_y))
            
            # 显示每个属性
            attr_y += 20
            for stat, value in item.stats.items():
                if stat == "attack":
                    self.render_text(f"攻击: +{value}", tooltip_x + 25, attr_y, (255, 200, 100))
                elif stat == "defense":
                    self.render_text(f"防御: +{value}", tooltip_x + 25, attr_y, (255, 200, 100))
                elif stat == "speed":
                    self.render_text(f"速度: +{value}", tooltip_x + 25, attr_y, (255, 200, 100))
                elif stat == "max_health":
                    self.render_text(f"最大生命: +{value}", tooltip_x + 25, attr_y, (255, 200, 100))
                elif stat == "max_qi":
                    self.render_text(f"最大内力: +{value}", tooltip_x + 25, attr_y, (255, 200, 100))
                else:
                    self.render_text(f"{stat}: +{value}", tooltip_x + 25, attr_y, (255, 200, 100))
                
                attr_y += 20
        
        # 消耗品效果
        if hasattr(item, "effects") and item.effects:
            effect_y = tooltip_y + 120
            effect_text = self.font.render("效果:", True, (255, 215, 0))
            self.screen.blit(effect_text, (tooltip_x + 15, effect_y))
            
            # 显示每个效果
            effect_y += 20
            for effect, value in item.effects.items():
                if effect == "health":
                    self.render_text(f"恢复生命: {value}", tooltip_x + 25, effect_y, (100, 255, 100))
                elif effect == "qi":
                    self.render_text(f"恢复内力: {value}", tooltip_x + 25, effect_y, (100, 100, 255))
                else:
                    self.render_text(f"{effect}: {value}", tooltip_x + 25, effect_y, (255, 255, 255))
                
                effect_y += 20
        
        # 物品价值
        value_text = self.font.render(f"价值: {item.value} 银两", True, (255, 215, 0))
        self.screen.blit(value_text, (tooltip_x + 15, tooltip_y + tooltip_height - 30))
    
    def _render_wrapped_text(self, text, x, y, max_width, color):
        """渲染自动换行文本，返回使用的总高度"""
        words = text.split()
        lines = []
        current_line = words[0] if words else ""
        
        for word in words[1:]:
            test_line = current_line + " " + word
            if self.font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        line_height = self.font.get_height()
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, color)
            self.screen.blit(text_surface, (x, y + i * line_height))
        
        # 返回使用的总高度
        return len(lines) * line_height
    
    def _get_realm_name(self, player):
        """获取玩家境界名称"""
        if hasattr(player, "cultivation_system") and player.cultivation_system:
            realm = player.cultivation_system.get_realm(player.level)
            if realm:
                return realm.name
        return "未知" 