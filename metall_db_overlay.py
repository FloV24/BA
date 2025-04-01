# -*- coding: utf-8 -*-

import sqlite3
import tkinter as tk
from tkinter import messagebox

# Funktion zum Hinzufügen von Metallen in die Datenbank
def add_metal(name, ordnungszahl, d_elektronen, oxidation, koordinationszahl, geometrie):
    conn = sqlite3.connect("metalle.db")
    cursor = conn.cursor()

    # SQL-Befehl, um Daten in die Tabelle 'metalle' einzufügen
    cursor.execute("INSERT INTO metalle (name, ordnungszahl, d_elektronen, oxidation, koordinationszahl, geometrie) VALUES (?, ?, ?, ?, ?, ?)", 
                   (name, ordnungszahl, d_elektronen, oxidation, koordinationszahl, geometrie))

    conn.commit()
    conn.close()

# Funktion zum Überprüfen und Hinzufügen der Metall-Daten
def submit():
    name = entry_name.get()
    ordnungszahl = entry_ordnungszahl.get()
    d_elektronen = entry_d_elektronen.get()
    oxidation = entry_oxidation.get()
    koordinationszahl = entry_koordinationszahl.get()
    geometrie = geometrie_var.get()  # Wert aus Dropdown-Menü

    if not (name and ordnungszahl and d_elektronen and oxidation and koordinationszahl and geometrie):
        messagebox.showerror("Fehler", "Alle Felder müssen ausgefüllt werden!")
        return

    try:
        ordnungszahl = int(ordnungszahl)
        d_elektronen = int(d_elektronen)
        oxidation = int(oxidation)
        koordinationszahl = int(koordinationszahl)
    except ValueError:
        messagebox.showerror("Fehler", "Ordnungszahl, d-Elektronen, Oxidation und Koordinationszahl müssen Ganzzahlen sein!")
        return

    add_metal(name, ordnungszahl, d_elektronen, oxidation, koordinationszahl, geometrie)
    messagebox.showinfo("Erfolg", f"{name} wurde erfolgreich zur Datenbank hinzugefügt!")

    # Felder leeren
    entry_name.delete(0, tk.END)
    entry_ordnungszahl.delete(0, tk.END)
    entry_d_elektronen.delete(0, tk.END)
    entry_oxidation.delete(0, tk.END)
    entry_koordinationszahl.delete(0, tk.END)

# Tkinter Fenster erstellen
root = tk.Tk()
root.title("Metall-Datenbank")

# GUI-Elemente (Labels und Eingabefelder)
tk.Label(root, text="Name des Metalls:").grid(row=0, column=0, padx=10, pady=5)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Ordnungszahl:").grid(row=1, column=0, padx=10, pady=5)
entry_ordnungszahl = tk.Entry(root)
entry_ordnungszahl.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="d-Elektronen:").grid(row=2, column=0, padx=10, pady=5)
entry_d_elektronen = tk.Entry(root)
entry_d_elektronen.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Oxidationsstufe:").grid(row=3, column=0, padx=10, pady=5)
entry_oxidation = tk.Entry(root)
entry_oxidation.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Koordinationszahl:").grid(row=4, column=0, padx=10, pady=5)
entry_koordinationszahl = tk.Entry(root)
entry_koordinationszahl.grid(row=4, column=1, padx=10, pady=5)

# Dropdown-Menü für Geometrie
tk.Label(root, text="Geometrie:").grid(row=5, column=0, padx=10, pady=5)
geometrie_var = tk.StringVar()
geometrie_var.set("Oktaedrisch")  # Standardwert setzen
geometrie_options = ["Oktaedrisch", "Tetraedrisch", "Quadratisch-planar", "Trigonal-bipyramidal", "Linear", "Trigonal-planar", "Quadratisch-pyramidal", "Trigonal-prismatisch"]
geometrie_menu = tk.OptionMenu(root, geometrie_var, *geometrie_options)
geometrie_menu.grid(row=5, column=1, padx=10, pady=5)

# Button zum Absenden der Daten
submit_button = tk.Button(root, text="Metall hinzufügen", command=submit)
submit_button.grid(row=6, column=0, columnspan=2, pady=10)

# Fenster starten
root.mainloop()
