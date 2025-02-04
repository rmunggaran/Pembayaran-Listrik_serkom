from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.template_filter('get_nama_tarif')
def get_nama_tarif(value):
    try:
        name = db.tariffs.find_one({'_id': ObjectId(value)})
        nama_tarif = name['nama']
        return nama_tarif
    except ValueError:
        return value

@app.template_filter('get_nama_pelanggan')
def get_nama_pelanggan(value):
    try:
        name = db.customers.find_one({'_id': ObjectId(value)})
        nama_tarif = name['nama']
        return nama_tarif
    except ValueError:
        return value
    
@app.template_filter('format_rupiah')
def format_rupiah(value):
    try:
        value = int(value)
        return f"{value:,.0f}".replace(",", ".")
    except ValueError:
        return value

# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = db.users.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'warning')

    return render_template('login.html')

# Route for useristrator dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user=db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('dashboard.html', user=user)

@app.route('/editprofile', methods=['POST'])
def edit_user():
    try:
        user_id = request.form.get('id')
        user = db.users.find_one({"_id": ObjectId(user_id)})

        if not user:
            return jsonify({'status': 'error', 'msg': f'Error: User tidak ditemukan.'})

        username = request.form.get('username')
        
        update_data = {
            "username": username,
        }

        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            return jsonify({'status': 'success', 'msg': 'Data user berhasil diperbarui'})
        else:
            return jsonify({'status': 'warning', 'msg': 'Tidak ada perubahan data.'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': f'Error: {e}'})
    
@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        flash('Harap login terlebih dahulu!', 'warning')
        return redirect(url_for('login'))
    
    user_id = request.form.get('id')
    user = db.users.find_one({"_id": ObjectId(user_id)})
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    new_password_confirmation = request.form.get('new_password_confirmation')

    if not check_password_hash(user['password'], current_password):
        return jsonify({'status': 'warning', 'msg': f'Password lama salah'})

    if new_password != new_password_confirmation:
        return jsonify({'status': 'warning', 'msg': f'Password baru dan konfirmasi password tidak cocok.'})

    if len(new_password) < 6:
        return jsonify({'status': 'warning', 'msg': f'Password baru harus lebih dari 6 karakter.'})

    hashed_password = generate_password_hash(new_password)
    result = db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed_password}}
    )
    if result.modified_count > 0:
        return jsonify({'status': 'success', 'msg': 'Password berhasil diganti.'})
    else:
        return jsonify({'status': 'error', 'msg': f'Error: Terjadi kesalahan, password tidak dapat diubah.'})


# Route for managing electricity tariffs
@app.route('/tariffs', methods=['GET', 'POST'])
def manage_tariffs():
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    tariffs = db.tariffs.find()
    data_count = db.tariffs.count_documents({})
    user=db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('tariffs.html', data=tariffs,data_count=data_count,user=user)

# Route for managing customers
@app.route('/customers')
def manage_customers():
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    customers = db.customers.find()
    tariffs = list(db.tariffs.find())
    user=db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('customers.html', data=customers ,data_count = db.customers.count_documents({}),user=user, tarif=tariffs)

# Route for managing bills
@app.route('/bills')
def manage_bills():
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    bills = db.bills.find()
    customers = list(db.customers.find())
    user=db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('bills.html', data=bills, data_count = db.customers.count_documents({}),user=user, pelaggan=customers)

