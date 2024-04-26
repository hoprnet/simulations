import click

BOLD = "\033[1m"
RESET = "\033[0m"

class StrippedLine:
    def __init__(self, line: str):
        self.line = line
        self.lemas = line.split()

        temp = line.split(" at block ")[-1].split()
        self.block, self.checksum = temp[0].strip(), temp[-1].strip()

    def __eq__(self, other):
        return self.block == other.block and self.checksum == other.checksum
    
    def show(self, text: str):
        print(f"{BOLD}{text:30s}{RESET}{self.block} ({self.checksum})")

def import_files(*names: list[str]):
    for name in names:
        with open(name, 'r') as f:
            yield f.readlines()

@click.command()
@click.option("--left", "leftfile", help="Path to the left file")
@click.option("--right", "rightfile", help="Path to the right file")
def main(leftfile: str, rightfile: str):
    left, right = import_files(leftfile, rightfile)

    l_striped = [StrippedLine(l) for l in left]
    r_striped = [StrippedLine(r) for r in right]

    l_blocks = sorted(map(lambda x: x.block, l_striped))
    r_blocks = sorted(map(lambda x: x.block, r_striped))

    # Find the first block that is shared between two lists
    first_shared_block = sorted(set(l_blocks).intersection(r_blocks))[0]
    l_start, r_start = l_blocks.index(first_shared_block), r_blocks.index(first_shared_block)
    idx = sum([l == r for l, r in zip(l_striped[l_start:], r_striped[r_start:])]) - 1
 
    assert r_striped[r_start+idx] == l_striped[l_start+idx], "Last common block is not the same"
    assert r_striped[r_start+idx+1] != l_striped[l_start+idx+1], "Next block is the same"

    l_striped[0].show("First block from L-side")
    r_striped[0].show("First block from R-side")
    print("-" * 108)
    l_striped[-1].show("Last block from L-side")
    r_striped[-1].show("Last block from R-side")
    print("-" * 108)
    l_striped[l_start].show("First common block")
    r_striped[r_start+idx].show("Last common block")

if __name__ == "__main__":
    main()