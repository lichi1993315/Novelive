import pygame
import sys
from util import get_font

# 初始化 pygame
pygame.init()

# 创建窗口
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("中文字符测试")

# 加载中文字体
chinese_font = get_font(is_ascii=False, size=24)
ascii_font = get_font(is_ascii=True, size=24)

# 待测试的常用中文字符
test_chars = [
    "竹", "茶", "亭", "桥", "像", "阶", "石", "门", "墙", "水", 
    "山", "花", "草", "树", "路", "洞", "井", "塔", "殿", "城",
    "狼", "虎", "猪", "妖", "魔", "贼", "侠", "师", "医", "店",
    "掌", "长", "铁", "药", "藏", "村", "界", "功", "剑", "刀"
]

def render_chars():
    screen.fill((0, 0, 0))  # 黑色背景
    
    # 显示标题
    title = chinese_font.render("中文字符渲染测试", True, (255, 255, 255))
    screen.blit(title, (width // 2 - title.get_width() // 2, 30))
    
    # 显示说明
    hint = chinese_font.render("按数字键1-9选择字体大小，按ESC退出", True, (200, 200, 200))
    screen.blit(hint, (width // 2 - hint.get_width() // 2, 70))
    
    # 显示当前字体大小
    size_text = chinese_font.render(f"当前字体大小: {chinese_font.get_height()}", True, (200, 200, 0))
    screen.blit(size_text, (width // 2 - size_text.get_width() // 2, 100))
    
    # 渲染每个字符
    y_pos = 150
    x_pos = 50
    chars_per_row = 10
    
    for i, char in enumerate(test_chars):
        # 检查是否需要换行
        if i % chars_per_row == 0 and i > 0:
            y_pos += 60
            x_pos = 50
        
        # 渲染字符
        char_surface = chinese_font.render(char, True, (255, 255, 255))
        screen.blit(char_surface, (x_pos, y_pos))
        
        # 渲染序号
        index_surface = ascii_font.render(f"{i+1}", True, (150, 150, 150))
        screen.blit(index_surface, (x_pos, y_pos + 30))
        
        x_pos += 70
    
    pygame.display.flip()

def main():
    global chinese_font, ascii_font
    
    # 游戏主循环
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # 切换字体大小
                elif event.key in range(pygame.K_1, pygame.K_9 + 1):
                    size = (event.key - pygame.K_0) * 6 + 12  # 18-66
                    chinese_font = get_font(is_ascii=False, size=size)
                    ascii_font = get_font(is_ascii=True, size=size)
        
        render_chars()
        pygame.time.wait(100)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 