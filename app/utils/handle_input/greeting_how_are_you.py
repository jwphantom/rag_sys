import re

salutations = [
    "bonjour",
    "bonsoir",
    "salut",
    "coucou",
    "hello",
    "hi",
    "hey",
    "bienvenue",
    "yo",
    "salutations",
    "bonne journée",
    "bonne soirée",
    "bon matin",
    "bon après-midi",
]

# List of regex patterns for greetings
greeting_patterns = [
    r"\bbonjour\b",
    r"\bbonsoir\b",
    r"\bsalut\b",
    r"\bcoucou\b",
    r"\bhello\b",
    r"\bhi\b",
    r"\bhey\b",
    r"\bbienvenue\b",
    r"\byo\b",
    r"\bsalutations\b",
    r"\bbonne journée\b",
    r"\bbonne soirée\b",
    r"\bbon matin\b",
    r"\bbon après-midi\b",
]

how_are_you_patterns = [
    r"\bcomment ça va\b",
    r"\bça va\b",
    r"\bcomment allez[\- ]?vous\b",
    r"\bça roule\b",
    r"\bcomment vas[\- ]?tu\b",
    r"\bj'espère que tu vas bien\b",
    r"\bj'espère que vous allez bien\b",
]


def is_greeting(text):
    text = text.lower()
    for word in salutations:
        if word in text:
            return True
    return False


def is_greeting_with_regex(text):
    text = text.lower()
    for pattern in greeting_patterns:
        if re.search(pattern, text):
            return True
    return False


def is_greeting_combined(text):
    return is_greeting(text) or is_greeting_with_regex(text)


def is_how_are_you(text):
    text = text.lower()
    for pattern in how_are_you_patterns:
        if re.search(pattern, text):
            return True
    return False


def handle_greeting_and_how_are_you(text):
    text_lower = text.lower()
    greeting = any(re.search(pattern, text_lower) for pattern in greeting_patterns)
    how_are_you = any(
        re.search(pattern, text_lower) for pattern in how_are_you_patterns
    )

    if greeting and how_are_you:
        return "Salut, je vais bien et vous ?"
    elif how_are_you:
        return "Je vais bien, merci. Comment puis-je vous aider ?"
    elif greeting:
        return "Salut, comment puis-je vous aider ?"
    return None
