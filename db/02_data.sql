-- SYNTHETIC. Operators and site names are invented; cities are real.
TRUNCATE stations RESTART IDENTITY;

INSERT INTO stations
  (name, operator, city, state, connector_type, power_kw, connectors, status, price_per_kwh, commissioned_on)
VALUES
  ('Phoenix Mall Hub',      'VoltGrid',   'Pune',      'Maharashtra',   'CCS2',    60.0, 4, 'live',        18.50, '2024-03-12'),
  ('Amanora Park Town',     'VoltGrid',   'Pune',      'Maharashtra',   'CCS2',   120.0, 6, 'live',        21.00, '2024-07-01'),
  ('Baner Road Plaza',      'ChargeNova', 'Pune',      'Maharashtra',   'Type2',   22.0, 2, 'live',        14.00, '2023-11-20'),
  ('Hinjewadi Tech Park',   'ChargeNova', 'Pune',      'Maharashtra',   'CCS2',   150.0, 8, 'live',        22.50, '2025-01-15'),
  ('Kharadi IT Annexe',     'PowerLoop',  'Pune',      'Maharashtra',   'Type2',   22.0, 4, 'maintenance', 14.50, '2024-05-09'),
  ('Wakad Junction',        'VoltGrid',   'Pune',      'Maharashtra',   'CHAdeMO', 50.0, 2, 'live',        19.00, '2023-08-30'),
  ('Viman Nagar Central',   'PowerLoop',  'Pune',      'Maharashtra',   'CCS2',    60.0, 4, 'planned',     NULL,  NULL),

  ('Koramangala Forum',     'ChargeNova', 'Bengaluru', 'Karnataka',     'CCS2',   120.0, 6, 'live',        20.00, '2024-02-18'),
  ('Whitefield Exchange',   'VoltGrid',   'Bengaluru', 'Karnataka',     'CCS2',   150.0,10, 'live',        23.00, '2025-03-02'),
  ('Indiranagar Metro',     'PowerLoop',  'Bengaluru', 'Karnataka',     'Type2',   22.0, 3, 'live',        13.50, '2023-06-11'),
  ('Electronic City Gate',  'ChargeNova', 'Bengaluru', 'Karnataka',     'CCS2',    60.0, 4, 'live',        18.00, '2024-09-25'),
  ('Hebbal Flyover Stop',   'VoltGrid',   'Bengaluru', 'Karnataka',     'CHAdeMO', 50.0, 2, 'maintenance', 19.50, '2023-12-04'),
  ('Jayanagar 4th Block',   'PowerLoop',  'Bengaluru', 'Karnataka',     'Type2',   11.0, 2, 'live',        12.00, '2023-04-19'),
  ('Marathahalli Bridge',   'ChargeNova', 'Bengaluru', 'Karnataka',     'CCS2',   120.0, 6, 'planned',     NULL,  NULL),

  ('Cyber Hub Level 2',     'VoltGrid',   'Gurugram',  'Haryana',       'CCS2',   150.0, 8, 'live',        24.00, '2024-11-08'),
  ('MG Road Metro Park',    'PowerLoop',  'Gurugram',  'Haryana',       'Type2',   22.0, 4, 'live',        15.00, '2024-01-22'),
  ('Golf Course Extension', 'ChargeNova', 'Gurugram',  'Haryana',       'CCS2',    60.0, 4, 'live',        19.50, '2023-10-14'),
  ('Sohna Road Depot',      'VoltGrid',   'Gurugram',  'Haryana',       'CCS2',   120.0, 6, 'maintenance', 21.50, '2025-02-27'),

  ('Connaught Place North', 'PowerLoop',  'New Delhi', 'Delhi',         'CCS2',    60.0, 4, 'live',        20.50, '2023-09-05'),
  ('Saket District Centre', 'VoltGrid',   'New Delhi', 'Delhi',         'CCS2',   120.0, 6, 'live',        22.00, '2024-06-17'),
  ('Dwarka Sector 21',      'ChargeNova', 'New Delhi', 'Delhi',         'Type2',   22.0, 3, 'live',        14.50, '2024-04-03'),
  ('Rohini West Terminal',  'PowerLoop',  'New Delhi', 'Delhi',         'CHAdeMO', 50.0, 2, 'live',        18.50, '2023-07-29'),
  ('Aerocity Arrival',      'VoltGrid',   'New Delhi', 'Delhi',         'CCS2',   150.0, 8, 'planned',     NULL,  NULL),

  ('Bandra Kurla Complex',  'ChargeNova', 'Mumbai',    'Maharashtra',   'CCS2',   150.0,10, 'live',        25.00, '2025-04-11'),
  ('Powai Lakeside',        'VoltGrid',   'Mumbai',    'Maharashtra',   'CCS2',    60.0, 4, 'live',        21.00, '2024-08-19'),
  ('Andheri East Junction', 'PowerLoop',  'Mumbai',    'Maharashtra',   'Type2',   22.0, 4, 'live',        16.00, '2023-05-23'),
  ('Lower Parel Mills',     'ChargeNova', 'Mumbai',    'Maharashtra',   'CCS2',   120.0, 6, 'maintenance', 23.50, '2024-10-30'),
  ('Navi Mumbai Vashi',     'VoltGrid',   'Mumbai',    'Maharashtra',   'CCS2',    60.0, 4, 'live',        19.00, '2024-02-07'),

  ('OMR Sholinganallur',    'PowerLoop',  'Chennai',   'Tamil Nadu',    'CCS2',   120.0, 6, 'live',        20.00, '2024-12-01'),
  ('T Nagar Ranganathan',   'ChargeNova', 'Chennai',   'Tamil Nadu',    'Type2',   22.0, 3, 'live',        14.00, '2023-03-16'),
  ('Guindy Industrial',     'VoltGrid',   'Chennai',   'Tamil Nadu',    'CCS2',    60.0, 4, 'live',        18.50, '2024-05-28'),
  ('Velachery Bypass',      'PowerLoop',  'Chennai',   'Tamil Nadu',    'CHAdeMO', 50.0, 2, 'planned',     NULL,  NULL),

  ('Hitec City Circle',     'VoltGrid',   'Hyderabad', 'Telangana',     'CCS2',   150.0, 8, 'live',        22.50, '2025-01-09'),
  ('Gachibowli Stadium',    'ChargeNova', 'Hyderabad', 'Telangana',     'CCS2',   120.0, 6, 'live',        21.00, '2024-07-14'),
  ('Banjara Hills Road 12', 'PowerLoop',  'Hyderabad', 'Telangana',     'Type2',   22.0, 3, 'live',        15.50, '2023-10-02'),
  ('Secunderabad Station',  'VoltGrid',   'Hyderabad', 'Telangana',     'CCS2',    60.0, 4, 'maintenance', 19.00, '2024-03-21'),

  ('Satellite SG Highway',  'ChargeNova', 'Ahmedabad', 'Gujarat',       'CCS2',   120.0, 6, 'live',        19.50, '2024-09-12'),
  ('Prahlad Nagar Garden',  'PowerLoop',  'Ahmedabad', 'Gujarat',       'Type2',   22.0, 2, 'live',        13.00, '2023-08-08'),
  ('Vastrapur Lake Point',  'VoltGrid',   'Ahmedabad', 'Gujarat',       'CCS2',    60.0, 4, 'live',        18.00, '2024-11-26'),

  ('Jaipur Malviya Nagar',  'ChargeNova', 'Jaipur',    'Rajasthan',     'CCS2',    60.0, 4, 'live',        18.50, '2024-06-05'),
  ('World Trade Park',      'VoltGrid',   'Jaipur',    'Rajasthan',     'Type2',   22.0, 3, 'live',        14.50, '2023-12-19');
