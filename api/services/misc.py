def process_request(text):
    words = text.split("*")
    return words, len(words)
