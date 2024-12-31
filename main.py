# main.py
from app import main_entry


def main():
    try:
        main_entry()
    except Exception as e:
        print(f"except as {e}")
        

if __name__ == "__main__":
    main()
