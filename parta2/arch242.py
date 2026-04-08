import sys, os

HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from parta1.assembler import Arch242Assembler
import emulator as emu

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 arch242.py input.asm")

    asm_path = sys.argv[1]
    asm_assembler = Arch242Assembler()
    instr_hex = asm_assembler.assemble(asm_path, "hex")

    emu.Arch242Emulator(instr_hex)

if __name__ == "__main__":
    main()