from flask import flash

def error_flash(message: str):
    return flash(f"\u2757 \u2003 {message} \u2003 \u2757")

def success_flash(message: str):
    return flash(f"\u2705 \u2003 {message} \u2003 \u2705")

def invalid_credentials():
    return error_flash("Väärä käyttäjänimi tai salasana")

def account_disabled():
    return success_flash("Tili on poistettu käytöstä")

def username_too_short():
    return error_flash("Käyttäjänimessä tulee olla vähintään 6 merkkiä")

def username_too_long():
    return error_flash("Käyttäjänimessä voi olla enintään 50 merkkiä")

def username_already_exists():
    return error_flash("Käyttäjänimi on varattu")

def password_too_short():
    return error_flash("Salasanassa tulee olla vähintään 6 merkkiä")

def invalid_date():
    return error_flash("Päivämäärä ei ole kelvollinen")

def invalid_zip_code():
    return error_flash("Postinumerossa tulee olla 5 numeroa")

def profile_updated():
    return success_flash("Profiilin päivitys onnistui")

def profile_update_error():
    return error_flash("Profiilin päivitys ei onnistunut")

def password_mismatch():
    return error_flash("Nykyinen salasana ei täsmää")

def password_changed():
    return success_flash("Salasanan vaihtaminen onnistui")

def password_change_error():
    return error_flash("Salasanan vaihtaminen ei onnistunut")

def wrong_password():
    return error_flash("Väärä salasana")

def account_deleted():
    return success_flash("Tilin poistaminen onnistui")

def account_delete_error():
    return error_flash("Tilin poistaminen ei onnistunut")

def user_search_input_too_long():
    return error_flash("Haussa voi olla enintään 50 merkkiä")

def account_disable_error():
    return error_flash("Tilin poistaminen käytöstä ei onnistunut")

def account_enable_error():
    return error_flash("Tilin ottaminen käyttöön ei onnistunut")

def no_title():
    return error_flash("Otsikko ei saa olla tyhjä")

def title_too_long():
    return error_flash("Otsikossa voi olla enintään 100 merkkiä")

def body_too_long():
    return error_flash("Lisätiedoissa voi olla enintään 1000 merkkiä")

def data_fetch_failed():
    return error_flash("Tietojen haku ei onnistunut")

def news_saved():
    return success_flash("Uutisen tallennus onnistui")

def news_save_error():
    return error_flash("Uutisen tallennus ei onnistunut")

def notice_saved():
    return success_flash("Ilmoituksen tallennus onnistui")

def notice_save_error():
    return error_flash("Ilmoituksen tallennus ei onnistunut")

def notice_status_update_error():
    return error_flash("Tilan päivitys ei onnistunut")

def notice_status_delete_error():
    return error_flash("Merkinnän poistaminen ei onnistunut")

def support_error():
    return error_flash("Komppaaminen ei onnistunut")

def invalid_start_date():
    return error_flash("Alkamispäivämäärä ei ole kelvollinen")

def invalid_end_date():
    return error_flash("Päättymispäivämäärä ei ole kelvollinen")

def start_date_after_end_date():
    return error_flash("Päättymispäivämäärä ei voi olla ennen alkamispäivämäärää")

def poll_saved():
    return success_flash("Kyselyn tallennus onnistui")

def poll_save_error():
    return error_flash("Kyselyn tallennus ei onnistunut")

def vote_error():
    return error_flash("Äänestäminen ei onnistunut")

def feedback_sent():
    return success_flash("Palautteen lähettäminen onnistui")

def feedback_send_error():
    return error_flash("Palautteen lähettäminen ei onnistunut")

def acknowledged():
    return success_flash("Huomioiduksi merkitseminen onnistui")

def acknowledging_error():
    return error_flash("Huomioiduksi merkitseminen ei onnistunut")

def unacknowledged():
    return success_flash("Huomioinnin peruminen onnistui")

def unacknowledging_error():
    return error_flash("Huomioinnin peruminen ei onnistunut")

def archived():
    return success_flash("Arkistointi onnistui")

def archiving_error():
    return error_flash("Arkistointi ei onnistunut")

def unarchived():
    return success_flash("Arkistoinnin peruminen onnistui")

def unarchiving_error():
    return error_flash("Arkistoinnin peruminen ei onnistunut")
