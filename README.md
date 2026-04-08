# CS 21 24.2 Project: Arch-242

A full-stack implementation of the **Arch-242** custom CPU architecture for CS 21 (Computer Organization and Architecture), 2nd Semester AY 2024–2025 at UP Diliman. The Arch-242 architecture and ISA were defined by the course instructors; this repository contains our group's implementation: an assembler, a graphical emulator, a Snake game written in Arch-242 assembly, and a hardware implementation in Logisim Evolution.

## Group Members & Contributions

| Member | Contributions |
|---|---|
| Lim, Eliana Mari P. | Emulator (Part A2), Snake Game (Part A3) |
| Ricaforte, Jarelle Gail E. | Snake Game (Part A3), Hardware Implementation (Part B) |
| Sacramento, Gabrielle Denise S. | Hardware Implementation (Part B) |
| Sim, Charlize S. | Assembler (Part A1), Snake Game (Part A3) |

---

## Arch-242 Architecture Overview

Arch-242 is a **Harvard architecture** (separate instruction and data memory) with the following properties:

- **Instruction addresses**: 16-bit wide
- **Data memory addresses**: 8-bit wide (256 addressable locations)
- **Instruction width**: 1 or 2 bytes; PC advances by the instruction's width after each execution

### Registers

| Name | Width | Description |
|---|---|---|
| RA, RB, RC, RD, RE | 4-bit each | General-purpose registers (indices 0–4) |
| ACC | 4-bit | Accumulator — destination of most arithmetic and logic operations |
| CF | 1-bit | Carry/borrow flag, set by arithmetic operations |
| TEMP | 16-bit | Holds the return address during a `call`; cleared on `ret` |
| IOA | 4-bit | I/O register; bits 0–3 correspond to Up, Down, Left, Right arrow keys |

### LED Matrix (Memory-Mapped I/O)

Data memory addresses **192–241** are memory-mapped to a **10-row × 20-column** LED matrix display. Only the lower nibble of each byte is used — each bit maps to one LED cell. The upper nibble is ignored.

| Data address | Bits used | Maps to |
|---|---|---|
| 192 | bits 0–3 | Row 0, Columns 0–3 |
| 193 | bits 0–3 | Row 0, Columns 4–7 |
| … | … | … |
| 241 | bits 0–3 | Row 9, Columns 16–19 |

---

## Instruction Set Reference

> **Notation:**
> - `MEM[RB:RA]` — 8-bit data memory address formed as `(RB << 4) | RA`
> - `MEM[RD:RC]` — 8-bit data memory address formed as `(RD << 4) | RC`
> - `<imm>` — an integer literal (decimal or `0x`-prefixed hex) or a **label name**
> - `<reg>` — register index: `0`=RA, `1`=RB, `2`=RC, `3`=RD, `4`=RE
> - All values are 4-bit (0–15) unless otherwise stated; overflow bits are discarded

### Memory Access

| Instruction | Bytes | Effect |
|---|---|---|
| `from-mba` | 1 | `ACC = MEM[RB:RA]` |
| `to-mba` | 1 | `MEM[RB:RA] = ACC` |
| `from-mdc` | 1 | `ACC = MEM[RD:RC]` |
| `to-mdc` | 1 | `MEM[RD:RC] = ACC` |
| `inc*-mba` | 1 | `MEM[RB:RA] = MEM[RB:RA] + 1` |
| `dec*-mba` | 1 | `MEM[RB:RA] = MEM[RB:RA] - 1` |
| `inc*-mdc` | 1 | `MEM[RD:RC] = MEM[RD:RC] + 1` |
| `dec*-mdc` | 1 | `MEM[RD:RC] = MEM[RD:RC] - 1` |
| `and*-mba` | 1 | `MEM[RB:RA] = ACC & MEM[RB:RA]` |
| `xor*-mba` | 1 | `MEM[RB:RA] = ACC ^ MEM[RB:RA]` |
| `or*-mba` | 1 | `MEM[RB:RA] = ACC \| MEM[RB:RA]` |

**Loading an address into RA/RB or RC/RD** is done with `rarb` / `rcrd`. The 8-bit immediate encodes both nibbles: the low nibble goes into the first register, and the high nibble into the second.

| Instruction | Bytes | Effect |
|---|---|---|
| `rarb <imm>` | 2 | `RA = low nibble of imm`, `RB = high nibble of imm` |
| `rcrd <imm>` | 2 | `RC = low nibble of imm`, `RD = high nibble of imm` |

