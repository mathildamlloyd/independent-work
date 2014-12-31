import string
import enchant
from bs4 import BeautifulSoup

# filter out non-whitespace or non-letter characters
def filter_func(char):
    return char == "\n" or char == " " or char == "-" or char == "'" or 65 <= ord(char) <= 90 or 97 <= ord(char) <= 122

# parse the email specified by filepath and return list of proper words
def parse_email(filepath):
    text = ""
    with open(filepath) as openfileobject:
        for idx, line in enumerate(openfileobject):
            text += line
    text = filter(lambda x: x in string.printable, text)
    parsed_text = BeautifulSoup(text).get_text()
    parsed_text = filter(filter_func, parsed_text).lower()
    parsed_text = parsed_text.replace("\n", " ")
    parsed_text = parsed_text.split(" ")
    sanitized_text = []
    d = enchant.Dict("en_US")
    for index, word in enumerate(parsed_text):
        if word != '' and d.check(word):
            sanitized_text.append(word)
    return sanitized_text
