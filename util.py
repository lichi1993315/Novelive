import pygame
import os

def load_chinese_font(size=24):
    """加载中文字体，尝试多种方法"""
    font = None
    
    # 方法1: 尝试加载当前目录中的字体文件
    font_files = ['simhei.ttf', 'simsun.ttc', 'msyh.ttf', 'SimHei.ttf', 'SourceHanSansSC-Regular.otf']
    for font_file in font_files:
        if os.path.exists(font_file):
            try:
                font = pygame.font.Font(font_file, size)
                print(f"加载字体文件: {font_file}")
                return font
            except:
                pass
    
    # 方法2: 尝试使用系统字体
    system_fonts = ['simhei', 'simsun', 'microsoftyahei', 'microsoftyaheimicrosoftyaheiui',
                   'dengxian', 'kaiti', 'fangsong', 'Arial Unicode MS']
    for font_name in system_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            print(f"加载系统字体: {font_name}")
            return font
        except:
            pass
    
    # 方法3: 最后使用默认字体（可能无法显示中文）
    print("警告: 未找到中文字体，使用默认字体")
    return pygame.font.Font(None, size)

def load_ascii_font(size=24):
    """加载用于ASCII字符的字体"""
    # 尝试加载常见的等宽字体，这些字体对ASCII符号的支持较好
    ascii_system_fonts = ['courier', 'consolas', 'monospace', 'lucidaconsole', 'dejavusansmono']
    for font_name in ascii_system_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            print(f"加载ASCII字体: {font_name}")
            return font
        except:
            pass
    
    # 如果找不到合适的等宽字体，使用Pygame默认字体
    print("使用默认ASCII字体")
    return pygame.font.Font(None, size)

# 全局字体对象，避免重复加载
chinese_font = None
ascii_font = None

def get_font(is_ascii=False, size=24):
    """根据需要获取适当的字体"""
    global chinese_font, ascii_font
    
    if is_ascii:
        if ascii_font is None:
            ascii_font = load_ascii_font(size)
        return ascii_font
    else:
        if chinese_font is None:
            chinese_font = load_chinese_font(size)
        return chinese_font 