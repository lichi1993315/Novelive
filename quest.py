class Quest:
    def __init__(self, quest_id, title, description, npc_id):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.npc_id = npc_id
        self.completed = False
        self.objectives = []
        self.experience_reward = 0
        self.item_rewards = []
    
    def add_objective(self, objective):
        self.objectives.append(objective)
    
    def add_reward(self, experience, items=None):
        self.experience_reward = experience
        if items:
            self.item_rewards.extend(items)
    
    def check_completion(self, player):
        # Check if all objectives are completed
        for objective in self.objectives:
            if not objective.is_completed():
                return False
        
        # All objectives are completed
        self.completed = True
        return True
    
    def get_objective_status(self):
        # Return a list of objectives with completion status and progress information
        return [(obj.get_progress_description(), obj.is_completed()) for obj in self.objectives]
    
    def reset(self):
        """重置任务状态"""
        self.completed = False
        for objective in self.objectives:
            objective.current_progress = 0

class QuestObjective:
    def __init__(self, description, objective_type, target_id=None, quantity=1):
        self.description = description
        self.objective_type = objective_type  # KILL, COLLECT, TALK, EXPLORE
        self.target_id = target_id
        self.quantity = quantity
        self.current_progress = 0
    
    def update_progress(self, amount=1):
        self.current_progress += amount
        if self.current_progress > self.quantity:
            self.current_progress = self.quantity
    
    def is_completed(self):
        return self.current_progress >= self.quantity
        
    def get_progress_description(self):
        """返回包含进度信息的描述文本"""
        return f"{self.description} ({self.current_progress}/{self.quantity})"

