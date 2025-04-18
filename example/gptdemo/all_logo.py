from pyfiglet import Figlet, FigletFont
from colorama import Fore, Style, init
import shutil
import os
import sys
import time



# 配置参数
TERMINAL_WIDTH = 120  # 根据实际终端调整
PAGE_SIZE = 3         # 每页展示字体数S
FALLBACK_FONT = "standard"  # 异常备用字体
TEXT_TO_RENDER = "iCell"     # 展示文本

def clear_screen():
    """清屏并设置黑色背景"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Style.RESET_ALL + "\033[40m")
	

def get_all_fonts():
    """获取可用字体列表[1,2,4](@ref)"""
    fonts = FigletFont().getFonts()
    # 过滤已知问题字体
    return [f for f in fonts if f not in {'1943', 'banner3'}]  

def generate_art(text, font_name):
    """带异常处理的字体生成"""
    try:
        f = Figlet(font=font_name, width=TERMINAL_WIDTH)
        return f"{Fore.CYAN}Font: {font_name.center(TERMINAL_WIDTH)}\n" + \
               f"{Fore.GREEN}{f.renderText(text)}"
    except Exception as e:
        return f"{Fore.RED}Failed to render '{font_name}': {str(e)}"

def display_fonts(fonts, start_idx=0):
    """分页展示字体"""
    clear_screen()
    
    # 页眉信息
    header = f"Total Fonts: {len(fonts)} | Current: {start_idx+1}-{min(start_idx+PAGE_SIZE, len(fonts))}"
    print(f"{Fore.YELLOW}{header.center(TERMINAL_WIDTH)}\n{'═'*TERMINAL_WIDTH}")
    
    # 分页生成内容
    for i in range(start_idx, min(start_idx+PAGE_SIZE, len(fonts))):
        art = generate_art(TEXT_TO_RENDER, fonts[i])
        for line in art.split('\n'):
            print(line.center(TERMINAL_WIDTH))
        print(f"{Fore.MAGENTA}{'═'*TERMINAL_WIDTH}")

def interactive_browser():
    """交互式浏览界面"""
    fonts = get_all_fonts()
    idx = 0
    
    while idx < len(fonts):
        display_fonts(fonts, idx)
        
        # 操作提示
        prompt = "[N]ext Page | [P]revious | [Q]uit | [G]oto: "
        print(f"\n{Fore.WHITE}{prompt.center(TERMINAL_WIDTH)}", end='')
        
        # 处理用户输入
        choice = input().lower()
        if choice == 'n':
            idx = min(idx + PAGE_SIZE, len(fonts)-1)
        elif choice == 'p':
            idx = max(0, idx - PAGE_SIZE)
        elif choice == 'g':
            try:
                goto = int(input("Enter font index (1-{}): ".format(len(fonts)))) - 1
                idx = max(0, min(goto, len(fonts)-1))
            except:
                print("Invalid input!")
                time.sleep(1)
        elif choice == 'q':
            break


def main():
    try:
        interactive_browser()
    except KeyboardInterrupt:
        print("\n{Fore.RED}Exiting...")
    finally:
        print(Style.RESET_ALL)    


def display_all_fonts(text="iCell", max_width=120):
    """一次性展示所有字体效果"""
    init()  # 初始化colorama
    terminal_width = min(shutil.get_terminal_size().columns, max_width)
    
    # 获取过滤后的字体列表（排除已知问题字体）
    all_fonts = [f for f in FigletFont().getFonts() if f not in {'1943', 'banner3', 'smkeyboard'}]
    
    print(f"{Fore.YELLOW}Total Fonts: {len(all_fonts)}".center(terminal_width))
    print(f"Preview Text: {text}\n{'═'*terminal_width}{Style.RESET_ALL}")

    for idx, font in enumerate(all_fonts, 1):
        try:
            f = Figlet(font=font, width=terminal_width)
            art = f.renderText(text)
            print(f"{Fore.CYAN}Font [{idx:03d}]: {font}")
            print(f"{Fore.GREEN}{art}")
            print(f"{Fore.MAGENTA}{'─'*terminal_width}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error in font '{font}': {str(e)}")
            print(f"{Fore.MAGENTA}{'─'*terminal_width}{Style.RESET_ALL}")

if __name__ == '__main__':
    display_all_fonts()        
    # main()
