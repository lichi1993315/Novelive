class NPC:
    """NPC类，用于游戏中的非玩家角色"""
    def __init__(self, name, x, y, char="N", color=(0, 255, 255), dialog=None, quests=None):
        self.name = name
        self.x = x
        self.y = y
        self.char = char  # 用于显示的字符
        self.color = color  # 显示颜色
        self.dialog = dialog if dialog else ["你好，旅行者。"]  # 默认对话
        self.current_dialog_index = 0  # 当前对话索引
        self.quests = quests if quests else []  # NPC可提供的任务列表
        self.quest_dialogs = {}  # 任务相关的特殊对话
        self.is_merchant = False  # 是否是商人
        self.items_for_sale = []  # 售卖的物品
        self.can_teach = False  # 是否可以教导技能
        self.teachable_techniques = []  # 可教导的技能
    
    def get_dialog(self, player=None):
        """获取对话内容，可根据玩家状态返回不同对话"""
        # 检查是否有任务相关对话
        if player:
            for quest in self.quests:
                # 如果玩家有任务且任务来自此NPC
                if quest in player.active_quests:
                    # 检查任务是否可以完成
                    if quest.check_completion(player):
                        if "complete" in self.quest_dialogs.get(quest.id, {}):
                            return self.quest_dialogs[quest.id]["complete"]
                    else:
                        if "active" in self.quest_dialogs.get(quest.id, {}):
                            return self.quest_dialogs[quest.id]["active"]
                # 如果玩家尚未接受任务
                elif quest not in player.completed_quests:
                    if "offer" in self.quest_dialogs.get(quest.id, {}):
                        return self.quest_dialogs[quest.id]["offer"]
                # 如果玩家已完成任务
                elif quest in player.completed_quests:
                    if "completed" in self.quest_dialogs.get(quest.id, {}):
                        return self.quest_dialogs[quest.id]["completed"]
        
        # 如果没有特殊对话，返回默认对话
        if 0 <= self.current_dialog_index < len(self.dialog):
            return self.dialog[self.current_dialog_index]
        return "..."
    
    def next_dialog(self):
        """进入下一段对话"""
        if self.current_dialog_index < len(self.dialog) - 1:
            self.current_dialog_index += 1
            return True
        else:
            self.current_dialog_index = 0
            return False
    
    def reset_dialog(self):
        """重置对话到初始状态"""
        self.current_dialog_index = 0
    
    def add_quest(self, quest, dialogs=None):
        """添加任务和相关对话"""
        self.quests.append(quest)
        if dialogs:
            self.quest_dialogs[quest.id] = dialogs
    
    def set_merchant(self, is_merchant=True, items=None):
        """设置NPC为商人并添加商品"""
        self.is_merchant = is_merchant
        if items:
            self.items_for_sale = items
    
    def set_teacher(self, can_teach=True, techniques=None):
        """设置NPC为技能教师并添加可教授技能"""
        self.can_teach = can_teach
        if techniques:
            self.teachable_techniques = techniques
    
    def add_dialog(self, text):
        """添加对话内容"""
        self.dialog.append(text)
    
    def set_dialog(self, dialog_list):
        """设置对话内容"""
        self.dialog = dialog_list
        self.current_dialog_index = 0


class Quest:
    """任务类，用于游戏中的任务系统"""
    def __init__(self, id, title, description, objectives=None, experience_reward=0, item_rewards=None):
        self.id = id  # 任务唯一ID
        self.title = title  # 任务标题
        self.description = description  # 任务描述
        self.objectives = objectives if objectives else []  # 任务目标列表
        self.experience_reward = experience_reward  # 经验奖励
        self.item_rewards = item_rewards if item_rewards else []  # 物品奖励
        
        # 任务状态
        self.completed_objectives = {obj["id"]: False for obj in self.objectives}
    
    def add_objective(self, id, description, target=None, count=1, complete_function=None):
        """添加任务目标"""
        objective = {
            "id": id,
            "description": description,
            "target": target,  # 目标对象（如怪物类型、物品名称等）
            "count": count,    # 需要的数量
            "current": 0,      # 当前进度
            "complete_function": complete_function  # 自定义完成检查函数
        }
        self.objectives.append(objective)
        self.completed_objectives[id] = False
    
    def update_objective(self, objective_id, progress=1):
        """更新任务目标进度"""
        for obj in self.objectives:
            if obj["id"] == objective_id:
                obj["current"] += progress
                if obj["current"] >= obj["count"]:
                    self.completed_objectives[objective_id] = True
                return True
        return False
    
    def check_completion(self, player=None):
        """检查任务是否完成"""
        # 如果有自定义完成检查函数，使用它
        for obj in self.objectives:
            if "complete_function" in obj and obj["complete_function"] and player:
                self.completed_objectives[obj["id"]] = obj["complete_function"](player, obj)
            
            # 检查物品收集类目标
            elif "target" in obj and obj["target"] and player and "type" in obj and obj["type"] == "collect":
                self.completed_objectives[obj["id"]] = player.has_item(obj["target"], obj["count"])
        
        # 检查所有目标是否都完成
        return all(self.completed_objectives.values())
    
    def complete(self, player):
        """完成任务，给予奖励"""
        if not self.check_completion(player):
            return False, "任务尚未完成"
        
        # 给予经验奖励
        player.gain_experience(self.experience_reward)
        
        # 给予物品奖励
        for item in self.item_rewards:
            player.add_to_inventory(item)
        
        # 从玩家活动任务中移除，并添加到已完成任务
        if self in player.active_quests:
            player.active_quests.remove(self)
            player.completed_quests.append(self)
        
        return True, f"完成任务：{self.title}，获得{self.experience_reward}点经验！"
    
    def get_objective_status(self):
        """获取任务目标状态，用于UI显示"""
        result = []
        for obj in self.objectives:
            desc = obj["description"]
            if "count" in obj and "current" in obj:
                desc += f" ({obj['current']}/{obj['count']})"
            completed = self.completed_objectives[obj["id"]]
            result.append((desc, completed))
        return result


# 任务目标类型的辅助函数
def kill_monster_objective(monster_type, count=1):
    """创建击杀怪物类型的任务目标"""
    return {
        "type": "kill",
        "target": monster_type,
        "count": count,
        "current": 0,
        "description": f"击杀{count}个{monster_type}"
    }

def collect_item_objective(item_name, count=1):
    """创建收集物品类型的任务目标"""
    return {
        "type": "collect",
        "target": item_name,
        "count": count,
        "current": 0,
        "description": f"收集{count}个{item_name}"
    }

def visit_location_objective(location_name):
    """创建访问地点类型的任务目标"""
    return {
        "type": "visit",
        "target": location_name,
        "count": 1,
        "current": 0,
        "description": f"前往{location_name}"
    }

def talk_to_npc_objective(npc_name):
    """创建与NPC对话类型的任务目标"""
    return {
        "type": "talk",
        "target": npc_name,
        "count": 1,
        "current": 0,
        "description": f"与{npc_name}交谈"
    } 