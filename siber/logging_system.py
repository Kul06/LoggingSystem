import tkinter as tk
from tkinter import messagebox, ttk
import logging
import time
import json
import os

# Loglama yapılandırması
logging.basicConfig(
    filename="system.logs.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Kullanıcılar için dosya adı
USER_FILE = "users.json"
locked_accounts = {}
failed_attempts = {}
LOCK_DURATION = 60


# Kullanıcıları yükleme
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            return json.load(file)
    return {}


# Kullanıcıları kaydetme
def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file)


# Giriş işlemi
def login(users, username, password, output_label, inputs):
    current_time = time.time()

    if username in locked_accounts:
        lock_time = locked_accounts[username]
        if current_time - lock_time < LOCK_DURATION:
            remaining_time = LOCK_DURATION - (current_time - lock_time)
            output_label.config(
                text=f"Hesap kilitli! {int(remaining_time)} saniye sonra tekrar deneyin."
            )
            logging.warning(f"Kilitli hesap giris denemesi: {username}")
            reset_inputs(inputs)
            return

    if username not in users:
        output_label.config(text="Kayitli olmayan kullanici!")
        logging.warning(f"Yetkisiz giris denemesi: {username}")
        reset_inputs(inputs)
        return

    if users[username] == password:
        output_label.config(text=f"Hos geldiniz, {username}!")
        logging.info(f"Kullanici giris yapti: {username}")
        failed_attempts.pop(username, None)
    else:
        output_label.config(text="Hatali sifre!")
        failed_attempts[username] = failed_attempts.get(username, 0) + 1
        logging.warning(f"Hatali giris denemesi: {username}")

        if failed_attempts[username] >= 3:
            locked_accounts[username] = current_time
            logging.critical(f"Hesap kilitlendi: {username}")
    reset_inputs(inputs)


# Yeni kullanıcı ekleme
def add_user(users, username, password, output_label, inputs):
    if username in users:
        output_label.config(text="Bu kullanici zaten kayitli!")
        reset_inputs(inputs)
        return
    users[username] = password
    save_users(users)
    output_label.config(text=f"{username} basariyla eklendi!")
    logging.info(f"Yeni kullanici eklendi: {username}")
    reset_inputs(inputs)


# Şifre değiştirme
def change_password(users, username, old_password, new_password, output_label, inputs):
    if username not in users:
        output_label.config(text="Bu kullanıcı kayıtlı değil!")
        logging.warning(f"Sifre degistirme icin yetkisiz kullanici denemesi: {username}")
        reset_inputs(inputs)
        return

    if users[username] != old_password:
        output_label.config(text="Eski sifre yanlis!")
        logging.warning(f"Yanlis şifre ile degistirme denemesi: {username}")
        reset_inputs(inputs)
        return

    users[username] = new_password
    save_users(users)
    output_label.config(text=f"{username} şifresi başarıyla değiştirildi!")
    logging.info(f"Şifre değiştirildi: {username}")
    reset_inputs(inputs)


# Kullanıcı silme
def delete_user(users, username, output_label, inputs):
    if username not in users:
        output_label.config(text="Bu kullanıcı zaten kayıtlı değil!")
        logging.warning(f"Silme denemesi: {username} kayıtlı değil.")
        reset_inputs(inputs)
        return

    del users[username]
    save_users(users)
    output_label.config(text=f"{username} başarıyla silindi!")
    logging.info(f"Kullanıcı silindi: {username}")
    reset_inputs(inputs)


# Kilitli hesapları görüntüleme
def list_locked_accounts(output_label):
    current_time = time.time()
    locked_list = [
        f"{username}: {int(LOCK_DURATION - (current_time - lock_time))} saniye"
        for username, lock_time in locked_accounts.items()
        if current_time - lock_time < LOCK_DURATION
    ]

    if locked_list:
        output_label.config(text="\n".join(locked_list))
    else:
        output_label.config(text="Şu anda kilitli hesap yok.")
    logging.info("Kilitli hesaplar sorgulandı.")


# Log arama
def search_logs_by_user(username, output_label, inputs):
    log_file = "system.logs.log"
    try:
        logging.info(f"Log arama başlatıldı: {username}")
        with open(log_file, "r") as file:
            logs = [line.strip() for line in file if username in line]

        if logs:
            output_label.config(text="\n".join(logs[-5:]))
            logging.info(f"{username} için log araması tamamlandı.")
        else:
            output_label.config(text=f"{username} için log bulunamadı.")
            logging.info(f"{username} için log bulunamadı.")
    except FileNotFoundError:
        output_label.config(text="Log dosyası bulunamadı.")
        logging.error("Log dosyası bulunamadı.")
    reset_inputs(inputs)


