import sqlite3
import os
import argparse

def list_molecules(db_path):
    """
    Gibt alle Moleküle in der Datenbank aus.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Abrufen aller Moleküle
    cursor.execute("SELECT id, molecule_name FROM molecules")
    molecules = cursor.fetchall()

    print("Moleküle in der Datenbank:")
    for molecule_id, molecule_name in molecules:
        print(f"ID: {molecule_id}, Name: {molecule_name}")

    conn.close()

def list_atoms(db_path, molecule_id):
    """
    Gibt alle Atome für ein bestimmtes Molekül aus.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Abrufen der Atome für das angegebene Molekül
    cursor.execute("""
        SELECT atom, x, y, z
        FROM atoms
        WHERE molecule_id = ?
    """, (molecule_id,))
    atoms = cursor.fetchall()

    print(f"Atome für Molekül mit ID {molecule_id}:")
    for atom, x, y, z in atoms:
        print(f"  Atom: {atom}, x: {x:.6f}, y: {y:.6f}, z: {z:.6f}")

    conn.close()
    return atoms

def save_ligand_to_xyz(db_path, molecule_id, output_dir):
    """
    Speichert die Atome eines Moleküls in einer XYZ-Datei im angegebenen Verzeichnis.
    """
    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Molekülname abrufen
    cursor.execute("SELECT molecule_name FROM molecules WHERE id = ?", (molecule_id,))
    result = cursor.fetchone()
    if result is None:
        raise ValueError(f"Kein Molekül mit ID {molecule_id} in der Datenbank gefunden.")
    molecule_name = result[0]

    # Atome abrufen (ohne sie in der Konsole auszugeben)
    atoms = list_atoms(db_path, molecule_id)

    # Verzeichnis erstellen, falls es nicht existiert
    os.makedirs(output_dir, exist_ok=True)

    # Dateipfad erstellen
    output_file = os.path.join(output_dir, f"{molecule_name}.xyz")

    # XYZ-Datei speichern
    with open(output_file, 'w') as file:
        file.write(f"{len(atoms)}\n")
        file.write(f"Molekuel: {molecule_name}\n")
        for atom, x, y, z in atoms:
            file.write(f"{atom} {x:.6f} {y:.6f} {z:.6f}\n")

    print(f"Die XYZ-Datei wurde unter '{output_file}' gespeichert.")

def delete_ligand(db_path, molecule_id):
    """
    Löscht einen Liganden und die zugehörigen Atome aus der Datenbank.
    Aktualisiert die IDs der verbleibenden Liganden, sodass sie wieder bei 1 beginnen.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Überprüfen, ob der Ligand existiert
    cursor.execute("SELECT molecule_name FROM molecules WHERE id = ?", (molecule_id,))
    result = cursor.fetchone()
    if result is None:
        print(f"Kein Ligand mit ID {molecule_id} in der Datenbank gefunden.")
        conn.close()
        return

    molecule_name = result[0]

    # Löschen der Atome des Liganden
    cursor.execute("DELETE FROM atoms WHERE molecule_id = ?", (molecule_id,))

    # Löschen des Liganden aus der Tabelle molecules
    cursor.execute("DELETE FROM molecules WHERE id = ?", (molecule_id,))

    # IDs der verbleibenden Liganden neu nummerieren
    cursor.execute("CREATE TEMPORARY TABLE molecules_backup AS SELECT molecule_name FROM molecules")
    cursor.execute("DELETE FROM molecules")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'molecules'")
    cursor.execute("INSERT INTO molecules (molecule_name) SELECT molecule_name FROM molecules_backup")
    cursor.execute("DROP TABLE molecules_backup")

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()

    print(f"Ligand '{molecule_name}' (ID: {molecule_id}) wurde erfolgreich aus der Datenbank gelöscht.")
    print("Die IDs der verbleibenden Liganden wurden aktualisiert.")

def reset_id_sequence(db_path, table_name):
    """
    Setzt die ID-Sequenz für eine Tabelle zurück.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Überprüfen, ob die Tabelle in sqlite_sequence existiert
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence';")
    if cursor.fetchone():
        # Sequenz für die angegebene Tabelle zurücksetzen
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = ?", (table_name,))
        print(f"Die ID-Sequenz für die Tabelle '{table_name}' wurde zurückgesetzt.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Argumentparser einrichten
    parser = argparse.ArgumentParser(description="Verwalte Liganden in der Datenbank.")
    parser.add_argument(
        "--db_path",
        default="c:/Users/Florian V/Documents/Komplexe/DB/Ligant.db",  # Standardpfad zur SQLite-Datenbank
        help="Pfad zur SQLite-Datenbank. Standard: c:/Users/Florian V/Documents/Komplexe/DB/Ligant.db"
    )
    parser.add_argument("--list_molecules", action="store_true", help="Listet alle Moleküle in der Datenbank auf.")
    parser.add_argument("--list_atoms", type=int, help="Listet die Atome eines Moleküls mit der angegebenen ID auf.")
    parser.add_argument("--save_xyz", type=int, help="Speichert ein Molekül mit der angegebenen ID als XYZ-Datei.")
    parser.add_argument(
        "--output_dir",
        default="c:/Users/Florian V/Documents/Komplexe/DB/Lig_Neu",
        help="Verzeichnis für die Ausgabe der XYZ-Datei. Standard: c:/Users/Florian V/Documents/Komplexe/DB/Lig_Neu"
    )
    parser.add_argument("--delete_ligand", type=int, help="Löscht einen Liganden mit der angegebenen ID aus der Datenbank.")

    args = parser.parse_args()

    # Aktionen basierend auf den Argumenten ausführen
    if args.list_molecules:
        list_molecules(args.db_path)

    if args.list_atoms is not None:
        list_atoms(args.db_path, args.list_atoms)

    if args.save_xyz is not None:
        save_ligand_to_xyz(args.db_path, args.save_xyz, args.output_dir)

    if args.delete_ligand is not None:
        delete_ligand(args.db_path, args.delete_ligand)