Example: `rarb 0xC3` → RA=3, RB=12, so `MEM[RB:RA]` addresses byte `0xC3` (195).

### Arithmetic

| Instruction | Bytes | Effect |
|---|---|---|
| `add-mba` | 1 | `ACC = ACC + MEM[RB:RA]`; CF = carry out |
| `addc-mba` | 1 | `ACC = ACC + MEM[RB:RA] + CF`; CF = carry out |
| `sub-mba` | 1 | `ACC = ACC - MEM[RB:RA]`; CF = borrow |
| `subc-mba` | 1 | `ACC = ACC - MEM[RB:RA] + CF`; CF = borrow |
| `inc` | 1 | `ACC = ACC + 1` |
| `dec` | 1 | `ACC = ACC - 1` |
| `inc*-reg <reg>` | 1 | `REG[reg] = REG[reg] + 1` |
| `dec*-reg <reg>` | 1 | `REG[reg] = REG[reg] - 1` |
| `add <imm>` | 2 | `ACC = ACC + imm` (imm: 0–15) |
| `sub <imm>` | 2 | `ACC = ACC - imm` (imm: 0–15) |
| `bcd` | 1 | If `ACC >= 10` or `CF == 1`: `ACC = ACC + 6`, `CF = 1` (BCD correction) |

### Logic & Rotation

| Instruction | Bytes | Effect |
|---|---|---|
| `and-ba` | 1 | `ACC = ACC & MEM[RB:RA]` |
| `xor-ba` | 1 | `ACC = ACC ^ MEM[RB:RA]` |
| `or-ba` | 1 | `ACC = ACC \| MEM[RB:RA]` |
| `and <imm>` | 2 | `ACC = ACC & imm` (imm: 0–15) |
| `xor <imm>` | 2 | `ACC = ACC ^ imm` (imm: 0–15) |
| `or <imm>` | 2 | `ACC = ACC \| imm` (imm: 0–15) |
| `rot-r` | 1 | Rotate ACC one bit right (bit 0 wraps to bit 3) |
| `rot-l` | 1 | Rotate ACC one bit left (bit 3 wraps to bit 0) |
| `rot-rc` | 1 | Rotate `CF:ACC` right: CF → bit 3 of ACC, bit 0 of ACC → CF |
| `rot-lc` | 1 | Rotate `CF:ACC` left: bit 3 of ACC → CF, CF → bit 0 of ACC |

### Register & ACC Operations

| Instruction | Bytes | Effect |
|---|---|---|
| `acc <imm>` | 1 | `ACC = imm` (imm: 0–15) |
| `to-reg <reg>` | 1 | `REG[reg] = ACC` |
| `from-reg <reg>` | 1 | `ACC = REG[reg]` |
| `r4 <imm>` | 2 | `RE = imm` (imm: 0–15; directly sets RE without going through ACC) |
| `clr-cf` | 1 | `CF = 0` |
| `set-cf` | 1 | `CF = 1` |

### Control Flow

Branch targets can be a numeric address or a **label name**. All branch instructions preserve the top bits of PC, keeping execution within the same memory page.

| Instruction | Bytes | Branches if… |
|---|---|---|
| `b <imm>` | 2 | Always (unconditional jump) |
| `call <imm>` | 2 | Always; saves `PC + 2` to TEMP first |
| `ret` | 1 | Always; restores PC from TEMP, clears TEMP |
| `beqz <imm>` | 2 | `ACC == 0` |
| `bnez <imm>` | 2 | `ACC != 0` |
| `beqz-cf <imm>` | 2 | `CF == 0` |
| `bnez-cf <imm>` | 2 | `CF != 0` |
| `bnz-a <imm>` | 2 | `RA != 0` |
| `bnz-b <imm>` | 2 | `RB != 0` |
| `bnz-d <imm>` | 2 | `RD != 0` |
| `b-bit <k> <imm>` | 2 | Bit `k` of ACC is 1 (k: 0=LSB … 3=MSB) |

### I/O & Miscellaneous

| Instruction | Bytes | Effect |
|---|---|---|
| `from-ioa` | 1 | `ACC = IOA` (reads current button state) |
| `nop` | 1 | No operation |
| `shutdown` | 2 | Stops execution (closes emulator / halts hardware) |
| `.byte <value>` | 1 | Assembler directive: places a raw byte into instruction memory |

