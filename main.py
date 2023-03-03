from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Loop through each column in the data record and create a new dictionary entry;
        # where the key is the name of the column and the value is the value of the column
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    rows_count = db.session.query(Cafe).count()
    random_row = random.randint(0, rows_count - 1)
    cafe = db.session.query(Cafe).offset(random_row).first()
    return jsonify(cafe=cafe.to_dict())


@app.route("/all", methods=["GET"])
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search", methods=["GET"])
def search_cafe():
    loc = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=loc).all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    # name = request.form["name"]
    # map_url = request.form["map_url"]
    # img_url = request.form["img_url"]
    # location = request.form["location"]
    # seats = request.form["seats"]
    # has_toilet = request.form["has_toilets"]
    # has_wifi = request.form["has_wifi"]
    # has_sockets = request.form["has_sockets"]
    # can_take_calls = request.form["can_take_calls"]
    # coffee_price = request.form["coffee_price"]
    new_cafe = Cafe(name=request.form["name"],
                    map_url=request.form["map_url"],
                    img_url=request.form["img_url"],
                    location=request.form["location"],
                    seats=request.form["seats"],
                    has_toilet=True if request.form["has_toilet"] == "true" else False,
                    has_wifi=True if request.form["has_wifi"] == "true" else False,
                    has_sockets=True if request.form["has_sockets"] == "true" else False,
                    can_take_calls=True if request.form["can_take_calls"] == "true" else False,
                    coffee_price=request.form["coffee_price"])
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    if not new_price:
        return jsonify(error="Invalid price"), 400

    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the price."), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if not api_key == "TopSecretAPIKey":
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(success="Successfully deleted the cafe."), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=True)
