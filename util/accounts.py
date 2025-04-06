from util.response import Response
from util.auth import extract_credentials
from util.auth import validate_password
import uuid
import bcrypt
from util.database import chat_collection
from util.database import user_collection
import html
import secrets
import hashlib
from util.database import account_collection
import pyotp
from dotenv import dotenv_values
import requests
from util.database import oauth_collection

from util.multipart import parse_multipart
from datetime import datetime
from util.database import video_collection
import json

import ffmpeg

def registration(request, handler):

    ## You actually need to implement GET and POST into the server.py for all these. 
    # For GET you need to render the registration page just like for chat.
    # Then for POST you need to store the information in database.

    # When register, you should look for author to see if the user registering,
    # Sent messages before and thus has a session cookie. Then you can just update,
    # their username and password to their existing author entry in users database.
    # If not make a new entry with their username and password.

    res = Response()
    response_headers = {}

    credientials_array = extract_credentials(request)
    username = credientials_array[0]
    password = credientials_array[1]

    same_username_exists = list(account_collection.find({"username": username}))

    # !!!You also need to check if they used something else than alphanumerics for username.
    # If did need return error.

    # Usernames must be unique. So if a user registers with a username already in the database,
    # we return a 400.
    if (same_username_exists):
        res.set_status(400, "Bad Request")
        error_body = "400 Bad Request. This username already exists."
        response_headers["Content-Type"] = "text/plain; charset=UTF-8"
        response_headers["Content-Length"] = str(len(error_body))
        res.headers(response_headers)
        res.text(error_body)
        handler.request.sendall(res.to_data())
        return
    
    # username_is_alphanumeric = valid_username(username)

    # if (not username_is_alphanumeric):
    #     res.set_status(400, "Bad Request")
    #     error_body = "400 Bad Request. The username can only contain alphanumeric characters."
    #     response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    #     response_headers["Content-Length"] = str(len(error_body))
    #     res.headers(response_headers)
    #     res.text(error_body)
    #     handler.request.sendall(res.to_data())
    #     return

    is_valid_password = validate_password(password)

    # If not a valid password, we'll return a 400 and stop this function.
    if (not is_valid_password):
        res.set_status(400, "Bad Request")
        error_body = "400 Bad Request. We can't register you. Make sure you meet the password requirements."
        response_headers["Content-Type"] = "text/plain; charset=UTF-8"
        response_headers["Content-Length"] = str(len(error_body))
        res.headers(response_headers)
        res.text(error_body)
        handler.request.sendall(res.to_data())
        return
    
    user_id = str(uuid.uuid4())

    salted_hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Checks if there is a cookie named session in the request, then check if there is a match in the database.
    # If there is, it means the user has sent messages as guest before and does has an entry in the user database
    # with fields like author and session, so we will just update that entry with id, username, and the salted
    # and hashed password.

    # ?????When I register, I'm not receving a "session" cookie, even when I sent messages as guest before.

    print("\n\n" + str(request.cookies) + "\n\n")

    if "session" in request.cookies and user_collection.find_one({"session": request.cookies["session"]}) is not None:

        print("\n\nA\n\n")

        result = user_collection.find_one({"session": request.cookies["session"]})
        print("result is", result)
        author = result["author"]
        print("author is", author)
        account_collection.insert_one({"id": user_id, "username": html.escape(username), "password": salted_hashed_password})
        print("added account")
        chat_collection.update_many({"author": author}, {"$set": {"author": html.escape(username)}})
        print("updated author")
    else:

        print("\n\nB\n\n")

        account_collection.insert_one({"id": user_id, "username": html.escape(username), "password": salted_hashed_password})




    # # ??? Do I need to escape html on passwords too? 
    # if "session" in request.cookies and list(user_collection.find({"session": request.cookies["session"]})):
    #     result = list(user_collection.find({"session": request.cookies["session"]}))[0]

    #     # This is for the Authenticated Chat. We need to only update a user to a guest session if they haven't already
    #     # logged in before. Since in the first login, we will set author to username, we can use this to check
    #     # if the same user logged in under a different account before and therefore create a new entry for username
    #     # instead of an update.
    #     if result.get("author") != result.get("username"):
    #         user_collection.update_one({"session": request.cookies["session"]}, {"$set": {"id": user_id, "username": html.escape(username), "password": salted_hashed_password}})
    #     else:
    #         user_collection.insert_one({"id": user_id, "username": html.escape(username), "password": salted_hashed_password})
    # else:
    #     user_collection.insert_one({"id": user_id, "username": html.escape(username), "password": salted_hashed_password})

    # Also what if someone writes guest message, logs in, logs out, writes another guest message, then logs in under
    # different account? Which account should the second guest message belong to?

    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    response_message = "200 OK User Created"
    response_headers["Content-Length"] = str(len(response_message))

    res.headers(response_headers)
    res.text(response_message)
    handler.request.sendall(res.to_data())


