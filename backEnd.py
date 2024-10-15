from model import db, KriteriaAsosiasi, MatriksKriteria, PerbandinganAlternatif, Kriteria, Alternatif

class BackEnd:
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.arrayNilaiPerbandinganKriteria = []
        self.arrayNilaiPerbandinganAlternatif = []

    def get_matrix_kriteria_from_db(self):
        # Fetch all unique criteria IDs from both columns
        criteria_ids = self.db_session.query(KriteriaAsosiasi.kriteria_id_1).union(
            self.db_session.query(KriteriaAsosiasi.kriteria_id_2)
        ).distinct().all()
        criteria_ids = [id[0] for id in criteria_ids]  # Flatten the result
        matrix_size = len(criteria_ids)

        # Initialize the criteria comparison matrix
        self.arrayNilaiPerbandinganKriteria = [[1.0 if i == j else None for j in range(matrix_size)] for i in range(matrix_size)]

        # Populate the criteria comparison matrix
        for record in self.db_session.query(KriteriaAsosiasi).all():
            try:
                kriteria1_id = criteria_ids.index(record.kriteria_id_1)
                kriteria2_id = criteria_ids.index(record.kriteria_id_2)
                
                if kriteria1_id < matrix_size and kriteria2_id < matrix_size:
                    nilai_record = self.db_session.query(MatriksKriteria).filter_by(asosiasi_id=record.id).first()
                    if nilai_record:
                        self.arrayNilaiPerbandinganKriteria[kriteria1_id][kriteria2_id] = nilai_record.nilai
                        self.arrayNilaiPerbandinganKriteria[kriteria2_id][kriteria1_id] = 1 / nilai_record.nilai if nilai_record.nilai != 0 else 0
            except ValueError as e:
                print(f"Error: {e} - Kriteria ID tidak ditemukan dalam criteria_ids")
        print("arrkrit= ", self.arrayNilaiPerbandinganKriteria)

    def get_matrix_alternatif_from_db(self):
        # Fetch all unique alternative IDs
        alternatif_ids = self.db_session.query(PerbandinganAlternatif.alternatif_id_1).union(
            self.db_session.query(PerbandinganAlternatif.alternatif_id_2)
        ).distinct().all()
        alternatif_ids = [id[0] for id in alternatif_ids]
        alternatif_size = len(alternatif_ids)

        # Fetch all unique kriteria IDs from PerbandinganAlternatif
        criteria_ids = self.db_session.query(PerbandinganAlternatif.kriteria_id).distinct().all()
        criteria_ids = [id[0] for id in criteria_ids]  # Flatten the result
        kriteria_size = len(criteria_ids)

        # Initialize a dictionary to hold matrices for each criterion
        self.arrayNilaiPerbandinganAlternatif = {kriteria_id: [[1.0 for _ in range(alternatif_size)] for _ in range(alternatif_size)] for kriteria_id in criteria_ids}

        # Populate the alternative comparison matrices based on kriteria_id
        for record in self.db_session.query(PerbandinganAlternatif).all():
            alternatif1_id = alternatif_ids.index(record.alternatif_id_1)
            alternatif2_id = alternatif_ids.index(record.alternatif_id_2)
            kriteria_id = record.kriteria_id
            
            # Get the matrix for the specific criterion
            if kriteria_id in self.arrayNilaiPerbandinganAlternatif:
                matrix = self.arrayNilaiPerbandinganAlternatif[kriteria_id]

                if alternatif1_id < alternatif_size and alternatif2_id < alternatif_size:
                    matrix[alternatif1_id][alternatif2_id] = record.nilai
                    matrix[alternatif2_id][alternatif1_id] = 1 / record.nilai if record.nilai != 0 else 1
        print(self.arrayNilaiPerbandinganAlternatif)
        # Print the matrices for each criterion
        for kriteria_id, matrix in self.arrayNilaiPerbandinganAlternatif.items():
            print(f"Kriteria ID {kriteria_id}:")
            for row in matrix:
                print(row)

    def hitungJumlahNilaiPerbandingan(self, matrix):
        return [sum(row) for row in zip(*matrix)]

    def hitungNilaiEigen(self, matrix, jumlahNilaiPerbandingan):
        return [[value / jumlahNilaiPerbandingan[j] for j, value in enumerate(row)] for row in matrix]

    def hitungJumlahNilaiEigen(self, arrNilaiEigen):
        return [sum(row) for row in arrNilaiEigen]

    def hitungRataEigen(self, arrJumlahNilaiEigen):
        return [total / len(arrJumlahNilaiEigen) for total in arrJumlahNilaiEigen]
    

    def hitungAHP(self):
        self.get_matrix_kriteria_from_db()  # Get criteria matrix from database
        jumlahNilaiPerbandinganKriteria = self.hitungJumlahNilaiPerbandingan(self.arrayNilaiPerbandinganKriteria)
        arrNilaiEigenKriteria = self.hitungNilaiEigen(self.arrayNilaiPerbandinganKriteria, jumlahNilaiPerbandinganKriteria)
        arrJumlahNilaiEigenKriteria = self.hitungJumlahNilaiEigen(arrNilaiEigenKriteria)
        arrRatarataKriteria = self.hitungRataEigen(arrJumlahNilaiEigenKriteria)
        # print("jumlahNilaiPerbandinganKriteria", jumlahNilaiPerbandinganKriteria)
        # print("arrNilaiEigenKriteria", arrNilaiEigenKriteria)
        # print("arrJumlahNilaiEigenKriteria", arrJumlahNilaiEigenKriteria)
        # print("arrRatarataKriteria", arrRatarataKriteria)
        
        self.get_matrix_alternatif_from_db()  # Get alternative matrix from database
        arrRatarataAlternatif = []
        for kriteria_id, matrix in self.arrayNilaiPerbandinganAlternatif.items():
            jumlahNilaiPerbandingan = self.hitungJumlahNilaiPerbandingan(matrix)
            arrNilaiEigen = self.hitungNilaiEigen(matrix, jumlahNilaiPerbandingan)
            arrJumlahNilaiEigen = self.hitungJumlahNilaiEigen(arrNilaiEigen)
            arrRatarata = self.hitungRataEigen(arrJumlahNilaiEigen)
            arrRatarataAlternatif.append(arrRatarata)
        arrRatarataAlternatif = list(map(list, zip(*arrRatarataAlternatif)))

        print("arrRatarataAlternatif:", arrRatarataAlternatif)

        return arrRatarataKriteria, arrRatarataAlternatif