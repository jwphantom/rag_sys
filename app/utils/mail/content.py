import email
from email.header import decode_header
from email.parser import BytesParser
from email.policy import default
import os
import re
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, parseaddr

from app.utils.handle_input.handle_string import add_newlines_before_names

username = os.environ.get("USERNAME")


def decode_mime_words(s):
    return " ".join(
        word.decode(encoding or "utf-8") if isinstance(word, bytes) else word
        for word, encoding in decode_header(s)
    )


def get_email_content(email_message):
    content = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                content += part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="ignore"
                )
    else:
        content = email_message.get_payload(decode=True).decode(
            email_message.get_content_charset() or "utf-8", errors="ignore"
        )
    return content


def clean_and_format_content(email_message):

    body = get_email_content(email_message)

    content = re.sub(r"^>+", "", body, flags=re.MULTILINE).strip()

    single_line = re.sub(r"\s+", " ", content)

    parts = re.split(
        r"(?=(?:On|Le) (?:\w{3},|\w{3}\.) \d{1,2} (?:\w{3}|\w{3}\.) \d{4})", single_line
    )

    # Remove empty elements from parts
    parts = [part.strip() for part in parts if part.strip()]

    new_response = ""

    if (
        not (
            parts
            and re.match(r"(?:On|Le) .+(?:wrote|a écrit) ?:", parts[0], re.IGNORECASE)
        )
    ) and (len(parts) == 1):
        return single_line, f"User: {single_line}", parts

    if not (
        parts and re.match(r"(?:On|Le) .+(?:wrote|a écrit) ?:", parts[0], re.IGNORECASE)
    ):
        new_response = parts[0]
        single_line = " ".join(parts[1:])

    replies = re.findall(
        r"(?:On .*? wrote:|Le .*? a écrit :).*?(?=On .*? wrote:|Le .*? a écrit :|$)",
        single_line,
        re.DOTALL,
    )

    if replies:
        formatted_replies = []
        for reply in replies:
            email_match = re.search(r"<([^>]+)>", reply)
            message_start = (
                reply.find("wrote:") + 6
                if "wrote:" in reply
                else reply.find("écrit :") + 7
            )
            email = email_match.group(1) if email_match else "No email found"
            message = reply[message_start:].strip()

            cut_index = message.find("MBalla 2, Centre, Yaoundé")
            if cut_index != -1:
                message = message[: cut_index + len("MBalla 2")].strip()

            formatted_reply = f"{email}: {message}"
            formatted_replies.append(formatted_reply)

        # Clean spaces and replace email addresses

        clean_replies = []
        for reply in formatted_replies:
            clean_reply = reply.strip()

            clean_reply = re.sub(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                lambda m: "Skylia" if m.group() == username else "User",
                clean_reply,
            )
            clean_replies.append(clean_reply)

        if len(new_response) > 0:
            single_string = f"User: {new_response}\n" + "\n".join(clean_replies)

        else:

            single_string = f"\n".join(clean_replies)

        # Remove "Get Outlook" message and everything up to the next "User:" line
        single_string = re.sub(
            r"Get Outlook.*?(?=User:|$)", "", single_string, flags=re.DOTALL
        )

        # Fix formatting to ensure "Me:" and "User:" are on separate lines
        single_string = re.sub(r"(Me:|User:)\s*", r"\n\1 ", single_string)

        # Remove any extra newlines and leading/trailing whitespace
        single_string = re.sub(r"\n+", "\n", single_string).strip()

        return new_response, add_newlines_before_names(single_string), parts
    else:
        return new_response, f"User: {single_line}", parts


# mail="""
# Hotesse de l'air


# Le jeu. 10 oct. 2024 à 03:06, <campus@irdsm-aviation.com> a écrit :

# > Oui, nous proposons plusieurs formations. Pourriez-vous nous dire quelle
# > formation vous intéresse ?
# >
# > User: J'aimerais savoir si C'etait possible de faire une formation chez
# > vous
# """

# new_request, history, parts = clean_and_format_content(mail)
