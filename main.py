from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configurare baza de date pe un server extern (exemplu folosind PostgreSQL pe un server cloud)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@hostname/database_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Model pentru masuratori de mediu
class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat()
        }


# Initializare baza de date
@app.before_first_request
def create_tables():
    db.create_all()


# Endpoint GET pentru colectia de masuratori
@app.route('/measurements', methods=['GET'])
def get_measurements():
    measurements = Measurement.query.all()
    return jsonify([m.to_dict() for m in measurements]), 200


# Endpoint POST pentru adaugarea unei masuratori
@app.route('/measurements', methods=['POST'])
def create_measurement():
    data = request.get_json()
    if not data.get('type') or not data.get('value') or not data.get('unit') or not data.get('timestamp'):
        return jsonify({"error": "Missing required fields."}), 400

    measurement = Measurement(
        type=data['type'],
        value=data['value'],
        unit=data['unit'],
        timestamp=data['timestamp']
    )
    db.session.add(measurement)
    db.session.commit()
    return jsonify(measurement.to_dict()), 201


# Endpoint GET pentru un item specific
@app.route('/measurements/<int:id>', methods=['GET'])
def get_measurement(id):
    measurement = Measurement.query.get(id)
    if not measurement:
        return jsonify({"error": "Measurement not found."}), 404
    return jsonify(measurement.to_dict()), 200


# Endpoint PUT pentru actualizarea unui item
@app.route('/measurements/<int:id>', methods=['PUT'])
def update_measurement(id):
    data = request.get_json()
    measurement = Measurement.query.get(id)
    if not measurement:
        return jsonify({"error": "Measurement not found."}), 404

    measurement.type = data.get('type', measurement.type)
    measurement.value = data.get('value', measurement.value)
    measurement.unit = data.get('unit', measurement.unit)
    measurement.timestamp = data.get('timestamp', measurement.timestamp)

    db.session.commit()
    return jsonify(measurement.to_dict()), 200


# Endpoint DELETE pentru stergerea unui item
@app.route('/measurements/<int:id>', methods=['DELETE'])
def delete_measurement(id):
    measurement = Measurement.query.get(id)
    if not measurement:
        return jsonify({"error": "Measurement not found."}), 404

    db.session.delete(measurement)
    db.session.commit()
    return '', 204


# Servire pagina HTML principala
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
