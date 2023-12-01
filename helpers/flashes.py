from flask import flash

def invalid_credentials():
    return flash("Väärä käyttäjänimi tai salasana")

def account_disabled():
    return flash("Tili on poistettu käytöstä")

def username_too_short():
    return flash("Käyttäjänimessä tulee olla vähintään 6 merkkiä")

def username_too_long():
    return flash("Käyttäjänimessä voi olla enintään 50 merkkiä")

def password_too_short():
    return flash("Salasanassa tulee olla vähintään 6 merkkiä")

def invalid_date():
    return flash("Päivämäärä ei ole kelvollinen")

def invalid_zip_code():
    return flash("Postinumerossa tulee olla 5 numeroa")

def profile_updated():
    return flash("Profiilin päivitys onnistui")

def profile_update_error():
    return flash("Profiilin päivitys ei onnistunut")

def password_mismatch():
    return flash("Nykyinen salasana ei täsmää")

def password_changed():
    return flash("Salasanan vaihtaminen onnistui")

def password_change_error():
    return flash("Salasanan vaihtaminen ei onnistunut")

def account_deleted():
    return flash("Tilin poistaminen onnistui")

def account_delete_error():
    return flash("Tilin poistaminen ei onnistunut")

def account_disable_error():
    return flash("Tilin poistaminen käytöstä ei onnistunut")

def account_enable_error():
    return flash("Tilin ottaminen käyttöön ei onnistunut")

def no_title():
    return flash("Otsikko ei saa olla tyhjä")

def title_too_long():
    return flash("Otsikossa voi olla enintään 100 merkkiä")

def body_too_long():
    return flash("Lisätiedoissa voi olla enintään 1000 merkkiä")

def data_fetch_failed():
    return flash("Tietojen haku ei onnistunut")

def news_saved():
    return flash("Uutisen tallennus onnistui")

def news_save_error():
    return flash("Uutisen tallennus ei onnistunut")

def notice_saved():
    return flash("Ilmoituksen tallennus onnistui")

def notice_save_error():
    return flash("Ilmoituksen tallennus ei onnistunut")

def notice_status_update_error():
    return flash("Tilan päivitys ei onnistunut")

def notice_status_delete_error():
    return flash("Merkinnän poistaminen ei onnistunut")

def support_error():
    return flash("Komppaaminen ei onnistunut")

def invalid_start_date():
    return flash("Alkamispäivämäärä ei ole kelvollinen")

def invalid_end_date():
    return flash("Päättymispäivämäärä ei ole kelvollinen")

def start_date_before_end_date():
    return flash("Alkamispäivämäärän on oltava ennen päättymispäivämäärää")

def poll_saved():
    return flash("Kyselyn tallennus onnistui")

def poll_save_error():
    return flash("Kyselyn tallennus ei onnistunut")

def vote_error():
    return flash("Äänestäminen ei onnistunut")

def feedback_sent():
    return flash("Palautteen lähettäminen onnistui")

def feedback_send_error():
    return flash("Palautteen lähettäminen ei onnistunut")

def acknowledged():
    return flash("Huomioiduksi merkitseminen onnistui")

def acknowledging_error():
    return flash("Huomioiduksi merkitseminen ei onnistunut")

def unacknowledged():
    return flash("Huomioinnin peruminen onnistui")

def unacknowledging_error():
    return flash("Huomioinnin peruminen ei onnistunut")

def archived():
    return flash("Arkistointi onnistui")

def archiving_error():
    return flash("Arkistointi ei onnistunut")

def unarchived():
    return flash("Arkistoinnin peruminen onnistui")

def unarchiving_error():
    return flash("Arkistoinnin peruminen ei onnistunut")
