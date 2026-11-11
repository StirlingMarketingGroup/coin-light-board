// Coin light board firmware, ATtiny202.
//
// Press the button: red and blue alternate at 2 Hz.
// Press again: lights off. Lights also switch off on their own after
// AUTO_OFF_S, so a coin left on, or switched on in a shipping box, keeps its
// battery. Between runs the chip sleeps in power-down.
//
// Pins: PA1 -> red channel, PA2 -> blue channel, PA6 <- button to GND.

#ifndef F_CPU
#define F_CPU 3333333UL // factory default: 20 MHz oscillator / 6
#endif

#include <avr/interrupt.h>
#include <avr/io.h>
#include <avr/sleep.h>
#include <util/delay.h>

#define LED_RED PIN1_bm
#define LED_BLUE PIN2_bm
#define BUTTON PIN6_bm

#define HALF_CYCLE_MS 250 // red 250 ms, blue 250 ms = 2 cycles a second
#define AUTO_OFF_S 60
#define TICK_MS 10
#define DEBOUNCE_TICKS 3

#define TICKS_PER_HALF_CYCLE (HALF_CYCLE_MS / TICK_MS)
#define HALF_CYCLES_BEFORE_OFF (AUTO_OFF_S * 1000UL / HALF_CYCLE_MS)

// The button interrupt only wakes the chip. The main loop reads the pin.
ISR(PORTA_PORT_vect) { PORTA.INTFLAGS = BUTTON; }

static uint8_t pressed(void) { return !(VPORTA.IN & BUTTON); }

// Sleeps until the button goes from up to down. The chip sleeps while the
// button is held too, so a coin packed with its button pressed does not sit
// awake draining the lower cell.
static void sleep_until_press(void) {
	uint8_t seenUp = 0;

	for (;;) {
		_delay_ms(TICK_MS * DEBOUNCE_TICKS);
		if (!pressed()) {
			seenUp = 1;
		} else if (seenUp) {
			return;
		}
		sleep_mode();
	}
}

// Returns when the user presses again or the auto-off time runs out.
static void flash(void) {
	// The press that started the run is still held. A new press only counts
	// after the button has stayed up for DEBOUNCE_TICKS.
	uint8_t ticksReleased = 0;

	for (uint16_t halfCycle = 0; halfCycle < HALF_CYCLES_BEFORE_OFF; halfCycle++) {
		if (halfCycle & 1) {
			PORTA.OUTCLR = LED_RED;
			PORTA.OUTSET = LED_BLUE;
		} else {
			PORTA.OUTCLR = LED_BLUE;
			PORTA.OUTSET = LED_RED;
		}

		for (uint8_t tick = 0; tick < TICKS_PER_HALF_CYCLE; tick++) {
			_delay_ms(TICK_MS);
			if (!pressed()) {
				if (ticksReleased < DEBOUNCE_TICKS) {
					ticksReleased++;
				}
			} else if (ticksReleased >= DEBOUNCE_TICKS) {
				return;
			} else {
				ticksReleased = 0;
			}
		}
	}
}

int main(void) {
	PORTA.DIRSET = LED_RED | LED_BLUE;
	// Both-edges sensing wakes the chip from power-down on every pin.
	PORTA.PIN6CTRL = PORT_PULLUPEN_bm | PORT_ISC_BOTHEDGES_gc;
	// Unconnected pins float. Switching their input buffers off stops that
	// from drawing current in sleep.
	PORTA.PIN3CTRL = PORT_ISC_INPUT_DISABLE_gc;
	PORTA.PIN7CTRL = PORT_ISC_INPUT_DISABLE_gc;

	set_sleep_mode(SLEEP_MODE_PWR_DOWN);
	sei();

	for (;;) {
		sleep_until_press();
		flash();
		PORTA.OUTCLR = LED_RED | LED_BLUE;
	}
}
