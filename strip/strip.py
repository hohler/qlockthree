import abc
import time


class Color():
    r = None
    g = None
    b = None

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class Strip(ABC):
    strip = None
    led_count = 0

    color_white_bright = Color(200, 200, 200)
    color_white_dark = Color(30, 30, 30)
    color_green = Color(0, 128, 0)
    color_red = Color(139, 0, 0)

    leds_currently_on = []
    leds_to_turn_on = []

    is_environment_bright = True

    color_generator = None

    @abc.abstractmethod
    def __init__(self):
        pass

    def set_pixel(self, led_nr, color=None):
        if not color:
            color = self.get_color()
        self.leds_to_turn_on.append({"led_nr": led_nr, "r": color.r, "g": color.g, "b": color.b})

    def clear_all(self):
        for led in range(self.led_count):
            self.set_pixel(led, Color(0, 0, 0))

        self.strip.show()

    def test(self):
        self.clear_all()
        for led in range(self.strip.numPixels()):
            self.set_pixel(led, self.color_white_bright)
            self.show()
            time.sleep(0.1)

    def get_changes(self):
        return [x for x in self.leds_currently_on if x not in self.leds_to_turn_on], [x for x in self.leds_to_turn_on if x not in self.leds_currently_on]

    def get_color(self):
        if self.color_generator:
            generated_color = self.color_generator(self.is_environment_bright)
            if generated_color:
                return generated_color
        return self.color_white_bright if self.is_environment_bright else self.color_white_dark

    @abc.abstractmethod
    def show(self):
        pass
