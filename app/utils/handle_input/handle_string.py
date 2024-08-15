import re


def parse_string_to_list_of_dicts(input_string):
    import re

    parts = re.split(r"(Skylia|User)\s*:", input_string)
    result = []
    current_dict = {}
    speaker = None
    first_speaker = None
    count = 0

    for i in range(1, len(parts), 2):
        speaker = parts[i].strip()
        content = parts[i + 1].strip()
        count += 1

        if first_speaker is None:
            first_speaker = speaker

        if speaker == "Skylia":
            if current_dict and "User" in current_dict:
                result.append(current_dict)
                current_dict = {}
            current_dict["Skylia"] = content
        elif speaker == "User":
            if "User" in current_dict:
                current_dict["User"] += f" {content}"
            else:
                if current_dict:
                    result.append(current_dict)
                current_dict = {"User": content}

    if current_dict:
        result.append(current_dict)

    if count > 2:
        return count, first_speaker
    else:
        return count, result


def add_newlines_before_names(input_string):
    import re

    # Modifier l'expression régulière pour ne correspondre qu'aux cas où "User" ou "Skylia" apparaissent après une ponctuation, une fin de ligne, ou au début du texte
    output_string = re.sub(r"(?<!\S)(User|Skylia):", r"\n\1:", input_string)

    # Retirer le premier \n si le texte commence par cela
    if output_string.startswith("\n"):
        output_string = output_string[1:]

    return output_string
