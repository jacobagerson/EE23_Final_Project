#ifndef SYNTH_H
#define SYNTH_H

#include <stdint.h>

// ==============================
// INIT
// ==============================

void synth_init(void);

// ==============================
// NOTE CONTROL
// ==============================

// velocity: 0–127 (raw MIDI)
void note_on(uint8_t note, float velocity);

void note_off(uint8_t note);

// ==============================
// AUDIO GENERATION
// ==============================

// returns sample in range ~[-1, 1]
float synth_sample(void);

#endif
