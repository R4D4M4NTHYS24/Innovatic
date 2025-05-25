from email_io import fetch_new_emails, send_email

def main():
    mails = fetch_new_emails()
    print("Correos leídos:", mails)
    if mails:
        remitente = mails[0]["from"]
        ok = send_email(
            remitente,
            "Prueba final via Device Code",
            "¡Correo enviado correctamente!"
        )
        print("Envío completado:", ok)
    else:
        print("No hay correos en la bandeja para pruebas.")

if __name__ == "__main__":
    main()
