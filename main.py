from flask import Flask,send_file
from io import BytesIO
from PIL import Image
import asyncio
from bleak import BleakClient

# Adres MAC/BLE kamery GoPro (możesz sprawdzić np. przez nRF Connect)
GOPRO_BLE_ADDRESS = "df:7a:f1:08:26:51"
# UUID charakterystyki do wysyłania komend (do ustalenia dla GoPro)
GOPRO_CHARACTERISTIC_UUID = "b5f90072-aa8d-11e3-9046-0002a5d5c51b"

app = Flask(__name__)

ble_client = BleakClient(GOPRO_BLE_ADDRESS)

gopro_connected =False

async def connect_gopro():
    global ble_client
    global gopro_connected
    while True:
        try:
            print(f"🔗 Próba połączenia z GoPro ({GOPRO_BLE_ADDRESS})...")

            await ble_client.connect()

            if await ble_client.is_connected():
                print("✅ Połączono z GoPro!")
                gopro_connected = True

                break  # Wyjście z pętli po udanym połączeniu
        except Exception as e:
            print(f"⚠️ Błąd połączenia: {e}, ponawiam próbę...")
            await asyncio.sleep(5)  # Poczekaj 5 sek i spróbuj ponownie

async def send_ble_command():
    """Funkcja łączy się przez BLE i wysyła komendę."""
    global ble_client
    try:
        if await ble_client.is_connected():
            print("Połączono z GoPro!")
            command = bytes([0x03, 0x01, 0x01, 0x01])  # Przykładowa komenda, trzeba dopasować
            await ble_client.write_gatt_char(GOPRO_CHARACTERISTIC_UUID, command)
            print("Komenda wysłana!")
            return "Komenda wysłana do GoPro!"
        else:
            return "Nie udało się połączyć z GoPro."
    except Exception as e:
        return f"Błąd: {e}"

@app.route("/shutter", methods=["GET"])
def handle_request():
    """Obsługa żądania HTTP - wysyła komendę przez BLE."""
    if  gopro_connected:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(send_ble_command())
        return result
    else:
        img = Image.new("RGB", (200, 100), color=(255, 0, 0))  # Czerwony obrazek
        img_io = BytesIO()
        img.save(img_io, "JPEG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/jpeg")

if __name__ == "__main__":
    asyncio.run(connect_gopro())
    app.run(host="0.0.0.0", port=5000)
