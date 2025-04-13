from flask import Flask, request, jsonify, __version__
from strip import Color, Strip

app = Flask(__name__)

stored_color = None
stored_brightness = 100
strip = None

@app.route("/color", methods=["POST"])
def receive_color():
    global stored_color, stored_brightness
    data = request.get_json()

    try:
        red = int(data.get("red"))
        green = int(data.get("green"))
        blue = int(data.get("blue"))
        brightness = int(data.get("brightness", 100))
        assert 0 <= red <= 255
        assert 0 <= green <= 255
        assert 0 <= blue <= 255
        assert 0 <= brightness <= 100
    except (ValueError, TypeError, AssertionError):
        return jsonify({"error": "invalid rgb values"}), 400

    stored_color = Color(red, green, blue)
    stored_brightness = brightness
    strip.set_color_changed()
    return jsonify({"message": "color set"})


@app.route("/color", methods=["GET"])
def get_color():
    if stored_color is None:
        dict = Color(0, 0, 0).serialize()
        dict["brightness"] = stored_brightness
        return jsonify(dict)

    dict = stored_color.serialize()
    dict["brightness"] = stored_brightness

    return jsonify(dict)


@app.route("/color", methods=["DELETE"])
def delete_color():
    global stored_color, stored_brightness
    stored_color = None
    stored_brightness = 100
    strip.set_color_changed()
    return jsonify({"message": "color unset"})


def color_generator(is_environment_bright):
    if stored_color is None:
        return None
    if is_environment_bright:
        # with adjusted color by brightness
        return Color(
            int(stored_color.r * stored_brightness / 100),
            int(stored_color.g * stored_brightness / 100),
            int(stored_color.b * stored_brightness / 100)
        )

    return darken_color(stored_color)


def darken_color(color):
    darkness_factor = 6.66 * (1+(100-stored_brightness)/100)
    return Color(int(color.r / darkness_factor), int(color.g / darkness_factor), int(color.b / darkness_factor))


def start_api(strip_instance):
    global strip
    strip = strip_instance
    print("Flask version: ", __version__)
    app.run("0.0.0.0", 5000, False)
