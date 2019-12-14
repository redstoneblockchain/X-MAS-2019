
#include <cstdint>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define debugf(...) fprintf(stderr, __VA_ARGS__)

class VM {
public:
  uint8_t ram[0x10000];
  bool block[0x10000];
  uint16_t pc;
  uint8_t a;

  VM() {
    memset(ram, 0, sizeof(ram));
    memset(block, 0, sizeof(block));
    pc = 0x100;
    a = 0;
  }

  void loadrom(FILE *fp, size_t size) {
    if (size != fread(ram + 0x100, 1, size, fp)) {
      debugf("failed to load ROM\n");
    }
  }

  uint8_t next8() {
    uint8_t x = ram[pc];
    jump(pc + 1);
    return x;
  }

  void tick() {
    uint8_t op = next8();
    uint8_t arg = next8();

    if (op == 0xBE && arg == 0xEF) {
      debugf("magic $BEEF\n");
      jump(0x100);
      a = 0x42;
      return;
    }

    if (op == 0xEE && arg == 0xEE) {
      debugf("nop\n");
      return;
    }

    if (op == 0x13 && arg == 0x37) {
      // printf("serial: $%02x %c\n", a, a);
      fwrite(&a, 1, 1, stdout);
      fflush(stdout);

      if (a != '{' && a != '}' && a != '-' && a != '_' && a != '.' && !isalnum(a)) {
        exit(1);
      }

      return;
    }

    switch (op) {
    case 0x00:
      debugf("add #$%02x\n", arg);
      a += arg;
      break;
    case 0x01:
      debugf("lda #$%02x\n", arg);
      a = arg;
      break;
    case 0x02:
      debugf("xor #$%02x\n", arg);
      a ^= arg;
      break;
    case 0x03:
      debugf("ora #$%02x\n", arg);
      a |= arg;
      break;
    case 0x04:
      debugf("and #$%02x\n", arg);
      a &= arg;
      break;
    case 0x60:
      debugf("cmp #$%02x\n", arg);
      // a = (a == arg) ? 1 : 0;
      a = compare(arg);
      break;
    default:
      uint8_t mode = op >> 4;
      uint16_t addr = ((op & 0b1111) << 8) | arg;

      switch (mode) {
      case 0x02:
        debugf("jmp $%04x\n", addr);
        jump(addr);
        break;
      case 0x03:
        debugf("jz  $%04x\n", addr);

        if (a == 0) {
          jump(addr);
        }

        break;
      case 0x04:
        debugf("je1 $%04x\n", addr);

        if (a == 1) {
          jump(addr);
        }

        break;
      case 0x05:
        debugf("jff $%04x\n", addr);

        if (a == 255) {
          jump(addr);
        }

        break;
      case 0x07:
        debugf("cmp [$%04x]\n", addr);
        // a = (a == ram[addr]) ? 1 : 0;
        a = compare(ram[addr]);

        break;
      case 0x08:
        debugf("lda [$%04x]\n", addr);
        a = ram[addr];
        break;
      case 0x09:
        debugf("blk $%04x\n", addr);
        block[addr] = 1;
        break;
      case 0x0A:
        debugf("unb $%04x\n", addr);
        block[addr] = 0;
        break;
      case 0x0C:
        debugf("frb $%04x\n", addr);
        // ram[addr] = ram[addr] ^ 0x42;
        write(addr, ram[addr] ^ 0x42);
        break;
      case 0x0D:
        debugf("xor [$%04x]\n", addr);
        // ram[addr] = ram[addr] ^ a;
        write(addr, ram[addr] ^ a);
        break;
      case 0x0F:
        debugf("sta $%04x\n", addr);
        // ram[addr] = a;
        write(addr, a);
        break;
      default:
        // debugf("unk $%02x $%02x\n", op, arg);
        // exit(1);
        a--;
        break;
      }

      break;
    }
  }

  void jump(uint16_t n) {
    pc = n & 0b111111111111;
  }

  void write(uint16_t addr, uint8_t value) {
    addr &= 0b111111111111;

    if (!block[addr]) {
      ram[addr] = value;
    }
  }

  uint8_t compare(uint8_t x) {
    if (a == x) {
      return 0;
    } else if (a < x) {
      return 1;
    } else {
      return 255;
    }
  }
};

int main() {
  VM vm;
  
  vm.loadrom(stdin, 3840);

  while (true) {
    vm.tick();
  }

  return 0;
}
