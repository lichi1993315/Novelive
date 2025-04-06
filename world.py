import random
import pygame
from entity import NPC, Monster, Item
from util import get_font

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.npcs = []
        self.monsters = []
        self.items = []
        self.portals = {}  # 传送门
        
        # 当前区域
        self.current_area = "xiaoyao"
        
        # 武侠世界特色地形元素
        self.terrain_chars = {
            "floor": ".",       # 地面
            "wall": "#",        # 墙壁
            "tree": "T",        # 树
            "water": "~",       # 水
            "mountain": "^",    # 山
            "portal": "O",      # 传送门
            "flower": "*",      # 花/花园
            "bamboo": ":",      # 竹林
            "waterfall": "W",   # 瀑布
            "pavilion": "P",    # 亭台
            "teahouse": "C",    # 茶室
            "stream": "~",      # 小溪
            "bridge": "=",      # 石桥
            "statue": "S",      # 雕像
            "stairs": ">",      # 石阶
            "rock": "r",        # 怪石
            "grass": ",",       # 草地
            "path": ".",        # 小路
            "door": "+",        # 门
            "stairs_up": "<",   # 上楼梯
            "stairs_down": ">"  # 下楼梯
        }
        
        # 武侠世界特色地形颜色
        self.terrain_colors = {
            "floor": (60, 60, 60),       # 地面
            "wall": (120, 120, 120),     # 墙壁
            "tree": (0, 150, 0),         # 树
            "water": (0, 100, 255),      # 水
            "mountain": (150, 75, 0),    # 山
            "portal": (255, 255, 0),     # 传送门
            "flower": (255, 100, 255),   # 花/花园
            "bamboo": (100, 200, 0),     # 竹林
            "waterfall": (120, 200, 255),# 瀑布
            "pavilion": (180, 130, 70),  # 亭台
            "teahouse": (160, 120, 60),  # 茶室
            "stream": (100, 150, 255),   # 小溪
            "bridge": (150, 150, 150),   # 石桥
            "statue": (200, 200, 200),   # 雕像
            "stairs": (170, 170, 170),   # 石阶
            "rock": (140, 140, 140),     # 怪石
            "grass": (100, 180, 100),    # 草地
            "path": (190, 170, 130),     # 小路
            "door": (150, 75, 0),        # 门
            "stairs_up": (200, 200, 0),  # 上楼梯
            "stairs_down": (200, 200, 0) # 下楼梯
        }
        
        # 定义哪些地形是可通行的
        self.walkable_terrain = {
            "floor": True,
            "path": True,
            "grass": True,
            "flower": True,
            "bridge": True,
            "portal": True,
            "stairs": True,
            "door": True,
            "stairs_up": True,
            "stairs_down": True
        }
        
        # 现在初始化grid（在terrain_chars定义之后）
        self.grid = [[self.terrain_chars["floor"] for _ in range(width)] for _ in range(height)]
        
        # 区域信息
        self.area_info = {
            "xiaoyao": {"name": "逍遥阁", "type": "peaceful"},
            "forest": {"name": "幽暗森林", "type": "dangerous"},
            "mountain": {"name": "太华山", "type": "dangerous"},
            "village": {"name": "平安村", "type": "peaceful"},
            "cave": {"name": "秘境洞窟", "type": "dungeon"}
        }
        
        # 初始化各区域
        self.initialize_xiaoyao()
        
        # 设置当前区域为逍遥阁
        self.current_area = "xiaoyao"
        
    def is_position_valid(self, x, y):
        """检查坐标是否有效，返回(是否有效, 原因)元组"""
        # Check bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False, "你不能离开当前区域"
        
        # 获取当前位置的地形
        terrain = self.grid[y][x]
        
        # 检查地形是否可通行
        terrain_type = None
        for type_name, char in self.terrain_chars.items():
            if terrain == char:
                terrain_type = type_name
                break
        
        if terrain_type:
            if not self.walkable_terrain.get(terrain_type, False):
                reason = ""
                if terrain_type == "wall":
                    reason = "那里是墙壁，无法通行"
                elif terrain_type == "water":
                    reason = "那里是水域，无法通行"
                elif terrain_type == "waterfall":
                    reason = "那里是瀑布，无法通行"
                elif terrain_type == "mountain":
                    reason = "那里是陡峭的山脉，无法通行"
                elif terrain_type == "tree":
                    reason = "那里有茂密的树木，无法通行"
                elif terrain_type == "bamboo":
                    reason = "竹林太密，难以穿行"
                elif terrain_type == "stream":
                    reason = "那里是溪流，需要从桥上通过"
                elif terrain_type == "rock":
                    reason = "那里有巨石阻挡，无法通行"
                elif terrain_type == "statue":
                    reason = "那里有一尊雕像"
                elif terrain_type == "pavilion":
                    reason = "那里是亭台，先绕行吧"
                elif terrain_type == "teahouse":
                    reason = "那是茶室，需要从门口进入"
                else:
                    reason = f"那里是{terrain}，无法通行"
                return False, reason
        
        # Check if there's an NPC or monster at this position
        for npc in self.npcs:
            if npc.x == x and npc.y == y:
                return False, f"那里站着{npc.char}"
        
        for monster in self.monsters:
            if monster["x"] == x and monster["y"] == y:
                return False, f"那里有{monster['name']}"
        
        return True, "可以通行"
    
    def get_npc_at(self, x, y):
        for npc in self.npcs:
            if npc.x == x and npc.y == y:
                return npc
        return None
    
    def get_monster_at(self, x, y):
        for monster in self.monsters:
            if monster["x"] == x and monster["y"] == y:
                # 将怪物字典转换为Monster对象
                monster_obj = Monster(
                    monster["x"], 
                    monster["y"], 
                    monster["char"],
                    monster["name"]
                )
                # 复制属性
                monster_obj.health = monster["hp"]
                monster_obj.max_health = monster["max_hp"]
                monster_obj.attack = monster["attack"]
                monster_obj.defense = monster["defense"]
                # 添加怪物索引，用于后续更新
                monster_obj.index = self.monsters.index(monster)
                return monster_obj
        return None
    
    def check_portal(self, x, y):
        """检查指定位置是否有传送门"""
        if (x, y) in self.portals:
            return self.portals[(x, y)]
        return None
    
    def update(self):
        # Move monsters randomly - reduce movement probability from 30% to 10%
        for monster in self.monsters:
            if random.random() < 0.1:  # 降低移动概率，从0.3改为0.1
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])
                new_x, new_y = monster["x"] + dx, monster["y"] + dy
                if self.is_position_valid(new_x, new_y):
                    monster["x"], monster["y"] = new_x, new_y
    
    def render(self, screen, font, start_x, start_y, player_x, player_y):
        """渲染游戏世界"""
        grid_size = 20  # 每个网格单元格的像素大小
        
        # 加载ASCII字体用于特殊字符
        ascii_font = get_font(is_ascii=True, size=24)
        
        # 确定可见区域的尺寸
        visible_width = min(30, self.width - start_x)
        visible_height = min(20, self.height - start_y)
        
        # 渲染地图元素
        for y in range(visible_height):
            for x in range(visible_width):
                world_x = start_x + x
                world_y = start_y + y
                
                if 0 <= world_x < self.width and 0 <= world_y < self.height:
                    # 计算屏幕坐标
                    screen_x = x * grid_size + grid_size // 2
                    screen_y = y * grid_size + grid_size // 2
                    
                    # 获取当前位置的地形
                    terrain = self.grid[world_y][world_x]
                    
                    # 绘制地形
                    char_color = self.terrain_colors.get("floor", (100, 100, 100))  # 默认颜色
                    
                    # 根据地形字符设置颜色
                    for terrain_type, char in self.terrain_chars.items():
                        if terrain == char:
                            char_color = self.terrain_colors.get(terrain_type, (100, 100, 100))
                            break
                    
                    # 检查是否为ASCII字符
                    is_ascii = all(ord(c) < 128 for c in terrain)
                    
                    # 根据字符类型选择合适的字体
                    render_font = ascii_font if is_ascii else font
                        
                    # 绘制地形字符
                    text = render_font.render(terrain, True, char_color)
                    screen.blit(text, (screen_x - text.get_width() // 2, screen_y - text.get_height() // 2))
        
        # 绘制NPC
        for npc in self.npcs:
            if start_x <= npc.x < start_x + visible_width and start_y <= npc.y < start_y + visible_height:
                screen_x = (npc.x - start_x) * grid_size + grid_size // 2
                screen_y = (npc.y - start_y) * grid_size + grid_size // 2
                
                # 根据字符是否为ASCII选择字体
                is_ascii = all(ord(c) < 128 for c in npc.char)
                render_font = ascii_font if is_ascii else font
                
                text = render_font.render(npc.char, True, (0, 255, 255))  # NPC使用青色
                screen.blit(text, (screen_x - text.get_width() // 2, screen_y - text.get_height() // 2))
        
        # 绘制怪物
        for monster in self.monsters:
            if start_x <= monster["x"] < start_x + visible_width and start_y <= monster["y"] < start_y + visible_height:
                screen_x = (monster["x"] - start_x) * grid_size + grid_size // 2
                screen_y = (monster["y"] - start_y) * grid_size + grid_size // 2
                
                # 根据字符是否为ASCII选择字体
                is_ascii = all(ord(c) < 128 for c in monster["char"])
                render_font = ascii_font if is_ascii else font
                
                text = render_font.render(monster["char"], True, (255, 0, 0))  # 怪物使用红色
                screen.blit(text, (screen_x - text.get_width() // 2, screen_y - text.get_height() // 2))
        
        # 绘制玩家
        if start_x <= player_x < start_x + visible_width and start_y <= player_y < start_y + visible_height:
            screen_x = (player_x - start_x) * grid_size + grid_size // 2
            screen_y = (player_y - start_y) * grid_size + grid_size // 2
            
            # 玩家字符"@"是ASCII，使用ASCII字体
            text = ascii_font.render("@", True, (255, 255, 255))  # 玩家使用白色
            screen.blit(text, (screen_x - text.get_width() // 2, screen_y - text.get_height() // 2))
        
        # 绘制区域信息
        area_info = self.area_info.get(self.current_area)
        if area_info:
            area_name = area_info.get('name', self.current_area)
            text = font.render(f"区域: {area_name}", True, (200, 200, 0))
            screen.blit(text, (10, 560))
    
    def get_current_map(self):
        """获取当前区域的地图"""
        # 直接返回grid
        return self.grid

    def initialize_xiaoyao(self):
        """初始化逍遥阁区域"""
        # 清空当前地图
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = self.terrain_chars["floor"]
        
        # 清空NPC和怪物
        self.npcs = []
        self.monsters = []
        
        # 绘制逍遥阁的外墙
        for x in range(self.width):
            self.grid[0][x] = self.terrain_chars["wall"]
            self.grid[self.height-1][x] = self.terrain_chars["wall"]
        for y in range(self.height):
            self.grid[y][0] = self.terrain_chars["wall"]
            self.grid[y][self.width-1] = self.terrain_chars["wall"]
            
        # 创建内部分隔墙
        # 中央大厅区域
        for x in range(10, 30):
            for y in range(5, 20):
                if (x == 10 or x == 29) and 5 <= y <= 19:
                    self.grid[y][x] = self.terrain_chars["wall"]
                if (y == 5 or y == 19) and 10 <= x <= 29:
                    self.grid[y][x] = self.terrain_chars["wall"]
        
        # 创建门
        self.grid[5][20] = self.terrain_chars["door"]  # 中央大厅北门
        self.grid[19][20] = self.terrain_chars["door"]  # 中央大厅南门
        self.grid[12][10] = self.terrain_chars["door"]  # 中央大厅西门
        self.grid[12][29] = self.terrain_chars["door"]  # 中央大厅东门
        
        # 创建练功房
        for x in range(32, 38):
            for y in range(7, 15):
                if (x == 32 or x == 37) and 7 <= y <= 14:
                    self.grid[y][x] = self.terrain_chars["wall"]
                if (y == 7 or y == 14) and 32 <= x <= 37:
                    self.grid[y][x] = self.terrain_chars["wall"]
        self.grid[14][34] = self.terrain_chars["door"]  # 练功房门
        
        # 创建藏经阁
        for x in range(32, 38):
            for y in range(17, 23):
                if (x == 32 or x == 37) and 17 <= y <= 22:
                    self.grid[y][x] = self.terrain_chars["wall"]
                if (y == 17 or y == 22) and 32 <= x <= 37:
                    self.grid[y][x] = self.terrain_chars["wall"]
        self.grid[17][34] = self.terrain_chars["door"]  # 藏经阁门
        
        # 创建客房
        for x in range(3, 8):
            for y in range(7, 12):
                if (x == 3 or x == 7) and 7 <= y <= 11:
                    self.grid[y][x] = self.terrain_chars["wall"]
                if (y == 7 or y == 11) and 3 <= x <= 7:
                    self.grid[y][x] = self.terrain_chars["wall"]
        self.grid[11][5] = self.terrain_chars["door"]  # 客房门
        
        # 创建药房
        for x in range(3, 8):
            for y in range(15, 20):
                if (x == 3 or x == 7) and 15 <= y <= 19:
                    self.grid[y][x] = self.terrain_chars["wall"]
                if (y == 15 or y == 19) and 3 <= x <= 7:
                    self.grid[y][x] = self.terrain_chars["wall"]
        self.grid[15][5] = self.terrain_chars["door"]  # 药房门
        
        # 创建传送门
        self.grid[2][20] = self.terrain_chars["portal"]  # 通往荒野的传送门
        self.portals[(20, 2)] = "wilderness"
        
        self.grid[20][2] = self.terrain_chars["portal"]  # 通往古墓的传送门
        self.portals[(2, 20)] = "mountain"
        
        self.grid[20][38] = self.terrain_chars["portal"]  # 通往少林寺的传送门
        self.portals[(38, 20)] = "village"
        
        # 添加花园 - 中央庭院
        for x in range(15, 25):
            for y in range(8, 14):
                self.grid[y][x] = self.terrain_chars["floor"]  # 先清空
        
        for x in range(16, 24):
            for y in range(9, 13):
                if random.random() < 0.6:
                    self.grid[y][x] = self.terrain_chars["flower"]
        
        # 添加一个中央亭台
        self.grid[11][20] = self.terrain_chars["pavilion"]
        
        # 添加竹林 - 右上角
        for x in range(30, 38):
            for y in range(2, 6):
                if random.random() < 0.7:
                    self.grid[y][x] = self.terrain_chars["bamboo"]
        
        # 添加小溪和石桥 - 下方区域
        for x in range(5, 35):
            y = 22
            self.grid[y][x] = self.terrain_chars["stream"]
        
        # 石桥
        self.grid[22][15] = self.terrain_chars["bridge"]
        self.grid[22][25] = self.terrain_chars["bridge"]
        
        # 添加茶室
        self.grid[3][25] = self.terrain_chars["teahouse"]
        
        # 添加小路
        for y in range(19, 22):
            self.grid[y][15] = self.terrain_chars["path"]
            self.grid[y][25] = self.terrain_chars["path"]
        
        # 添加山石
        for _ in range(8):
            x = random.randint(1, 9)
            y = random.randint(1, 6)
            self.grid[y][x] = self.terrain_chars["rock"]
        
        # 添加草地
        for x in range(1, self.width-1):
            for y in range(1, self.height-1):
                if self.grid[y][x] == self.terrain_chars["floor"] and random.random() < 0.1:
                    self.grid[y][x] = self.terrain_chars["grass"]
        
        # 添加雕像 - 大厅中央
        self.grid[12][20] = self.terrain_chars["statue"]
        
        # 添加NPC
        self.add_xiaoyao_npcs()
    
    def initialize_forest(self):
        """初始化幽暗森林区域"""
        # 清空当前地图
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = self.terrain_chars["floor"]
        
        # 清空NPC和怪物
        self.npcs = []
        self.monsters = []
        
        # 外围围墙
        for x in range(self.width):
            self.grid[0][x] = self.terrain_chars["wall"]
            self.grid[self.height-1][x] = self.terrain_chars["wall"]
        for y in range(self.height):
            self.grid[y][0] = self.terrain_chars["wall"]
            self.grid[y][self.width-1] = self.terrain_chars["wall"]
        
        # 添加一些树木
        for _ in range(60):
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            self.grid[y][x] = self.terrain_chars["tree"]
        
        # 添加一些水域
        for _ in range(20):
            x = random.randint(5, self.width-5)
            y = random.randint(5, self.height-5)
            size = random.randint(1, 3)
            for dx in range(-size, size+1):
                for dy in range(-size, size+1):
                    if 0 < x+dx < self.width-1 and 0 < y+dy < self.height-1:
                        if random.random() < 0.7:
                            self.grid[y+dy][x+dx] = self.terrain_chars["water"]
        
        # 添加一些山脉
        for _ in range(10):
            x = random.randint(5, self.width-5)
            y = random.randint(5, self.height-5)
            size = random.randint(1, 2)
            for dx in range(-size, size+1):
                for dy in range(-size, size+1):
                    if 0 < x+dx < self.width-1 and 0 < y+dy < self.height-1:
                        if random.random() < 0.8:
                            self.grid[y+dy][x+dx] = self.terrain_chars["mountain"]
        
        # 添加小溪
        stream_y = 12
        for x in range(5, 35):
            self.grid[stream_y][x] = self.terrain_chars["stream"]
        
        # 石桥
        self.grid[stream_y][15] = self.terrain_chars["bridge"]
        self.grid[stream_y][25] = self.terrain_chars["bridge"]
        
        # 添加一个瀑布
        waterfall_x = 30
        for y in range(5, stream_y):
            self.grid[y][waterfall_x] = self.terrain_chars["waterfall"]
        
        # 添加一个隐秘小亭
        small_pavilion_x = 33
        small_pavilion_y = 7
        self.grid[small_pavilion_y][small_pavilion_x] = self.terrain_chars["pavilion"]
        
        # 清理亭子周围的树木和山脉
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = small_pavilion_x + dx, small_pavilion_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx] in [self.terrain_chars["tree"], self.terrain_chars["mountain"]]:
                        self.grid[ny][nx] = self.terrain_chars["floor"]
        
        # 添加草地
        for x in range(1, self.width-1):
            for y in range(1, self.height-1):
                if self.grid[y][x] == self.terrain_chars["floor"] and random.random() < 0.2:
                    self.grid[y][x] = self.terrain_chars["grass"]
        
        # 添加小路
        for x in range(1, stream_y):
            self.grid[stream_y - 3][x] = self.terrain_chars["path"]
        
        # 添加返回逍遥阁的传送门
        self.grid[stream_y - 3][self.width-2] = self.terrain_chars["portal"]
        self.portals[(self.width-2, stream_y - 3)] = "xiaoyao"
        
        # 添加到村庄的传送门
        self.grid[self.height-2][20] = self.terrain_chars["portal"]
        self.portals[(20, self.height-2)] = "village"
        
        # 添加怪物
        self.add_forest_monsters()
    
    def initialize_mountain(self):
        """初始化太华山区域"""
        # 清空当前地图
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = self.terrain_chars["floor"]
        
        # 清空NPC和怪物
        self.npcs = []
        self.monsters = []
        
        # 创建基本地形 - 减少山脉和石头的比例
        for y in range(self.height):
            for x in range(self.width):
                if y == 0 or y == self.height-1 or x == 0 or x == self.width-1:
                    self.grid[y][x] = self.terrain_chars["wall"]  # 边界
                else:
                    rand = random.random()
                    if rand < 0.2:  # 减少山的比例从35%到20%
                        self.grid[y][x] = self.terrain_chars["mountain"]  # 山
                    elif rand < 0.25:  # 减少石头的比例从15%到5%
                        self.grid[y][x] = self.terrain_chars["rock"]  # 怪石
                    elif rand < 0.4:  # 增加草地比例
                        self.grid[y][x] = self.terrain_chars["grass"]  # 草地
                    # 否则保持为floor
        
        # 创建主通道网络 - 确保山区连通性
        # 水平主通道
        for y in range(5, self.height-5, 6):
            for x in range(1, self.width-1):
                self.grid[y][x] = self.terrain_chars["path"]
        
        # 垂直主通道
        for x in range(5, self.width-5, 8):
            for y in range(1, self.height-1):
                self.grid[y][x] = self.terrain_chars["path"]
        
        # 添加一条主要小路 - 连接山顶和山脚
        for y in range(1, self.height-1):
            self.grid[y][15] = self.terrain_chars["path"]
        
        # 添加石阶
        for y in range(5, 10, 2):
            self.grid[y][15] = self.terrain_chars["stairs"]
        
        # 添加一些竹林 - 减少数量
        for y in range(3, 8):
            for x in range(25, 30):
                if random.random() < 0.5:  # 降低生成概率
                    self.grid[y][x] = self.terrain_chars["bamboo"]
        
        # 添加山顶茶室
        self.grid[2][15] = self.terrain_chars["teahouse"]
        
        # 清理茶室周围
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if 0 <= 2+dy < self.height and 0 <= 15+dx < self.width:
                    self.grid[2+dy][15+dx] = self.terrain_chars["floor"]
                    # 确保茶室外围有一圈小路
                    if abs(dx) == 2 or abs(dy) == 2:
                        self.grid[2+dy][15+dx] = self.terrain_chars["path"]
        
        # 添加瀑布和小溪
        waterfall_x = 25
        for y in range(8, 15):
            self.grid[y][waterfall_x] = self.terrain_chars["waterfall"]
        
        # 确保瀑布周围可通行
        for dx in range(-1, 2):
            for y in range(8, 15):
                if dx != 0 and 0 <= waterfall_x+dx < self.width:
                    self.grid[y][waterfall_x+dx] = self.terrain_chars["floor"]
        
        # 添加小溪
        for x in range(25, 35):
            self.grid[15][x] = self.terrain_chars["stream"]
        
        # 确保小溪两岸可通行
        for x in range(25, 35):
            if 0 <= 15-1 < self.height:
                self.grid[15-1][x] = self.terrain_chars["path"]
            if 0 <= 15+1 < self.height:
                self.grid[15+1][x] = self.terrain_chars["path"]
        
        # 添加桥梁穿过小溪
        self.grid[15][28] = self.terrain_chars["bridge"]
        self.grid[15][32] = self.terrain_chars["bridge"]
        
        # 确保出口附近区域可通行
        # 下方出口 - 回到逍遥阁的传送门
        self.grid[self.height-1][15] = self.terrain_chars["portal"]
        for dy in range(-3, 0):
            for dx in range(-2, 3):
                if 0 <= self.height-1+dy < self.height and 0 <= 15+dx < self.width:
                    self.grid[self.height-1+dy][15+dx] = self.terrain_chars["path"]
        
        # 上方出口 - 通往秘境洞窟的传送门
        self.grid[1][15] = self.terrain_chars["portal"]
        for dy in range(0, 3):
            for dx in range(-2, 3):
                if 0 <= 1+dy < self.height and 0 <= 15+dx < self.width:
                    self.grid[1+dy][15+dx] = self.terrain_chars["path"]
        
        # 添加传送门
        self.portals[(15, self.height-1)] = "xiaoyao"
        self.portals[(15, 1)] = "cave"
        
        # 再次确保主要路径完全连通
        for y in range(1, self.height-1):
            # 主路上的墙或岩石清除
            if self.grid[y][15] in [self.terrain_chars["wall"], self.terrain_chars["mountain"], self.terrain_chars["rock"]]:
                self.grid[y][15] = self.terrain_chars["path"]
        
        # 添加一些怪物
        self.add_mountain_monsters()
    
    def initialize_village(self):
        """初始化平安村区域"""
        # 清空当前地图
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = self.terrain_chars["floor"]
        
        # 清空NPC和怪物
        self.npcs = []
        self.monsters = []
        
        # 创建基本地形
        for y in range(self.height):
            for x in range(self.width):
                if y == 0 or y == self.height-1 or x == 0 or x == self.width-1:
                    self.grid[y][x] = self.terrain_chars["wall"]  # 边界
                # 默认为空地
        
        # 添加一些房屋
        for house_idx in range(5):
            house_x = 5 + house_idx * 7
            house_y = 5
            for i in range(house_y, house_y+5):
                for j in range(house_x, house_x+5):
                    if i == house_y or i == house_y+4 or j == house_x or j == house_x+4:
                        self.grid[i][j] = self.terrain_chars["wall"]
        
        # 添加另一排房屋
        for house_idx in range(5):
            house_x = 5 + house_idx * 7
            house_y = 15
            for i in range(house_y, house_y+5):
                for j in range(house_x, house_x+5):
                    if i == house_y or i == house_y+4 or j == house_x or j == house_x+4:
                        self.grid[i][j] = self.terrain_chars["wall"]
        
        # 添加村庄中央的广场
        for y in range(10, 15):
            for x in range(15, 25):
                self.grid[y][x] = self.terrain_chars["path"]
        
        # 广场中央的雕像
        self.grid[12][20] = self.terrain_chars["statue"]
        
        # 添加茶馆
        self.grid[7][30] = self.terrain_chars["teahouse"]
        
        # 添加花园
        for y in range(8, 12):
            for x in range(32, 36):
                if random.random() < 0.7:
                    self.grid[y][x] = self.terrain_chars["flower"]
        
        # 添加小溪和桥
        for x in range(1, self.width-1):
            self.grid[20][x] = self.terrain_chars["stream"]
        
        # 桥
        self.grid[20][10] = self.terrain_chars["bridge"]
        self.grid[20][20] = self.terrain_chars["bridge"]
        self.grid[20][30] = self.terrain_chars["bridge"]
        
        # 添加一些草地
        for _ in range(50):
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            if self.grid[y][x] == self.terrain_chars["floor"]:
                self.grid[y][x] = self.terrain_chars["grass"]
        
        # 出口到其他区域
        self.grid[1][20] = self.terrain_chars["portal"]  # 通往幽暗森林的传送门
        
        # 添加传送门
        self.portals[(20, 1)] = "forest"
        
        # 添加一些村民NPC
        self.add_village_npcs()
    
    def initialize_cave(self):
        """初始化秘境洞窟区域"""
        # 清空当前地图
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = self.terrain_chars["floor"]
        
        # 清空NPC和怪物
        self.npcs = []
        self.monsters = []
        
        # 创建基本地形 - 减少墙壁生成概率，从30%降至20%
        for y in range(self.height):
            for x in range(self.width):
                if y == 0 or y == self.height-1 or x == 0 or x == self.width-1:
                    self.grid[y][x] = self.terrain_chars["wall"]  # 边界
                else:
                    if random.random() < 0.2:  # 降低墙壁概率
                        self.grid[y][x] = self.terrain_chars["wall"]  # 洞窟内部的墙壁
        
        # 创建主通道网络 - 确保地牢连通性
        # 水平主通道
        for y in range(3, self.height-3, 5):
            for x in range(1, self.width-1):
                self.grid[y][x] = self.terrain_chars["floor"]
        
        # 垂直主通道
        for x in range(3, self.width-3, 5):
            for y in range(1, self.height-1):
                self.grid[y][x] = self.terrain_chars["floor"]
        
        # 添加一些分支通道以增加探索性
        for _ in range(10):
            # 选择随机起点(从主通道上的点)
            start_y = random.choice(range(3, self.height-3, 5))
            start_x = random.randint(1, self.width-2)
            
            # 随机方向和长度的通道
            direction = random.choice(["up", "down", "left", "right"])
            length = random.randint(3, 7)
            
            if direction == "up":
                for i in range(1, length+1):
                    if 0 <= start_y-i < self.height:
                        self.grid[start_y-i][start_x] = self.terrain_chars["floor"]
            elif direction == "down":
                for i in range(1, length+1):
                    if 0 <= start_y+i < self.height:
                        self.grid[start_y+i][start_x] = self.terrain_chars["floor"]
            elif direction == "left":
                for i in range(1, length+1):
                    if 0 <= start_x-i < self.width:
                        self.grid[start_y][start_x-i] = self.terrain_chars["floor"]
            elif direction == "right":
                for i in range(1, length+1):
                    if 0 <= start_x+i < self.width:
                        self.grid[start_y][start_x+i] = self.terrain_chars["floor"]
        
        # 为BOSS创建特殊区域
        boss_room_x = self.width // 2 - 3
        boss_room_y = 5
        boss_room_width = 6
        boss_room_height = 6
        
        # 创建BOSS房间
        for y in range(boss_room_y, boss_room_y + boss_room_height):
            for x in range(boss_room_x, boss_room_x + boss_room_width):
                if 0 <= y < self.height and 0 <= x < self.width:
                    # 房间边界为墙
                    if (y == boss_room_y or y == boss_room_y + boss_room_height - 1 or 
                        x == boss_room_x or x == boss_room_x + boss_room_width - 1):
                        self.grid[y][x] = self.terrain_chars["wall"]
                    else:
                        self.grid[y][x] = self.terrain_chars["floor"]
        
        # 为BOSS房间创建入口
        self.grid[boss_room_y + boss_room_height - 1][boss_room_x + boss_room_width // 2] = self.terrain_chars["floor"]
        
        # 添加一条通往BOSS房间的明确路径
        path_x = boss_room_x + boss_room_width // 2
        for y in range(boss_room_y + boss_room_height, self.height - 5):
            self.grid[y][path_x] = self.terrain_chars["floor"]
            # 在路径两侧添加一些随机地板，增加宽度
            if random.random() < 0.5:
                self.grid[y][path_x-1] = self.terrain_chars["floor"]
            if random.random() < 0.5:
                self.grid[y][path_x+1] = self.terrain_chars["floor"]
        
        # 添加一些怪石
        for _ in range(15):
            x = random.randint(5, self.width-5)
            y = random.randint(5, self.height-5)
            if self.grid[y][x] == self.terrain_chars["floor"]:
                self.grid[y][x] = self.terrain_chars["rock"]
        
        # 添加一些水池
        for _ in range(3):
            x = random.randint(5, self.width-5)
            y = random.randint(5, self.height-5)
            if self.grid[y][x] == self.terrain_chars["floor"]:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.grid[ny][nx] == self.terrain_chars["floor"] and random.random() < 0.8:
                                self.grid[ny][nx] = self.terrain_chars["water"]
        
        # 添加一些珍贵的草药（用花来表示）
        for _ in range(8):
            x = random.randint(5, self.width-5)
            y = random.randint(5, self.height-5)
            if self.grid[y][x] == self.terrain_chars["floor"]:
                self.grid[y][x] = self.terrain_chars["flower"]
        
        # 添加上下级的楼梯
        self.grid[10][10] = self.terrain_chars["stairs_down"]
        self.grid[15][15] = self.terrain_chars["stairs_up"]
        
        # 确保楼梯周围有通道
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if 0 <= 10+dy < self.height and 0 <= 10+dx < self.width:
                    self.grid[10+dy][10+dx] = self.terrain_chars["floor"]
                if 0 <= 15+dy < self.height and 0 <= 15+dx < self.width:
                    self.grid[15+dy][15+dx] = self.terrain_chars["floor"]
        
        # 添加一些特殊的雕像
        for _ in range(3):
            x = random.randint(5, self.width-5)
            y = random.randint(5, self.height-5)
            if self.grid[y][x] == self.terrain_chars["floor"]:
                self.grid[y][x] = self.terrain_chars["statue"]
        
        # 出口到太华山的传送门
        portal_x = 5
        portal_y = self.height-2
        self.grid[portal_y][portal_x] = self.terrain_chars["portal"]
        
        # 确保传送门周围有通道
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if 0 <= portal_y+dy < self.height and 0 <= portal_x+dx < self.width:
                    if self.grid[portal_y+dy][portal_x+dx] == self.terrain_chars["wall"]:
                        self.grid[portal_y+dy][portal_x+dx] = self.terrain_chars["floor"]
        
        # 添加传送门
        self.portals[(portal_x, portal_y)] = "mountain"
        
        # 添加一些怪物，确保它们在可通行的区域
        self.add_cave_monsters()
    
    def add_forest_monsters(self):
        """添加森林里的怪物"""
        monsters_types = [
            {"name": "灰狼", "char": "w", "hp": 30, "attack": 10, "defense": 3, "experience": 20},
            {"name": "山贼", "char": "b", "hp": 50, "attack": 12, "defense": 5, "experience": 25},
            {"name": "野猪", "char": "p", "hp": 40, "attack": 8, "defense": 7, "experience": 30}
        ]
        
        # 添加5只随机怪物
        for _ in range(5):
            # 尝试最多20次找到可通行位置
            for attempt in range(20):
                x = random.randint(5, self.width-5)
                y = random.randint(5, self.height-5)
                
                # 检查位置是否可通行（森林接受地面或草地）
                valid_terrains = [self.terrain_chars["floor"], self.terrain_chars["grass"]]
                if self.grid[y][x] in valid_terrains and self.is_position_valid(x, y)[0]:
                    # 随机选择一种怪物
                    monster_type = random.choice(monsters_types)
                    monster = {
                        "name": monster_type["name"],
                        "char": monster_type["char"],
                        "x": x,
                        "y": y,
                        "hp": monster_type["hp"],
                        "max_hp": monster_type["hp"],
                        "attack": monster_type["attack"],
                        "defense": monster_type["defense"],
                        "experience": monster_type["experience"]
                    }
                    self.monsters.append(monster)
                    break  # 成功创建，退出尝试循环
    
    def add_mountain_monsters(self):
        """添加太华山区域的怪物"""
        # 添加8只猛虎
        for _ in range(8):
            # 尝试最多20次找到可通行位置
            for attempt in range(20):
                x = random.randint(5, self.width-5)
                y = random.randint(5, self.height-5)
                
                # 检查位置是否可通行（山区接受草地和小路）
                valid_terrains = [self.terrain_chars["floor"], self.terrain_chars["grass"], self.terrain_chars["path"]]
                if self.grid[y][x] in valid_terrains and self.is_position_valid(x, y)[0]:
                    monster = {
                        "name": "猛虎",
                        "char": "t",
                        "x": x,
                        "y": y,
                        "hp": 70,
                        "max_hp": 70,
                        "attack": 15,
                        "defense": 8,
                        "experience": 40  # 添加经验值奖励
                    }
                    self.monsters.append(monster)
                    break  # 成功创建，退出尝试循环
        
        # 添加3只武林高手
        for _ in range(3):
            # 尝试最多20次找到可通行位置
            for attempt in range(20):
                x = random.randint(5, self.width-5)
                y = random.randint(5, self.height-5)
                
                # 检查位置是否可通行
                valid_terrains = [self.terrain_chars["floor"], self.terrain_chars["grass"], self.terrain_chars["path"]]
                if self.grid[y][x] in valid_terrains and self.is_position_valid(x, y)[0]:
                    monster = {
                        "name": "武林高手",
                        "char": "m",
                        "x": x,
                        "y": y,
                        "hp": 100,
                        "max_hp": 100,
                        "attack": 20,
                        "defense": 10,
                        "experience": 60  # 添加经验值奖励
                    }
                    self.monsters.append(monster)
                    break  # 成功创建，退出尝试循环
    
    def add_cave_monsters(self):
        """添加秘境洞窟的怪物"""
        # 在洞窟随机区域添加10个小妖
        for _ in range(10):
            # 尝试最多20次找到可通行位置
            for attempt in range(20):
                x = random.randint(5, self.width-5)
                y = random.randint(5, self.height-5)
                
                # 检查位置是否可通行且是地面
                if (self.grid[y][x] == self.terrain_chars["floor"] and 
                    self.is_position_valid(x, y)[0]):
                    monster = {
                        "name": "洞窟妖兽",
                        "char": "d",
                        "x": x,
                        "y": y,
                        "hp": 80,
                        "max_hp": 80,
                        "attack": 18,
                        "defense": 12,
                        "experience": 50  # 添加经验值奖励
                    }
                    self.monsters.append(monster)
                    break  # 成功创建，退出尝试循环
        
        # 在洞窟深处添加BOSS
        # 确定BOSS房间位置
        boss_room_center_x = self.width // 4
        boss_room_center_y = self.height // 4
        
        # 检查BOSS位置是否有效
        if (self.grid[boss_room_center_y][boss_room_center_x] == self.terrain_chars["floor"] and 
            self.is_position_valid(boss_room_center_x, boss_room_center_y)[0]):
            # 添加BOSS
            boss = {
                "name": "洞窟之主",
                "char": "D",
                "x": boss_room_center_x,
                "y": boss_room_center_y,
                "hp": 200,
                "max_hp": 200,
                "attack": 25,
                "defense": 15,
                "experience": 100  # 添加经验值奖励
            }
            self.monsters.append(boss)
    
    def add_village_npcs(self):
        """添加村庄NPC"""
        # 村长 - 关联任务ID 1: 村子的危机
        village_chief = NPC(24, 5, "长", "村长", [
            "欢迎来到平安村，年轻人。",
            "我们这里最近有些麻烦，灰狼出没，请帮帮我们。",
            "击退灰狼，我会给你丰厚的报酬。"
        ])
        self.npcs.append(village_chief)
        
        # 铁匠 - 关联任务ID 2: 材料收集
        blacksmith = NPC(15, 12, "铁", "铁匠", [
            "我是村里的铁匠，能打造各种武器。",
            "我需要一些特殊材料来打造更好的武器。",
            "如果你能从山上的猛虎那里获取虎骨，我会给你好处。"
        ])
        self.npcs.append(blacksmith)
        
        # 药商 - 关联任务ID 3: 草药采集
        herbalist = NPC(11, 9, "药", "药商", [
            "我这里有各种各样的药材。",
            "村里有很多病人需要药物，但我的草药库存不足。",
            "如果你能帮我采集草药，我会酬谢你的。"
        ])
        self.npcs.append(herbalist)
    
    def add_xiaoyao_npcs(self):
        """添加逍遥派NPC"""
        # 掌门人 - 关联任务ID 4: 武学考验
        master = NPC(20, 6, "掌", "掌门人", [
            "我是逍遥派掌门人，欢迎来到逍遥阁。",
            "要想成为一名真正的武林高手，必须勤修内功。",
            "我有一个考验，你需要证明自己的实力才能获得更高深的武学。"
        ])
        self.npcs.append(master)
        
        # 教习 - 关联任务ID 5: 修炼之路
        instructor = NPC(16, 10, "师", "教习", [
            "我是逍遥派教习，负责传授基础武学。",
            "想要进步就必须不断突破自己的境界。",
            "如果你能突破到蕴气境界，我会教你更高深的武学。"
        ])
        self.npcs.append(instructor)
        
        # 藏经阁管理员 - 关联任务ID 6: 古籍寻找
        librarian = NPC(24, 10, "藏", "藏经阁管理员", [
            "我是藏经阁管理员，负责保管逍遥派的武学秘籍。",
            "最近有几本古籍遗失了，应该是被散落在各处。",
            "如果你能找回这些残页，我可以教你一些失传已久的武学。"
        ])
        self.npcs.append(librarian)
        
        # 医师 - 关联任务ID 7: 医者仁心
        doctor = NPC(10, 15, "医", "医师", [
            "我是逍遥派医师，精通各种疗伤之术。",
            "近来有许多病重之人需要特效药，但缺少关键材料。",
            "如果你能从洞窟中的妖兽身上取得内丹，我可以制作特效药。"
        ])
        self.npcs.append(doctor)
        
        # 客栈老板 - 关联任务ID 8: 洞窟之谜
        innkeeper = NPC(20, 15, "店", "客栈老板", [
            "欢迎光临逍遥客栈，旅途劳顿了吧。",
            "最近有传闻说山脚下的洞窟中出现了一个强大的妖魔。",
            "如果你能解决这个威胁，我会让你知道一个秘密。"
        ])
        self.npcs.append(innkeeper)
    
    def change_area(self, area_name):
        """切换到不同的区域"""
        self.current_area = area_name
        
        if area_name == "xiaoyao" or area_name == "xiaoyao_pavilion":
            self.initialize_xiaoyao()
        elif area_name == "forest" or area_name == "wilderness":
            self.initialize_forest()
        elif area_name == "mountain":
            self.initialize_mountain()
        elif area_name == "village":
            self.initialize_village()
        elif area_name == "cave":
            self.initialize_cave()
        # 其他区域的生成方法可以在未来添加 

    def update_monster(self, monster):
        """更新怪物状态，在战斗后调用"""
        if hasattr(monster, 'index') and 0 <= monster.index < len(self.monsters):
            if monster.health <= 0:
                # 怪物被击败，从列表中移除
                self.monsters.pop(monster.index)
            else:
                # 更新怪物状态
                self.monsters[monster.index]["hp"] = monster.health 

class NPC:
    def __init__(self, x, y, char, name, dialogs=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.dialogs = dialogs or []
        self.current_dialog = 0
        self.temporary_dialogs = []  # 临时对话，用于任务等情况
    
    def reset_dialog(self):
        """重置对话状态"""
        self.current_dialog = 0
    
    def add_dialog(self, text):
        """添加对话文本到常规对话列表"""
        self.dialogs.append(text)
    
    def add_temp_dialog(self, text):
        """添加临时对话文本，用于任务等特殊情况"""
        self.temporary_dialogs.append(text)
    
    def get_next_dialog(self):
        """获取下一条对话，优先返回临时对话"""
        # 优先处理临时对话
        if self.temporary_dialogs:
            dialog = self.temporary_dialogs.pop(0)
            return dialog
            
        # 然后处理常规对话
        if self.current_dialog < len(self.dialogs):
            dialog = self.dialogs[self.current_dialog]
            self.current_dialog += 1
            return dialog
        
        return None 