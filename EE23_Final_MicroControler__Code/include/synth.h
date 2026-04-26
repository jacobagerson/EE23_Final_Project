#ifndef SYNTH_H
#define SYNTH_H

#include <stdint.h>

void synth_init(void);
void note_on(uint8_t note, float velocity);
void note_off(uint8_t note);
float synth_sample(void);
uint16_t synth_sample_u12(void);

#endif
