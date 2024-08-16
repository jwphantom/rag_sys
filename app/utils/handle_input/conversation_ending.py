from fuzzywuzzy import fuzz


def handle_conversation_ending(message):
    # Liste des expressions de fin de conversation
    end_conversations = [
        "Merci pour votre aide",
        "Merci beaucoup",
        "Merci",
        "Au revoir",
        "Bonne journée",
        "Bonne soirée",
        "À bientôt",
        "Cordialement",
        "Bien à vous",
        "Je vous remercie",
        "Merci encore",
        "Je vous souhaite une bonne journée",
        "Je vous souhaite une bonne soirée",
        "Prenez soin de vous",
        "C’est tout pour moi",
        "À la prochaine",
        "Je vous laisse",
        "C’est noté, merci",
        "Ok",
    ]

    def is_end_of_conversation(message, threshold=80):
        for end_phrase in end_conversations:
            similarity = fuzz.ratio(end_phrase.lower(), message.lower())
            if similarity >= threshold:
                return True
        return False

    def handle_end(message):
        if is_end_of_conversation(message):
            return True
        else:
            return False

    return handle_end(message)
