import io, rembg, aiohttp

from PIL import Image

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/remove-background-url")
async def remove_background_url(image_url: str):
  async with aiohttp.ClientSession() as session:

    async with session.get(image_url) as response:

        image = await response.read()
  
        try:

          output = rembg.remove(image)

          output_image = Image.open(io.BytesIO(output))

          cropped_image = output_image.crop(output_image.getbbox())  # Crop to the maximum extent

          cropped_image_bytes = io.BytesIO()

          cropped_image.save(cropped_image_bytes, format='PNG')

          cropped_image_bytes.seek(0)

        except Exception as e:

          return {'error': str(e)}

        return {'result': cropped_image_bytes.getvalue()}