@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    halaman = request.form.get('halaman')
    if halaman == "tarif":
        try:
            kode = request.form.get('kode')
            nama = request.form.get('nama')
            daya = request.form.get('daya')
            harga = request.form.get('harga')
            subsidi = request.form.get('subsidi') 

            insert_data = {
                "kode": kode,
                "nama": nama,
                "daya": daya,
                "harga": int(harga),  
                "subsidi": subsidi == "ya"  
            }

            result = db.tariffs.insert_one(insert_data)
            if result.inserted_id:
                return jsonify({'status': 'success', 'msg': 'Tarif berhasil ditambahkan'})
            else:
                return jsonify({'status': 'warning', 'msg': 'Tidak ada data yang ditambahkan.'})

        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'Error: {e}'})
        
    elif halaman == "pelanggan":
        try:
            nama = request.form.get('nama')
            nomor = request.form.get('nomor')
            alamat = request.form.get('alamat')
            tarif = request.form.get('tarif') 

            insert_data = {
                "nama": nama,
                "nomor": nomor,
                "alamat": alamat,
                "tarif": tarif
            }

            result = db.customers.insert_one(insert_data)
            if result.inserted_id:
                return jsonify({'status': 'success', 'msg': 'Tagihan berhasil ditambahkan'})
            else:
                return jsonify({'status': 'warning', 'msg': 'Tidak ada data yang ditambahkan.'})

        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'Error: {e}'})
        
    elif halaman == "tagihan":
        try:
            pemakaian = request.form.get('pemakaian')
            pelaggan = request.form.get('pelaggan')

            dataPelanggan = db.customers.find_one({"_id": ObjectId(pelaggan)})
            if not dataPelanggan:
                return jsonify({'status': 'error', 'msg': f'Error: dataPelanggan tidak ditemukan.'})
            
            tarif_id= dataPelanggan['tarif']
            dataTarif = db.tariffs.find_one({"_id": ObjectId(tarif_id)})
            if not dataTarif:
                return jsonify({'status': 'error', 'msg': f'Error: pelanggan_id tidak ditemukan.'})

            try:
                pemakaian = float(pemakaian)  
            except ValueError:
                return jsonify({'status': 'error', 'msg': 'Pemakaian tidak valid'})

            bulan=datetime.now().strftime("%B")
            total_tagihan = pemakaian * dataTarif['harga']

            insert_data = {
                "pemakaian": int(pemakaian),
                "pelaggan": pelaggan,
                "bulan": bulan,
                "total_tagihan": total_tagihan
            }

            result = db.bills.insert_one(insert_data)
            if result.inserted_id:
                return jsonify({'status': 'success', 'msg': 'Pelanggan berhasil ditambahkan'})
            else:
                return jsonify({'status': 'warning', 'msg': 'Tidak ada data yang ditambahkan.'})

        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'Error: {e}'})