def login(request, handler):

    print("\n\nThis is the login query stirng. Look for OTP.\n\n")
    print(str(request.body.decode()) + "\n\n")



    res = Response()
    response_headers = {}
    cookie_headers = {}

    print("\n\nA\n\n")

    credientials_array = extract_credentials(request)
    username = credientials_array[0]
    password = credientials_array[1]
    top = ""

    if len(credientials_array) >= 3:
        top = credientials_array[2]

    print(str(username))
    print(str(password))
    print(str(top))

    user_result = list(account_collection.find({"username": username}))

    print("\n\n" + str(user_result) + "\n\n")

    # Respond with 400 if username cannot be found in the users database.
    if (not user_result):
        print("\n\nB\n\n")


        res.set_status(400, "Bad Request")
        error_body = "400 Bad Request. This username does not exist."
        response_headers["Content-Type"] = "text/plain; charset=UTF-8"
        response_headers["Content-Length"] = str(len(error_body))
        res.headers(response_headers)
        res.text(error_body)
        handler.request.sendall(res.to_data())
        return
    
    # Respond with 400 if the password didn't match with the database.
    password_verified = bcrypt.checkpw(password.encode(), user_result[0]["password"].encode())


    print("\n\nC\n\n")


    if (not password_verified):

        print("\n\nD\n\n")


        res.set_status(400, "Bad Request")
        error_body = "400 Bad Request. Incorrect password."
        response_headers["Content-Type"] = "text/plain; charset=UTF-8"
        response_headers["Content-Length"] = str(len(error_body))
        res.headers(response_headers)
        res.text(error_body)
        handler.request.sendall(res.to_data())
        return
    

    # For HW2 AO1. Checks if a user hase OTP set up by checking if they have the secret field in 
    # the database. If they do and we didn't receive a TOP or it is incorrect, return 401.
    secret_result = user_result[0].get("secret")

    print("\n\nSecret\n")
    print(str(secret_result))

    print("\n\nTOP: " + top + "\n\n")
    
    if secret_result:
        correct_totp = pyotp.TOTP(secret_result).verify(top)

        print("correct_totp:" + str(correct_totp) + "\n\n")


        if (top == "") or (not correct_totp):
            res.set_status(401, "Unauthorized")
            error_body = "401 Unauthorized. One Time Password is Incorrect."
            response_headers["Content-Type"] = "text/plain; charset=UTF-8"
            response_headers["Content-Length"] = str(len(error_body))
            res.headers(response_headers)
            res.text(error_body)
            handler.request.sendall(res.to_data())
            return


    # Generates an auth token in string.
    auth_token = secrets.token_bytes(32).hex()

    hashed_auth_token = hashlib.sha256(auth_token.encode()).hexdigest()

    # !!!*** Assuming usernames are unqiue. Come back after Piazza answer. If usernames not unique maybe use the user id
    # or loop through all usernames found and check each password.
    auth_update = account_collection.update_one({"username": username}, {"$set": {"auth_token": hashed_auth_token}})

    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    response_message = "200 OK User Logged In"
    response_headers["Content-Length"] = str(len(response_message))

    cookie_auth_token = auth_token + "; Max-Age=10800; HttpOnly; Secure"
    cookie_headers["auth_token"] = cookie_auth_token

    res.cookies(cookie_headers)
    res.headers(response_headers)
    res.text(response_message)



    handler.request.sendall(res.to_data())


