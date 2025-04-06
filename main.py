import pygame
import time
from game import Game

def main():
    # 初始化pygame
    pygame.init()
    
    # 创建游戏实例
    game = Game()
    
    # 控制帧率
    clock = pygame.time.Clock()
    FPS = 30  # 降低帧率，使游戏速度更慢
    
    # 游戏主循环
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 处理输入
            game.handle_input(event)
        
        # 更新游戏状态
        game.update()
        
        # 渲染游戏
        game.render()
        
        # 刷新屏幕
        pygame.display.flip()
        
        # 控制帧率
        clock.tick(FPS)
    
    # 退出pygame
    pygame.quit()

if __name__ == "__main__":
    main() 