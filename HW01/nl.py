import fileinput


def main():
    lineno = 1
    with fileinput.input() as f:
        for line in f:
            print(f"{lineno} {line}", end="")
            lineno += 1


if __name__ == "__main__":
    main()