def logout(request, handler):
    res = Response()
    response_headers = {}
    cookie_headers = {}

    print("\n\nLogging Out Print Statement!")
    print(str(request.cookies) +"\n\n")

    if "auth_token" not in request.cookies:
        res.set_status(400, "Bad Request")
        error_body = "400 Bad Request. No auth_token."
        response_headers["Content-Type"] = "text/plain; charset=UTF-8"
        response_headers["Content-Length"] = str(len(error_body))
        res.headers(response_headers)
        res.text(error_body)
        handler.request.sendall(res.to_data())
        return

    hashed_auth_token = request.cookies["auth_token"]    # KeyError auth_token doesn't exist as a key.
    hashed_auth_token = hashlib.sha256(hashed_auth_token.encode()).hexdigest()

    auth_results = account_collection.find_one({"auth_token": hashed_auth_token})

    if not auth_results:
        res.set_status(400, "Bad Request")
        error_body = "400 Bad Request. Incorrect auth_token."
        response_headers["Content-Type"] = "text/plain; charset=UTF-8"
        response_headers["Content-Length"] = str(len(error_body))
        res.headers(response_headers)
        res.text(error_body)
        handler.request.sendall(res.to_data())
        return

    delete_auth = account_collection.update_one({"auth_token": hashed_auth_token}, {"$unset": {"auth_token": None}})

    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    response_message = "200 OK User Logged Out"
    response_headers["Content-Length"] = str(len(response_message))

    # Removing the auth_token cookie by setting max age to 0.
    cookie_headers["auth_token"] = "; Max-Age=0; HttpOnly; Secure"

    res.cookies(cookie_headers)
    res.headers(response_headers)
    res.text(response_message)
    handler.request.sendall(res.to_data())


# The username must be unique. So you need to go back and add code to make sure it is unique
# when they register. If not don't let them. Then finish the rest of the logout code.


    # ??? For removing auth tokens, what if there was a collision with the auth token? Should i delete one
    # or delete many?


def return_user_profile(request, handler):
    res = Response()
    response_headers = {}

    if "auth_token" in request.cookies:
        auth_token = request.cookies["auth_token"]
        hashed_auth_token = hashlib.sha256(auth_token.encode()).hexdigest()

        account_results = list(account_collection.find({"auth_token": hashed_auth_token}, {"_id": 0, "password": 0, "auth_token": 0}))
        
        if account_results:
            user_profile = account_results[0]
            res.json(user_profile)
            handler.request.sendall(res.to_data())
            return
        


    res.set_status(401, "Unauthorized")

    error_body = {}
    res.json(error_body)
    handler.request.sendall(res.to_data())


# TA said You need to just pull all entries in the database, and use Python .startswith() to check if what they 
# typed in starts with that. Then build you own list.

def user_search(request, handler):
    res = Response()
    json_body = {}

    # Get the query string from the body.
    query_string = request.path

    print("\n\n This is the request query string!! \n\n")
    print(str(query_string) + "\n\n")

    i = 0

    # Code to get the username from the query_string.
    username_start_index = 0

    question_mark_detected = False
    for character in query_string:
        if character == "?":
            question_mark_detected = True

        elif character == "=" and question_mark_detected:
            username_start_index = i + 1
            break

        i += 1

    username = query_string[username_start_index:]

    print("\n\n" + str(username) + "\n\n")


    user_match_list = []

    # This makes sure that when the user hasn't typed anything into the search yet, it doesn't return any names.
    if username == "":
        json_body["users"] = user_match_list
        res.json(json_body)
        handler.request.sendall(res.to_data())
        return


    user_results_list = list(account_collection.find({}, {"_id": 0, "password": 0, "auth_token": 0, "secret": 0}))
    for user in user_results_list:
        if user["username"].startswith(username):
            user_match_list.append(user)


    # print("\n\n" + str(user_results_list) + "\n\n")

    json_body["users"] = user_match_list
    res.json(json_body)


    print("\n\n" + str(json_body) + "\n\n")


    handler.request.sendall(res.to_data())


