
CHARGER_IP = '10.0.1.1'
CHARGER_PORT = 12345

MAX_CHARGE_PERCENTAGE = 80
CHARGING_SPEED = 1

USERS = [
    {
        'UUID': '1234-5678-9101',
        'name': 'Elias',
        'valid_payment': True,
        'email': "user@gmail.com",
        'cars': [
            {
                'WIN': '1234567890ABCDEF',
                'nickname': 'Elbil',
                'make': 'Tesla',
                'model': 'Model S',
                'year': 2019
            }
        ]
    }
]

INFO = {
    'owner': "navn navnesen",
    'status': "connected",
    'current_charge': 27,
    'max_capacity': 100,
    'max_speed': CHARGING_SPEED,
}