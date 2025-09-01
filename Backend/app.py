from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="agriconnect"
)
cursor = db.cursor()

@app.route('/')
def index():
    cursor.execute("SELECT * FROM donations")
    donations = cursor.fetchall()
    return render_template('index.html', donations=donations)

@app.route('/donate', methods=['POST'])
def donate():
    name = request.form['name']
    location = request.form['location']
    food_amount = request.form['food_amount']

    cursor.execute(
        "INSERT INTO donations (name, location, food_amount) VALUES (%s, %s, %s)",
        (name, location, food_amount)
    )
    db.commit()

    flash("Thank you! Your donation has been recorded.")  # Flash message
    return redirect(url_for('index'))

# -------- Crop recommendation rules (simple + hackathon-friendly) ----------
def recommend_crop(soil, rainfall, season):
    soil = soil.lower().strip()
    rainfall = rainfall.lower().strip()
    season = season.lower().strip()

    # Very simple rule set you can expand later
    if soil == "loamy" and rainfall == "high":
        crops = ["Maize", "Beans", "Bananas"]
    elif soil == "loamy" and rainfall == "medium":
        crops = ["Maize", "Beans", "Tomatoes"]
    elif soil == "sandy" and season == "dry":
        crops = ["Millet", "Sorghum", "Cassava"]
    elif soil == "sandy" and rainfall == "low":
        crops = ["Cowpeas", "Groundnuts"]
    elif soil == "clay" and rainfall in ["medium", "high"]:
        crops = ["Rice", "Sweet Potatoes"]
    else:
        crops = ["Cowpeas", "Cassava", "Green Grams"]

    return crops

# ------------------------- Farmer page -------------------------
@app.route("/farmer", methods=["GET", "POST"])
def farmer():
    if request.method == "POST":
        soil = request.form["soil"]
        rainfall = request.form["rainfall"]
        season = request.form["season"]

        crops = recommend_crop(soil, rainfall, season)

        # Save query + result to DB
        rec_str = ", ".join(crops)
        cursor.execute(
            "INSERT INTO farmer_queries (soil, rainfall, season, recommended) VALUES (%s, %s, %s, %s)",
            (soil, rainfall, season, rec_str)
        )
        db.commit()

        # Get recent history (latest 5)
        cursor.execute("SELECT soil, rainfall, season, recommended, created_at FROM farmer_queries ORDER BY id DESC LIMIT 5")
        history = cursor.fetchall()

        return render_template("farmer.html", crops=crops, soil=soil, rainfall=rainfall, season=season, history=history)

    # GET: just show empty form + recent history
    cursor.execute("SELECT soil, rainfall, season, recommended, created_at FROM farmer_queries ORDER BY id DESC LIMIT 5")
    history = cursor.fetchall()
    return render_template("farmer.html", crops=None, soil=None, rainfall=None, season=None, history=history)
