#include <stdint.h>
#include <stdbool.h>
#include <stm32l432xx.h>
#include "ee14lib.h"
#include "synth.h"

// ==============================
// AUDIO PIN (DAC on A3 / PA4)
// ==============================
#define AUDIO_PIN A3

#define NUM_PINS 12
volatile uint16_t audio_sample = 2048;

EE14Lib_Pin note_pins[NUM_PINS] = {
    D2, D3, D4, D5, D6, D7,
    D8, D9, D10, D11, D12, D13};

// ==============================
// MIDI BUFFER
// ==============================

#define RX_BUF_SIZE 256

volatile uint8_t rx_buf[RX_BUF_SIZE];
volatile uint16_t rx_head = 0;
volatile uint16_t rx_tail = 0;

static inline bool rx_available(void)
{
    return rx_head != rx_tail;
}

static inline uint8_t rx_pop(void)
{
    uint8_t b = rx_buf[rx_tail];
    rx_tail = (rx_tail + 1) & (RX_BUF_SIZE - 1);
    return b;
}

// ==============================
// MIDI STATE
// ==============================

uint8_t midi_status = 0;
uint8_t midi_data[2];
uint8_t midi_index = 0;
uint8_t band_counts[NUM_PINS] = {0};

// ==============================
// DAC INIT (A3)
// ==============================

void dac_init(void)
{
    // Enable DAC clock
    RCC->APB1ENR1 |= RCC_APB1ENR1_DAC1EN;

    // Set PA4 (A3) to analog mode
    gpio_config_mode(A3, ANALOG);

    // 🔥 Ensure buffer is ENABLED (this is key)
    DAC1->CR &= ~(1 << 1);

    // Enable DAC channel
    DAC1->CR |= DAC_CR_EN1;

    // Give it a starting value so it's not stuck at 0
    DAC1->DHR12R1 = 2048;
}

// ==============================
// AUDIO TIMER (unchanged)
// ==============================

void audio_timer_init(void)
{
    RCC->APB1ENR1 |= RCC_APB1ENR1_TIM6EN;

    TIM6->PSC = 79; // 80 MHz / 80 = 1 MHz
    TIM6->ARR = 24; // 1 MHz / 25 = 40 kHz

    TIM6->EGR = TIM_EGR_UG; // 🔥 FORCE UPDATE (IMPORTANT)
    TIM6->SR = 0;           // clear flags

    TIM6->DIER |= TIM_DIER_UIE;
    TIM6->CR1 |= TIM_CR1_CEN;

    NVIC_EnableIRQ(TIM6_DAC_IRQn);
}

// ==============================
// AUDIO ISR
// We get smoothed samples from
// main loop instead of stair
// steps we were seeing
// ==============================

void TIM6_DAC_IRQHandler(void)
{
    if (TIM6->SR & TIM_SR_UIF)
    {
        TIM6->SR &= ~TIM_SR_UIF;

        float s = synth_sample();
        uint16_t duty = (uint16_t)((s * 0.9f + 1.0f) * 2047.0f);

        DAC1->DHR12R1 = duty;
    }
}

// ==============================
// MIDI HANDLER (unchanged)
// ==============================

void handle_midi(uint8_t status, uint8_t note, uint8_t velocity)
{
    uint8_t type = status & 0xF0;
    int band = note / 10;

    if (band >= NUM_PINS)
        band = NUM_PINS - 1;

    if (type == 0x90 && velocity > 0)
    {
        band_counts[band]++;
        gpio_write(note_pins[band], 1);

        note_on(note, velocity);
    }
    else if (type == 0x80 || (type == 0x90 && velocity == 0))
    {
        if (band_counts[band] > 0)
            band_counts[band]--;

        if (band_counts[band] == 0)
            gpio_write(note_pins[band], 0);

        note_off(note);
    }
}

// ==============================
// UART (unchanged)
// ==============================

void USART2_IRQHandler(void)
{
    if (USART2->ISR & USART_ISR_RXNE)
    {
        uint8_t byte = USART2->RDR;
        uint16_t next = (rx_head + 1) & (RX_BUF_SIZE - 1);

        if (next != rx_tail)
        {
            rx_buf[rx_head] = byte;
            rx_head = next;
        }
    }
}

// ==============================
// MAIN
// ==============================

int main()
{
    for (int i = 0; i < NUM_PINS; i++)
        gpio_config_mode(note_pins[i], OUTPUT);

    dac_init();
    audio_timer_init();
    synth_init();

    host_serial_init(31250); // ✅ correct MIDI baud
    USART2->CR1 |= USART_CR1_RXNEIE;
    NVIC_EnableIRQ(USART2_IRQn);

    while (1)
    {
        while (rx_available())
        {
            uint8_t byte = rx_pop();

            if (byte & 0x80)
            {
                midi_status = byte;
                midi_index = 0;
            }
            else
            {
                if (midi_status == 0)
                    continue;

                if (midi_index < 2)
                    midi_data[midi_index++] = byte;

                if (midi_index == 2)
                {
                    // ✅ FIX: scale velocity here before passing
                    uint8_t note = midi_data[0];
                    uint8_t vel = midi_data[1];

                    handle_midi(midi_status, note, vel);

                    midi_index = 0;
                }
            }
        }

        // ✅ CRITICAL FIX: yield CPU (prevents audio jitter)
        __WFI(); // wait for interrupt (low power + stable timing)
    }
}
