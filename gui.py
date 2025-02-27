import tkinter as tk
import tkinter.ttk as ttk
import threading
import pandas as pd
from scrap import get_business_data
from tkinter import filedialog

# Küresel değişkenler
data_list = []
count = 1
stop_scraping = False

# Türkiye'deki tüm şehirler
sehirler = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan",
    "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu",
    "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ",
    "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır",
    "Isparta", "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri",
    "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa",
    "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun",
    "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak",
    "Van", "Yalova", "Yozgat", "Zonguldak"
]






def kategori_ara():
    """Arama işlemini başlatır."""
    global stop_scraping
    stop_scraping = False

    kategori = entry.get()
    sehir = sehir_combobox.get()

    if not kategori:
        return

    full_query = f"{sehir} {kategori}"  # Örn: "İstanbul Cafe"

    button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    progress.start()
    tree.delete(*tree.get_children())
    global data_list
    data_list = []

    # Scraping işlemini başlat
    thread = threading.Thread(target=scrape_and_update_gui, args=(full_query,), daemon=True)
    thread.start()


def scrape_and_update_gui(kategori):
    """İşletmeleri bulur ve GUI'ye ekler."""
    global count
    count = 1

    for item in get_business_data(kategori):
        if stop_scraping:
            break

        root.after(0, update_gui, item)
        data_list.append(item)

    root.after(0, stop_progress_bar)


def update_gui(item):
    """GUI'yi anında günceller."""
    global count
    tree.insert("", tk.END, values=(count, item["Ad"], item["Adres"], item["Telefon"]))
    count += 1
    progress.step(10)


def stop_progress_bar():
    """Progress bar'ı durdurur ve butonları aktif eder."""
    progress.stop()
    button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)


def save_to_excel():
    """Verileri Excel olarak kaydeder."""
    if not data_list:
        return

    df = pd.DataFrame(data_list)
    df.insert(0, "ID", range(1, len(df) + 1))

    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                             filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])

    if file_path:
        df.to_excel(file_path, index=False)
        print(f"Veriler {file_path} olarak kaydedildi!")


def stop_scraping_process():
    """Durdur butonuna basıldığında işlemi kes."""
    global stop_scraping
    stop_scraping = True
    stop_progress_bar()


def close_app():
    """Programı kapatır."""
    root.quit()
    root.destroy()


# ** Tkinter GUI **
root = tk.Tk()
root.title("Google Map Scrap")
root.geometry("1000x600")
root.configure(bg="#f5f5f5")  # Açık gri arka plan

# ** Başlık **
label = tk.Label(root, text="Google Map Veri Çekme", font=("Arial", 18, "bold"), bg="#f5f5f5", fg="#333")
label.pack(pady=10)

# ** Şehir Seçme Alanı **
frame_sehir = tk.Frame(root, bg="#f5f5f5")
frame_sehir.pack()

sehir_label = tk.Label(frame_sehir, text="Şehir Seçin:", font=("Arial", 12), bg="#f5f5f5")
sehir_label.pack(side=tk.LEFT, padx=5)

sehir_combobox = ttk.Combobox(frame_sehir, values=sehirler, font=("Arial", 12), state="readonly", width=20)
sehir_combobox.pack(side=tk.LEFT, padx=5)
sehir_combobox.set("İstanbul")  # Varsayılan şehir

# ** Kategori Girişi **
entry = tk.Entry(root, width=50, font=("Arial", 12))
entry.pack(pady=10)

# ** Butonlar (Ara & Durdur) **
frame_buttons = tk.Frame(root, bg="#f5f5f5")
frame_buttons.pack()

button = tk.Button(frame_buttons, text="Ara", command=kategori_ara, font=("Arial", 12), bg="#4CAF50", fg="white", padx=20)
button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(frame_buttons, text="Durdur", command=stop_scraping_process, font=("Arial", 12), bg="#F44336", fg="white", padx=20, state=tk.DISABLED)
stop_button.pack(side=tk.LEFT, padx=5)

# ** Progress Bar **
progress = ttk.Progressbar(root, length=300, mode='determinate')
progress.pack(pady=10)

# ** Sonuçlar (Treeview) **
frame = tk.Frame(root)
frame.pack(pady=10, fill=tk.BOTH, expand=True)

columns = ("ID", "Firma Adı", "Adres", "Telefon")
tree = ttk.Treeview(frame, columns=columns, show="headings")

tree.heading("ID", text="ID")
tree.heading("Firma Adı", text="Firma Adı")
tree.heading("Adres", text="Adres")
tree.heading("Telefon", text="Telefon")

tree.column("ID", width=50)
tree.column("Firma Adı", width=250)
tree.column("Adres", width=300)
tree.column("Telefon", width=150)

scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(fill=tk.BOTH, expand=True)

# ** Kaydet & Kapat Butonları **
frame_bottom = tk.Frame(root, bg="#f5f5f5")
frame_bottom.pack(pady=10)

save_button = tk.Button(frame_bottom, text="Kaydet", command=save_to_excel, font=("Arial", 12), bg="#2196F3", fg="white", padx=20)
save_button.pack(side=tk.LEFT, padx=5)

close_button = tk.Button(frame_bottom, text="Kapat", command=close_app, font=("Arial", 12), bg="#757575", fg="white", padx=20)
close_button.pack(side=tk.LEFT, padx=5)

root.mainloop()
