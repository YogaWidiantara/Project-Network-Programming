import smtplib
import imaplib
import email as email_module
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import decode_header
import os

def send_email_with_options(email, receiver_email, subject, password, message=None, image_paths=None, text_file_path=None):
    # Membuat pesan
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Baca pesan dari file jika ada
    if text_file_path and os.path.isfile(text_file_path):
        try:
            with open(text_file_path, 'r', encoding='utf-8') as text_file:
                file_message = text_file.read()
                if message:
                    message += "\n\n" + file_message
                else:
                    message = file_message
            print(f"Teks dari file {os.path.basename(text_file_path)} ditambahkan ke email.")
        except Exception as e:
            print(f"Gagal membaca file teks: {str(e)}")
    else:
        if text_file_path:
            print(f"File teks tidak ditemukan: {text_file_path}")

    if not message:
        message = "Tidak ada pesan yang diberikan."

    msg.attach(MIMEText(message, 'plain'))

    # Menambahkan gambar jika ada
    if image_paths:
        for image_path in image_paths:
            if os.path.isfile(image_path):
                try:
                    with open(image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        image_mime = MIMEImage(img_data, name=os.path.basename(image_path))
                        msg.attach(image_mime)
                    print(f"Gambar {os.path.basename(image_path)} ditambahkan ke email.")
                except Exception as e:
                    print(f"Gagal melampirkan gambar: {str(e)}")
            else:
                print(f"File gambar tidak ditemukan: {image_path}")

    # Mengirim email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, receiver_email, msg.as_string())
        server.quit()
        print("Email terkirim ke " + receiver_email)
    except Exception as e:
        print("Gagal mengirim email: ", str(e))

# Fungsi untuk membaca email dari server IMAP
def read_emails(email_address, password):
    try:
        # Koneksi ke server IMAP
        print("Menghubungkan ke server IMAP...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        print("Login...")
        mail.login(email_address, password)

        # Pilih INBOX
        print("Memilih INBOX...")
        mail.select("inbox")

        # Cari semua email
        print("Mencari semua email...")
        status, messages = mail.search(None, "ALL")

        if status != "OK":
            print("Gagal mencari email. Status:", status)
            return

        email_ids = messages[0].split()
        if not email_ids:
            print("Tidak ada email yang ditemukan.")
            return

        print(f"\nTotal email ditemukan: {len(email_ids)}")

        for num, email_id in enumerate(email_ids[-5:], 1):  # Menampilkan 5 email terakhir
            print(f"Mengambil email {num}...")
            status, data = mail.fetch(email_id, "(RFC822)")

            if status != "OK":
                print(f"Gagal mengambil email {num}. Status:", status)
                continue

            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email_module.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    from_ = msg.get("From")
                    date_ = msg.get("Date")
                    print(f"\nEmail {num}:")
                    print(f"Subject: {subject}")
                    print(f"From: {from_}")
                    print(f": {date_}")
                    

                    # Jika pesan email multipart
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # Ambil isi email
                                body = part.get_payload(decode=True).decode()
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    print(f"Body: {body}")
                            except Exception as e:
                                print(f"Gagal memproses bagian pesan: {str(e)}")
                    else:
                        # Jika pesan email tidak multipart
                        try:
                            body = msg.get_payload(decode=True).decode()
                            print(f"Body: {body}")
                        except Exception as e:
                            print(f"Gagal memproses pesan: {str(e)}")

        # Logout
        print("Logout...")
        mail.logout()
    except imaplib.IMAP4.error as e:
        print("Kesalahan IMAP:", str(e))
    except Exception as e:
        print("Gagal membaca email: ", str(e))

# Fungsi utama dengan menu tambahan untuk membaca email
def main():
    email = input("SENDER EMAIL: ")
    receiver_email = input("RECEIVER EMAIL: ")
    subject = input("SUBJECT: ")
    password = input("PASSWORD: ")

    print("Pilih Opsi:")
    print("1. Kirim email dengan pesan saja")
    print("2. Kirim email dengan pesan dan gambar")
    print("3. Kirim email dengan pesan dari file teks")
    print("4. Kirim email dengan pesan dan file teks serta gambar")
    print("5. Baca email")

    option = ("Masukkan pilihan Anda (1/2/3/4/5): ")

    image_paths = []
    if option == "1":
        message = input("MESSAGE: ")
        send_email_with_options(email, receiver_email, subject, password, message=message)
    elif option == "2":
        message = input("MESSAGE: ")
        while True:
            image_path = input("PATH TO IMAGE (or press Enter to stop): ")
            if image_path:
                image_paths.append(image_path)
            else:
                break
        send_email_with_options(email, receiver_email, subject, password, message=message, image_paths=image_paths)
    elif option == "3":
        text_file_path = input("PATH TO TEXT FILE: ")
        send_email_with_options(email, receiver_email, subject, password, text_file_path=text_file_path)
    elif option == "4":
        message = input("MESSAGE (leave empty if using text file): ")
        text_file_path = input("PATH TO TEXT FILE: ")
        while True:
            image_path = input("PATH TO IMAGE (or press Enter to stop): ")
            if image_path:
                image_paths.append(image_path)
            else:
                break
        send_email_with_options(email, receiver_email, subject, password, message=message, image_paths=image_paths, text_file_path=text_file_path)
    elif option == "5":
        read_emails(email, password)
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()
