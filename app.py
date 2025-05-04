import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Încarcă variabilele de mediu din fișierul .env
load_dotenv()

# Crearea aplicației Flask
app = Flask(__name__)

# Configurarea bazei de date
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Crearea obiectului db pentru SQLAlchemy
db = SQLAlchemy(app)


# Crearea modelului pentru măsurători
class Measurement(db.Model):
    __tablename__ = 'measurements'
    id = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Measurement {self.id}, {self.date}, {self.value}>'


# Crează tabelele în baza de date
with app.app_context():
    db.create_all()


# Ruta pentru a obține toate măsurătorile
@app.route('/measurements', methods=['GET'])
def get_measurements():
    measurements = Measurement.query.all()
    result = []
    for measurement in measurements:
        result.append({
            'id': measurement.id,
            'value': measurement.value,
            'date': measurement.date
        })
    return jsonify(result)


# Ruta pentru a obține o măsurătoare specifică
@app.route('/measurements/<id>', methods=['GET'])
def get_specific_measurement(id):
    date = request.args.get('date')  # Obținem data din query string

    # Dacă data este specificată, căutăm măsurătoarea pentru acea dată
    if date:
        measurement = Measurement.query.filter_by(id=id, date=date).first()
        if measurement:
            return jsonify({'id': measurement.id, 'value': measurement.value, 'date': measurement.date})
        else:
            return jsonify({'error': 'Measurement not found for the specified date.'}), 404
    else:
        # Dacă nu există data, returnăm măsurătoarea pentru id-ul dat
        measurement = Measurement.query.filter_by(id=id).first()
        if measurement:
            return jsonify({'id': measurement.id, 'value': measurement.value, 'date': measurement.date})
        else:
            return jsonify({'error': 'Measurement not found.'}), 404


# Ruta pentru a adăuga o nouă colecție de măsurători
@app.route('/measurements/collection', methods=['POST'])
def add_measurements_collection():
    new_data = request.get_json()

    if not isinstance(new_data, list):
        return jsonify({'error': 'Input data must be a list of measurements.'}), 400

    for entry in new_data:
        id = entry.get('id')
        value = entry.get('value')
        date = entry.get('date')

        if not id or value is None or not date:
            return jsonify({'error': 'Each measurement must have an id, value, and date.'}), 400

        # Verificăm dacă măsurătoarea există deja
        measurement = Measurement.query.filter_by(id=id, date=date).first()
        if not measurement:
            # Dacă măsurătoarea nu există, o adăugăm în baza de date
            new_measurement = Measurement(id=id, value=value, date=date)
            db.session.add(new_measurement)
            db.session.commit()

    return jsonify({'message': 'Measurements collection added successfully!'}), 201


# Ruta pentru a adăuga o măsurătoare
@app.route('/measurements', methods=['POST'])
def add_measurement():
    data = request.get_json()
    id = data.get('id')
    value = data.get('value')
    date = data.get('date')

    if not id or value is None or not date:
        return jsonify({'error': 'Each measurement must have an id, value, and date.'}), 400

    # Verificăm dacă măsurătoarea există deja
    measurement = Measurement.query.filter_by(id=id, date=date).first()
    if not measurement:
        new_measurement = Measurement(id=id, value=value, date=date)
        db.session.add(new_measurement)
        db.session.commit()
        return jsonify({'message': 'Measurement added successfully!'}), 201
    else:
        return jsonify({'error': 'Measurement already exists for this id and date.'}), 400


# Ruta pentru a actualiza o măsurătoare
@app.route('/measurements/<id>', methods=['PUT'])
def update_measurement(id):
    data = request.get_json()
    date = data.get('date')
    value = data.get('value')

    measurement = Measurement.query.filter_by(id=id, date=date).first()
    if measurement:
        measurement.value = value
        db.session.commit()
        return jsonify({'message': 'Measurement updated successfully!'})
    else:
        return jsonify({'error': 'Measurement not found for update.'}), 404


# Ruta pentru a reseta toate valorile măsurătorilor la 1
@app.route('/measurements/reset', methods=['PUT'])
def reset_all_measurements():
    measurements = Measurement.query.all()
    for measurement in measurements:
        measurement.value = 1
    db.session.commit()
    return jsonify({'message': 'All measurements have been reset to 1.'})


# Ruta pentru a șterge o măsurătoare specifică
@app.route('/measurements/<id>', methods=['DELETE'])
def delete_measurement(id):
    data = request.get_json()
    date = data.get('date')

    measurement = Measurement.query.filter_by(id=id, date=date).first()
    if measurement:
        db.session.delete(measurement)
        db.session.commit()
        return jsonify({'message': 'Measurement deleted successfully!'})
    else:
        return jsonify({'error': 'Measurement not found for deletion.'}), 404


# Ruta pentru a șterge toate măsurătorile
@app.route('/measurements', methods=['DELETE'])
def delete_all_measurements():
    db.session.query(Measurement).delete()
    db.session.commit()
    return jsonify({'message': 'All measurements deleted successfully!'}), 200


if __name__ == '__main__':
    app.run(debug=True)
