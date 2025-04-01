# -*- coding: utf-8 -*-
import sqlite3  # Importiert SQLite für die Datenbank

# Verbindung zur Datenbank herstellen (wird erstellt, falls nicht vorhanden)
conn = sqlite3.connect("metalle.db")
cursor = conn.cursor()

# Tabelle für Metalle erstellen, falls sie noch nicht existiert
cursor.execute("""
CREATE TABLE IF NOT EXISTS metalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Automatische ID für jeden Eintrag
    name TEXT NOT NULL,                     -- Name des Metalls (z. B. Kupfer)
    ordnungszahl INTEGER NOT NULL,          -- Ordnungszahl (z. B. 29 für Kupfer)
    d_elektronen INTEGER NOT NULL,          -- Anzahl der d-Elektronen
    oxidation INTEGER NOT NULL,             -- Oxidationsstufe (z. B. +2)
    koordinationszahl INTEGER NOT NULL,     -- Koordinationszahl (z. B. 4)
    geometrie TEXT NOT NULL                 -- Geometrie (z. B. quadratisch-planar)
)
""")

# Änderungen speichern und Verbindung schließen
conn.commit()
conn.close()

# Funktion zum Hinzufügen von Metallen
def add_metal(name, ordnungszahl, d_elektronen, oxidation, koordinationszahl, geometrie):
    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect("metalle.db")
    cursor = conn.cursor()

    # SQL-Befehl, um Daten in die Tabelle 'metalle' einzufügen
    cursor.execute("INSERT INTO metalle (name, ordnungszahl, d_elektronen, oxidation, koordinationszahl, geometrie) VALUES (?, ?, ?, ?, ?, ?)", 
                   (name, ordnungszahl, d_elektronen, oxidation, koordinationszahl, geometrie))

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()

# Funktion zum Abrufen von Daten
def fetch_data():
    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect("metalle.db")
    cursor = conn.cursor()

    # SQL-Befehl, um alle Daten aus der Tabelle 'metalle' zu holen
    cursor.execute("SELECT * FROM metalle")
    rows = cursor.fetchall()

    # Alle Zeilen durchgehen und ausgeben
    for row in rows:
        print(row)

    # Verbindung schließen
    conn.close()



# Daten abrufen und ausgeben
fetch_data()
