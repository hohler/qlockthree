from fastapi import FastAPI
from pydantic import BaseModel, conint
from typing import Optional
from strip import Color
import uvicorn

app = FastAPI()


class RGBColor(BaseModel):
    red: conint(ge=0, le=255)
    green: conint(ge=0, le=255)
    blue: conint(ge=0, le=255)


stored_color: Optional[RGBColor] = None


@app.post("/color")
def set_color(color: RGBColor):
    global stored_color
    stored_color = color
    return {"success": True}


def color_generator(is_environment_bright):
    if stored_color is None:
        return None
    if is_environment_bright:
        return Color(stored_color.red, stored_color.green, stored_color.blue)
    # return generate_dark_color()
    return Color(stored_color.red, stored_color.green, stored_color.blue)


def start_api():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