def update_profile(request, handler):
    res = Response()
    response_headers = {}

    credientials_array = extract_credentials(request)
    new_username = credientials_array[0]
    new_password = credientials_array[1]

    same_username_exists = list(account_collection.find({"username": new_username}))

    if "auth_token" in request.cookies:
        hashed_auth_token = request.cookies["auth_token"]
        hashed_auth_token = hashlib.sha256(hashed_auth_token.encode()).hexdigest()
        results = list(account_collection.find({"auth_token": hashed_auth_token}))
        if results:
            # If there is a same username, we can't allow the user to change to that username.
            # But also check if the user just inputted their username and a new password. Let
            # them do that.
            if same_username_exists and same_username_exists[0].get("auth_token") != results[0].get("auth_token"):
                res.set_status(400, "Bad Request")
                error_body = "400 Bad Request. This username already exists."
                response_headers["Content-Type"] = "text/plain; charset=UTF-8"
                response_headers["Content-Length"] = str(len(error_body))
                res.headers(response_headers)
                res.text(error_body)
                handler.request.sendall(res.to_data())
                return
            
            
            # username_is_alphanumeric = valid_username(new_username)

            # if (not username_is_alphanumeric):
            #     res.set_status(400, "Bad Request")
            #     error_body = "400 Bad Request. The username can only contain alphanumeric characters."
            #     response_headers["Content-Type"] = "text/plain; charset=UTF-8"
            #     response_headers["Content-Length"] = str(len(error_body))
            #     res.headers(response_headers)
            #     res.text(error_body)
            #     handler.request.sendall(res.to_data())
            #     return
    

            is_valid_password = validate_password(new_password)

            # If not a valid password, we'll return a 400 and stop this function.
            if (not is_valid_password and new_password != ""):
                res.set_status(400, "Bad Request")
                error_body = "400 Bad Request. Make sure you meet the password requirements."
                response_headers["Content-Type"] = "text/plain; charset=UTF-8"
                response_headers["Content-Length"] = str(len(error_body))
                res.headers(response_headers)
                res.text(error_body)
                handler.request.sendall(res.to_data())
                return
            
            if new_username:
                account_collection.update_one({"auth_token": hashed_auth_token}, {"$set": {"username": new_username}})

            if new_password:
                salted_hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                account_collection.update_one({"auth_token": hashed_auth_token}, {"$set": {"password": salted_hashed_password}})
                
            response_headers["Content-Type"] = "text/plain; charset=UTF-8"
            response_message = "200 OK Changed Username and/or Password."
            response_headers["Content-Length"] = str(len(response_message))

            res.headers(response_headers)
            res.text(response_message)
            handler.request.sendall(res.to_data())
            return


    res.set_status(400, "Bad Request")
    error_body = "400 Bad Request. You must be logged in to change your username/password."
    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    response_headers["Content-Length"] = str(len(error_body))
    res.headers(response_headers)
    res.text(error_body)
    handler.request.sendall(res.to_data())


    
# def valid_username(username):
#     for character in username:
#         if character >= "a" and character <= "z":
#             continue
#         elif character >= "A" and character <= "Z":
#             continue
#         elif character >= "0" and character <= "9":
#             continue
#         else:
#             return False
        
#     return True


def one_time_password(request, handler):
    res = Response()
    response_headers = {}
    
    secrets_key = pyotp.random_base32()

    if "auth_token" in request.cookies:
        hashed_auth_token = request.cookies["auth_token"]
        hashed_auth_token = hashlib.sha256(hashed_auth_token.encode()).hexdigest()
        results = list(account_collection.find({"auth_token": hashed_auth_token}))
        if results:
            account_collection.update_one({"auth_token": hashed_auth_token}, {"$set": {"secret": secrets_key}})

            json_body = {}
            json_body["secret"] = secrets_key
            res.json(json_body)
            handler.request.sendall(res.to_data())
            return


    res.set_status(401, "Unauthorized")
    error_body = "401 Unauthorized. You must be logged in to change to set up OTP."
    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    response_headers["Content-Length"] = str(len(error_body))
    res.headers(response_headers)
    res.text(error_body)
    handler.request.sendall(res.to_data())


