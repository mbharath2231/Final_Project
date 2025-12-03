# scripts/config.py

# ---------------------------------------------------------
# 1. API KEYS (PASTE YOURS HERE)
# ---------------------------------------------------------
ADZUNA_APP_ID  = "4754d954"
ADZUNA_APP_KEY = "ccada37fb80ad1dca86725f13f365a45"
BLS_API_KEY    = "f6f87ced7a0c4da49d713c60b8c4d9cf"

# ---------------------------------------------------------
# 2. STATE ABBREVIATIONS (Used for parsing locations)
# ---------------------------------------------------------
STATE_MAP = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
}

# ---------------------------------------------------------
# 3. CITY REFERENCE (Used for enriching economic data)
# ---------------------------------------------------------
CITY_TO_STATE = {
    'New York': 'NY', 'Los Angeles': 'CA', 'Chicago': 'IL', 'Dallas': 'TX', 'Houston': 'TX',
    'Washington DC': 'DC', 'Miami': 'FL', 'Philadelphia': 'PA', 'Atlanta': 'GA', 'Boston': 'MA',
    'Phoenix': 'AZ', 'San Francisco': 'CA', 'Seattle': 'WA', 'San Diego': 'CA', 'Denver': 'CO',
    'Austin': 'TX', 'San Jose': 'CA', 'Nashville': 'TN', 'Charlotte': 'NC', 'Raleigh': 'NC',
    'Portland': 'OR', 'Minneapolis': 'MN', 'Detroit': 'MI', 'Tampa': 'FL', 'Orlando': 'FL',
    'Baltimore': 'MD', 'St. Louis': 'MO', 'Pittsburgh': 'PA', 'Sacramento': 'CA', 'Las Vegas': 'NV',
    'San Antonio': 'TX', 'Kansas City': 'MO', 'Columbus': 'OH', 'Indianapolis': 'IN', 'Cleveland': 'OH',
    'Cincinnati': 'OH', 'Salt Lake City': 'UT', 'Madison': 'WI', 'Milwaukee': 'WI', 'Buffalo': 'NY',
    'Richmond': 'VA', 'Virginia Beach': 'VA', 'Providence': 'RI', 'Hartford': 'CT', 'New Orleans': 'LA',
    'Louisville': 'KY', 'Memphis': 'TN', 'Oklahoma City': 'OK', 'Tulsa': 'OK', 'Albuquerque': 'NM',
    'Tucson': 'AZ', 'El Paso': 'TX', 'Honolulu': 'HI', 'Omaha': 'NE'
}

# ---------------------------------------------------------
# 4. TECH SKILLS LIST (Dictionary for NLP)
# ---------------------------------------------------------
TECH_SKILLS = [
    "Python", "SQL", "AWS", "Machine Learning", "Deep Learning", "Pandas", "NumPy",
    "Tableau", "Power BI", "Excel", "Spark", "Hadoop", "Java", "C++", "C#",
    "Azure", "GCP", "Docker", "Kubernetes", "Linux", "Git", "TensorFlow", "PyTorch",
    "Scikit-learn", "NLP", "Computer Vision", "R", "SAS", "Matlab", "Scala",
    "Airflow", "Snowflake", "Databricks", "Redshift", "BigQuery", "NoSQL", "MongoDB",
    "PostgreSQL", "React", "Angular", "Vue", "JavaScript", "HTML", "CSS", "Node.js",
    "Django", "Flask", "Spring", "API", "REST", "GraphQL", "DevOps", "CI/CD",
    "Terraform", "Jenkins", "Ansible", "JIRA", "Agile", "Scrum"
]

# ---------------------------------------------------------
# 5. STATE COORDINATES (Centroids for Map Visualization)
# ---------------------------------------------------------
STATE_COORDS = {
    'AL': (32.8, -86.8), 'AK': (61.3, -152.4), 'AZ': (33.7, -111.4), 'AR': (34.9, -92.3),
    'CA': (36.1, -119.6), 'CO': (39.0, -105.3), 'CT': (41.6, -72.7), 'DC': (38.9, -77.0),
    'DE': (39.3, -75.5), 'FL': (27.7, -81.5), 'GA': (33.0, -83.6), 'HI': (21.0, -157.4),
    'ID': (44.2, -114.4), 'IL': (40.3, -88.9), 'IN': (39.8, -86.2), 'IA': (42.0, -93.2),
    'KS': (38.5, -96.7), 'KY': (37.6, -84.6), 'LA': (31.1, -91.8), 'ME': (44.6, -69.3),
    'MD': (39.0, -76.8), 'MA': (42.2, -71.5), 'MI': (43.3, -84.5), 'MN': (45.6, -93.9),
    'MS': (32.7, -89.6), 'MO': (38.4, -92.2), 'MT': (46.9, -110.4), 'NE': (41.1, -98.2),
    'NV': (38.3, -117.2), 'NH': (43.4, -71.5), 'NJ': (40.2, -74.5), 'NM': (34.8, -106.2),
    'NY': (42.1, -74.9), 'NC': (35.6, -79.8), 'ND': (47.5, -99.7), 'OH': (40.3, -82.9),
    'OK': (35.5, -96.9), 'OR': (44.5, -122.0), 'PA': (40.5, -77.2), 'RI': (41.6, -71.5),
    'SC': (33.8, -80.9), 'SD': (44.2, -99.9), 'TN': (35.7, -86.6), 'TX': (31.0, -97.5),
    'UT': (40.1, -111.8), 'VT': (44.0, -72.7), 'VA': (37.7, -78.1), 'WA': (47.4, -120.7),
    'WV': (38.4, -80.9), 'WI': (44.2, -89.6), 'WY': (42.7, -107.2)
}