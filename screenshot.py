import openai
import json
import os
import time
from selenium import webdriver
from PIL import Image, ImageDraw, ImageOps
from dotenv import load_dotenv

load_dotenv()

def screenshot_and_edit(url):
    # Function to take a screenshot, round the corners, and add a background
    driver = webdriver.Chrome()  # or webdriver.Chrome()
    driver.get(url)

    # Get the dimensions of the webpage
    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    rectangles = []

    # Split the screenshot into rectangles if it's too big
    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width

            rectangles.append((ii, i, top_width,top_height))

            ii = ii + viewport_width

        i = i + viewport_height

    stitched_image = Image.new('RGB', (total_width, total_height))
    previous = None
    part = 0

    for rectangle in rectangles:
        if not previous is None:
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            time.sleep(0.2)

        file_name = "part_{0}.png".format(part)
        driver.get_screenshot_as_file(file_name)
        screenshot = Image.open(file_name)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])

        stitched_image.paste(screenshot, offset)

        del screenshot
        os.remove(file_name)
        part = part + 1
        previous = rectangle

    stitched_image.save('screenshot.png')
    driver.quit()

    img = Image.open('screenshot.png')
    radius = 12  # radius of the rounded corners
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new('L', img.size, 255)
    w, h = img.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))  # top left
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))  # bottom left
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))  # top right
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))  # bottom right
    img.putalpha(alpha)
    img_with_bg = Image.new('RGB', img.size, '#FF5533')
    img_with_bg.paste(img, mask=img.split()[3])  # 3 is the alpha channel

        # Add a border
    border_color = '#FF5533'
    border_width = 100
    img_with_border = ImageOps.expand(img_with_bg, border=border_width, fill=border_color)
    img_with_border.save('screenshot.png', 'PNG')


    return "Screenshot taken and edited."

openai.api_key = os.getenv("OPENAI_API_KEY")

def run_conversation(question):
    # Step 1 Use function calling capacity to get the function and arguments to call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "user", "content": question}],
        functions=[
            {
                "name": "download_images",
                "description": "Download images from a webpage",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the webpage to download images from"
                        }
                    },
                    "required": ["url"],
                },
            }
        ],
        function_call="auto",
    )

    message = response["choices"][0]["message"]

    # Step 2, check if the model wants to call a function
    if message.get("function_call"):
        function_name = message["function_call"]["name"]

        # Step 3, call the function
        function_response = screenshot_and_edit(
            url=json.loads(message["function_call"]["arguments"]).get("url")
        )

        # Step 4, send model the info on the function call and function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "user", "content": question},
                message,
                {
                    "role": "system",
                    "content": f'{{"function_response": "{function_response}", "function_name": "{function_name}"}}'
                }
            ],
        )
        return second_response["choices"][0]["message"]["content"]

if __name__ == "__main__":      
    print(run_conversation("Take a screenshot of https://figma.com"))
