
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response,make_response, jsonify #import modul dari flask (kerangka web)database di Flask
import os
import secrets 
import csv
from io import StringIO
from flask_marshmallow import Marshmallow
from datetime import datetime
from model import db, KriteriaAsosiasi, PerbandinganAlternatif, Kriteria, Alternatif, User, Hasil, RelKriteria, MatriksKriteria
from backEnd import BackEnd #implementasi khusus dari algoritma Analytic Hierarchy Process (AHP)python




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ahp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key=secrets.token_hex(16)
db.init_app(app)

users = {
    "admin": {"username": "admin", "email": "admin@example.com", "password": "admin123"}
}
# data = [
#     {"id": 1, "Nama": "Gaji Ayah", "Gaji_Ayah": 500000, "Gaji_Ibu": 500000, "Jumlah_Tanggungan": 0, "Pembayaran_Listrik": 0},
#     {"id": 2, "Nama": "Gaji Ibu", "Gaji_Ayah": 500000, "Gaji_Ibu": 500000, "Jumlah_Tanggungan": 0, "Pembayaran_Listrik": 0},
#     {"id": 3, "Nama": "Jumlah Tanggungan", "Gaji_Ayah": 500000, "Gaji_Ibu": 500000, "Jumlah_Tanggungan": 0, "Pembayaran_Listrik": 0}
# ]
# data_alternatif = [
#     {"id": 1, "Nama": "vina", "Gaji_Ayah": 500000, "Gaji_Ibu": 500000, "Jumlah_Tanggungan": 0, "Pembayaran_Listrik": 0},
#     {"id": 2, "Nama": "vina", "Gaji_Ayah": 500000, "Gaji_Ibu": 500000, "Jumlah_Tanggungan": 0, "Pembayaran_Listrik": 0},
#     {"id": 3, "Nama": "vina", "Gaji_Ayah": 500000, "Gaji_Ibu": 500000, "Jumlah_Tanggungan": 0, "Pembayaran_Listrik": 0}
# ]

ma = Marshmallow(app)  # Initialize Marshmallow with your Flask app

class AlternatifSchema(ma.Schema):
    class Meta:
        fields = ("id", "nama_mahasiswa")

alternatif_schema = AlternatifSchema()


@app.route('/', methods=["GET", 'POST'])
def login():
    if request.method=='POST':
        username=request.form ['username']
        password=request.form ['password']
        # user = users.get(username)
        user = User.query.filter_by(user_name = username).first()

        if user and user.password == password :
            session['username']=user.user_name
            flash('login berhasil','success')
            return redirect(url_for('home'))
        else : 
            flash('password salah',"danger")
    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))
    

@app.route('/kriteria')
def kriteria():
    if 'username' in session:
        data = Kriteria.query.all()
        return render_template('kriteria.html', data=data)
    else:
        return redirect(url_for('login'))


@app.route('/kriteria/add', methods=['GET', 'POST'])
def add_kriteria():
    if 'username' in session:
        if request.method == 'POST':
            nama_kriteria = request.form['nama']
            new_kriteria = Kriteria(nama_kriteria=nama_kriteria)
            db.session.add(new_kriteria)
            db.session.commit()
            return redirect(url_for('kriteria'))
        return render_template('add_kriteria.html')
    else:
        return redirect(url_for('login'))
    

@app.route('/kriteria/delete/<int:id>')
def delete_kriteria(id):
    if 'username' in session:
        kriteria = Kriteria.query.get_or_404(id)
        db.session.delete(kriteria)
        db.session.commit()
        return redirect(url_for('kriteria'))
    else:
        return redirect(url_for('login'))

@app.route('/kriteria/edit/<int:id>', methods=['GET', 'POST'])
def edit_kriteria(id):
    if 'username' in session:
        kriteria = Kriteria.query.get_or_404(id)
        if request.method == 'POST':
            kriteria.nama_kriteria = request.form['nama']
            db.session.commit()
            return redirect(url_for('kriteria'))
        return render_template('edit_kriteria.html', kriteria=kriteria)
    else:
        return redirect(url_for('login'))

@app.route('/alternatif')
def alternatif():
    if 'username' in session:
        data = Alternatif.query.all()
        return render_template('alternatif.html', data=data)
    else:
        return redirect(url_for('login'))

@app.route('/alternatif/add', methods=['GET', 'POST'])
def add_alternatif():
    if 'username' in session:
        if request.method == 'POST':
            nama_mahasiswa = request.form['nama']
            new_alternatif = Alternatif(nama_mahasiswa = nama_mahasiswa)
            db.session.add(new_alternatif)
            db.session.commit()
            return redirect(url_for('alternatif'))
        return render_template('add_alternatif.html')
    else:
        return redirect(url_for('login'))

