import numpy as np
import argparse
import os
import sqlite3  # Für die Datenbank

def load_xyz(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        atom_count = int(lines[0].strip())
        atoms = []
        cu_found = False  # Flag, um zu überprüfen, ob ein Cu-Atom vorhanden ist

        for line in lines[2:2 + atom_count]:
            parts = line.split()
            # Überprüfen, ob ein Cu-Atom vorhanden ist
            if parts[0] == "Cu":
                cu_found = True
                continue  # Überspringe das Cu-Atom
            atoms.append((parts[0], np.array([float(parts[1]), float(parts[2]), float(parts[3])])))

        # Ausgabe, ob ein Cu-Atom gefunden wurde oder nicht
        if cu_found:
            print("Hinweis: Ein Cu-Atom wurde gefunden und entfernt.")
        else:
            print("Hinweis: Kein Cu-Atom in der Eingabedatei gefunden. Alle Atome werden verarbeitet.")

        return atoms

def save_to_database(db_path, molecule_name, atoms):
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabelle erstellen, falls sie noch nicht existiert
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS molecules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            molecule_name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            molecule_id INTEGER NOT NULL,
            atom TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            z REAL NOT NULL,
            FOREIGN KEY (molecule_id) REFERENCES molecules (id)
        )
    ''')

    # Molekül in die Datenbank einfügen
    cursor.execute('INSERT INTO molecules (molecule_name) VALUES (?)', (molecule_name,))
    molecule_id = cursor.lastrowid

    # Atome in die Datenbank einfügen
    for atom, coord in atoms:
        cursor.execute('INSERT INTO atoms (molecule_id, atom, x, y, z) VALUES (?, ?, ?, ?, ?)',
                       (molecule_id, atom, coord[0], coord[1], coord[2]))

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()
    print(f"Molekül '{molecule_name}' wurde in der Datenbank gespeichert.")

def align_ligand(atoms, central_atom_index):
    central_atom = atoms[central_atom_index][1]
    transformed_atoms = []

    # Translation: Verschiebe das zentrale Atom zum Ursprung
    for atom, coord in atoms:
        transformed_coord = coord - central_atom
        transformed_atoms.append((atom, transformed_coord))

    # Berechne den Schwerpunkt des Liganden (ohne das zentrale Atom)
    ligand_coords = np.array([coord for atom, coord in transformed_atoms if not np.all(coord == [0, 0, 0])])
    centroid = np.mean(ligand_coords, axis=0)

    # Ziel: Zentriere den Liganden entlang der z-Achse
    z_axis = np.array([0, 0, 1])
    rotation_axis = np.cross(centroid, z_axis)
    rotation_angle = np.arccos(np.dot(centroid, z_axis) / (np.linalg.norm(centroid) * np.linalg.norm(z_axis)))

    # Normiere die Rotationsachse
    if np.linalg.norm(rotation_axis) > 1e-6:
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
        rotation_matrix = rotation_matrix_from_axis_angle(rotation_axis, rotation_angle)

        # Wende die Rotation auf alle Atome an
        for i, (atom, coord) in enumerate(transformed_atoms):
            transformed_atoms[i] = (atom, np.dot(rotation_matrix, coord))

    return transformed_atoms

def rotation_matrix_from_axis_angle(axis, angle):
    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)
    ux, uy, uz = axis
    return np.array([
        [cos_theta + ux**2 * (1 - cos_theta), ux * uy * (1 - cos_theta) - uz * sin_theta, ux * uz * (1 - cos_theta) + uy * sin_theta],
        [uy * ux * (1 - cos_theta) + uz * sin_theta, cos_theta + uy**2 * (1 - cos_theta), uy * uz * (1 - cos_theta) - ux * sin_theta],
        [uz * ux * (1 - cos_theta) - uy * sin_theta, uz * uy * (1 - cos_theta) + ux * sin_theta, cos_theta + uz**2 * (1 - cos_theta)]
    ])

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Align ligand in an XYZ file along the z-axis and save to a database.")
    parser.add_argument("input_file", help="Name of the input XYZ file (located in Lig_Alt directory).")
    parser.add_argument("molecule_name", help="Name of the molecule to store in the database.")
    parser.add_argument("central_atom_index", type=int, help="Index of the central atom (0-based, after Cu is removed).")
    parser.add_argument("--db_path", default="c:/Users/Florian V/Documents/Komplexe/DB/Ligant.db", help="Path to the SQLite database file.")

    args = parser.parse_args()

    # Verzeichnis für Eingabedateien
    input_dir = "c:/Users/Florian V/Documents/Komplexe/DB/Lig_Alt"
    input_file_path = os.path.join(input_dir, args.input_file)

    # Überprüfen, ob die Eingabedatei existiert
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"Die Eingabedatei '{input_file_path}' wurde nicht gefunden.")

    # Laden, transformieren und speichern
    atoms = load_xyz(input_file_path)
    transformed_atoms = align_ligand(atoms, args.central_atom_index)
    save_to_database(args.db_path, args.molecule_name, transformed_atoms)

    print(f"Transformierte Daten wurden in der Datenbank '{args.db_path}' gespeichert.")