# county -> recommended crops (Kenya, 47 counties)
crop_recommendations = {
    "Nairobi": ["Kale (Sukuma wiki)", "Tomatoes", "Irish potatoes", "Leafy vegetables"],
    "Mombasa": ["Coconut", "Cassava", "Mango", "Banana"],
    "Kwale": ["Cassava", "Coconut", "Cashew", "Mango"],
    "Kilifi": ["Cassava", "Coconut", "Mango", "Pigeon peas"],
    "Tana River": ["Rice (irrigated)", "Mango", "Banana", "Pigeon peas"],
    "Lamu": ["Coconut", "Cashew", "Mango", "Salt-tolerant vegetables"],
    "Taita-Taveta": ["Maize", "Green grams", "Cassava", "Horticultural vegetables"],
    "Garissa": ["Sorghum", "Millet", "Cowpeas", "Drought-tolerant vegetables"],
    "Wajir": ["Sorghum", "Millet", "Cowpeas", "Drought fodder"],
    "Mandera": ["Sorghum", "Millet", "Cowpeas", "Date palms"],
    "Marsabit": ["Drought-tolerant sorghum", "Millet", "Pigeon peas", "Fodder shrubs"],
    "Isiolo": ["Sorghum", "Millet", "Cowpeas", "Fodder (Napier/legume mixes where irrigated)"],
    "Meru": ["Coffee", "Tea (highland pockets)", "Irish potatoes", "Miraa (khat)"],
    "Tharaka-Nithi": ["Macadamia (where suitable)", "Tea (highlands)", "Coffee", "Banana"],
    "Embu": ["Coffee", "Tea (upper slopes)", "Irish potatoes", "Macadamia"],
    "Kitui": ["Pigeon peas", "Cassava", "Millet", "Cowpeas (drought tolerant legumes)"],
    "Machakos": ["Pigeon peas", "Cassava", "Kales", "Sunflower"],
    "Makueni": ["Pigeon peas", "Cassava", "Millet", "Fruit trees (mango, citrus)"],
    "Nyandarua": ["Irish potatoes", "Vegetables (kale, spinach)", "Barley", "Dairy fodder"],
    "Nyeri": ["Tea (highlands)", "Coffee", "Potatoes", "Vegetables"],
    "Kirinyaga": ["Rice (irrigation in Mwea)", "Tea (slopes)", "Coffee", "Maize"],
    "Murang'a": ["Tea (highlands)", "Coffee", "Kales", "Irish potatoes"],
    "Kiambu": ["Tea (where high), vegetables, avocado, coffee (pockets)"],
    "Turkana": ["Drought-tolerant sorghum", "Millet", "Cowpeas", "Opuntia/fruit for arid areas"],
    "West Pokot": ["Maize (highlands)", "Sorghum", "Beans", "Groundnuts"],
    "Samburu": ["Sorghum", "Millet", "Cowpeas", "Fodder shrubs"],
    "Trans Nzoia": ["Maize", "Irish potatoes", "Wheat", "Vegetables"],
    "Uasin Gishu": ["Maize", "Wheat", "Potatoes", "Onions"],
    "Elgeyo-Marakwet": ["Maize (terraces)", "Vegetables", "Tea (pockets)"],
    "Nandi": ["Tea (highlands)", "Maize", "Irish potatoes", "Vegetables"],
    "Baringo": ["Maize (irrigated), sorghum, millet, pawpaw (irrigated pockets)"],
    "Laikipia": ["Wheat", "Barley", "Horticulture (greenhouse)", "Forage crops"],
    "Nakuru": ["Irish potatoes", "Maize", "Vegetables", "Onions"],
    "Narok": ["Maize", "Wheat (uplands)", "Barley", "Vegetables"],
    "Kajiado": ["Drought-tolerant legumes", "Fodder crops", "Olives (dryland)"],
    "Kericho": ["Tea", "Maize", "Vegetables", "Irish potatoes"],
    "Bomet": ["Tea", "Maize", "Irish potatoes", "Vegetables"],
    "Kakamega": ["Sugarcane", "Maize", "Banana (matoke)", "Beans"],
    "Vihiga": ["Tea (highland pockets)", "Maize", "Vegetables", "Banana"],
    "Bungoma": ["Sugarcane", "Maize", "Beans", "Banana"],
    "Busia": ["Maize", "Sugarcane (in parts)", "Groundnuts", "Cassava"],
    "Siaya": ["Rice (irrigated pockets)", "Maize", "Sugarcane (pockets)", "Beans"],
    "Kisumu": ["Rice (Ahero), Maize, Sugarcane (pockets), Vegetables"],
    "Homa Bay": ["Maize", "Sugarcane (pockets)", "Cassava", "Beans"],
    "Migori": ["Sugarcane", "Maize", "Tea (highlands)", "Pineapple (pockets)"],
    "Kisii": ["Banana", "Tea (highlands)", "Irish potatoes", "Avocado"],
    "Nyamira": ["Tea", "Banana", "Irish potatoes", "Vegetables"]
}

@app.route("/recommend", methods=["POST"])
def recommend():
    location = request.form["location"].strip().title()  # normalize input
    crops = crop_recommendations.get(location)

    if not crops:
        flash(f"Sorry, no specific data for '{location}'. Try another county.")
        return redirect(url_for("index"))

    flash(f"In {location}, suitable crops are: {', '.join(crops)}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