---

## Setup

**Requirements:** Python 3.10+, Pyxel 2.8.10, Logisim Evolution

1. Clone this repository or download and extract the ZIP.
2. Install Python dependencies:

```sh
pip install -r requirements.txt
```

or

```sh
pip3 install -r requirements.txt
```

3. Install **Logisim Evolution** (required for Part B only) from the [Logisim Evolution releases page](https://github.com/logisim-evolution/logisim-evolution/releases) based on your device.

---

## Part A1: Assembler

Translates Arch-242 assembly (`.asm`) into binary or Logisim-compatible hex output.

### How to Run

From the **root directory**:

```sh
python parta1/assembler.py <input_file.asm> <bin | hex>
```

The output file is written alongside the input file with the corresponding extension (e.g., `input.hex`).

### Supported Syntax

**Labels** — define with `label_name:`, reference by name in any branch or call instruction. Forward references are supported.

```asm
main_loop:
    from-ioa
    beqz no_input       # branch if ACC == 0
    b process_input

no_input:
    nop
    b main_loop
```

**Comments** — `#` starts a comment to end of line (inline or full-line).

**Immediate values** — both decimal (`10`) and hex (`0xA`, `0xFF`) are accepted. Case-insensitive.

**`.byte` directive** — places a raw byte value directly into instruction memory:
```asm
.byte 0x2F
```

### Error Reporting

Line-specific errors are reported with the offending line number:
```
Error at line 15: Invalid register number: 7
Error at line 23: Immediate value too large for add: 20
Error at line 31: Unknown instruction: invalidop
```

### Notes / Assumptions
- `.byte` values are placed in **instruction memory** (same address space as instructions) and increment the program counter accordingly.

---

## Part A2: Emulator

A Pyxel-based graphical emulator that executes Arch-242 programs and displays output on a 10-row × 20-column LED matrix window.

### How to Run

From the **root directory**, pass any `.asm` file directly — the emulator calls the assembler internally:

```sh
python parta2/arch242.py <input_file.asm>
```

### Controls

| Key | IOA bit | Action |
|---|---|---|
| ↑ Up | bit 0 | Move snake up |
| ↓ Down | bit 1 | Move snake down |
| ← Left | bit 2 | Move snake left |
| → Right | bit 3 | Move snake right |

### Debugging Mode

Disabled by default. To enable, open [parta2/emulator.py](parta2/emulator.py) and set:

```python
self.debugging = True
```

When enabled, every executed instruction is logged to `parta2/logs/debugging.txt` with the current PC, instruction name, ACC, CF, TEMP, registers, and IOA values.

### Notes / Assumptions
- Both instruction memory and data memory are treated as **byte-addressable**.
- The LED display window is **10 rows × 20 columns**, matching the memory mapping table (addresses 192–241).

---

## Part A3: Snake Game

A Snake game written entirely in Arch-242 assembly, playable in the emulator.

### How to Play

```sh
python parta2/arch242.py parta3/snake.asm
```

- Use the **arrow keys** to steer the snake.
- Eat food to grow and increase your score (max score: 15).
- The game restarts automatically when the snake hits a wall or itself.

### Game Rules
- Snake starts with length 3 and moves every game tick.
- Score starts at 0 and increments each time food is eaten.
- Score display is shown on the LED matrix alongside the game grid.

### Notes / Assumptions
- On restart, the snake respawns and continues moving in the **most recent direction**.
- Pressing the key **opposite** to the current direction is treated as a self-collision and triggers a restart (e.g., pressing Left while moving Right).

---

## Part B: Logisim Hardware Implementation

A Logisim Evolution circuit that implements the Arch-242 processor in hardware.

### How to Run

1. Open `partb/Arch242.circ` in **Logisim Evolution**.
2. Navigate to the **InstrMem** subcircuit.
3. Right-click the ROM component → **Load Image → Hex**.
4. Select the `.hex` file generated by the assembler.
5. Start the simulation.

To generate a `.hex` file from assembly:

```sh
python parta1/assembler.py <input_file.asm> hex
```

The `.hex` output is placed in the same directory as the input `.asm` file.

### Notes / Assumptions
- Instruction memory is **byte-addressable**; data memory is **nibble-addressable**.
- The LED matrix and IOA input buttons are not implemented in the hardware.