@app.route('/alternatif/delete/<int:id>')
def delete_alternatif(id):
    if 'username' in session:
        alternatif = Alternatif.query.get_or_404(id)
        db.session.delete(alternatif)
        db.session.commit()
        return redirect(url_for('alternatif'))
    else :
        return redirect(url_for('login'))

@app.route('/alternatif/edit/<int:id>', methods=['GET', 'POST'])
def edit_alternatif(id):
    if 'username' in session : 
        alternatif = Alternatif.query.get_or_404(id)
        if request.method == 'POST':
            alternatif.nama_mahasiswa = request.form['nama']
            db.session.commit()
            return redirect(url_for('alternatif'))
        return render_template('edit_alternatif.html', alternatif=alternatif)
    else :
        return redirect(url_for('login'))
    
@app.route('/add_sub/<int:id>', methods=['GET', 'POST'])
def add_sub(id):
    alternatif = Alternatif.query.get_or_404(id)
    kriteria_list = Kriteria.query.all()

    existing_sub_kriteria = {}
    for kriteria in kriteria_list:
        existing_sub_kriteria[kriteria.id] = RelKriteria.query.filter_by(
            mahasiswa_id=alternatif.id,
            kriteria_id=kriteria.id
        ).first()

    if request.method == 'POST':
        # Proses data formulir
        for kriteria_id in request.form:
            if kriteria_id.startswith('sub_kriteria_'):
                sub_kriteria = request.form[kriteria_id]
                kriteria_id = int(kriteria_id.split('_')[2])

                # Periksa apakah data sudah ada
                existing_sub_kriteria = RelKriteria.query.filter_by(
                    mahasiswa_id=alternatif.id,
                    kriteria_id=kriteria_id
                ).first()

                if existing_sub_kriteria:
                    # Update data yang sudah ada
                    existing_sub_kriteria.sub_kriteria = sub_kriteria
                    db.session.commit()
                else:
                    # Buat data baru
                    rel_kriteria = RelKriteria(
                        mahasiswa_id=alternatif.id,
                        kriteria_id=kriteria_id,
                        sub_kriteria=sub_kriteria
                    )
                    db.session.add(rel_kriteria)
                    db.session.commit()

        return redirect(url_for('alternatif'))  # Redirect ke halaman alternatif
    else:
        return render_template(
            'add_sub.html',
            kriteria_list=kriteria_list,
            alternatif=alternatif,
            existing_sub_kriteria=existing_sub_kriteria
        )
    
# @app.route('/alternatif/addsub/<int:id>', methods=['GET', 'POST'])
# def add_sub(id):
#     if 'username' in session :

    
@app.route('/perbandingan_kriteria', methods=['GET', 'POST'])
def perbandingan_kriteria():
    if 'username' in session:
        kriteria = Kriteria.query.all()
        comparisons = []
        for i in range(len(kriteria)):
            for j in range(i+1, len(kriteria)):
                asosiasi = KriteriaAsosiasi.query.filter_by(
                    kriteria_id_1=kriteria[i].id,
                    kriteria_id_2=kriteria[j].id
                ).first()
                if asosiasi:
                    nilai = MatriksKriteria.query.filter_by(asosiasi_id=asosiasi.id).first()
                    value = int(nilai.nilai) if nilai else '1'
                else:
                    value = '1'

                comparisons.append({
                    'name': f"{kriteria[i].nama_kriteria}_{kriteria[j].nama_kriteria}",
                    'option1': kriteria[i].nama_kriteria,
                    'option2': kriteria[j].nama_kriteria,
                    'value': value
                })

        matrix_rows = []
        for i in range(len(kriteria)):
            row = []
            for j in range(len(kriteria)):
                asosiasi = KriteriaAsosiasi.query.filter_by(
                    kriteria_id_1=kriteria[i].id,
                    kriteria_id_2=kriteria[j].id
                ).first()
                row.append(1 if not asosiasi or not MatriksKriteria.query.filter_by(asosiasi_id=asosiasi.id).first() else MatriksKriteria.query.filter_by(asosiasi_id=asosiasi.id).first().nilai)
            matrix_rows.append(row)

        if request.method == 'POST':
            save_comparison()  # Panggil fungsi save_comparison
            return redirect(url_for('perbandingan_kriteria'))

        enumerated_matrix_rows = enumerate(matrix_rows)

        return render_template('perbandingan_kriteria.html', 
                               kriteria=kriteria, 
                               comparisons=comparisons,
                               matrix_rows=enumerated_matrix_rows)

    else:
        return redirect(url_for('login'))

