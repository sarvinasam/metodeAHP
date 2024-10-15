from flask_sqlalchemy import SQLAlchemy 


db = SQLAlchemy()
class KriteriaAsosiasi(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kriteria_id_1 = db.Column(db.Integer, db.ForeignKey('kriteria.id', ondelete='CASCADE'), nullable=False)
    kriteria_id_2 = db.Column(db.Integer, db.ForeignKey('kriteria.id', ondelete='CASCADE'), nullable=False)

    kriteria_1 = db.relationship('Kriteria', foreign_keys=[kriteria_id_1], backref="asosiasi_kriteria_1", cascade="all") 
    kriteria_2 = db.relationship('Kriteria', foreign_keys=[kriteria_id_2], backref="asosiasi_kriteria_2", cascade="all") 
    matriks_kriteria = db.relationship('MatriksKriteria', backref="asosiasi_mat", cascade="all, delete-orphan")

class PerbandinganAlternatif(db.Model):
    __tablename__ = 'perbandingan_alternatif'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kriteria_id = db.Column(db.Integer, db.ForeignKey('kriteria.id'), nullable=False)
    alternatif_id_1 = db.Column(db.Integer, db.ForeignKey('alternatif.id'), nullable=False)
    alternatif_id_2 = db.Column(db.Integer, db.ForeignKey('alternatif.id'), nullable=False)
    nilai = db.Column(db.Float, nullable=False)

    # Hubungan ke model Kriteria dan Alternatif
    kriteria = db.relationship('Kriteria', backref="perbandingan_alternatif_krit")
    alternatif_1 = db.relationship('Alternatif', foreign_keys=[alternatif_id_1], backref="perbandingan_alternatif_1_krit")
    alternatif_2 = db.relationship('Alternatif', foreign_keys=[alternatif_id_2], backref="perbandingan_alternatif_2_krit")

    def __repr__(self):
        return f'<PerbandinganAlternatif {self.kriteria.nama_kriteria} : {self.alternatif_1.nama_mahasiswa} - {self.alternatif_2.nama_mahasiswa} : {self.nilai}>'


class Kriteria(db.Model): #model database untuk kriteria
    __tablename__ = 'kriteria'
    id = db.Column(db.Integer, primary_key=True)
    nama_kriteria = db.Column(db.String(255), nullable=False) 
    rel_kriteria = db.relationship("RelKriteria", backref="kriteria_rel", cascade="all") 
    asosiasi_1 = db.relationship('KriteriaAsosiasi', foreign_keys=[KriteriaAsosiasi.kriteria_id_1], backref="kriteria_as_1")
    asosiasi_2 = db.relationship('KriteriaAsosiasi', foreign_keys=[KriteriaAsosiasi.kriteria_id_2], backref="kriteria_as_2")
    perbandingan_alternatif = db.relationship('PerbandinganAlternatif', backref='kriteria_alt', cascade='all, delete-orphan')


    def __repr__(self):
        return f"<Kriteria {self.nama_kriteria}>"

class Alternatif(db.Model): #model database untuk alternatif
    __tablename__ = 'alternatif'
    id = db.Column(db.Integer, primary_key=True)
    nama_mahasiswa = db.Column(db.String(255), nullable=False)
    rel_kriteria = db.relationship("RelKriteria", backref="alternatif_rel", cascade="all") # Hapus delete-orphan
    perbandingan_alternatif_1 = db.relationship('PerbandinganAlternatif', foreign_keys=[PerbandinganAlternatif.alternatif_id_1], backref='alternatif_1_krit', cascade='all, delete-orphan')
    perbandingan_alternatif_2 = db.relationship('PerbandinganAlternatif', foreign_keys=[PerbandinganAlternatif.alternatif_id_2], backref='alternatif_2_krit', cascade='all, delete-orphan')


    def __repr__(self):
        return f"<Alternatif {self.nama_mahasiswa}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False) 
    email = db.Column(db.String(255), nullable=False) 
    password = db.Column(db.String(255), nullable=False) 

class Hasil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_mahasiswa = db.Column(db.String(100), nullable=False)
    total_ranking = db.Column(db.Float, nullable=False)

class RelKriteria(db.Model):
    __tablename__ = 'rel_kriteria'
    id = db.Column(db.Integer, primary_key=True)
    mahasiswa_id = db.Column(db.Integer, db.ForeignKey('alternatif.id', ondelete='CASCADE'), nullable=False)
    kriteria_id = db.Column(db.Integer, db.ForeignKey('kriteria.id', ondelete='CASCADE'), nullable=False)
    sub_kriteria = db.Column(db.String(255), nullable=False)
    # Hubungan ke model lain
    mahasiswa = db.relationship("Alternatif", backref="rel_kriteria_alt")
    kriteria = db.relationship("Kriteria", backref="rel_kriteria_krit")

    def __repr__(self):
        return f"<RelKriteria {self.sub_kriteria}>"



# Model MatriksKriteria
class MatriksKriteria(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asosiasi_id = db.Column(db.Integer, db.ForeignKey('kriteria_asosiasi.id', ondelete='CASCADE'), nullable=False)
    nilai = db.Column(db.Float, nullable=False)

    asosiasi = db.relationship('KriteriaAsosiasi', backref="matriks_kriteria_as")