def auth_github(request, handler):
    res = Response()
    response_headers = {}

    res.set_status(302, "Found")

    config = dotenv_values(".env")

    location_header = "https://github.com/login/oauth/authorize?"
    location_header += "client_id=" + config["GITHUB_CLIENT_ID"]
    location_header += "&redirect_uri="

    redirect_uri = config["REDIRECT_URI"]

    percent_encoding_mapping = {":": "%3A"}

    for character in redirect_uri:
        if character in percent_encoding_mapping:
            location_header += percent_encoding_mapping[character]
        else:
            location_header += character

    location_header += "&scope=user:email&scope=repo"

    response_headers["Location"] = location_header

    res.headers(response_headers)
    handler.request.sendall(res.to_data())


def auth_callback(request, handler):
    request_path = request.path

    i = 0
    for character in request_path:
        if character == "=":
            break

        i += 1

    auth_code = request_path[i+1:]

    config = dotenv_values(".env")

    client_id = config["GITHUB_CLIENT_ID"]
    client_secret = config["GITHUB_CLIENT_SECRET"]

    # redirect_uri = config["REDIRECT_URI"]
    # percent_encoded_redirect_uri = ""

    # percent_encoding_mapping = {":": "%3A"}

    # for character in redirect_uri:
    #     if character in percent_encoding_mapping:
    #         percent_encoded_redirect_uri += percent_encoding_mapping[character]
    #     else:
    #         percent_encoded_redirect_uri += character

    # print("\n\n" + str(percent_encoded_redirect_uri) + "\n\n")
    
    parameters = {"client_id": client_id, "client_secret": client_secret, "code": auth_code}
    # "redirect_uri": percent_encoded_redirect_uri

    url = "https://github.com/login/oauth/access_token"

    response = requests.post(url, data=parameters, headers={"Accept": "application/json"})

    if response.status_code != 200:
        return

    response_body = response.json()

    print("\n\nGitHub response print!!\n\n")
    print(str(response_body) + "\n\n")

    access_token = response_body.get("access_token")

    url = "https://api.github.com/user"

    authorization_data = "Bearer " + access_token

    access_data = {"Authorization": authorization_data}

    response = requests.get(url, headers=access_data)

    if response.status_code != 200:
        return
    
    response_body = response.json()

    print("\n\nUsername GitHub Response Print Statement!\n\n")
    print(str(response_body) + "\n\n")

    username = response_body.get("login")

    

    # Generates an auth token in string.
    auth_token = secrets.token_bytes(32).hex()

    hashed_auth_token = hashlib.sha256(auth_token.encode()).hexdigest()

    oauth_collection.insert_one({"username": username, "access_token": access_token, "auth_token": hashed_auth_token})

    res = Response()
    response_headers = {}
    cookie_headers = {}

    res.set_status(302, "Found")
    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    # response_message = "200 OK User Logged In"
    # response_headers["Content-Length"] = str(len(response_message))

    cookie_auth_token = auth_token + "; Max-Age=10800; HttpOnly; Secure"
    cookie_headers["auth_token"] = cookie_auth_token

    response_headers["Location"] = "/"

    res.cookies(cookie_headers)
    res.headers(response_headers)
    # res.text(response_message)

    handler.request.sendall(res.to_data())



