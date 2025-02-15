from pymongo import MongoClient
from util.response import Response
import uuid
from util.database import chat_collection
from util.database import user_collection
import json
import html
import requests

def create_message(request, handler):
    res = Response()
    response_headers = {}
    response_body = "Message Sent"

    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    response_headers["Content-Length"] = str(len(response_body))

    res.headers(response_headers)

    cookie_headers = {}

    message_id = str(uuid.uuid4())
    session = str(uuid.uuid4())
    author = str(uuid.uuid4())

    #print("\n\nIn Create Message\n\n")
    #print("\n\n" + str(request.cookies) + "\n\n")

    if "session" in request.cookies:
        #print("\n\nA\n\n")
        results = list(user_collection.find({"session": request.cookies["session"]}))
        
        if results:
            #print("\n\nB\n\n")
            author = results[0]["author"]
            session = results[0]["session"]
        else:
            user_entry = {}
            user_entry["author"] = author
            user_entry["session"] = session

            # Generates a user picture for first time messages and saves the imageURL in 
            # the users collection.
            imageURL = dicebear(author)
            user_entry["imageURL"] = imageURL

            user_collection.insert_one(user_entry)
        
            session = session + "; Max-Age=10800; HttpOnly"
            cookie_headers["session"] = session
            session = session.rstrip("; Max-Age=10800; HttpOnly")

    else:
        #print("\n\nC\n\n")
        user_entry = {}
        user_entry["author"] = author
        user_entry["session"] = session

        # Generates a user picture for first time messages and saves the imageURL in 
        # the users collection.
        imageURL = dicebear(author)
        user_entry["imageURL"] = imageURL
        
        user_collection.insert_one(user_entry)

        session = session + "; Max-Age=10800; HttpOnly"
        cookie_headers["session"] = session
        session = session.rstrip("; Max-Age=10800; HttpOnly")

        

    #cookie_headers["id"] = message_id

    res.cookies(cookie_headers)

    res.text(response_body)

    request_body = json.loads(request.body)
    user_message = request_body["content"]

    database_entry = {}
    database_entry["author"] = author
    database_entry["id"] = message_id
    database_entry["content"] = html.escape(user_message)
    database_entry["updated"] = False
    database_entry["reactions"] = {}
    
    # This is to add in a "nickname" field to the message if the nickname() function was called
    # and thus that author's user collection entry has a nickname field.
    results = list(user_collection.find({"session": session}))
    if "nickname" in results[0]:
        message_nickname = results[0]["nickname"]
        database_entry["nickname"] = message_nickname


    # Adds the Dicebear profile pic to each message using the saved imageURL in the users collection.
    message_imageURL = results[0]["imageURL"]
    database_entry["imageURL"] = message_imageURL


    chat_collection.insert_one(database_entry)

    handler.request.sendall(res.to_data())


# Handles generating a unique user picture by using the Dicebear api and Python requests library.
def dicebear(author):
    url = "https://api.dicebear.com/9.x/pixel-art/svg?seed=" + author

    dicebear_response = requests.get(url)

    imageURL = "/public/imgs/profile-pics/" + author + ".svg"

    with open("." + imageURL, "wb") as file:
        file.write(dicebear_response.content)

    return imageURL




def get_message(request, handler):
    res = Response()
    response_headers = {}

    results = list(chat_collection.find({}, {"_id": 0, "session": 0}))

    json_body = {}
    json_body["messages"] = results
    #json_body = json.dumps(json_body, default=str)


    #print(list(chat_collection.find({})))
    #print("\n\n" + json_body + "\n\n")


    res.json(json_body)

    json_body = json.dumps(json_body, default=str)
    body_length = str(len(json_body.encode()))
    response_headers["Content-Length"] = body_length

    res.headers(response_headers)

    handler.request.sendall(res.to_data())



def update_message(request, handler):
    res = Response()
    response_headers = {}

    request_body = json.loads(request.body.decode())
    updated_message = request_body["content"]

    message_id = request.path.lstrip("/api/chats/")
    if "session" in request.cookies:
        user_results = list(user_collection.find({"session": request.cookies["session"]}))
        author_of_session = None
        if user_results:
            author_of_session = user_results[0]["author"]
        message_results = list(chat_collection.find({"id": message_id, "author": author_of_session}))
        if user_results and message_results:
            update = chat_collection.update_one({"id": message_id, "author": author_of_session}, {"$set": {"content": updated_message, "updated": True}})

            response_headers["Content-Type"] = "text/plain; charset=UTF-8"

            response_message = "200 OK Updated"
            response_headers["Content-Length"] = str(len(response_message))

            res.headers(response_headers)
            res.text(response_message)
            handler.request.sendall(res.to_data())
            return
        
        # Look over this error handling part again
    res.set_status(403, "Forbidden")
    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    error_message = "403 Forbidden"
    response_headers["Content-Length"] = str(len(error_message))
    res.headers(response_headers)
    res.text(error_message)
    handler.request.sendall(res.to_data())


def delete_message(request, handler):
    res = Response()
    response_headers = {}

    message_id = request.path.lstrip("/api/chats/")
    if "session" in request.cookies:
        user_results = list(user_collection.find({"session": request.cookies["session"]}))
        author_of_session = None
        if user_results:
            author_of_session = user_results[0]["author"]
        message_results = list(chat_collection.find({"id": message_id, "author": author_of_session}))
        if user_results and message_results:
            delete = chat_collection.delete_one({"id": message_id, "author": author_of_session})

            response_headers["Content-Type"] = "text/plain; charset=UTF-8"

            response_message = "200 OK Deleted"
            response_headers["Content-Length"] = str(len(response_message))

            res.headers(response_headers)
            res.text(response_message)
            handler.request.sendall(res.to_data())
            return
        
    res.set_status(403, "Forbidden")
    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    error_message = "403 Forbidden"
    response_headers["Content-Length"] = str(len(error_message))
    res.headers(response_headers)
    res.text(error_message)
    handler.request.sendall(res.to_data())



