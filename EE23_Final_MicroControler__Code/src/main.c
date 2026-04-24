#include <stdio.h>
#include <stdint.h>
#include <stm32l432xx.h>
#include "ee14lib.h"

#define LINE_BUFFER_LEN 100
#define HOST_BAUD 9600U
#define MIDI_BAUD 31250U
#define MIDI_FRAME_BITS 30U


int main()
{
    host_serial_init(HOST_BAUD);
    gpio_config_mode(A0, INPUT);
    gpio_config_pullup(A0, PULL_UP);
    cycle_counter_init();
    gpio_config_mode(D12,OUTPUT);


    char linebuf[LINE_BUFFER_LEN];
    uint8_t midi_words[3] = {0};

    printf("A0 MIDI monitor ready at %lu baud\r\n", (unsigned long)HOST_BAUD);
    printf("Expecting %lu baud MIDI data on A0\r\n", (unsigned long)MIDI_BAUD);

    while (1)
    {
        if (midi_read_message(midi_words))
        {
            int bytes_to_write = snprintf(
                linebuf,
                LINE_BUFFER_LEN,
                "MIDI: 0x%02X 0x%02X 0x%02X\r\n",
                midi_words[0],
                midi_words[1],
                midi_words[2]);
            serial_write(USART2, linebuf, bytes_to_write);
        }
        if(midi_words[1] == 0x30)
        {
            gpio_write(D12,1);
        } else {
            gpio_write(D12,0);
        }

    }
}
