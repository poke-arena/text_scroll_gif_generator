import io, aiohttp
#import tempfile

from PIL import Image, ImageDraw, ImageFont

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, StreamingResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.clientsession = None
app.cache = {}

async def img(url: str):
   if app.clientsession is None:
       app.clientsession = aiohttp.ClientSession()
   if url not in app.cache:
       async with app.clientsession.get(url) as resp_:
           resp = await resp_.read()
           app.cache[url] = Image.open(io.BytesIO(resp)).convert("RGBA")
   return app.cache[url]


@app.get("/text_to_gif")
async def text_to_gif(text: str, theme: str="dark", custom_text_color="#000000", body_color="#FFFFFF", custom_icon=None):
    if theme.lower() == "light":
        announce_bg = await img("https://cdn.discordapp.com/attachments/1043603765212749944/1128685099584589834/Untitled186_20230712192107.png")
        announce_mask = await img("https://cdn.discordapp.com/attachments/1043603765212749944/1128685099311955988/Untitled186_20230712192116.png")
        text_color = "#37383A"
    elif theme.lower() == "dark":
        announce_mask = await img("https://cdn.discordapp.com/attachments/1043603765212749944/1128681074743058452/Untitled186_20230712190358.png")
        announce_bg = await img("https://cdn.discordapp.com/attachments/1043603765212749944/1128681074290081882/Untitled186_20230712190350.png")
        text_color = "#FFFFFF"
    elif theme.lower() == "custom":
        announce_mask = await img("https://cdn.discordapp.com/attachments/1043603765212749944/1128681074743058452/Untitled186_20230712190358.png")
        announce_bg = await img("https://cdn.discordapp.com/attachments/1043603765212749944/1128681074290081882/Untitled186_20230712190350.png")
        new_mask = Image.new(announce_bg.size, body_color)
        text_color = custom_text_color
        announce_mask.paste(new_mask, mask=new_mask)
        announce_bg.paste(new_mask, mask=new_mask)
        if custom_icon is not None:
            icon = await img(custom_icon)
            height = announce_mask.size[1] - 4
            width = round(icon.size[0] * (height / icon.size[1]))
            if width > announce_mask.size[1]+2:
                height = announce_mask.size[1]+2
            icon = icon.resize((height, width))
            announce_mask.paste(icon, (10, 2), mask=icon)
            
    image_width, image_height = announce_bg.size
    scroll_speed = 2
    font = ImageFont.truetype("RobotoCondensed-Regular.ttf", 30)
    text_width, text_height = font.getsize(text)
    num_frames = max(50, int(text_width + image_width / scroll_speed))
    
    frames = []
    
    for frame in range(num_frames):
        image = announce_bg.copy()
        draw = ImageDraw.Draw(image)
        offset = image_width - (frame * scroll_speed)
        draw.text((offset, 3), text, font=font, fill=text_color)
        frames.append(image)
        image_mask = announce_mask.copy()
        image.paste(image_mask, (0,0), mask=image_mask.convert("RGBA"))
        if offset <= ((-1*text_width)-10):
            break
    scroll_gif = io.BytesIO()
    frames[0].save(scroll_gif, format="GIF", append_images=frames[1:], save_all=True, duration=38, loop=0)

    scroll_gif.seek(0)
    return StreamingResponse(scroll_gif, media_type="image/gif")
