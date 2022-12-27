from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import requests
import nina_string_helper
import place_converter

baseUrl = "https://warnung.bund.de/api31"


@dataclass
class CovidRules:
    vaccine_info: str
    contact_terms: str
    school_kita_rules: str
    hospital_rules: str
    travelling_rules: str
    fines: str


def get_covid_rules(city_name) -> CovidRules:
    """
    Gets current covid rules from the NinaApi for a city and returns them as a CovidRules class
    If the city_name is not valid, an indirect ValueError is thrown (forwarded from place_converter)
    :param city_name: Each city may have different covid_rules
    :return: CovidRules class
    """
    city_code = place_converter.get_district_id(city_name)
    # der city_code muss 12 Stellig sein, was fehlt muss mit 0en aufgefüllt werden laut doku
    # https://github.com/bundesAPI/nina-api/blob/main/Beispielcode/Python/CoronaZahlenNachGebietscode.py
    city_code = nina_string_helper.expand_location_id_with_zeros(city_code)

    # aktuelle Coronameldungen abrufen nach Gebietscode
    covid_info_api = "/appdata/covid/covidrules/DE/"
    response_raw = requests.get(baseUrl + covid_info_api + city_code + ".json")

    response = response_raw.json()

    vaccine_info = nina_string_helper.filter_html_tags(response["rules"][0]["text"])
    contact_terms = nina_string_helper.filter_html_tags(response["rules"][1]["text"])
    school_kita_rules = nina_string_helper.filter_html_tags(response["rules"][2]["text"])
    hospital_rules = nina_string_helper.filter_html_tags(response["rules"][3]["text"])
    travelling_rules = nina_string_helper.filter_html_tags(response["rules"][4]["text"])
    fines = nina_string_helper.filter_html_tags(response["rules"][5]["text"])

    return CovidRules(vaccine_info, contact_terms, school_kita_rules, hospital_rules, travelling_rules, fines)


@dataclass
class CovidInfo:
    infektionsgefahr_stufe: str
    sieben_tage_inzidenz_kreis: str
    sieben_tage_inzidenz_bundesland: str
    allgemeine_hinweise: str


def get_covid_infos(city_name) -> CovidInfo:
    """
    Gets current covid infos from the NinaApi for a certain city and returns them as a CovidInfo class
    If the city_name is not valid, an indirect ValueError is thrown (forwarded from place_converter)
    :param city_name:
    :return:
    """
    city_code = place_converter.get_district_id(city_name)
    # der city_code muss 12 Stellig sein, was fehlt muss mit 0en aufgefüllt werden laut doku
    # https://github.com/bundesAPI/nina-api/blob/main/Beispielcode/Python/CoronaZahlenNachGebietscode.py
    city_code = nina_string_helper.expand_location_id_with_zeros(city_code)

    # aktuelle Coronameldungen abrufen nach Gebietscode
    covid_info_api = "/appdata/covid/covidrules/DE/"

    response_raw = requests.get(baseUrl + covid_info_api + city_code + ".json")
    response = response_raw.json()
    infektion_danger_level = response["level"]["headline"]

    inzidenz_split = str(response["level"]["range"]).split("\n")

    sieben_tage_inzidenz_kreis = inzidenz_split[0]
    sieben_tage_inzidenz_bundesland = inzidenz_split[1]
    general_tips = nina_string_helper.filter_html_tags(response["generalInfo"])
    return CovidInfo(infektion_danger_level, sieben_tage_inzidenz_kreis, sieben_tage_inzidenz_bundesland, general_tips)


class WarningSeverity(Enum):
    Minor = 0
    Moderate = 1
    Severe = 2
    Unknown = 3


def _get_warning_severity(warn_severity: str) -> WarningSeverity:
    """
    translates a string into an enum of WarningSeverity
    :param warn_severity: the exact Enum as a String, for example: "Minor" <- valid  " Minor" <- returns WarningSeverity.Unknown
    :return: if the string is a valid enum, the enum if not: WarningSeverity.Unknown
    """
    try:
        return WarningSeverity[warn_severity]
    except KeyError:
        return WarningSeverity.Unknown


class WarningType(Enum):
    Update = 0
    Alert = 1
    Unknown = 2


def _get_warning_type(warn_type: str) -> WarningType:
    """
    translates a string into an enum of WarningType
    :param warn_type: the exact Enum as a String, for example: "Minor" <- valid  " Minor" <- returns WarningType.Unknown
    :return: if the string is a valid enum, the enum if not: WarningType.Unknown
    """
    try:
        return WarningType[warn_type]
    except KeyError:
        return WarningType.Unknown


@dataclass
class GeneralWarning:
    id: str
    version: int
    start_date: str
    severity: WarningSeverity
    type: WarningType
    title: str


def _translate_time(nina_time: str) -> str:
    dt = datetime.fromisoformat(nina_time)

    # Convert the datetime object to a string in a specific format
    normal_time_string = dt.strftime("%Y-%m-%d %I:%M")
    return normal_time_string


