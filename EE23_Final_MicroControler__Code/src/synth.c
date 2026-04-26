#include "synth.h"
#include <math.h>
#include <stdlib.h>

#define MAX_VOICES 20
#define SAMPLE_RATE 40000.0f
#define TWO_PI 6.28318530718f

typedef struct
{
    uint8_t note; // 🔥 track note identity
    float freq;
    float phase;

    float amp;        // current amplitude
    float target_amp; // 🔥 for smoothing

    uint8_t active;
} Voice;

static Voice voices[MAX_VOICES];

// ==============================
// INIT
// ==============================

void synth_init()
{
    int i;
    for (i = 0; i < MAX_VOICES; i++)
    {
        voices[i].active = 0;
        voices[i].amp = 0;
        voices[i].target_amp = 0;
    }
}

// ==============================
// MIDI → FREQ
// ==============================

static float midi_to_freq(uint8_t note)
{
    return 440.0f * powf(2.0f, (note - 69) / 12.0f);
}

// ==============================
// NOTE ON (phase-safe)
// ==============================

void note_on(uint8_t note, float velocity)
{
    float f = midi_to_freq(note);
    float vel = velocity / 127.0f;
    int i;

    // reuse existing
    for (i = 0; i < MAX_VOICES; i++)
    {
        if (voices[i].active && voices[i].note == note)
        {
            voices[i].target_amp = vel;
            return;
        }
    }

    // find free voice
    for (i = 0; i < MAX_VOICES; i++)
    {
        if (!voices[i].active)
        {
            voices[i].note = note;
            voices[i].freq = f;

            // 🔥 RANDOM PHASE (CRITICAL)
            voices[i].phase = ((float)rand() / RAND_MAX) * TWO_PI;

            voices[i].amp = 0;
            voices[i].target_amp = vel;
            voices[i].active = 1;
            return;
        }
    }

    // 🔥 VOICE STEAL (if full)
    int steal = 0;
    float min_amp = 1e9;

    for (i = 0; i < MAX_VOICES; i++)
    {
        if (voices[i].amp < min_amp)
        {
            min_amp = voices[i].amp;
            steal = i;
        }
    }

    voices[steal].note = note;
    voices[steal].freq = f;
    voices[steal].phase = ((float)rand() / RAND_MAX) * TWO_PI;
    voices[steal].amp = 0;
    voices[steal].target_amp = vel;
    voices[steal].active = 1;
}
// ==============================
// NOTE OFF (smooth decay)
// ==============================

void note_off(uint8_t note)
{
    int i;

    for (i = 0; i < MAX_VOICES; i++)
    {
        if (voices[i].active && voices[i].note == note)
        {
            voices[i].target_amp = 0; // 🔥 smooth release
        }
    }
}

// ==============================
// AUDIO SAMPLE
// ==============================

float synth_sample()
{
    float out = 0.0f;
    int i;

    for (i = 0; i < MAX_VOICES; i++)
    {
        if (voices[i].active)
        {
            // 🔥 smooth amplitude (prevents clicks)
            voices[i].amp += 0.002f * (voices[i].target_amp - voices[i].amp);

            // 🔥 kill voice when faded out
            if (voices[i].amp < 0.0005f && voices[i].target_amp == 0)
            {
                voices[i].active = 0;
                continue;
            }

            float p = voices[i].phase;
            float a = voices[i].amp;

            // 🔥 richer harmonic (still lightweight)
            float sample =
                sinf(p) +
                0.5f * sinf(2.0f * p) +
                0.25f * sinf(3.0f * p);

            out += sample * a;

            // update phase
            voices[i].phase += TWO_PI * voices[i].freq / SAMPLE_RATE;
            if (voices[i].phase > TWO_PI)
                voices[i].phase -= TWO_PI;
        }
    }

    // 🔥 soft clip instead of hard clamp (sounds better)
    if (out > 1.0f)
        out = 1.0f;
    if (out < -1.0f)
        out = -1.0f;

    // 🔥 small noise (optional)
    float noise = ((float)rand() / RAND_MAX - 0.5f) * 0.003f;
    out += noise;

    return out;
}
