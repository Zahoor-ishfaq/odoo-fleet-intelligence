import xmlrpc.client
import random
from datetime import datetime, timedelta
from faker import Faker

URL = 'http://localhost:8069'
DB = 'fleet_dev'
USERNAME = 'admin@test.com'
PASSWORD = 'Zahur123'

NUM_VEHICLES = 20
NUM_TRIPS = 500
NUM_FUEL_LOGS = 1000
NUM_MAINTENANCE = 200

fake = Faker()

SAUDI_CITIES = {
    'Riyadh': (24.7136, 46.6753),
    'Jeddah': (21.4858, 39.1925),
    'Dammam': (26.4207, 50.0888),
    'Mecca': (21.3891, 39.8579),
    'Medina': (24.5247, 39.5692),
    'Taif': (21.2703, 40.4158),
    'Tabuk': (28.3835, 36.5662),
    'Abha': (18.2164, 42.5053),
    'Khobar': (26.2172, 50.1971),
    'Buraidah': (26.3260, 43.9750),
    'Hail': (27.5219, 41.6907),
    'Najran': (17.4924, 44.1277),
    'Jubail': (27.0046, 49.6600),
    'Yanbu': (24.0894, 38.0618),
}

CITY_LIST = list(SAUDI_CITIES.keys())

VEHICLE_MAKES = [
    ('Toyota', ['Hilux', 'Hiace', 'Land Cruiser', 'Dyna']),
    ('Isuzu', ['D-Max', 'NPR', 'FVR', 'FTR']),
    ('Mercedes-Benz', ['Actros', 'Sprinter', 'Atego']),
    ('Hyundai', ['H1', 'Porter', 'HD65', 'HD78']),
    ('Mitsubishi', ['Canter', 'L200', 'Fuso']),
    ('MAN', ['TGS', 'TGX']),
    ('Volvo', ['FH', 'FM']),
]

MAINTENANCE_TYPES = ['oil_change', 'tire_change', 'brake_service', 'engine_repair', 'general_service']
MAINTENANCE_WEIGHTS = [40, 20, 15, 10, 15]

SAUDI_FIRST_NAMES = ['Ahmed', 'Mohammed', 'Abdullah', 'Khalid', 'Omar', 'Faisal', 'Saad', 'Fahad',
                    'Nasser', 'Turki', 'Sultan', 'Bandar', 'Waleed', 'Yousef', 'Ibrahim', 'Salem']
SAUDI_LAST_NAMES = ['Al-Ghamdi', 'Al-Harbi', 'Al-Otaibi', 'Al-Qahtani', 'Al-Shehri', 'Al-Zahrani',
                   'Al-Malki', 'Al-Dosari', 'Al-Anazi', 'Al-Mutairi', 'Al-Shammari', 'Al-Juhani']


def connect():
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        raise RuntimeError('Authentication failed')
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    return uid, models


def create(models, uid, model_name, values):
    return models.execute_kw(DB, uid, PASSWORD, model_name, 'create', [values])


def haversine_km(city_a, city_b):
    import math
    lat1, lon1 = SAUDI_CITIES[city_a]
    lat2, lon2 = SAUDI_CITIES[city_b]
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return r * c


def saudi_driver_name():
    return f'{random.choice(SAUDI_FIRST_NAMES)} {random.choice(SAUDI_LAST_NAMES)}'


def generate_plate():
    letters = random.sample('ABDEGHJKLNRSTUVXZ', 3)
    digits = random.randint(1000, 9999)
    return f'{"".join(letters)} {digits}'


def generate_vehicles(models, uid):
    print('Generating vehicles...')
    ids = []
    for _ in range(NUM_VEHICLES):
        make, model_list = random.choice(VEHICLE_MAKES)
        vehicle_id = create(models, uid, 'fleet.vehicle.custom', {
            'plate_number': generate_plate(),
            'make': make,
            'model': random.choice(model_list),
            'year': random.randint(2015, 2024),
            'status': random.choices(['active', 'maintenance', 'inactive'], weights=[80, 15, 5])[0],
            'odometer': round(random.uniform(20000, 350000), 0),
        })
        ids.append(vehicle_id)
    print(f'  Created {len(ids)} vehicles')
    return ids