def _poll_general_warning(api_string: str) -> list[GeneralWarning]:
    response_raw = requests.get(baseUrl + api_string)
    response = response_raw.json()

    warning_list = []

    if response is None:
        return warning_list

    for i in range(0, len(list(response))):
        id_response = response[i]["id"]
        version = response[i]["version"]

        start_date = _translate_time(response[i]["startDate"])

        severity = _get_warning_severity(response[i]["severity"])
        response_type = _get_warning_type(response[i]["type"])
        title = response[i]["i18nTitle"]["de"]
        warning_list.append(GeneralWarning(id=id_response, version=version, start_date=start_date, severity=severity,
                                           type=response_type, title=title))

    return warning_list


def poll_biwapp_warning() -> list[GeneralWarning]:
    biwapp_api = "/biwapp/mapData.json"
    return _poll_general_warning(biwapp_api)


def poll_katwarn_warning() -> list[GeneralWarning]:
    katwarn_api = "/katwarn/mapData.json"
    return _poll_general_warning(katwarn_api)


def poll_mowas_warning() -> list[GeneralWarning]:
    mowas_api = "/mowas/mapData.json"
    return _poll_general_warning(mowas_api)


def poll_dwd_warning() -> list[GeneralWarning]:
    dwd_api = "/dwd/mapData.json"
    return _poll_general_warning(dwd_api)


def poll_lhp_warning() -> list[GeneralWarning]:
    lhp_api = "/lhp/mapData.json"
    return _poll_general_warning(lhp_api)


def poll_police_warning() -> list[GeneralWarning]:
    police_api = "/police/mapData.json"
    return _poll_general_warning(police_api)


"""
warningList = poll_biwapp_warning()  # for testing you just need to change which warning method you call here
for warning in warningList:
    print("\n")
    print(warning.id)
    print(warning.version)
    print(warning.severity)
    print(warning.type)
    print(warning.title)
    print(warning.start_date)
"""


@dataclass
class DetailedWarningInfoArea:
    area_description: str
    geocode: list[str]


@dataclass
class DetailedWarningInfo:
    event: str  # noch keine Ahnung was das sein soll
    severity: WarningSeverity
    date_expires: str
    headline: str
    description: str
    area: list[DetailedWarningInfoArea]


@dataclass
class DetailedWarning:
    id: str
    sender: str
    date_sent: str
    status: str
    infos: list[DetailedWarningInfo]


def _get_detailed_warning_infos_area_geocode(response_geocode) -> list[str]:
    geocode = []
    if response_geocode is None:
        return geocode

    for i in range(0, len(response_geocode)):
        geocode.append(response_geocode[i]["value"])

    return geocode


def _get_detailed_warning_infos_area(response_area) -> list[DetailedWarningInfoArea]:
    area = []
    if response_area is None:
        return area

    for i in range(0, len(response_area)):
        area_description = response_area[i]["areaDesc"]
        geocode = _get_detailed_warning_infos_area_geocode(response_area[i]["geocode"])
        area.append(
            DetailedWarningInfoArea(area_description=area_description, geocode=geocode)
        )

    return area


def _get_detailed_warning_infos(response_infos) -> list[DetailedWarningInfo]:
    infos = []
    if response_infos is None:
        return infos

    for i in range(0, len(response_infos)):
        event = response_infos[i]["event"]
        severity = _get_warning_severity(response_infos[i]["severity"])
        date_expires = _translate_time(response_infos[i]["expires"])
        headline = response_infos[i]["headline"]
        description = nina_string_helper.filter_html_tags(response_infos[i]["description"])
        area = _get_detailed_warning_infos_area(response_infos[i]["area"])

        infos.append(
            DetailedWarningInfo(event=event, severity=severity, date_expires=date_expires, headline=headline,
                                description=description, area=area)
        )

    return infos


def get_detailed_warning(warning_id: str) -> DetailedWarning:
    """
    This method should be called after a warning with one of the poll_****_warning methods was received
    :param warning_id: warning id is extracted from the poll_****_warning method return type: GeneralWarning.id
    :return:
    """
    response_raw = requests.get(baseUrl + "/warnings/" + warning_id + ".json")
    response = response_raw.json()
    print(response_raw.text)

    id_response = response["identifier"]
    sender = response["sender"]
    date_sent = _translate_time(response["sent"])
    status = response["status"]
    infos = _get_detailed_warning_infos(response["info"])

    return DetailedWarning(id=id_response, sender=sender, date_sent=date_sent, status=status, infos=infos)


"""
warning = poll_biwapp_warning()[0] #for testing the individual warning method needs to return a warning (not always the case, just iterate through biwap, katwarn, police, etc...)
warning = get_detailed_warning(warning.id)
print(warning.id)
print(warning.status)
print(warning.sender)
print(warning.date_sent)
print("INFOS: ")
for i in range(0, len(warning.infos)):
    print("\t"+warning.infos[i].event)
    print("\t"+warning.infos[i].severity.name)
    print("\t"+warning.infos[i].date_expires)
    print("\t"+warning.infos[i].headline)
    print("\t"+warning.infos[i].description)
    print("\tAREA: ")
    for j in range(0, len(warning.infos[i].area)):
        print("\t\t"+ warning.infos[i].area[i].area_description)
        for l in range(0, len(warning.infos[i].area[j].geocode)):
            print ("\t\tGEOCODE:")
            print("\t\t\t"+ warning.infos[i].area[i].geocode[l])
"""