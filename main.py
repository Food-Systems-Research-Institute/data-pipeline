from utils import see_tables

def main():
    print("Hello from data-pipeline!")


if __name__ == "__main__":
    see_tables("raw_ers", show_columns=True)
    main()