@app.route('/Edit', methods=['POST'])
def Edit():
    halaman = request.form.get('halaman')
    if halaman == "tarif":
        try:
            tariffs_id = request.form.get('id')
            tariffs = db.tariffs.find_one({"_id": ObjectId(tariffs_id)})
            if not tariffs:
                return jsonify({'status': 'error', 'msg': f'Error: Id tariffs tidak ditemukan.'})
            kode = request.form.get('kode')
            nama = request.form.get('nama')
            daya = request.form.get('daya')
            harga = request.form.get('harga')
            subsidi = request.form.get('subsidi')
            update_data = {
                "kode": kode,
                "nama": nama,
                "daya": daya,
                "harga": int(harga),
                "subsidi": subsidi == "ya"
            }
            result = db.tariffs.update_one(
                {"_id": ObjectId(tariffs_id)},
                {"$set": update_data}
            )
            if result.matched_count > 0:
                if result.modified_count > 0:
                    return jsonify({'status': 'success', 'msg': 'tariffs berhasil diedit'})
                else:
                    return jsonify({'status': 'info', 'msg': 'Tidak ada perubahan data.'})
            else:
                return jsonify({'status': 'error', 'msg': 'Id tariffs tidak ditemukan.'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'Error: {e}'})
        
    elif halaman == "pelanggan":
        try:
            pelanggan_id = request.form.get('id')
            pelanggan = db.customers.find_one({"_id": ObjectId(pelanggan_id)})

            if not pelanggan:
                return jsonify({'status': 'error', 'msg': f'Error: Id pelanggan tidak ditemukan.'})
            
            nama = request.form.get('nama')
            nomor = request.form.get('nomor')
            alamat = request.form.get('alamat')
            tarif = request.form.get('tarif') 
            
            update_data = {
                "nama": nama,
                "nomor": nomor,
                "alamat": alamat,
                "tarif": tarif
            }
            result = db.customers.update_one(
                {"_id": ObjectId(pelanggan_id)},
                {"$set": update_data}
            )
            if result.matched_count > 0:
                if result.modified_count > 0:
                    return jsonify({'status': 'success', 'msg': 'pelanggan berhasil diedit'})
                else:
                    return jsonify({'status': 'info', 'msg': 'Tidak ada perubahan data.'})
            else:
                return jsonify({'status': 'error', 'msg': 'Id pelanggan tidak ditemukan.'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'Error: {e}'})
        
    elif halaman == "tagihan":
        try:
            tagihan_id = request.form.get('id')
            tagihan = db.bills.find_one({"_id": ObjectId(tagihan_id)})

            if not tagihan:
                return jsonify({'status': 'error', 'msg': f'Error: Id tagihan tidak ditemukan.'})
            
            pemakaian = request.form.get('pemakaian')
            pelaggan = request.form.get('pelaggan')

            dataPelanggan = db.customers.find_one({"_id": ObjectId(pelaggan)})
            if not dataPelanggan:
                return jsonify({'status': 'error', 'msg': f'Error: dataPelanggan tidak ditemukan.'})
            
            tarif_id= dataPelanggan['tarif']
            dataTarif = db.tariffs.find_one({"_id": ObjectId(tarif_id)})
            if not dataTarif:
                return jsonify({'status': 'error', 'msg': f'Error: pelanggan_id tidak ditemukan.'})

            try:
                pemakaian = float(pemakaian)  
            except ValueError:
                return jsonify({'status': 'error', 'msg': 'Pemakaian tidak valid'})

            bulan=datetime.now().strftime("%B")
            total_tagihan = pemakaian * dataTarif['harga']
            
            update_data = {
                "pemakaian": int(pemakaian),
                "pelaggan": pelaggan,
                "bulan": bulan,
                "total_tagihan": total_tagihan
            }
            result = db.bills.update_one(
                {"_id": ObjectId(tagihan_id)},
                {"$set": update_data}
            )
            if result.matched_count > 0:
                if result.modified_count > 0:
                    return jsonify({'status': 'success', 'msg': 'tagihan berhasil diedit'})
                else:
                    return jsonify({'status': 'info', 'msg': 'Tidak ada perubahan data.'})
            else:
                return jsonify({'status': 'error', 'msg': 'Id tagihan tidak ditemukan.'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'Error: {e}'})
    
@app.route('/hapus', methods=['POST'])
def hapus():
    halaman = request.form.get('halaman')
    if halaman == "tarif":
        try:
            id = request.form.get('id')
            tarif = db.tariffs.find_one({'_id': ObjectId(id)})

            if not tarif:
                return jsonify({'status': 'warning', 'msg': 'Data tidak ditemukan.'})

            result = db.tariffs.delete_one({'_id': ObjectId(id)})

            if result.deleted_count > 0:
                return jsonify({'status': 'success', 'msg': 'Tarif berhasil dihapus'})
            else:
                return jsonify({'status': 'warning', 'msg': 'Gagal menghapus data.'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'Error: {str(e)}'})
    
    elif halaman == "pelanggan":
        try:
            id = request.form.get('id')
            pelanggan = db.customers.find_one({'_id': ObjectId(id)})

            if not pelanggan:
                return jsonify({'status': 'warning', 'msg': 'Data tidak ditemukan.'})

            result = db.customers.delete_one({'_id': ObjectId(id)})

            if result.deleted_count > 0:
                return jsonify({'status': 'success', 'msg': 'pelanggan berhasil dihapus'})
            else:
                return jsonify({'status': 'warning', 'msg': 'Gagal menghapus data.'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'Error: {str(e)}'})
        
    elif halaman == "tagihan":
        try:
            id = request.form.get('id')
            tagihan = db.bills.find_one({'_id': ObjectId(id)})

            if not tagihan:
                return jsonify({'status': 'warning', 'msg': 'Data tidak ditemukan.'})

            result = db.bills.delete_one({'_id': ObjectId(id)})

            if result.deleted_count > 0:
                return jsonify({'status': 'success', 'msg': 'tagihan berhasil dihapus'})
            else:
                return jsonify({'status': 'warning', 'msg': 'Gagal menghapus data.'})
        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'Error: {str(e)}'})

# Route for logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)