# Girdi alanlarını sıfırlama
def reset_inputs(inputs):
    for input_field in inputs:
        input_field.delete(0, tk.END)


# Ana Arayüz
def main_menu():
    users = load_users()
    window = tk.Tk()
    window.title("Kullanıcı Yönetim Sistemi")
    window.geometry("800x600")

    notebook = ttk.Notebook(window)

    # Giriş Yap Sekmesi
    login_frame = ttk.Frame(notebook)
    notebook.add(login_frame, text="Giriş Yap")
    tk.Label(login_frame, text="Kullanıcı Adı:").pack()
    login_username = tk.Entry(login_frame)
    login_username.pack()
    tk.Label(login_frame, text="Şifre:").pack()
    login_password = tk.Entry(login_frame, show="*")
    login_password.pack()
    login_output = tk.Label(login_frame, text="", fg="blue")
    login_output.pack()
    tk.Button(
        login_frame,
        text="Giriş Yap",
        command=lambda: login(
            users, login_username.get(), login_password.get(), login_output, [login_username, login_password]
        ),
    ).pack()

    # Yeni Kullanıcı Ekle Sekmesi
    add_user_frame = ttk.Frame(notebook)
    notebook.add(add_user_frame, text="Yeni Kullanıcı Ekle")
    tk.Label(add_user_frame, text="Kullanıcı Adı:").pack()
    add_username = tk.Entry(add_user_frame)
    add_username.pack()
    tk.Label(add_user_frame, text="Şifre:").pack()
    add_password = tk.Entry(add_user_frame, show="*")
    add_password.pack()
    add_output = tk.Label(add_user_frame, text="", fg="blue")
    add_output.pack()
    tk.Button(
        add_user_frame,
        text="Kullanıcı Ekle",
        command=lambda: add_user(
            users, add_username.get(), add_password.get(), add_output, [add_username, add_password]
        ),
    ).pack()

    # Şifre Değiştir Sekmesi
    change_password_frame = ttk.Frame(notebook)
    notebook.add(change_password_frame, text="Şifre Değiştir")
    tk.Label(change_password_frame, text="Kullanıcı Adı:").pack()
    cp_username = tk.Entry(change_password_frame)
    cp_username.pack()
    tk.Label(change_password_frame, text="Eski Şifre:").pack()
    cp_old_password = tk.Entry(change_password_frame, show="*")
    cp_old_password.pack()
    tk.Label(change_password_frame, text="Yeni Şifre:").pack()
    cp_new_password = tk.Entry(change_password_frame, show="*")
    cp_new_password.pack()
    cp_output = tk.Label(change_password_frame, text="", fg="blue")
    cp_output.pack()
    tk.Button(
        change_password_frame,
        text="Şifre Değiştir",
        command=lambda: change_password(
            users, cp_username.get(), cp_old_password.get(), cp_new_password.get(), cp_output, [cp_username, cp_old_password, cp_new_password]
        ),
    ).pack()

    # Kullanıcı Sil Sekmesi
    delete_user_frame = ttk.Frame(notebook)
    notebook.add(delete_user_frame, text="Kullanıcı Sil")
    tk.Label(delete_user_frame, text="Kullanıcı Adı:").pack()
    del_username = tk.Entry(delete_user_frame)
    del_username.pack()
    del_output = tk.Label(delete_user_frame, text="", fg="blue")
    del_output.pack()
    tk.Button(
        delete_user_frame,
        text="Kullanıcı Sil",
        command=lambda: delete_user(users, del_username.get(), del_output, [del_username]),
    ).pack()

    # Kilitli Hesaplar Sekmesi
    locked_frame = ttk.Frame(notebook)
    notebook.add(locked_frame, text="Kilitli Hesaplar")
    locked_output = tk.Label(locked_frame, text="", fg="blue")
    locked_output.pack()
    tk.Button(
        locked_frame,
        text="Kilitli Hesapları Göster",
        command=lambda: list_locked_accounts(locked_output),
    ).pack()

    # Log Ara Sekmesi
    log_search_frame = ttk.Frame(notebook)
    notebook.add(log_search_frame, text="Log Ara")
    tk.Label(log_search_frame, text="Kullanıcı Adı:").pack()
    log_username = tk.Entry(log_search_frame)
    log_username.pack()
    log_output = tk.Label(log_search_frame, text="", fg="blue")
    log_output.pack()
    tk.Button(
        log_search_frame,
        text="Log Ara",
        command=lambda: search_logs_by_user(log_username.get(), log_output, [log_username]),
    ).pack()

    notebook.pack(expand=True, fill="both")
    window.mainloop()


# Programı başlat
if __name__ == "__main__":
    main_menu()
