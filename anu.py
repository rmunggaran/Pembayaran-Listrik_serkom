from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb+srv://test:riksa252@cluster0.4blko.mongodb.net/")
db = client.listrik_pascabayar 
users_collection = db.users
tarif_collection = db.tarif
customers_collection = db.customers
bills_collection = db.bills





# import time
# Uji performa query
# start = time.time()
# cari_user("admin123")
# end = time.time()
# print("Waktu eksekusi query:", end - start, "detik")



# # Menampilkan semua tagihan
# def tampilkan_semua_tagihan():
#     tagihan = db.bills.find()
#     for t in tagihan:
#         print(t)

# # Tambah tagihan baru
# def tambah_tagihan(pelanggan_id, tahun, bulan, pemakaian):
#     tagihan = {
#         "tbPelanggan_id": pelanggan_id,
#         "tahun_tagihan": tahun,
#         "bulan_tagihan": bulan,
#         "pemakaian": pemakaian
#     }
#     db.bills.insert_one(tagihan)
#     print("Tagihan berhasil ditambahkan.")

# # Contoh penggunaan
# tampilkan_semua_tagihan()
# tambah_tagihan("64fa95c3c5", "2025", 1, 350)




# db.users.create_index("username", unique=True)
# print("Indeks berhasil dibuat.")



# def cari_user(username):
#     user = db.users.find_one({"username": username})
#     if user:
#         print("Data User:", user)
#     else:
#         print("User tidak ditemukan.")

# cari_user("admin123")


def simpan_data_user(username, password, hak_akses):
    data = {
        "username": username,
        "password": generate_password_hash(password),  
        "hak_akses": hak_akses
    }
    db.users.insert_one(data)
    print("Data user berhasil disimpan.")

# simpan_data_user("admin123", "riksa", 1)

# def ubah_data_user(username, data_baru):
#     db.users.update_one({"username": username}, {"$set": data_baru})
#     print("Data user berhasil diubah.")

# ubah_data_user("admin123", {"hak_akses": "2"})


# tarif_collection.insert_one({
#     "tbUser_id": "",
#     "kdtarif": "",
#     "beban": "",
#     "tarif_perkwh": "",
# })

# customers_collection.insert_one({
#     "tbTarifListrik_id": "",
#     "nama_pelanggan": "",
#     "nomor": "",
#     "alamat": "",
# })

# bills_collection.insert_one({
#     "tbPelanggan_id": "",
#     "tahun_tagihan": "",
#     "bulan_tagihan": "",
#     "pemakaian": "",
# })