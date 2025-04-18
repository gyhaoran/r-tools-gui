from pyfiglet import Figlet
from colorama import Fore, Style


ICELL_LOGO_WIDTH = 110


def icell_logo(font):        
    f = Figlet(font=font, width=ICELL_LOGO_WIDTH)

    print(Style.RESET_ALL + "\033[40m")
    print("\033[97m")

    icell = f.renderText('iCell').strip('\n')
    for line in icell.split('\n'):
        print(line.center(ICELL_LOGO_WIDTH))


    print(f"\n{'═'*ICELL_LOGO_WIDTH}")
    print("Automated Standard Cell Generation and Optimization".center(ICELL_LOGO_WIDTH))
    print(f"\n{'Copyright © 2023~2025 NCTIEDA'.center(ICELL_LOGO_WIDTH)}\n")

    print(Style.RESET_ALL + Fore.RESET + "\033[0m")


if __name__ == '__main__':
    for font in ['varsity', 'slant', 'standard', 'epic', '3d_diagonal', 'blocks']:
        print(f"font: {font}\n")
        icell_logo(font)