# HW3 LO
def upload_avatar(request, handler):
    my_multipart = parse_multipart(request)

    # print("\n\nMultiPart Data\n\n")
    # print(my_multipart.boundary)
    # print(str(my_multipart.parts))

    content_disposition_header = my_multipart.parts[0].headers.get("Content-Disposition")

    print("\n\n Printing Content Disposition! \n\n")
    print(my_multipart.parts[0].headers)

    avatar_filename = ""
    if content_disposition_header:
            for filename in content_disposition_header.split(";"):
                if filename.lstrip().lower().startswith("filename="):
                    avatar_filename = filename.lstrip().removeprefix("filename=")
                    break

    # print(avatar_filename)

    image_type = ""
    # The filename is wrapped in double quotes. So you need to check for the image type plus a double quote.
    if avatar_filename.endswith(".jpg\""):
        image_type = ".jpg"

    elif avatar_filename.endswith(".png\""):
        image_type = ".png"

    elif avatar_filename.endswith(".gif\""):
        image_type = ".gif"



    avatar_image = my_multipart.parts[0].content

    server_avatar_filename = str(uuid.uuid4())

    imageURL = "/public/imgs/avatar-pics/" + server_avatar_filename + image_type

    with open("." + imageURL, "wb") as file:
        file.write(avatar_image)

    
    if "auth_token" in request.cookies:
        hashed_auth_token = request.cookies["auth_token"]
        hashed_auth_token = hashlib.sha256(hashed_auth_token.encode()).hexdigest()
        results = list(account_collection.find({"auth_token": hashed_auth_token}))
        if results:
            account_update = account_collection.update_one({"auth_token": hashed_auth_token}, {"$set": {"imageURL": imageURL}})
            username = results[0]["username"]
            chat_update = chat_collection.update_many({"author": username}, {"$set": {"imageURL": imageURL}})

            
    res = Response()
    response_headers = {}
    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    response_message = "200 OK Avatar Picture Uploaded"
    response_headers["Content-Length"] = str(len(response_message))

    res.headers(response_headers)
    res.text(response_message)
    handler.request.sendall(res.to_data())
    
            

