from fuzzywuzzy import fuzz


def handle_response_confirmation_informations(message):
    # Liste des expressions de confirmation
    confirm_informations = [
        "C'est exact",
        "Exact",
        "Je confirme",
        "Merci",
        "reçu",
        "Oui c'est bien cela",
        "Oui les informations ci-dessus sont les miennes",
        "Oui effectivement ce sont mes informations enregistrées lors de ma demande d'admission",
        "Correct",
        "C'est correct",
        "Les informations sont correctes",
        "Tout est bon",
        "C'est bien ça",
        "Parfait",
        "Ça me semble correct",
        "Bien reçu",
        "Je valide ces informations",
        "C'est conforme",
        "Rien à signaler",
        "Tout est en ordre",
    ]

    def is_confirmation(message, threshold=80):
        for confirm in confirm_informations:
            similarity = fuzz.ratio(confirm.lower(), message.lower())
            if similarity >= threshold:
                return True
        return False

    def handle_confirmation(message):
        if is_confirmation(message):
            return True
        else:
            return False

    return handle_confirmation(message)
