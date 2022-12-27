import json
from enum import Enum

# See the MVP document for all possible options

file_path = "data/data.json"

DEFAULT_DATA = {
    "current_state": 0,
    "receive_warnings": True,
    "receive_covid_information": 0,
    "locations": {
    },
    "recommendations": [
        "München",
        "Frankfurt",
        "Berlin"
    ],
    "language": "german"
}


class WarnType(Enum):
    WEATHER = "weather"
    BIWAPP = "biwapp"


class ReceiveInformation(Enum):
    NEVER = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3


class Language(Enum):
    GERMAN = "german"


class Attributes(Enum):
    CHAT_ID = "chat_id"
    CURRENT_STATE = "current_state"
    RECEIVE_WARNINGS = "receive_warnings"
    COVID_AUTO_INFO = "receive_covid_information"
    LOCATIONS = "locations"
    RECOMMENDATIONS = "recommendations"
    LANGUAGE = "language"


def _read_file(path: str) -> dict:
    with open(path, "r") as file_object:
        json_content = file_object.read()
        return json.loads(json_content)


def _write_file(path: str, data: dict):
    with open(path, 'w') as writefile:
        json.dump(data, writefile, indent=4)


def remove_user(chat_id: int):
    """
    Removes a User from the database. If the user is not in the database this method does nothing.

    Attributes:
        chat_id: Integer used to identify the user to be removed
    """
    all_user = _read_file(file_path)

    if str(chat_id) in all_user:
        del all_user[str(chat_id)]
        _write_file(file_path, all_user)


def set_receive_warnings(chat_id: int, new_value: bool):
    """
    Sets receive_warnings of the user (chat_id) to the new value (new_value)

    Arguments:
        chat_id: Integer to identify the user
        new_value: Boolean of the new value
    """
    all_user = _read_file(file_path)
    cid = str(chat_id)

    if not (cid in all_user):
        all_user[cid] = DEFAULT_DATA

    all_user[cid][Attributes.RECEIVE_WARNINGS.value] = new_value

    _write_file(file_path, all_user)


def get_receive_warnings(chat_id: int) -> bool:
    """
    Returns if the user currently wants to receive warnings or not

    Arguments:
        chat_id: Integer to identify the user

    Returns:
        Boolean representing if the user currently wants to receive warnings
    """
    all_user = _read_file(file_path)

    if str(chat_id) in all_user:
        return all_user[str(chat_id)][Attributes.RECEIVE_WARNINGS.value]
    return DEFAULT_DATA[Attributes.CURRENT_STATE.value]


def get_user_state(chat_id: int) -> int:
    """
    Returns the state the user (chat_id) is currently in.

    Arguments:
        chat_id: Integer to identify the user

    Returns:
        Integer value of the state the user is currently in or 0 if the user is not in the database yet
    """
    all_user = _read_file(file_path)

    if str(chat_id) in all_user:
        return all_user[str(chat_id)][Attributes.CURRENT_STATE.value]
    return DEFAULT_DATA[Attributes.CURRENT_STATE.value]


def set_user_state(chat_id: int, new_state: int):
    """
    Sets the state of the user (chat_id) to the new state (new_state)

    Arguments:
        chat_id: Integer to identify the user
        new_state: Integer of the new state
    """
    all_user = _read_file(file_path)
    cid = str(chat_id)

    if not (cid in all_user):
        all_user[cid] = DEFAULT_DATA

    all_user[cid][Attributes.CURRENT_STATE.value] = new_state

    _write_file(file_path, all_user)


def set_auto_covid_information(chat_id: int, how_often: ReceiveInformation):
    """
    Sets how often the user (chat_id) wants to receive covid information

    Arguments:
        chat_id: Integer to identify the user
        how_often: ReceiveInformation representing how often the user wants to receive covid information
    """
    all_user = _read_file(file_path)
    cid = str(chat_id)

    if not (cid in all_user):
        all_user[cid] = DEFAULT_DATA

    all_user[cid][Attributes.COVID_AUTO_INFO.value] = how_often.value

    _write_file(file_path, all_user)


def get_auto_covid_information(chat_id: int) -> ReceiveInformation:
    """
    Returns how often the user currently wants to receive covid updates

    Arguments:
        chat_id: Integer to identify the user

    Returns:
        ReceiveInformation representing how often the user currently wants to receive covid updates
    """
    all_user = _read_file(file_path)
    cid = str(chat_id)

    if cid in all_user:
        return ReceiveInformation(all_user[cid][Attributes.COVID_AUTO_INFO.value])
    return ReceiveInformation(DEFAULT_DATA[Attributes.COVID_AUTO_INFO.value])


