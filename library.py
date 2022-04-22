import requests
import ctypes
def download_image_from_url(url, save_path):

    """
    Downloads an image from nasa'a APOD

    :param url: the url of the image being downloaded
    :param save_path: the path to the directory and file to which the picture will be saved  
    """


    response = requests.get(url)
    if response.status_code == 200:
     with open(save_path, 'wb') as file:
            file.write(response.content)
     print('Success!')
    else:
     print('Fialed, Response code:',response.status_code)
     return

    
def set_desktop_background_image(image):

    """
    Sets an image as the user's desktop background

    :param image: the image taht the background will be
    """
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image, 0)