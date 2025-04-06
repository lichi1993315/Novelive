import pygame
from collections import deque

class LogSystem:
    def __init__(self, max_logs=8):
        """初始化日志系统
        
        Args:
            max_logs: 最大显示的日志条数，默认为8条
        """
        self.logs = deque(maxlen=max_logs)
        self.colors = {
            "info": (200, 200, 200),    # 普通信息
            "combat": (255, 100, 100),  # 战斗相关
            "item": (100, 255, 100),    # 物品相关
            "warning": (255, 255, 0),   # 警告信息
            "system": (100, 100, 255),  # 系统信息
            "success": (0, 255, 0)      # 成功信息
        }
    
    def add(self, message, log_type="info"):
        """添加一条日志
        
        Args:
            message: 日志内容
            log_type: 日志类型，决定显示颜色
        """
        color = self.colors.get(log_type, self.colors["info"])
        self.logs.append({"message": message, "type": log_type, "color": color})
    
    def clear(self):
        """清空所有日志"""
        self.logs.clear()
    
    def render(self, screen, font, x, y, width, line_height=25):
        """渲染日志到屏幕
        
        Args:
            screen: pygame屏幕对象
            font: 渲染用字体
            x, y: 日志区域左上角位置
            width: 日志区域宽度
            line_height: 每行日志的高度
        """
        # 绘制日志背景
        log_height = len(self.logs) * line_height
        log_bg = pygame.Rect(x, y, width, log_height)
        pygame.draw.rect(screen, (0, 0, 0), log_bg)
        pygame.draw.rect(screen, (50, 50, 50), log_bg, 1)
        
        # 渲染每条日志
        for i, log in enumerate(self.logs):
            log_text = font.render(log["message"], True, log["color"])
            screen.blit(log_text, (x + 10, y + i * line_height))
    
    def get_recent_logs(self):
        """获取最近的日志列表，用于UI渲染
        
        Returns:
            list: 日志列表
        """
        return list(self.logs) 