class QuestSystem:
    def __init__(self):
        self.quests = {}
        self.initialize_quests()
    
    def initialize_quests(self):
        # 创建任务库
        from item import Equipment, Consumable, Material, QuestItem
        
        # 村庄任务 - 村长
        village_wolf_quest = Quest(1, "村子的危机", "村庄周围的灰狼越来越多，威胁村民安全。请帮助清理周围的狼群。", "长")
        village_wolf_quest.add_objective(QuestObjective("击杀灰狼", "KILL", "灰狼", 3))
        # 添加一把精致的普通武器作为奖励
        wolf_fang_sword = Equipment("狼牙剑", "用灰狼獠牙制成的锋利短剑，挥舞时带有一丝凌厉的气息。", 
                              "武器", {"attack": 8}, level_req=9, rarity="优秀", value=120)
        village_wolf_quest.add_reward(100, [wolf_fang_sword])
        self.quests[1] = village_wolf_quest
        
        # 村庄任务 - 铁匠
        blacksmith_quest = Quest(2, "材料收集", "铁匠需要特殊材料来打造新的武器。", "铁")
        blacksmith_quest.add_objective(QuestObjective("收集虎骨", "COLLECT", "虎骨", 2))
        # 铁匠打造的精钢武器
        steel_hammer = Equipment("精钢锤", "铁匠亲自打造的精钢锤，沉重而坚固，能够造成不俗的伤害。", 
                           "武器", {"attack": 12, "defense": 3}, level_req=8, rarity="优秀", value=180)
        health_potion = Consumable("强效回复药", "铁匠秘制的回复药剂，能够迅速恢复生命力。", 
                            {"health": 50}, rarity="优秀", value=50)
        blacksmith_quest.add_reward(150, [steel_hammer, health_potion])
        self.quests[2] = blacksmith_quest
        
        # 村庄任务 - 药商
        herb_quest = Quest(3, "草药采集", "药商需要特殊草药来制作疗伤药。", "药")
        herb_quest.add_objective(QuestObjective("收集草药", "COLLECT", "草药", 5))
        # 药商配制的强力药剂
        qi_potion = Consumable("灵气丹", "药商使用珍贵药材炼制的丹药，服用后能够恢复大量内力。", 
                         {"qi": 60}, rarity="稀有", value=100)
        herb_armor = Equipment("草药护甲", "药商用特殊草药浸泡处理过的轻便护甲，具有一定的防御能力。", 
                         "护甲", {"defense": 10, "max_health": 20}, level_req=9, rarity="优秀", value=150)
        herb_quest.add_reward(80, [qi_potion, herb_armor])
        self.quests[3] = herb_quest
        
        # 逍遥阁任务 - 掌门人
        master_quest = Quest(4, "武学考验", "掌门人想要测试你的武艺。", "掌")
        master_quest.add_objective(QuestObjective("击败山贼", "KILL", "山贼", 5))
        master_quest.add_objective(QuestObjective("击败猛虎", "KILL", "猛虎", 1))
        # 掌门人赐予的名贵武器
        jade_sword = Equipment("青玉剑", "逍遥阁掌门人亲自锻造的佳作，剑身通体青玉，锋利无比。", 
                         "武器", {"attack": 18, "speed": 2}, level_req=7, rarity="稀有", value=300)
        master_quest.add_reward(200, [jade_sword])
        self.quests[4] = master_quest
        
        # 逍遥阁任务 - 教习
        training_quest = Quest(5, "修炼之路", "要成为高手，需要不断修炼。", "师")
        training_quest.add_objective(QuestObjective("突破到蕴气境界", "LEVEL", "8", 1))
        # 修炼有成，获得进阶武器
        qiforce_gloves = Equipment("蕴气拳套", "能够引导体内气息的特殊拳套，修炼有成者能发挥其真正威力。", 
                            "武器", {"attack": 15, "max_qi": 30}, level_req=8, rarity="稀有", value=250)
        cultivation_manual = QuestItem("《气之要诀》", "记载了进阶蕴气技巧的秘籍，阅读后能更好地控制体内气息。", 5, rarity="稀有")
        training_quest.add_reward(250, [qiforce_gloves, cultivation_manual])
        self.quests[5] = training_quest
        
        # 逍遥阁任务 - 藏经阁管理员
        scroll_quest = Quest(6, "古籍寻找", "藏经阁需要找回丢失的古籍。", "藏")
        scroll_quest.add_objective(QuestObjective("收集残页", "COLLECT", "残页", 3))
        # 从古籍中获得的武学装备
        ancient_dagger = Equipment("残页匕首", "根据古籍记载的锻造手法制作的特殊匕首，轻巧锋利。", 
                            "武器", {"attack": 14, "speed": 3}, level_req=8, rarity="优秀", value=220)
        scroll_quest.add_reward(120, [ancient_dagger])
        self.quests[6] = scroll_quest
        
        # 逍遥阁任务 - 医师
        medicine_quest = Quest(7, "医者仁心", "医师需要制作特效药来救治村民。", "医")
        medicine_quest.add_objective(QuestObjective("收集妖兽内丹", "COLLECT", "内丹", 2))
        # 医师制作的回复药剂和护具
        master_potion = Consumable("神奇灵药", "医师倾尽所学制作的灵药，服用后能同时恢复生命和内力。", 
                            {"health": 80, "qi": 60}, rarity="稀有", value=200)
        healer_robe = Equipment("医者长袍", "医师赠送的特制长袍，穿戴后能增强体质。", 
                         "护甲", {"defense": 8, "max_health": 40}, level_req=7, rarity="稀有", value=200)
        medicine_quest.add_reward(180, [master_potion, healer_robe])
        self.quests[7] = medicine_quest
        
        # 洞窟探索任务 - 逍遥客栈老板
        cave_quest = Quest(8, "洞窟之谜", "有传闻说洞窟深处有一个强大的妖魔。", "店")
        cave_quest.add_objective(QuestObjective("击败洞窟之主", "KILL", "洞窟之主", 1))
        cave_quest.add_objective(QuestObjective("探索洞窟深处", "EXPLORE", "cave_boss_room", 1))
        # 洞窟之主掉落的传说武器
        cave_lord_blade = Equipment("洞窟魔刃", "从洞窟之主身上获得的神秘武器，蕴含着强大而诡异的力量。", 
                             "武器", {"attack": 25, "max_qi": 50}, level_req=7, rarity="传说", value=500)
        cave_essence = Consumable("洞窟精华", "从洞窟深处获得的神秘物质，服用后能大幅提升内力上限。", 
                           {"max_qi": 100}, rarity="稀有", value=300)
        cave_quest.add_reward(300, [cave_lord_blade, cave_essence])
        self.quests[8] = cave_quest
    
    def get_quest(self, quest_id):
        return self.quests.get(quest_id)
    
    def update_kill_objectives(self, player, monster_name):
        """更新击杀目标进度"""
        updated = False
        for quest in player.active_quests:
            for objective in quest.objectives:
                if objective.objective_type == "KILL" and objective.target_id == monster_name:
                    previous_progress = objective.current_progress
                    objective.update_progress()
                    updated = True
                    
                    # 如果是最新击杀，添加日志通知
                    if previous_progress != objective.current_progress:
                        if hasattr(self, 'log_system'):
                            self.log_system.add(f"任务进度：{objective.get_progress_description()}", "quest")
                    
                    if all(obj.is_completed() for obj in quest.objectives):
                        self.log_completion_status(quest)
        return updated
    
    def update_collect_objectives(self, player, item_name):
        """更新收集目标进度"""
        updated = False
        for quest in player.active_quests:
            for objective in quest.objectives:
                if objective.objective_type == "COLLECT" and objective.target_id == item_name:
                    previous_progress = objective.current_progress
                    objective.update_progress()
                    updated = True
                    
                    # 如果是最新收集，添加日志通知
                    if previous_progress != objective.current_progress:
                        if hasattr(self, 'log_system'):
                            self.log_system.add(f"任务进度：{objective.get_progress_description()}", "quest")
                    
                    if all(obj.is_completed() for obj in quest.objectives):
                        self.log_completion_status(quest)
        return updated
    
    def update_level_objectives(self, player, new_level):
        """更新等级目标进度"""
        updated = False
        for quest in player.active_quests:
            for objective in quest.objectives:
                if objective.objective_type == "LEVEL" and objective.target_id == str(new_level):
                    previous_progress = objective.current_progress
                    objective.update_progress()
                    updated = True
                    
                    # 如果是最新等级突破，添加日志通知
                    if previous_progress != objective.current_progress:
                        if hasattr(self, 'log_system'):
                            self.log_system.add(f"任务进度：{objective.get_progress_description()}", "quest")
                    
                    if all(obj.is_completed() for obj in quest.objectives):
                        self.log_completion_status(quest)
        return updated
    
    def update_explore_objectives(self, player, area_id):
        """更新探索目标进度"""
        updated = False
        for quest in player.active_quests:
            for objective in quest.objectives:
                if objective.objective_type == "EXPLORE" and objective.target_id == area_id:
                    previous_progress = objective.current_progress
                    objective.update_progress()
                    updated = True
                    
                    # 如果是最新探索，添加日志通知
                    if previous_progress != objective.current_progress:
                        if hasattr(self, 'log_system'):
                            self.log_system.add(f"任务进度：{objective.get_progress_description()}", "quest")
                    
                    if all(obj.is_completed() for obj in quest.objectives):
                        self.log_completion_status(quest)
        return updated
    
    def log_completion_status(self, quest):
        """记录任务完成状态，用于通知日志系统"""
        # 该方法会被Game类通过回调调用
        pass
    
    def set_log_system(self, log_system):
        """设置日志系统引用"""
        self.log_system = log_system
        
        # 重定义log_completion_status方法来使用日志系统
        def log_completion(quest):
            if hasattr(self, 'log_system'):
                # 基本的任务完成通知
                self.log_system.add(f"任务「{quest.title}」的所有目标已完成，请向{quest.npc_id}报告。", "quest")
                
                # 如果有奖励，添加奖励预览
                reward_info = []
                if quest.experience_reward > 0:
                    reward_info.append(f"经验值: {quest.experience_reward}")
                
                # 添加物品奖励预览
                if quest.item_rewards:
                    item_names = []
                    for item in quest.item_rewards:
                        # 根据稀有度添加不同颜色提示
                        rarity_mark = ""
                        if item.rarity == "传说":
                            rarity_mark = "【传说】"
                        elif item.rarity == "稀有":
                            rarity_mark = "【稀有】"
                        elif item.rarity == "优秀":
                            rarity_mark = "【优秀】"
                        
                        item_names.append(f"{rarity_mark}{item.name}")
                    
                    reward_info.append(f"物品: {', '.join(item_names)}")
                
                # 如果有奖励信息，添加到日志
                if reward_info:
                    self.log_system.add(f"完成后可获得奖励: {'; '.join(reward_info)}", "quest")
        
        self.log_completion_status = log_completion
    
    def get_available_quests_for_npc(self, npc_char):
        """获取NPC可提供的任务"""
        available_quests = []
        for quest_id, quest in self.quests.items():
            if quest.npc_id == npc_char and not quest.completed:
                # 将符合条件的任务添加到可用任务列表（由对话系统进一步过滤）
                available_quests.append(quest)
        return available_quests 