@app.route('/save_comparison', methods=['POST'])
def save_comparison():
    if 'username' in session:
        # Hapus data lama dari database
        MatriksKriteria.query.delete()
        KriteriaAsosiasi.query.delete()
        db.session.commit()

        kriteria = Kriteria.query.all()
        kriteria_names = [k.nama_kriteria for k in kriteria]

        data = request.form.to_dict()

        matrix = []
        for i in range(len(kriteria_names)):
            row = []
            for j in range(len(kriteria_names)):
                if i == j:
                    row.append(1)
                else:
                    key1 = f"{kriteria_names[i]}_{kriteria_names[j]}_value"
                    key2 = f"{kriteria_names[j]}_{kriteria_names[i]}_value"
                    row.append(float(data[key1]) if key1 in data else (1 / float(data[key2]) if key2 in data else 1))
            matrix.append(row)

        for i in range(len(kriteria_names)):
            for j in range(len(kriteria_names)):
                asosiasi = KriteriaAsosiasi.query.filter_by(
                    kriteria_id_1=kriteria[i].id,
                    kriteria_id_2=kriteria[j].id
                ).first()
                if not asosiasi:
                    asosiasi = KriteriaAsosiasi(
                        kriteria_id_1=kriteria[i].id,
                        kriteria_id_2=kriteria[j].id
                    )
                    db.session.add(asosiasi)
                    db.session.commit()

                matriks = MatriksKriteria.query.filter_by(asosiasi_id=asosiasi.id).first()
                if matriks:
                    matriks.nilai = matrix[i][j]
                else:
                    matriks = MatriksKriteria(
                        asosiasi_id=asosiasi.id,
                        nilai=matrix[i][j]
                    )
                    db.session.add(matriks)

        db.session.commit()
        return redirect(url_for('perbandingan_kriteria'))
    else:
        return redirect(url_for('login'))

  
@app.route('/perbandingan_alternatif', methods=['GET', 'POST'])
def perbandingan_alternatif():
    if 'username' in session:

        kriteria = Kriteria.query.all()
        alternatif = Alternatif.query.all()
        rel_kriteria = RelKriteria.query.all()

        if request.method == "POST":
            selected_kriteria = request.form.get("selected_kriteria")
            selected_kriteria_id = Kriteria.query.filter_by(nama_kriteria=selected_kriteria).first().id
            data = request.form.to_dict()
            mahasiswa_names = [a.nama_mahasiswa for a in alternatif]

            # Hapus data lama dari PerbandinganAlternatif
            PerbandinganAlternatif.query.filter_by(kriteria_id=selected_kriteria_id).delete()
            db.session.commit()

            matrix = []
            for i in range(len(mahasiswa_names)):
                row = []
                for j in range(len(mahasiswa_names)):
                    if i == j:
                        row.append(1)
                    else: 
                        key1 = f"{mahasiswa_names[i]}_{mahasiswa_names[j]}_value"
                        key2 = f"{mahasiswa_names[j]}_{mahasiswa_names[i]}_value"
                        
                        if key1 in data:
                            row.append(float(data[key1]))
                        elif key2 in data:
                            row.append(1 / float(data[key2]))
                        else:
                            row.append(1)

                matrix.append(row)

            # Simpan perbandingan ke database
            for i in range(len(mahasiswa_names)):
                for j in range(len(mahasiswa_names)):
                    if i != j:
                        alternatif_1 = Alternatif.query.filter_by(nama_mahasiswa=mahasiswa_names[i]).first()
                        alternatif_2 = Alternatif.query.filter_by(nama_mahasiswa=mahasiswa_names[j]).first()

                        # Buat perbandingan baru
                        perbandingan_baru = PerbandinganAlternatif(
                            kriteria_id=selected_kriteria_id,
                            alternatif_id_1=alternatif_1.id,
                            alternatif_id_2=alternatif_2.id,
                            nilai=matrix[i][j]
                        )
                        db.session.add(perbandingan_baru)

            db.session.commit()
            return redirect(url_for('perbandingan_alternatif'))

        return render_template('perbandingan_alternatif.html', 
                               kriteria=kriteria, 
                               alternatif=alternatif_schema.dump(alternatif, many=True), 
                               rel_kriteria=rel_kriteria)
    else:
        return redirect(url_for('login'))