def get_subscriptions(chat_id: int) -> dict:
    """
    Returns a dictionary of subscriptions of the user (chat_id)

    Arguments:
        chat_id: Integer to identify the user

    Returns:
        a dictionary of subscriptions of the user
    """
    all_user = _read_file(file_path)

    if str(chat_id) in all_user:
        return all_user[str(chat_id)][Attributes.LOCATIONS.value]
    return DEFAULT_DATA[Attributes.LOCATIONS.value]


def add_subscription(chat_id: int, location: str, warning: WarnType, warning_level: int):
    """
    Adds/Sets the subscription for the user (chat_id) for the location and the warning given

    Arguments:
        chat_id: Integer to identify the user
        location: String with the location of the subscription
        warning: WarnType with the warning for the subscription
        warning_level: Integer representing the Level a warning is relevant to the user
    """
    all_user = _read_file(file_path)
    cid = str(chat_id)

    if not (cid in all_user):
        all_user[cid] = DEFAULT_DATA

    user = all_user[cid]

    if not (location in user[Attributes.LOCATIONS.value]):
        user[Attributes.LOCATIONS.value][location] = {warning.value: warning_level}
    else:
        user[Attributes.LOCATIONS.value][location][warning.value] = warning_level

    _write_file(file_path, all_user)


def delete_subscription(chat_id: int, location: str, warning: str):
    """
    Removes the subscription of user (chat_id) for the location and the warning given

    Arguments:
        chat_id: Integer to identify the user
        location: String with the location of the subscription
        warning: String with the warning of WarnType (e.g. WEATHER)
    """
    all_user = _read_file(file_path)
    cid = str(chat_id)

    if not (cid in all_user):
        return

    user = all_user[cid]
    if not (location in user[Attributes.LOCATIONS.value]):
        return
    if not (warning in user[Attributes.LOCATIONS.value][location]):
        return

    del user[Attributes.LOCATIONS.value][location][warning]

    if len(user[Attributes.LOCATIONS.value][location]) == 0:
        del user[Attributes.LOCATIONS.value][location]

    _write_file(file_path, all_user)


def get_suggestions(chat_id: int) -> list[str]:
    """
    Returns an array of suggestions of the user (chat_id)

    Arguments:
        chat_id: Integer to identify the user

    Returns:
        list of string with the recommendations (locations the user set or default locations)
    """
    all_user = _read_file(file_path)

    if str(chat_id) in all_user:
        return all_user[str(chat_id)][Attributes.RECOMMENDATIONS.value]
    return DEFAULT_DATA[Attributes.RECOMMENDATIONS.value]


def add_suggestion(chat_id: int, location: str):
    """
    This method adds a location to the recommended location list of a user. \n
    The list is sorted: The most recently added location is the first element and the least recently added location
    ist the last element

    Arguments:
        chat_id: Integer to identify the user
        location: String representing the location the user wants to be added to suggestions
    """
    all_user = _read_file(file_path)
    cid = str(chat_id)

    if not (cid in all_user):
        all_user[cid] = DEFAULT_DATA

    current_recommendations = all_user[cid][Attributes.RECOMMENDATIONS.value]
    i = 0
    prev_recommendation = location
    for recommendation in current_recommendations:
        tmp = recommendation
        current_recommendations[i] = prev_recommendation
        prev_recommendation = tmp
        i = i + 1
        if prev_recommendation == location:
            break

    _write_file(file_path, all_user)


def get_language(chat_id: int) -> Language:
    """
    Returns the language the user (chat_id) has currently active or the default language

    Arguments:
        chat_id: Integer to identify the user

    Returns:
        Language the user has currently active or the default language
    """
    all_user = _read_file(file_path)

    if str(chat_id) in all_user:
        return Language(all_user[str(chat_id)][Attributes.LANGUAGE.value])
    return Language(DEFAULT_DATA[Attributes.LANGUAGE.value])


def set_language(chat_id: int, new_language: Language):
    """
    Sets the language of the user (chat_id) to the new language (new_language)

    Arguments:
        chat_id: Integer to identify the user
        new_language: Language represents the new language the user wants
    """
    all_user = _read_file(file_path)
    cid = str(chat_id)

    if not (cid in all_user):
        all_user[cid] = DEFAULT_DATA

    all_user[cid][Attributes.LANGUAGE.value] = new_language.value

    _write_file(file_path, all_user)