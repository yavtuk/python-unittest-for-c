#include "gpio/gpio.h"
#include "gpio/gpio_lib.h"

int read_gpio(int number) {
    int retval;

	switch (number) {
	    case 0:
			retval = read_gpio0();
            break;
		case 1:
			retval = read_gpio1();
            break;
		default:
			retval = -1;
            break;
	}

    return retval;
}
