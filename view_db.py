 
import sqlite3
import os

# Find the database file
db_path = 'agrocare.db'

if not os.path.exists(db_path):
    print(f"❌ Database file '{db_path}' not found!")
    print("Make sure you have run the application first.")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 90)
print("🌾 AGROCARE - SENSOR DATA DATABASE")
print("=" * 90)

# Get all sensor readings
cursor.execute("""
    SELECT 
        s.id,
        f.name as field_name,
        s.soil_moisture,
        s.temperature,
        s.humidity,
        s.rainfall,
        s.timestamp
    FROM sensor_readings s
    JOIN fields f ON s.field_id = f.id
    ORDER BY s.timestamp DESC
""")

readings = cursor.fetchall()

if readings:
    print(f"\n📊 Total Sensor Readings: {len(readings)}\n")
    print(f"{'ID':<5} {'Field Name':<20} {'Moisture':<12} {'Temp':<10} {'Humidity':<10} {'Rainfall':<10} {'Timestamp':<20}")
    print("-" * 95)
    
    for row in readings:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<12}% {row[3]:<10}°C {row[4]:<10}% {row[5]:<10}mm {row[6][:19]:<20}")
else:
    print("\n⚠️ No sensor readings found!")
    print("1. Login to the application")
    print("2. Click 'Simulate Sensor Data' button")
    print("3. Run it 5-10 times")
    print("4. Then run this script again")

# Summary
print("\n" + "=" * 90)
print("📈 SUMMARY")
print("=" * 90)

cursor.execute("SELECT COUNT(*) FROM sensor_readings")
total = cursor.fetchone()[0]
print(f"📈 Total readings: {total}")

if total > 0:
    cursor.execute("SELECT AVG(soil_moisture) FROM sensor_readings")
    avg = cursor.fetchone()[0]
    print(f"💧 Average soil moisture: {avg:.1f}%")
    
    cursor.execute("SELECT MIN(soil_moisture), MAX(soil_moisture) FROM sensor_readings")
    min_m, max_m = cursor.fetchone()
    print(f"📉 Soil moisture range: {min_m:.1f}% - {max_m:.1f}%")
    
    cursor.execute("SELECT AVG(temperature) FROM sensor_readings")
    avg_t = cursor.fetchone()[0]
    print(f"🌡️ Average temperature: {avg_t:.1f}°C")
    
    cursor.execute("SELECT AVG(rainfall) FROM sensor_readings WHERE rainfall > 0")
    rain = cursor.fetchone()[0]
    if rain:
        print(f"☔ Average rainfall (when raining): {rain:.1f}mm")
    
    cursor.execute("SELECT COUNT(*) FROM sensor_readings WHERE rainfall > 0")
    rainy = cursor.fetchone()[0]
    print(f"🌧️ Readings with rain: {rainy} ({rainy/total*100:.1f}%)")

# Per field summary
print("\n📊 PER FIELD SUMMARY")
print("-" * 50)
cursor.execute("""
    SELECT 
        f.name,
        COUNT(s.id) as readings_count,
        ROUND(AVG(s.soil_moisture), 1) as avg_moisture,
        ROUND(AVG(s.temperature), 1) as avg_temp,
        ROUND(AVG(s.rainfall), 1) as avg_rain
    FROM sensor_readings s
    JOIN fields f ON s.field_id = f.id
    GROUP BY f.name
""")

for row in cursor.fetchall():
    print(f"🌾 {row[0]}: {row[1]} readings | Moisture: {row[2]}% | Temp: {row[3]}°C | Rain: {row[4]}mm")

conn.close()