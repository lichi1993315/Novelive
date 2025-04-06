<<<<<<< HEAD
# Novelive
让小说活过来
=======
# 尘世游 - 武侠 Roguelike 游戏

一个基于文字字符的武侠风格 Roguelike 游戏，使用 Python 和 Pygame 开发。游戏融合了传统 Roguelike 与中国武侠小说元素，创造了一个独特的游戏体验。

## 游戏特色

- **境界系统**: 从九品到洞玄，玩家通过修炼突破境界，获得更强大的能力
- **心法系统**: 选择先天心法，掌握特殊能力，后期可学习后天心法
- **招式系统**: 习得多样的武学招式，在战斗中灵活运用
- **多样场景**: 逍遥阁、荒野、古墓等多个场景可探索
- **随机生成**: 每次游戏都有不同的体验

## 游戏操作

- **WASD**: 移动角色
- **E**: 与NPC互动
- **B**: 尝试突破境界
- **C**: 查看角色状态
- **战斗中**:
  - **1**: 普通攻击
  - **2**: 特殊攻击（消耗内力）
  - **3**: 防御（恢复内力）
  - **4**: 使用招式

## 游戏元素

游戏使用 ASCII 字符表示游戏中的各种元素：

- **@**: 玩家角色
- **#**: 墙壁
- **T**: 树木
- **~**: 水域
- **^**: 山脉
- **+**: 门
- **</>**: 上/下楼梯（传送点）
- **NPC**:
  - **M**: 掌门
  - **I**: 教习
  - **L**: 藏经阁管理员
  - **D**: 医师
  - **K**: 客栈老板
- **怪物**:
  - **b**: 盗匪
  - **w**: 野狼
  - **C**: 盗匪首领

## 游戏系统

### 境界系统

游戏设计了九品到洞玄共十个境界等级：

1. **九品：淬体** - 凡躯极限
2. **八品：蕴气** - 内息初生
3. **七品：通脉** - 气行周天
4. **六品：凝罡** - 内气化罡
5. **五品：意动** - 心意相合
6. **四品：显形** - 意到形随
7. **三品：师法** - 法效天地
8. **二品：法域** - 意展成界
9. **一品：归真** - 返璞归元
10. **洞玄** - 窥道之境

### 心法系统

- **先天心法**: 角色出生自带的基础心法，提供基本属性加成
  - 太极心法
  - 少林心法
- **后天心法**: 游戏中可习得的额外心法，提供特殊能力
  - 九阳神功
  - 北冥神功

## 安装与运行

1. 确保已安装 Python 3.13
2. 安装依赖：
```
pip install pygame==2.6.1
```
3. 运行游戏：
```
python main.py
```

## 项目结构

- `main.py`: 游戏入口
- `game.py`: 游戏主逻辑
- `player.py`: 玩家角色
- `world.py`: 游戏世界
- `entity.py`: 实体（NPC、怪物等）
- `combat.py`: 战斗系统
- `cultivation.py`: 境界系统
- `heart_method.py`: 心法系统
- `technique.py`: 招式系统
- `dialog.py`: 对话系统
- `ui.py`: 用户界面
- `quest.py`: 任务系统

## 游戏目标

探索武侠世界，提升境界，掌握强大心法和招式，最终达到洞玄境界，窥探大道。
>>>>>>> 972ce84 (Initial commit)