@app.route('/get_sub_kriteria/<kriteria>')
def get_sub_kriteria(kriteria):
    kriteria_id = Kriteria.query.filter_by(nama_kriteria=kriteria).first().id
    sub_kriteria = RelKriteria.query.filter_by(kriteria_id=kriteria_id).all()
    return jsonify([{'sub_kriteria': s.sub_kriteria} for s in sub_kriteria])

@app.route('/get_comparison_value/<kriteria>/<alternatif_1>/<alternatif_2>')
def get_comparison_value(kriteria, alternatif_1, alternatif_2):
    kriteria_id = Kriteria.query.filter_by(nama_kriteria=kriteria).first().id
    alternatif_id_1 = Alternatif.query.filter_by(nama_mahasiswa=alternatif_1).first().id
    alternatif_id_2 = Alternatif.query.filter_by(nama_mahasiswa=alternatif_2).first().id

    comparison = PerbandinganAlternatif.query.filter_by(
        kriteria_id=kriteria_id,
        alternatif_id_1=alternatif_id_1,
        alternatif_id_2=alternatif_id_2
    ).first()

    if comparison:
        return jsonify({'nilai': (comparison.nilai)})
    else:
        return jsonify({'nilai': 1})

@app.route('/hasil_perangkingan')
def hasil_perangkingan():
    if 'username' in session:
        kriteria = Kriteria.query.all()
        alternatif = Alternatif.query.all()

        backend = BackEnd(db.session)

        arrRatarataKriteria, arrRatarataAlternatif = backend.hitungAHP()
        
        # Membangun ahp_results
        ahp_results = {k.nama_kriteria: arrRatarataKriteria[idx] for idx, k in enumerate(kriteria)}  # Ambil nilai rata-rata
        print("ahp_results:", ahp_results)

        # Hitung total skor untuk setiap alternatif
        final_scores = {}
        for idx, a in enumerate(alternatif):
            total_score = 0
            for k_idx, k in enumerate(kriteria):
                if k.nama_kriteria in ahp_results:
                    # Ambil bobot kriteria
                    bobot_kriteria = ahp_results[k.nama_kriteria]
                    # Ambil nilai alternatif untuk kriteria ini
                    nilai_alternatif = arrRatarataAlternatif[idx][k_idx]
                    print("bobot kriteria = ",bobot_kriteria)
                    print("nilai alternatif = ",nilai_alternatif)

                    # Pastikan nilai tidak None
                    if nilai_alternatif is not None:
                        # Mengalikan bobot kriteria dengan nilai alternatif
                        hasil_kali = bobot_kriteria * nilai_alternatif
                        print("hasil kali = ", hasil_kali)
                        total_score += hasil_kali

            print(f"Total Score untuk {a.nama_mahasiswa}: {total_score}")  # Debugging
            final_scores[a.nama_mahasiswa] = total_score

        # Mengurutkan hasil berdasarkan total skor
        sorted_results = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)

        # Menghapus hasil sebelumnya dan menyimpan yang baru
        Hasil.query.delete()
        db.session.commit()
        for nama_mahasiswa, total_ranking in sorted_results:
            hasil = Hasil(nama_mahasiswa=nama_mahasiswa, total_ranking=total_ranking)
            db.session.add(hasil)
        db.session.commit()

        return render_template('hasil_perangkingan.html', kriteria=kriteria, alternatif=alternatif, sorted_results=sorted_results)
    else:
        return redirect(url_for('login'))
@app.route('/download_ranking')
def download_ranking():
    if 'username' in session :
# Ambil data dari model Hasil
        hasil_data = Hasil.query.with_entities(Hasil.nama_mahasiswa, Hasil.total_ranking).all()

        # Buat output CSV menggunakan StringIO
        output = StringIO()
        writer = csv.writer(output)
        
        # Tulis header
        writer.writerow(['Nama Mahasiswa', 'Total Ranking'])
        
        # Tulis data
        for nama, ranking in hasil_data:
            writer.writerow([nama, ranking])
        
        # Kembali ke awal StringIO
        output.seek(0)

        # Kirim CSV sebagai respons
        return Response(
            output,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=hasil.csv"}
        )


        # return render_template('hasil_perangkingan.html', kriteria=kriteria, alternatif=alternatif, sorted_results=sorted_results)
    else :
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if 'username' in session :
        session.pop('username',None)
        flash('Anda telah logout','info')
        return redirect(url_for('login'))
    else :
        return redirect(url_for('login'))

if __name__ == '_main_':
    app.run(debug=True)