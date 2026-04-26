#include <stdint.h>
#include <stm32l432xx.h>
#include "ee14lib.h"

#define MIDI_BAUD 31250U
#define MIDI_FRAME_BITS 30U


static uint8_t extract_word(uint32_t frame, uint8_t start_bit)
{
    return (uint8_t)((frame >> start_bit) & 0xFFU);
}

void cycle_counter_init(void)
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}


/*
// This is used by snprintf(); see below.
#define LINE_BUFFER_LEN 100

int main()
{
    host_serial_init(9600);

    NVIC_EnableIRQ(USART2_IRQn);

    // For the code below, we're going to use our own pre-allocated buffer
    // and snprintf() instead of relying on printf().  This eliminates a couple
    // levels of indirection in the stdlib, so we have 100% confidence in what
    // is being buffered and sent.
    char linebuf[LINE_BUFFER_LEN];

    int count = 0;
    int bytes_written = 0;

    while (1)
    {
        // snprintf is like printf, except that it puts the formatted result
        // into a character buffer that you've allocated.  Then you can call
        // functions like serial_write() or serial_write_nonblocking() directly.
        gpio_config_mode(D13, OUTPUT);

        int bytes_to_write = snprintf(linebuf, LINE_BUFFER_LEN, "Loop %d\n", count++);
        bytes_written = serial_write_nonblocking(USART2, linebuf, bytes_to_write);

        // Or replace this with a proper timing function...
        for (volatile int x = 0; x < 10000; x++)
        {
        }
    }
}*/
