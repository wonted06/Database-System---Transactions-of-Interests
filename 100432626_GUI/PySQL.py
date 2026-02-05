import psycopg2

# Read your password securely
with open("pw.txt") as f:
    DB_password = f.read().strip()

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="fjk23wtu",
    user="fjk23wtu",
    password=DB_password,
    host="cmpstudb-01.cmp.uea.ac.uk",
    port="5432"
)

cur = conn.cursor()

# Set the search_path to your custom schema
cur.execute('SET search_path TO "100432626_data_definition_statements";')