def post_video(request, handler):
    # You'll need to escape the description.

    my_multipart = parse_multipart(request)

    # The video bytes should be at the third part of the multipart file. We'll
    # get its filename and confirm it is a .mp4
    content_disposition_header = my_multipart.parts[2].headers.get("Content-Disposition")

    video_filename = ""
    if content_disposition_header:
            for filename in content_disposition_header.split(";"):
                if filename.lstrip().lower().startswith("filename="):
                    video_filename = filename.lstrip().removeprefix("filename=")
                    break

    # print(avatar_filename)
    # print("\nPrinting Video Filename\n")
    # print(video_filename)

    
    # Our app only accepts .mp4 videos. If it is not we'll send a 400.
    if not video_filename.endswith(".mp4\""):
        res = Response()
        response_headers = {}
        res.set_status(400, "Bad Request")
        response_headers["Content-Type"] = "text/plain; charset=UTF-8"
        error_message = "400 Bad Request. We only accept .mp4 videos."
        response_headers["Content-Length"] = str(len(error_message))
        res.headers(response_headers)
        res.text(error_message)
        handler.request.sendall(res.to_data())
        return


    uploader_username = ""

    if "auth_token" in request.cookies:
        hashed_auth_token = request.cookies["auth_token"]
        hashed_auth_token = hashlib.sha256(hashed_auth_token.encode()).hexdigest()
        results = list(account_collection.find({"auth_token": hashed_auth_token}))
        if results:
            uploader_username = results[0]["username"]

    video_id = str(uuid.uuid4())

    video_title = html.escape(my_multipart.parts[0].content.decode())

    video_description = html.escape(my_multipart.parts[1].content.decode())

    # ??? Do I need to html escape the video bytes???

    video_data = my_multipart.parts[2].content

    video_file_name = str(uuid.uuid4())

    videoURL = "public/videos/" + video_file_name + ".mp4"

    with open("./" + videoURL, "wb") as file:
        file.write(video_data)

    created_at = str(datetime.now())

    database_entry = {}
    database_entry["author_id"] = uploader_username
    database_entry["title"] = video_title
    database_entry["description"] = video_description
    database_entry["video_path"] = videoURL
    database_entry["created_at"] = created_at
    database_entry["id"] = video_id

    


    # HW3 AO1 Code Begins
    audioURL = "public/videos/audio/" + video_file_name + ".mp3"
    video = ffmpeg.input(videoURL)
    video = ffmpeg.output(video, audioURL, format="mp3")
    ffmpeg.run(video, capture_stderr=True, capture_stdout=True, overwrite_output=True)

    video_duration = ffmpeg.probe(audioURL)
    video_duration = float(video_duration['format']['duration'])

    if (video_duration <= 60):
        api_url = "https://transcription-api.nico.engineer/transcribe"
        config = dotenv_values(".env")
        headers = {"Authorization": f"Bearer {config["SUBTITLE_API_TOKEN"]}"}
        with open(audioURL, 'rb') as audio:
            # You need to send a multipart request to Zaid's API. Read the requests library documentation on 
            # how to send a multipart request. Files are always multipart.
            mp3_file = {"file": (video_file_name + ".mp3", audio, 'audio/mpeg')}

            upload_response = requests.post(api_url, files=mp3_file, headers=headers)

            if upload_response.status_code == 200:
                transcription_id = upload_response.json()["unique_id"]
                database_entry["transcription_id"] = transcription_id
            else:
                print(upload_response.status_code + ": " + upload_response.text)                
    #

    # HW3 AO2 Code Begins
    five_thumbnails = []
    thumbnail_start_URL = "public/videos/thumbnails/" + video_file_name
    ffmpeg.input("./" + videoURL, ss=0).output("./" + thumbnail_start_URL + "_0" + ".jpg", vframes=1, update=1).run(overwrite_output=True)
    database_entry["thumbnailURL"] = thumbnail_start_URL + "_0" + ".jpg"
    five_thumbnails.append(thumbnail_start_URL + "_0" + ".jpg")

    frame = video_duration * 0.25
    ffmpeg.input("./" + videoURL, ss=frame).output("./" + thumbnail_start_URL + "_1" + ".jpg", vframes=1, update=1).run(overwrite_output=True)
    five_thumbnails.append(thumbnail_start_URL + "_1" + ".jpg")

    frame = video_duration * 0.50
    ffmpeg.input("./" + videoURL, ss=frame).output("./" + thumbnail_start_URL + "_2" + ".jpg", vframes=1, update=1).run(overwrite_output=True)
    five_thumbnails.append(thumbnail_start_URL + "_2" + ".jpg")

    frame = video_duration * 0.75
    ffmpeg.input("./" + videoURL, ss=frame).output("./" + thumbnail_start_URL + "_3" + ".jpg", vframes=1, update=1).run(overwrite_output=True)
    five_thumbnails.append(thumbnail_start_URL + "_3" + ".jpg")

    ffmpeg.input("./" + videoURL, ss=video_duration-1).output("./" + thumbnail_start_URL + "_4" + ".jpg", vframes=1, update=1).run(overwrite_output=True)
    five_thumbnails.append(thumbnail_start_URL + "_4" + ".jpg")

    database_entry["thumbnails"] = five_thumbnails
    #

    # # HW3 AO3 Code Begins
    # ffmpeg.input(videoURL).output("public/videos/" + video_file_name + "_720p.m3u8", f="hls", s="1280x720", hls_segment_filename="public/videos/" + video_file_name + "_720p_%05d.ts", hls_list_size=0).run()

    # # vcodec="libx264",
    # #     acodec="aac",
    # # hls_time=10,
    # #     hls_playlist_type="vod",
    # #     #hls_flags="independent_segments",

    # ffmpeg.input(video).output("public/videos/" + video_file_name + "_480p.m3u8", f="hls", s="854x480", hls_time=10, hls_segment_filename="public/videos/" + video_file_name + "_480p_%05d.ts", hls_list_size=0).run()

    # # vcodec="libx264",
    # #     acodec="aac",
    # # hls_playlist_type="vod",
    # #     #hls_flags="independent_segments",

    ffmpeg.input(videoURL).output("public/videos/" + video_file_name + "_480p.m3u8", f='hls', s="854x480", vcodec="libx264", acodec="aac", hls_time=10, hls_playlist_type="vod", hls_flags="independent_segments", hls_list_size=0).run()

    ffmpeg.input(videoURL).output("public/videos/" + video_file_name + "_144p.m3u8", f='hls', s="256x144", vcodec="libx264", acodec="aac", hls_time=10, hls_playlist_type="vod", hls_flags="independent_segments", hls_list_size=0).run()


    main_index_data = "#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=854x480\n" + video_file_name + "_480p.m3u8\n#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=256x144\n" + video_file_name + "_144p.m3u8"

    with open("./public/videos/" + video_file_name + ".m3u8", "w") as main_index:
        main_index.write(main_index_data)


    database_entry["hls_path"] = "public/videos/" + video_file_name + ".m3u8"

    # #
    




    video_collection.insert_one(database_entry)

    res = Response()
    json_body = {}
    json_body["id"] = video_id

    res.json(json_body)
    handler.request.sendall(res.to_data())


