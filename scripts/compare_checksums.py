import click

def import_files(*names: list[str]):
    for name in names:
        with open(name, 'r') as f:
            yield f.readlines()

def strip_checksum(data: str):
    lemas = data.split(" at block ")[-1].split()
    return lemas[0].strip(), lemas[-1].strip()

def show_results(description: str, value: tuple[str, str]):
    print(f"{description:30s}{value[0]} ({value[1]})")

@click.command()
@click.option("--left", "leftfile", help="Path to the left file")
@click.option("--right", "rightfile", help="Path to the right file")
def main(leftfile: str, rightfile: str):
    left, right = import_files(leftfile, rightfile)
    
    idx = sum([strip_checksum(l) == strip_checksum(r) for l, r in zip(left, right)])
    
    assert strip_checksum(right[idx-1]) == strip_checksum(left[idx-1]), "Last common block is not the same"
    assert strip_checksum(right[idx]) != strip_checksum(left[idx]), "Next block is the same"

    show_results("Last block from L-side", strip_checksum(left[-1]))
    show_results("Last block from R-side", strip_checksum(right[-1]))
    print("-" * 108)
    show_results("Last common block", strip_checksum(right[idx-1]))

if __name__ == "__main__":
    main()