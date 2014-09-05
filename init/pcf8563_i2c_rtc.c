/*
  * pcf8563_i2c_rtc.c - example of accessing a PCF8563 via the BSC0 (I2C) peripheral on a BCM2835 (Raspberry Pi)
  *
  * Copyright 2012 Kevin Sangeelee.
  * Released as GPLv2, see <http://www.gnu.org/licenses/>
  *
  * This is intended as an example of using Raspberry Pi hardware registers to drive an RTC chip. Use at your own risk or
  * not at all. As far as possible, I've omitted anything that doesn't relate to the RTC or the Raspi registers. There are more
  * conventional ways of doing this using kernel drivers, though they're harder to follow what's happening in hardware.
  */
#include <stdio.h>
#include <time.h>
#include <fcntl.h>
#include <sys/mman.h>

#define IOBASE   0x20000000

#define BSC0_BASE (IOBASE + 0x205000)
#define GPIO_BASE (IOBASE + 0x200000)

#define BSC0_C        *(bsc0.addr + 0x00)
#define BSC0_S        *(bsc0.addr + 0x01)
#define BSC0_DLEN    *(bsc0.addr + 0x02)
#define BSC0_A        *(bsc0.addr + 0x03)
#define BSC0_FIFO    *(bsc0.addr + 0x04)

#define BSC_C_I2CEN    (1 << 15)
#define BSC_C_INTR    (1 << 10)
#define BSC_C_INTT    (1 << 9)
#define BSC_C_INTD    (1 << 8)
#define BSC_C_ST    (1 << 7)
#define BSC_C_CLEAR    (1 << 4)
#define BSC_C_READ    1

#define START_READ    BSC_C_I2CEN|BSC_C_ST|BSC_C_CLEAR|BSC_C_READ
#define START_WRITE    BSC_C_I2CEN|BSC_C_ST

#define BSC_S_CLKT    (1 << 9)
#define BSC_S_ERR    (1 << 8)
#define BSC_S_RXF    (1 << 7)
#define BSC_S_TXE    (1 << 6)
#define BSC_S_RXD    (1 << 5)
#define BSC_S_TXD    (1 << 4)
#define BSC_S_RXR    (1 << 3)
#define BSC_S_TXW    (1 << 2)
#define BSC_S_DONE    (1 << 1)
#define BSC_S_TA    1

#define CLEAR_STATUS    BSC_S_CLKT|BSC_S_ERR|BSC_S_DONE

#define PAGESIZE 4096
#define BLOCK_SIZE 4096

struct bcm2835_peripheral {
    unsigned long addr_p;
    int mem_fd;
    void *map;
    volatile unsigned int *addr;
};

struct bcm2835_peripheral gpio = {GPIO_BASE};
struct bcm2835_peripheral bsc0 = {BSC0_BASE};

// Some forward declarations...
void dump_bsc_status();
int map_peripheral(struct bcm2835_peripheral *p);
void unmap_peripheral(struct bcm2835_peripheral *p);

int systohc = 0;
int hctosys = 0;
struct tm t;
time_t now;

