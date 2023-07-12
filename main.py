import io, aiohttp

from PIL import Image, ImageDraw, ImageFont

from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse

app = FastAPI()

session = aiohttp.ClientSession()

async def img(url):
   async with session.get(f"https://cdn.discordapp.com/attachments/{url}") as resp_:
       resp = await resp_.read()
       return Image.open(BytesIO(resp))


@app.get("/text_to_gif")
async def text_to_gif(text: str, theme: str="dark"):
    if theme.lower() == "light":
        announce_bg = await img("1043603765212749944/1128685099584589834/Untitled186_20230712192107.png")
        announce_mask = await img("1043603765212749944/1128685099311955988/Untitled186_20230712192116.png")
    else:
        announce_mask = await img("1043603765212749944/1128681074743058452/Untitled186_20230712190358.png")
        announce_bg = await img("1043603765212749944/1128681074290081882/Untitled186_20230712190350.png")
    image_width = ann_bg.size[0]
    scroll_speed = 2
    font = ImageFont.truetype("RobotoCondensed-Regular.ttf", 30)
    text_width, text_height = font.getsize(text)
    image_height = ann_bg.size[1]
    num_frames = max(50, int(text_width + image_width / scroll_speed))
    frames = []
    for frame in range(num_frames):
        image = ann_bg.copy()
        draw = ImageDraw.Draw(image)
        offset = image_width - (frame * scroll_speed)
        draw.text((offset, 3), text, font=font, fill="#FFFFFF")
        frames.append(image)
        if offset <= (-1*text_width):
            break
        agf = ann_mask.copy()
        image.paste(agf, (0,0), mask=agf.convert("RGBA"))
    scroll_gif = io.BytesIO()
    frames[0].save(scroll_gif, format="GIF", append_images=frames[1:], save_all=True, duration=38, loop=0)

    scroll_gif.seek(0)
    return StreamingResponse(scroll_gif, media_type="image/gif")  
    #return {'result': scroll_gif.getvalue()}
    
