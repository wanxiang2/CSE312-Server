
def extract_credentials(request):
    # Get the query string from the body. Then decode it.
    query_string = request.body.decode()

    i = 0

    # Code to get the username from the query_string.
    username_start_index = 0
    username_end_index = 0

    for character in query_string:
        if character == "=":
            username_start_index = i + 1
        elif character == "&":
            username_end_index = i   # This is actually index of &, but we're leaving it like this since Python slicing doesn't including the ending index.
            i += 1
            break

        i += 1

    username = query_string[username_start_index:username_end_index]

    # Code to get the password from the query_string.
    password_start_index = 0
    password_end_index = len(query_string)
    while i < len(query_string):
        if query_string[i] == "=":
            password_start_index = i + 1
        elif query_string[i] == "&":
            password_end_index = i
            i += 1
            break
        
        i += 1

    password = query_string[password_start_index:password_end_index]


    # If the query string has a one-time password, we extract that into top.
    top = ""

    if i < len(query_string):
        top_start_index = 0
        while i < len(query_string):
            if query_string[i] == "=":
                top_start_index = i + 1
                break

            i += 1

        top = query_string[top_start_index:]


    # Decode the percent encoding in the password.
    decoded_password = ""
    i = 0

    while i < len(password):
        if password[i] == "%":
            hex_encoding = password[i+1:i+3]
            decoded_hex = chr(int(hex_encoding, 16)) # We have to decode the special chars, so we convert it from hex to base 10 int, then convert to the character.
            decoded_password = decoded_password + decoded_hex
            i += 3
        else:
            decoded_password = decoded_password + password[i]
            i += 1


    res = []
    res.append(username)
    res.append(decoded_password)

    if top:
        res.append(top)

    return res


def validate_password(password):
    password_length = False
    contains_lowercase = False
    contains_uppercase = False
    contains_number = False
    contains_special = False

    no_invalid = True

    if len(password) >= 8:
        password_length = True


    special_characters = {"!", "@", "#", "$", "%", "^", "&", "(", ")", "-", "_", "="}

    for character in password:
        if character >= "a" and character <= "z":
            contains_lowercase = True
            
        elif character >= "A" and character <= "Z":
            contains_uppercase = True
        
        elif character >= "0" and character <= "9":
            contains_number = True
            
        elif character in special_characters:
            contains_special = True

        else:
            no_invalid = False

    
    if (password_length and contains_lowercase and contains_uppercase and contains_number and contains_special and no_invalid):
        return True

    return False

    

    