// BCD helper functions only apply to BCD 0-99 (one byte) values
unsigned int bcdtod(unsigned int bcd) {
    return ((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f);
}
unsigned int dtobcd(unsigned int d) {
    return ((d / 10) << 4) + (d % 10);
}

// Function to wait for the I2C transaction to complete
void wait_i2c_done() {
        //Wait till done, let's use a timeout just in case
        int timeout = 50;
        while((!((BSC0_S) & BSC_S_DONE)) && --timeout) {
            usleep(1000);
        }
        if(timeout == 0)
            printf("wait_i2c_done() timeout. Something went wrong.\n");
}

////////////////
//  main()
////////////////
int main(int argc, char *argv[]) {

    if(argc == 2) {
        if(!strcmp(argv[1], "-w"))
            systohc = 1;
        if(!strcmp(argv[1], "-s"))
            hctosys = 1;
    }

    if(map_peripheral(&gpio) == -1) {
        printf("Failed to map the physical GPIO registers into the virtual memory space.\n");
        return -1;
    }
    if(map_peripheral(&bsc0) == -1) {
        printf("Failed to map the physical BSC0 (I2C) registers into the virtual memory space.\n");
        return -1;
    }

    /* BSC0 is on GPIO 0 & 1 */
    *gpio.addr &= ~0x3f; // Mask out bits 0-5 of FSEL0 (i.e. force to zero)
    *gpio.addr |= 0x24;  // Set bits 0-5 of FSEL0 to binary '100100'

    // I2C Device Address 0x51 (hardwired into the RTC chip)
    BSC0_A = 0x51;

    if(systohc) {

        printf("Setting RTC from system clock\n");

        now = time(NULL);
        gmtime_r(&now, &t);    // explode time_t (now) into an struct tm

        //////
        // Write Operation to set the time (writing 15 of the 16 RTC registers to
        // also reset status, alarm, and timer settings).
        //////
        BSC0_DLEN = 16;
        BSC0_FIFO = 0;        // Addr 0
        BSC0_FIFO = 0;        // control1
        BSC0_FIFO = 0;        // control2
        BSC0_FIFO = dtobcd(t.tm_sec);        // seconds
        BSC0_FIFO = dtobcd(t.tm_min);    // mins
        BSC0_FIFO = dtobcd(t.tm_hour);    // hours
        BSC0_FIFO = dtobcd(t.tm_mday);    // days
        BSC0_FIFO = dtobcd(t.tm_wday);    // weekdays (sun 0)
        BSC0_FIFO = dtobcd(t.tm_mon + 1);    // months 0-11 --> 1-12
        BSC0_FIFO = dtobcd(t.tm_year - 100);    // years
        BSC0_FIFO = 0x0;    // alarm min
        BSC0_FIFO = 0x0;    // alarm hour
        BSC0_FIFO = 0x0;    // alarm day
        BSC0_FIFO = 0x0;    // alarm weekday
        BSC0_FIFO = 0x0;    // CLKOUT control
        BSC0_FIFO = 0x0;    // timer control

        BSC0_S = CLEAR_STATUS; // Reset status bits (see #define)
        BSC0_C = START_WRITE;    // Start Write (see #define)

        wait_i2c_done();
    }

    //////
    // Write operation to restart the PCF8563 register at index 2 ('secs' field)
    //////
    BSC0_DLEN = 1;    // one byte
    BSC0_FIFO = 2;    // value 2
    BSC0_S = CLEAR_STATUS; // Reset status bits (see #define)
    BSC0_C = START_WRITE;    // Start Write (see #define)

    wait_i2c_done();

    //////
    // Start Read of RTC chip's time
    //////
    BSC0_DLEN = 7;
    BSC0_S = CLEAR_STATUS; // Reset status bits (see #define)
    BSC0_C = START_READ;    // Start Read after clearing FIFO (see #define)

    wait_i2c_done();

    // Store the values read in the tm structure, after masking unimplemented bits.
    t.tm_sec = bcdtod(BSC0_FIFO & 0x7f);
    t.tm_min = bcdtod(BSC0_FIFO & 0x7f);
    t.tm_hour = bcdtod(BSC0_FIFO & 0x3f);
    t.tm_mday = bcdtod(BSC0_FIFO & 0x3f);
    t.tm_wday = bcdtod(BSC0_FIFO & 0x07);
    t.tm_mon = bcdtod(BSC0_FIFO & 0x1f) - 1; // 1-12 --> 0-11
    t.tm_year = bcdtod(BSC0_FIFO) + 100;

    printf("%02d:%02d:%02d %02d/%02d/%02d (UTC on PCF8563)\n",
        t.tm_hour,t.tm_min,t.tm_sec,
        t.tm_mday,t.tm_mon + 1,t.tm_year - 100);

    if(hctosys) {
        printf("Setting system clock from RTC\n");
        now = timegm(&t);
        stime(&now);
    }

    unmap_peripheral(&gpio);
    unmap_peripheral(&bsc0);

    // Done!
}

// Exposes the physical address defined in the passed structure using mmap on /dev/mem
int map_peripheral(struct bcm2835_peripheral *p)
{
   // Open /dev/mem
   if ((p->mem_fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
      printf("Failed to open /dev/mem, try checking permissions.\n");
      return -1;
   }

   p->map = mmap(
      NULL,
      BLOCK_SIZE,
      PROT_READ|PROT_WRITE,
      MAP_SHARED,
      p->mem_fd,  // File descriptor to physical memory virtual file '/dev/mem'
      p->addr_p      // Address in physical map that we want this memory block to expose
   );

   if (p->map == MAP_FAILED) {
        perror("mmap");
        return -1;
   }

   p->addr = (volatile unsigned int *)p->map;

   return 0;
}

void unmap_peripheral(struct bcm2835_peripheral *p) {

    munmap(p->map, BLOCK_SIZE);
    close(p->mem_fd);
}

void dump_bsc_status() {

    unsigned int s = BSC0_S;

    printf("BSC0_S: ERR=%d  RXF=%d  TXE=%d  RXD=%d  TXD=%d  RXR=%d  TXW=%d  DONE=%d  TA=%d\n",
        (s & BSC_S_ERR) != 0,
        (s & BSC_S_RXF) != 0,
        (s & BSC_S_TXE) != 0,
        (s & BSC_S_RXD) != 0,
        (s & BSC_S_TXD) != 0,
        (s & BSC_S_RXR) != 0,
        (s & BSC_S_TXW) != 0,
        (s & BSC_S_DONE) != 0,
        (s & BSC_S_TA) != 0 );
}
