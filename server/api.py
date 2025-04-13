from flask import Flask, request, jsonify

app = Flask(__name__)

stored_color = None


@app.route("/color", methods=["POST"])
def receive_color():
    global stored_color
    data = request.get_json()

    try:
        red = int(data.get("red"))
        green = int(data.get("green"))
        blue = int(data.get("blue"))
        assert 0 <= red <= 255
        assert 0 <= green <= 255
        assert 0 <= blue <= 255
    except (ValueError, TypeError, AssertionError):
        return jsonify({"error": "invalid rgb values"}), 400

    stored_color = {"red": red, "green": green, "blue": blue}
    return jsonify({"message": "color set"})


@app.route("/color", methods=["GET"])
def get_color():
    if stored_color is None:
        return jsonify({"message": "no color set yet"})
    return jsonify(stored_color)


def color_generator(is_environment_bright):
    if stored_color is None:
        return None
    if is_environment_bright:
        return Color(stored_color.red, stored_color.green, stored_color.blue)
    # return generate_dark_color()
    return Color(stored_color.red, stored_color.green, stored_color.blue)


def start_api():
    app.run(port=5000, debug=False, use_reloader=False)
