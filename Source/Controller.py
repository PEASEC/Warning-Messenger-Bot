import ChatSender
import TextTemplates
import NinaService


def start(chat_id):
    ChatSender.start(chat_id, TextTemplates.get_greeting_string())


def corona(chat_id, city_name):
    ChatSender.send_chat_action(chat_id, "typing")
    infos = NinaService.get_covid_infos(city_name)
    message = TextTemplates.get_corona_string()
    message = message.replace("%inzidenz", infos.infektion_danger_level)
    message = message.replace("%bund", infos.sieben_tage_inzidenz_bundesland)
    message = message.replace("%kreis", infos.sieben_tage_inzidenz_kreis)
    message = message.replace("%tips", infos.general_tips)
    ChatSender.send_message(chat_id, city_name+":\n"+message)
