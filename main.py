import requests
import yt_dlp
from bs4 import BeautifulSoup
import os # Będziemy używać tego do Replit Secrets

# --- Konfiguracja ---
# Zastąp te wartości swoimi.
LOGIN_URL = "https://ADRES-STRONY-Z-LOGINEM.pl"
KURSY_URL = "https://ADRES-STRONY-Z-PIERWSZA-LEKCJA.pl"

# Użyj Replit Secrets do przechowywania loginu i hasła!
# Po lewej stronie w Replit kliknij ikonę kłódki (Secrets).
# Utwórz dwa sekrety:
# klucz: USERNAME   wartość: twoj_login@email.com
# klucz: PASSWORD   wartość: twoje_super_tajne_haslo
MOJ_LOGIN = os.environ.get('USERNAME')
MOJE_HASLO = os.environ.get('PASSWORD')

# Nazwy plików
PLIK_Z_COOKIES = 'cookies.txt'

def zaloguj_i_zapisz_sesje():
    """
    Loguje się na stronę i zapisuje ciasteczka sesji do pliku.
    """
    print(f"Próba logowania do: {LOGIN_URL}")
    
    # Tworzymy sesję. To kluczowe. 
    # Sesja będzie automatycznie przechowywać ciasteczka (cookies).
    with requests.Session() as sesja:
        
        # KROK 1: (Opcjonalny, ale często wymagany)
        # Najpierw pobierz stronę logowania, aby dostać token CSRF.
        # Wiele stron używa go do zabezpieczenia formularzy.
        try:
            response_get = sesja.get(LOGIN_URL)
            response_get.raise_for_status() # Sprawdź, czy nie ma błędu
            
            # Tutaj musiałbyś przeszukać HTML w poszukiwaniu tokenu
            # Np. <input type="hidden" name="_csrf_token" value="ABC123XYZ">
            # soup = BeautifulSoup(response_get.text, 'lxml')
            # token = soup.find('input', {'name': '_csrf_token'})['value']
            # print("Pobrano token CSRF (jeśli istnieje).")
            
        except requests.exceptions.RequestException as e:
            print(f"Błąd podczas pobierania strony logowania: {e}")
            return False

        # KROK 2: Przygotowanie danych do wysłania (payload)
        # MUSISZ ZNALEŹĆ NAZWY PÓL!
        # Kliknij PPM na pole loginu -> "Zbadaj" (Inspect) 
        # i znajdź atrybut 'name' tagu <input>.
        
        dane_logowania = {
            'nazwa_pola_loginu': MOJ_LOGIN,     # np. 'email' albo 'username'
            'nazwa_pola_hasla': MOJE_HASLO,      # np. 'password'
            # 'nazwa_tokenu_csrf': token        # Jeśli strona tego wymaga
        }
        
        # KROK 3: Wysłanie żądania logowania (POST)
        try:
            response_post = sesja.post(LOGIN_URL, data=dane_logowania)
            response_post.raise_for_status()

            # Sprawdzenie, czy logowanie się udało
            # (Np. szukając tekstu "Wyloguj" na stronie wynikowej)
            if "Wyloguj" in response_post.text or "Mój profil" in response_post.text:
                print("Logowanie pomyślne!")
            else:
                print("Logowanie nie powiodło się. Sprawdź dane logowania lub nazwy pól.")
                # print(response_post.text) # Odkomentuj, by zobaczyć, co zwróciła strona
                return False

        except requests.exceptions.RequestException as e:
            print(f"Błąd podczas wysyłania formularza logowania: {e}")
            return False

        # KROK 4: Zapisanie ciasteczek sesji do pliku
        # To jest format, który yt-dlp potrafi odczytać.
        with open(PLIK_Z_COOKIES, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in sesja.cookies:
                f.write(
                    f"{cookie.domain}\t"
                    f"{'TRUE' if cookie.domain.startswith('.') else 'FALSE'}\t"
                    f"{cookie.path}\t"
                    f"{'TRUE' if cookie.secure else 'FALSE'}\t"
                    f"{int(cookie.expires) if cookie.expires else 0}\t"
                    f"{cookie.name}\t"
                    f"{cookie.value}\n"
                )
        print(f"Zapisano ciasteczka sesji do pliku: {PLIK_Z_COOKIES}")
        return True


def pobierz_wideo_z_linku(url_lekcji):
    """
    Pobiera wideo z danej lekcji, używając zapisanych ciasteczek.
    """
    if not os.path.exists(PLIK_Z_COOKIES):
        print("Brak pliku z cookies! Najpierw uruchom funkcję logowania.")
        return

    print(f"Próba pobrania wideo ze strony: {url_lekcji}")

    # Konfiguracja yt-dlp
    opcje_ydl = {
        'outtmpl': '%(title)s.%(ext)s', # Nazwa pliku wyjściowego
        'cookiefile': PLIK_Z_COOKIES,    # Kluczowe: użyj zapisanych ciasteczek!
        'noplaylist': True,              # Pobierz tylko ten jeden film
        'format': 'best',                # Pobierz najlepszą dostępną jakość
        
        # Vimeo może wymagać "Referer" (strony, z której odtwarzasz)
        'add_header': [
            f'Referer: {url_lekcji}',
            'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ],
    }

    # Uruchomienie yt-dlp
    try:
        with yt_dlp.YoutubeDL(opcje_ydl) as ydl:
            # yt-dlp jest na tyle inteligentny, że sam znajdzie 
            # link do Vimeo/innego playera na podanej stronie.
            ydl.download([url_lekcji])
        print("Pobieranie zakończone pomyślnie.")
        
    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania yt-dlp: {e}")


# --- Główna logika skryptu ---
if __name__ == "__main__":
    
    # 1. Najpierw logujemy się i zapisujemy sesję
    if zaloguj_i_zapisz_sesje():
        
        # 2. Jeśli logowanie się udało, pobieramy wideo
        #    (Możesz tu wstawić listę wszystkich URL-i do lekcji)
        pobierz_wideo_z_linku(KURSY_URL)
        
        # p_w_z_l("https://ADRES-STRONY-Z-DRUGA-LEKCJA.pl")
        # p_w_z_l("https://ADRES-STRONY-Z-TRZECIA-LEKCJA.pl")
        
    else:
        print("Nie udało się zalogować. Zatrzymuję skrypt.")

    # 3. (Opcjonalnie) Posprzątaj po sobie
    if os.path.exists(PLIK_Z_COOKIES):
        os.remove(PLIK_Z_COOKIES)
        print("Usunięto plik cookies.")