def add_emoji(request, handler):
    res = Response()
    response_headers = {}

    cookie_headers = {}

    message_id = request.path.lstrip("/api/reaction/")

    emoji_author = ""

    if "session" not in request.cookies:
        session = str(uuid.uuid4())
        author = str(uuid.uuid4())

        user_entry = {}
        user_entry["author"] = author
        user_entry["session"] = session
        user_collection.insert_one(user_entry)

        session = session + "; Max-Age=10800"
        cookie_headers["session"] = session
        res.cookies(cookie_headers)

        emoji_author = author
    else:
        results = list(user_collection.find({"session": request.cookies["session"]}))
        
        if results:
            emoji_author = results[0]["author"]
        else:
            session = str(uuid.uuid4())
            author = str(uuid.uuid4())

            user_entry = {}
            user_entry["author"] = author
            user_entry["session"] = session
            user_collection.insert_one(user_entry)

            session = session + "; Max-Age=10800"
            cookie_headers["session"] = session
            res.cookies(cookie_headers)

            emoji_author = author

        

    request_body = json.loads(request.body)
    user_emoji = request_body["emoji"]

    print("\n\nPrinting message to add emoji!!!\n\n")
    print(str(list(chat_collection.find({"id": message_id}))) + "\n")

    message_to_add_emoji = list(chat_collection.find({"id": message_id}))[0]

    current_reactions = message_to_add_emoji["reactions"]
    if user_emoji in current_reactions:
        if emoji_author not in current_reactions[user_emoji]:
            current_reactions[user_emoji].append(emoji_author)
        else:
            res.set_status(403, "Forbidden")
            response_headers["Content-Type"] = "text/plain; charset=UTF-8"
            error_message = "403 Forbidden"
            response_headers["Content-Length"] = str(len(error_message))
            res.headers(response_headers)
            res.text(error_message)
            handler.request.sendall(res.to_data())
            return
    else:
        current_reactions[user_emoji] = [emoji_author]

    chat_collection.update_one({"id": message_id}, {"$set": {"reactions": current_reactions}})

    response_headers["Content-Type"] = "text/plain; charset=UTF-8"

    response_message = "200 OK Updated"
    response_headers["Content-Length"] = str(len(response_message))

    res.headers(response_headers)
    res.text(response_message)
    handler.request.sendall(res.to_data())
    

def remove_emoji(request, handler):
    res = Response()
    response_headers = {}

    message_id = request.path.lstrip("/api/reaction/")

    if "session" in request.cookies:
        print("\n\nA\n\n")

        user_results = list(user_collection.find({"session": request.cookies["session"]}))
        emoji_author = ""

        if user_results:
            emoji_author = user_results[0]["author"]


        message_to_delete_emoji = list(chat_collection.find({"id": message_id}))
        if user_results and message_to_delete_emoji:
            print("\n\nB\n\n")


            print("\n\n" + str(message_to_delete_emoji) + "\n\n")
            current_reactions = message_to_delete_emoji[0]["reactions"]

            request_body = json.loads(request.body)
            user_emoji = request_body["emoji"]

            if user_emoji in current_reactions:

                print("\n\nC\n\n")

                if emoji_author in current_reactions[user_emoji]:

                    print("\n\nD\n\n")


                    current_reactions[user_emoji].remove(emoji_author)

                    if len(current_reactions[user_emoji]) == 0:
                        del current_reactions[user_emoji]

                    delete_emoji = chat_collection.update_one({"id": message_id}, {"$set": {"reactions": current_reactions}})

                    response_headers["Content-Type"] = "text/plain; charset=UTF-8"

                    response_message = "200 OK Deleted"
                    response_headers["Content-Length"] = str(len(response_message))

                    res.headers(response_headers)
                    res.text(response_message)
                    handler.request.sendall(res.to_data())
                    return
                
    res.set_status(403, "Forbidden")
    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    error_message = "403 Forbidden"
    response_headers["Content-Length"] = str(len(error_message))
    res.headers(response_headers)
    res.text(error_message)
    handler.request.sendall(res.to_data())


def nickname(request, handler):
    res = Response()
    response_headers = {}

    if "session" in request.cookies:
        results = list(user_collection.find({"session": request.cookies["session"]}))
        author = ""

        if results:
            author = results[0]["author"]

            request_body = json.loads(request.body)
            user_nickname = request_body["nickname"]
        
            user_update_nickname = user_collection.update_one({"author": author}, {"$set": {"nickname": user_nickname}})
            update_nickname = chat_collection.update_many({"author": author}, {"$set": {"nickname": user_nickname}})

            response_headers["Content-Type"] = "text/plain; charset=UTF-8"

            response_message = "200 OK Updated"
            response_headers["Content-Length"] = str(len(response_message))

            res.headers(response_headers)
            res.text(response_message)
            handler.request.sendall(res.to_data())
            return


    res.set_status(403, "Forbidden")
    response_headers["Content-Type"] = "text/plain; charset=UTF-8"
    error_message = "403 Forbidden"
    response_headers["Content-Length"] = str(len(error_message))
    res.headers(response_headers)
    res.text(error_message)
    handler.request.sendall(res.to_data())

