#include "synth.h"
#include <math.h>

#define MAX_VOICES 8
#define SAMPLE_RATE 20000.0f
#define TWO_PI 6.28318530718f

typedef struct
{
    float freq;
    float phase;
    float amp;
    uint8_t active;
} Voice;

static Voice voices[MAX_VOICES];

void synth_init()
{
    for (int i = 0; i < MAX_VOICES; i++)
        voices[i].active = 0;
}

static float midi_to_freq(uint8_t note)
{
    return 440.0f * powf(2.0f, (note - 69) / 12.0f);
}

void note_on(uint8_t note, float velocity)
{
    float f = midi_to_freq(note);

    for (int i = 0; i < MAX_VOICES; i++)
    {
        if (!voices[i].active)
        {
            voices[i].freq = f;
            voices[i].phase = 0;
            voices[i].amp = velocity;
            voices[i].active = 1;
            return;
        }
    }
}

void note_off(uint8_t note)
{
    float f = midi_to_freq(note);

    for (int i = 0; i < MAX_VOICES; i++)
    {
        if (voices[i].active && fabsf(voices[i].freq - f) < 1.0f)
            voices[i].active = 0;
    }
}

float synth_sample()
{
    float out = 0;
    int count = 0;

    for (int i = 0; i < MAX_VOICES; i++)
    {
        if (voices[i].active)
        {
            out += sinf(voices[i].phase) * voices[i].amp;

            voices[i].phase += TWO_PI * voices[i].freq / SAMPLE_RATE;
            if (voices[i].phase > TWO_PI)
                voices[i].phase -= TWO_PI;

            count++;
        }
    }

    if (count > 0)
        out /= count;

    return out;
}