def generate_trips(models, uid, vehicle_ids):
    print('Generating trips...')
    workhorses = random.sample(vehicle_ids, k=max(1, len(vehicle_ids) // 3))
    ids = []
    for i in range(NUM_TRIPS):
        vehicle_id = random.choice(workhorses) if random.random() < 0.6 else random.choice(vehicle_ids)
        origin = random.choice(CITY_LIST)
        destination = random.choice([c for c in CITY_LIST if c != origin])
        distance = haversine_km(origin, destination) * random.uniform(1.05, 1.25)
        distance = round(distance, 1)

        start = fake.date_time_between(start_date='-6M', end_date='now')
        avg_speed_kmh = random.uniform(60, 85)
        duration_hours = distance / avg_speed_kmh
        end = start + timedelta(hours=duration_hours)

        rate_per_km = random.uniform(2.5, 4.5)
        revenue = round(distance * rate_per_km, 2)

        fuel_cost = distance * random.uniform(0.28, 0.42) * 2.33
        driver_cost = duration_hours * random.uniform(35, 55)
        cost = round(fuel_cost + driver_cost + random.uniform(50, 200), 2)

        if random.random() < 0.12:
            revenue = round(revenue * random.uniform(0.4, 0.7), 2)

        trip_id = create(models, uid, 'fleet.trip', {
            'name': f'TRIP/{start.year}/{i+1:05d}',
            'vehicle_id': vehicle_id,
            'driver_name': saudi_driver_name(),
            'origin': origin,
            'destination': destination,
            'distance_km': distance,
            'start_time': start.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end.strftime('%Y-%m-%d %H:%M:%S'),
            'revenue': revenue,
            'cost': cost,
        })
        ids.append(trip_id)
        if (i + 1) % 100 == 0:
            print(f'  {i+1}/{NUM_TRIPS} trips')
    print(f'  Created {len(ids)} trips')
    return ids


def generate_fuel_logs(models, uid, vehicle_ids):
    print('Generating fuel logs...')
    ids = []
    odometers = {vid: random.uniform(20000, 100000) for vid in vehicle_ids}
    anomaly_count = 0

    for i in range(NUM_FUEL_LOGS):
        vehicle_id = random.choice(vehicle_ids)
        date = fake.date_between(start_date='-6M', end_date='today')
        km_since_last = random.uniform(200, 600)
        odometers[vehicle_id] += km_since_last
        liters = km_since_last * random.uniform(0.30, 0.40)
        price_per_liter = round(random.uniform(2.18, 2.45), 2)
        cost = liters * price_per_liter

        is_anomaly = random.random() < 0.10
        if is_anomaly:
            anomaly_type = random.choice(['over_report', 'ghost_fuel', 'inflated_cost'])
            if anomaly_type == 'over_report':
                liters *= random.uniform(2.0, 3.5)
                cost = liters * price_per_liter
            elif anomaly_type == 'ghost_fuel':
                odometers[vehicle_id] -= km_since_last * random.uniform(0.90, 0.98)
                cost = liters * price_per_liter
            elif anomaly_type == 'inflated_cost':
                cost = liters * price_per_liter * random.uniform(1.8, 2.5)
            anomaly_count += 1

        liters = round(liters, 2)
        cost = round(cost, 2)

        fuel_id = create(models, uid, 'fleet.fuel.log', {
            'name': f'FUEL/{date.year}/{i+1:05d}',
            'vehicle_id': vehicle_id,
            'date': date.strftime('%Y-%m-%d'),
            'liters': liters,
            'cost': cost,
            'odometer': round(odometers[vehicle_id], 1),
        })
        ids.append(fuel_id)
        if (i + 1) % 200 == 0:
            print(f'  {i+1}/{NUM_FUEL_LOGS} fuel logs')

    print(f'  Created {len(ids)} fuel logs ({anomaly_count} anomalies injected)')
    return ids


def generate_maintenance(models, uid, vehicle_ids):
    print('Generating maintenance records...')
    ids = []
    high_mileage = random.sample(vehicle_ids, k=max(1, len(vehicle_ids) // 3))
    for i in range(NUM_MAINTENANCE):
        vehicle_id = random.choice(high_mileage) if random.random() < 0.7 else random.choice(vehicle_ids)
        mtype = random.choices(MAINTENANCE_TYPES, weights=MAINTENANCE_WEIGHTS)[0]
        date = fake.date_between(start_date='-1y', end_date='today')

        cost_ranges = {
            'oil_change': (150, 400),
            'tire_change': (1500, 4000),
            'brake_service': (500, 1500),
            'engine_repair': (3000, 15000),
            'general_service': (300, 800),
        }
        cost = round(random.uniform(*cost_ranges[mtype]), 2)
        odometer = round(random.uniform(30000, 400000), 0)
        next_due = odometer + random.choice([5000, 10000, 15000, 20000])

        maint_id = create(models, uid, 'fleet.maintenance.custom', {
            'name': f'MAINT/{date.year}/{i+1:05d}',
            'vehicle_id': vehicle_id,
            'maintenance_type': mtype,
            'date': date.strftime('%Y-%m-%d'),
            'cost': cost,
            'odometer_at_service': odometer,
            'next_due_km': next_due,
        })
        ids.append(maint_id)
    print(f'  Created {len(ids)} maintenance records')
    return ids


if __name__ == '__main__':
    uid, models = connect()
    print(f'Connected to Odoo. UID: {uid}\n')

    vehicle_ids = generate_vehicles(models, uid)
    generate_trips(models, uid, vehicle_ids)
    generate_fuel_logs(models, uid, vehicle_ids)
    generate_maintenance(models, uid, vehicle_ids)

    print('\nAll data generated successfully.')