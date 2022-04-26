""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_dir_path [apod_date]

Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)

History:
  Date        Author    Description
  2022-03-11  J.Dalby   Initial creation
  2022-04-25  B.Cromwell Completed project
"""
from sys import argv, exit
from datetime import datetime, date
from hashlib import sha256
from os import path
import ctypes
import requests
import re
import sqlite3
def main():

    



    
    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)
    
    # Download today's APOD
    #thumb_url = apod_info_dict['thumbnail_url']
    try:
        image_url = apod_info_dict['thumbnail_url']
        image_msg = download_apod_image(image_url)
        image_sha256 = sha256(image_msg).hexdigest()
        image_size = round((len(requests.get(image_url).content)/1024), 2)# this will show size in KB, if you want in bytes just remove the /1024, and on line 184 the print says KB so careful of that
        image_path = get_image_path(image_url, image_dir_path, apod_info_dict['title'])#usually I use regex to get the name for the image out of the url
                                                                                   #however if it is a video then I use the title because the url
                                                                                   #is something like 'https://img.youtube.com/vi/m8qvOpcDt1o/0.jpg'
                                                                                   #so instead I jsut use the title for videos only, I still use regex 
                                                                                   #on the url for images 
                                                                                   #the same regex way could be used for videos as well but the name of 
                                                                                   #the example given (march 30 2022 btw) would then be 0.jpg because
                                                                                   #m8qvOpcDt1o/0.jpg isnt allowed as a file name, and I COULD make that whole 
                                                                                   #name work but I think the title is just a better way to go about the videos.
    except:
        image_url = apod_info_dict['url']
        image_msg = download_apod_image(image_url)
        image_sha256 = sha256(image_msg).hexdigest()
        image_size = round((len(requests.get(image_url).content)/1024), 2)
        image_path = get_image_path(image_url, image_dir_path, apod_info_dict['title'])

    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)

def get_image_dir_path():#complete
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):#if the path exists
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date():#complete
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    return apod_date

def get_image_path(image_url, dir_path, title):#complete
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
    title2 = ''
    try:
        image_name = re.search('https://apod.nasa.gov/apod/image/[0-9]+/(.*)', image_url).group(1)#getting the name of the image from the url
        return path.join(dir_path, image_name)
    except:
        
        for i in range(len(title)):#if no match that means it is a video, so the cool title thing I was on about earlier
            if title[i] == ' ':#if there's a space
                title2 = title2 + '_'#make it an underscore so it still works in the path
            elif title[i] == ':':#unsure if this actually ended up being a problem or not but frankly I just want to go get icecream and it works just fine anyway
                pass#getting rid of ':'s
            else:
                title2 = title2 + title[i]#making the path compatible title
        image_name = (title2 + ".jpg")
        return path.join(dir_path, image_name)

def get_apod_info(date):#complete
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """    
    key = 'api_key=wDf3aHj9BCIidi5sDNEUyKuT9GFCTgxYH69gjpsV'#user's key
    dateparam = 'date=' + date
    getstring = ('https://api.nasa.gov/planetary/apod?' + key + '&' + dateparam + '&thumbs=true')#for a while I had date in here instead of dateparam and couldn't figure out why I was having
                                                                                                #syntax errors
    response = requests.get(getstring)

    print('Getting NASA\'s APOD Information...', end = '')
    
    if response.status_code == 200:#if it works
     print('Success!')
     return response.json()
    else:
     print('Failed, Response code:',response.status_code)
     
def print_apod_info(image_url, image_path, image_size, image_sha256):#complete
    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """    
    print("the url of the image is", image_url)#all of this is straightforward
    print("The path the image was saved to is", image_path)
    print("The size of the image is ", image_size, "KB", sep = "")
    print("The SHA256 value of the image is", image_sha256)

def download_apod_image(image_url):#complete
    """
    Downloads an image from a specified URL.

    :param image_url: URL of image
    :returns: Response message that contains image data
    """
    response = requests.get(image_url)
    print('Downloading Image..', end = "")#if it works
    if response.status_code == 200:
     print('Success!')
     return response.content
    else:
     print('Failed, Response code:',response.status_code)
     return

def save_image_file(image_msg, image_path):#complete
    """
    Extracts an image file from an HTTP response message
    and saves the image file to disk.

    :param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    """

    print('Saving image path..', end = "")
    with open(image_path, 'wb') as file:
        file.write(image_msg)#saves the image to the specified path
        print('Success! Image saved to', image_path)


def create_image_db(db_path):#complete
    """
    Creates an image database if it doesn't already exist.
    Also creates a table if it doesn't already exist

    :param db_path: Path of .db file
    :returns: None
    """
    print('connection to the database:' , db_path)
    myConnection = sqlite3.connect(db_path)#makes the database if it doesn't already exist, also, makes a table if it doesn't already exist,
    myCursor = myConnection.cursor()#otherwise this entire blick of code does nothing

    createImageTable = """ CREATE TABLE IF NOT EXISTS images (
                            path text NOT NULL,
                            size integer NOT NULL,
                            hash text PRIMARY KEY
                        );"""

    myCursor.execute(createImageTable)

    myConnection.commit()
    myConnection.close()

def add_image_to_db(db_path, image_path, image_size, image_sha256):#complete
    """
    Adds a specified APOD image to the DB.

    :param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()
    print("Image was not already in database, adding now!")
    addImageQuery = """INSERT INTO images (
                        path,
                        size,
                        hash)
                        VALUES (?,?,?);"""

    newImage = (image_path, image_size, image_sha256)
    myCursor.execute(addImageQuery,newImage)#putting the info into the database
    

    myConnection.commit()
    myConnection.close()

def image_already_in_db(db_path, image_sha256):#complete
    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """ 
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()

    images = myCursor.execute("SELECT * FROM images;")
    for image in images:#will iterate through everything in the database and if the hash matches then the pic is already there
        if image[2] == image_sha256:
            print("Image was already in database")
            return True

    myConnection.commit()
    myConnection.close()

def set_desktop_background_image(image_path):#complete
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)#one sweet sweet line of code you taught us in the pokeimageviewer thing

main()#all done