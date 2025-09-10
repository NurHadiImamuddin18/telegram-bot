from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("TOKEN")
app = Application.builder().token(TOKEN).build()

# Struktur materi
menu = {
    "K3": ["APD", "SAFETY RIDING", "do and don't", "Listrik", "Ketinggian", "ruangan terbatas", "bekerja di jalan"],
    "IODN": ["FTM", "TIANG", "DUCT & POLONGAN", "ODC", "ODP", "STANDART INSTALASI FTTH"],
    "QC": ["QC FTM", "QC ODC", "QC AKSESORIS", "QC ODP"],
    "BPSM": []  # langsung ke foto, tidak ada sub-menu
}

# Lokasi folder foto
base_path = "materi"

# === Fungsi tampilkan menu utama ===
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("K3", callback_data="menu_K3")],
        [InlineKeyboardButton("IODN", callback_data="menu_IODN")],
        [InlineKeyboardButton("QC", callback_data="menu_QC")],
        [InlineKeyboardButton("BPSM", callback_data="menu_BPSM")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pilih Kelompok Materi:", reply_markup=get_main_menu())

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("menu_"):
        group = data.split("_")[1]

        # Jika BPSM -> langsung kirim foto, lalu kembali ke menu utama
        if group == "BPSM":
            folder_path = os.path.join(base_path, "BPSM")
            if os.path.exists(folder_path):
                files = os.listdir(folder_path)
                for file in files:
                    with open(os.path.join(folder_path, file), "rb") as f:
                        await query.message.reply_photo(photo=f)
                await query.message.reply_text("✅ Materi BPSM telah dikirimkan.")
            else:
                await query.message.reply_text("Belum ada materi untuk BPSM.")

            # Balik ke menu utama
            await query.message.reply_text("⬅️ Kembali ke menu utama:", reply_markup=get_main_menu())

        else:
            # selain BPSM tampilkan list materi
            keyboard = [[InlineKeyboardButton(m, callback_data=f"materi_{group}_{m}")] for m in menu[group]]
            keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_groups")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=f"Pilih materi {group}:", reply_markup=reply_markup)

    elif data.startswith("materi_"):
        _, group, materi = data.split("_", 2)
        folder_path = os.path.join(base_path, group, materi)
        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            for file in files:
                with open(os.path.join(folder_path, file), "rb") as f:
                    await query.message.reply_photo(photo=f)

            await query.message.reply_text(f"✅ Materi {materi} telah dikirimkan.")

            # Balik ke submenu materi (bukan ke menu utama)
            keyboard = [[InlineKeyboardButton(m, callback_data=f"materi_{group}_{m}")] for m in menu[group]]
            keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_groups")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(text=f"Pilih materi {group}:", reply_markup=reply_markup)
        else:
            await query.message.reply_text(f"Belum ada materi untuk {materi}")

    elif data == "back_to_groups":
        await query.edit_message_text("Pilih Kelompok Materi:", reply_markup=get_main_menu())

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
