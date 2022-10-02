import os.path
import os
import webbrowser
from io import BytesIO
from time import sleep

import numpy as np
import requests
from PIL import ImageOps
from PIL import Image
from fimage import *
from random import *
from fimage import Preset
import requests
import json
import tempfile
from pathlib import Path


# Constants
MAX_FILTERS = 4
MIN_BRIGHTNESS = 20
MAX_BRIGHTNESS = 45

MIN_CONTRAST = 20
MAX_CONTRAST = 45

MIN_SATURATION = 20
MAX_SATURATION = 45

MIN_FILTER_VALUE = 10
MAX_FILTER_VALUE = 100
# A list with all the filters that the program uses
available_filters = [
    "Sepia",
    "Vibrance",
    "Hue",
    "Gamma",
    "Clip",
    "Exposure",
]


# A custom created class inheriting FImage
class NFImage(FImage):
    def initialize(self, image):
        self.original_image = image
        self.image = ImageOps.exif_transpose(self.original_image)
        self.exif_data = self.image.getexif()
        self.image_array = ImageArray(np.array(self.image))


# This class is a preset which is applied once. Every time the values are randomized
class ApplyBCS(Preset):
    filters = [
        Brightness(randint(MIN_BRIGHTNESS, MAX_BRIGHTNESS)),
        Contrast(randint(MIN_CONTRAST, MAX_CONTRAST)),
        Saturation(randint(MIN_SATURATION, MAX_SATURATION)),
    ]


# Global variables
chosen_filters = []  # A list which is used to track the chosen filters
num_filters = 0   # The number of filters we have chosen
search = None  # The phrase that is used to search for an image


# A function that checks if a chosen filter already exists in the list of chosen filters
def check_repeating(chosen):
    for i in range(0, len(chosen_filters)):
        if chosen in chosen_filters:
            return True  # If the filter is contained in the list it returns True
    return False  # Else it returns False


# A function that chooses the filters
def chose_filters():
    global num_filters  # Uses the global variable

    for i in range(0, num_filters):
        chosen = available_filters[randint(0, len(available_filters) - 1)]  # The chosen variable is assigned a random filter string from the available filters list
        if check_repeating(chosen):  # Here it is checked if the filter already exists and if it does we go back 1 time and choose another one
            i -= 1
            continue
        print(f"Chosen {chosen}")
        chosen_filters.append(chosen)  # Finally the chosen filter is added to the list of chosen filters


# A function that converts the strings to filter functions
def convert_filter(image, filter_text):
    possibles = globals().copy()  # Here the global variables are copied to the possibles variable
    possibles.update(locals())  # Then the local variables are added
    _filter = possibles.get(filter_text)  # Finally the code tries to get a variable/function with the filter name

    if not _filter:  # Then it is checked  if the filter variable we got exists
        raise NotImplementedError(f"Function {filter_text} not implemented")

    # Here it is specifically checked if the filter name is colorize because colorize needs to have 4 args not like
    # the other filters which require only 1
    if filter_text == "Colorize":  # And then the filters are applied
        image.apply(Colorize(randint(0, 255), randint(0, 255), randint(0, 255), randint(MIN_FILTER_VALUE, MAX_FILTER_VALUE)))
    else:
        image.apply(_filter(randint(MIN_FILTER_VALUE, MAX_FILTER_VALUE)))

    print(f"Applied {filter_text}")


# A function which applies the filters
def apply_filters(image):

    global num_filters

    num_filters = randint(1, MAX_FILTERS)  # A random number of filters is chosen

    chose_filters()  # Then the function for choosing filters is called

    for i in chosen_filters:
        convert_filter(image, i)  # And then every filter is converted and applied


# A function that searches the nasa database for an image
def search_image():
    url = "https://images-api.nasa.gov/search?q="  # This is the start of the url
    global search
    search = input("Enter phrase: ")  # Here the user inputs the phrase for searching
    url = url + search  # Here the part of the url is joined with the phrase
    response = requests.get(url)  # Then a request is made to the nasa database
    json_dict = response.json()  # Here the response is converted to a json
    # Then it is checked if there are any contents
    if json_dict['collection']['items']:
        url = json_dict['collection']['items'][0]['links'][0]['href']  # Then the url of the image is taken
        response = requests.get(url)  # Then the url of the image is saved
        return Image.open(BytesIO(response.content))  # Finally the image is returned
    return None  # If there aren't contents, nothing is returned


# The main function
def main():
    searched = search_image()  # Here the image is searched for
    if not searched:  # If an image is not found the program closes
        print("Image not found!")
        sleep(3)  # The exiting is delayed so the user can se what happened
        exit(-1)

    image = NFImage.__new__(NFImage, searched)  # A new object of the NFImage is created so that the super __init__ method is not called
    image.initialize(searched)  # Then the initialize function of the class is called
    image.apply(ApplyBCS)  # The Preset is applied
    apply_filters(image)  # The filters are applied
    filename = f"{search}_art.jpg"  # A file name is made
    p = os.path.join(tempfile.gettempdir(), filename)  # The path to the temp directory is created
    image.save(p)  # And the image is saved to the temp directory of the user

    # Because the default image browser for Windows is Images a html_file is made and then opened in the browser
    html_template = f"""
    <!DOCTYPE html>
    <html>
    
       <head>
          <title>{search}_art</title>
       </head>
        
       <body>
          <img src = "{filename}" alt = "..." />
       </body>
        
    </html>
    """
    html_path = os.path.join(tempfile.gettempdir(), f"{search}_art.html")  # The path to the html file
    html_file = open(html_path, "w")  # Creating the file
    html_file.write(html_template)  # Writing to the file
    html_file.close()  # Closing the file
    html_uri = Path(html_path).as_uri()  # Getting the uri of the html file
    webbrowser.open(html_uri)  # And finally opening it in the browser


if __name__ == "__main__":
    main()