def get_all_videos(request, handler):
    res = Response()
    json_body = {}
    
    video_results = list(video_collection.find({}, {"_id": 0}))

    json_body["videos"] = video_results

    res.json(json_body)
    handler.request.sendall(res.to_data())


def get_single_video(request, handler):
    video_id = request.path.removeprefix("/api/videos/").strip()

    res = Response()
    json_body = {}

    video_result = video_collection.find_one({"id": video_id}, {"_id": 0})

    # find_one() will return None if it couldn't find one that matches the id. 
    # So we'll return a 404 Not Found.
    if not video_result:
        response_headers = {}
        res.set_status(404, "Not Found")
        response_headers["Content-Type"] = "text/plain; charset=UTF-8"
        error_message = "404 Not Found. The video you requested does not exist."
        response_headers["Content-Length"] = str(len(error_message))
        res.headers(response_headers)
        res.text(error_message)
        handler.request.sendall(res.to_data())
        return

    json_body["video"] = video_result

    res.json(json_body)
    handler.request.sendall(res.to_data())


# HW3 AO1 Code
def get_transcription(request, handler):

    video_id = request.path.removeprefix("/api/transcriptions/")
    
    transcription_id = video_collection.find_one({"id": video_id})["transcription_id"]

    api_url = "https://transcription-api.nico.engineer/transcriptions/" + transcription_id
    
    config = dotenv_values(".env")
    headers = {"Authorization": f"Bearer {config["SUBTITLE_API_TOKEN"]}"}
    
    vtt_response = requests.get(api_url, headers=headers)

    # print("\nThis is the API reponse body!")
    # print(str(vtt_response))
    # print()
    # print(str(vtt_response.content))
    
    res = Response()

    if vtt_response.status_code == 420:
        #print("\nGot back a 420.\n")

        res.set_status(400, "Bad Request")
        res.text("400 Bad Request. Transcription not ready or not found.")
        
    elif vtt_response.status_code == 200:
        #res.text(vtt_response.text) # remove

        vtt_data_url = vtt_response.content.decode()
        vtt_data_url = json.loads(vtt_data_url)
        vtt_data_url = vtt_data_url["s3_url"]
        vtt_data = requests.get(vtt_data_url)

        # print("\nTHis is the vtt file data\n")
        # print(vtt_data.content)
        # print()
        res.bytes(vtt_data.content)

    handler.request.sendall(res.to_data())

#

# ???When we send the GET to the API, do we get back a link to the VTT or just the VTT?
# Do we just do vtt_response.text and send it as a response? Or do we need to save
# it in public folder?

# ???What path should I put instead ffmpeg.probe()? It keeps saying can't find file.


# HW3 AO2 Code
def change_thumbnail(request, handler):
    video_id = request.path.removeprefix("/api/thumbnails/")

    thumbnail_data = json.loads(request.body)
    new_thumbnail = thumbnail_data["thumbnailURL"]

    update_result = video_collection.update_one({"id": video_id}, {"$set": {"thumbnailURL": new_thumbnail}})

    res = Response()
    my_json = {}
    my_json["message"] = "200 OK. Thumbnail is updated."
    res.json(my_json)

    handler.request.sendall(res.to_data())