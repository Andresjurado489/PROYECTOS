import pandas as pd
import numpy as np
import sqlite3
import json
import os
import csv
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import plotly.express as px
from PIL import Image as PILImage
import openpyxl

# Configuración de la base de datos
DB_FILE = "equipos_futbol.db"

# Configuración de paginación
EQUIPOS_POR_PAGINA = 10

# Máximo de goles por partido
MAX_GOLES_POR_PARTIDO = 10

# Diccionario de traducciones
TRADUCCIONES = {
    "es": {
        "title": "Gestión de Estadísticas de Fútbol",
        "search_label": "Buscar (ID o Nombre):",
        "prev_page": "Anterior",
        "next_page": "Siguiente",
        "page_label": "Página {0} de {1}",
        "id": "ID",
        "nombre": "Nombre",
        "partidos": "Partidos",
        "puntos": "Puntos",
        "goles_favor": "Goles a favor",
        "goles_contra": "Goles en contra",
        "puntos_local": "Puntos local",
        "puntos_visitante": "Puntos visitante",
        "diferencia": "Diferencia goles",
        "porcentaje": "Porcentaje victorias",
        "goles_partido": "Goles por partido",
        "id_equipo": "ID del equipo",
        "nombre_equipo": "Nombre",
        "partidos_jugados": "Partidos jugados",
        "ganados": "Ganados",
        "empatados": "Empatados",
        "perdidos": "Perdidos",
        "goles_a_favor": "Goles a favor",
        "goles_en_contra": "Goles en contra",
        "puntos_local_entry": "Puntos local",
        "puntos_visitante_entry": "Puntos visitante",
        "agregar": "Agregar equipo",
        "mostrar": "Mostrar estadísticas",
        "actualizar": "Actualizar equipo",
        "eliminar": "Eliminar equipo",
        "graficos": "Generar gráficos",
        "pdf": "Generar PDF",
        "exportar_csv": "Exportar a CSV",
        "importar_csv": "Importar desde CSV",
        "exportar_excel": "Exportar a Excel",
        "idioma": "Idioma:",
        "ranking": "Top 5 Equipos por Puntos",
        "error": "Error"
    },
    "en": {
        "title": "Football Statistics Management",
        "search_label": "Search (ID or Name):",
        "prev_page": "Previous",
        "next_page": "Next",
        "page_label": "Page {0} of {1}",
        "id": "ID",
        "nombre": "Name",
        "partidos": "Matches",
        "puntos": "Points",
        "goles_favor": "Goals For",
        "goles_contra": "Goals Against",
        "puntos_local": "Home Points",
        "puntos_visitante": "Away Points",
        "diferencia": "Goal Difference",
        "porcentaje": "Win Percentage",
        "goles_partido": "Goals per Match",
        "id_equipo": "Team ID",
        "nombre_equipo": "Name",
        "partidos_jugados": "Matches Played",
        "ganados": "Wins",
        "empatados": "Draws",
        "perdidos": "Losses",
        "goles_a_favor": "Goals For",
        "goles_en_contra": "Goals Against",
        "puntos_local_entry": "Home Points",
        "puntos_visitante_entry": "Away Points",
        "agregar": "Add Team",
        "mostrar": "Show Statistics",
        "actualizar": "Update Team",
        "eliminar": "Delete Team",
        "graficos": "Generate Graphs",
        "pdf": "Generate PDF",
        "exportar_csv": "Export to CSV",
        "importar_csv": "Import from CSV",
        "exportar_excel": "Export to Excel",
        "idioma": "Language:",
        "ranking": "Top 5 Teams by Points",
        "error": "Error"
    }
}

def init_db():
    """Inicializa la base de datos SQLite."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipos (
                id_equipo TEXT PRIMARY KEY,
                nombre TEXT,
                partidos_jugados INTEGER,
                ganados INTEGER,
                empatados INTEGER,
                perdidos INTEGER,
                goles_a_favor INTEGER,
                goles_en_contra INTEGER,
                puntos_totales INTEGER,
                puntos_local INTEGER,
                puntos_visitante INTEGER,
                diferencia_goles INTEGER,
                porcentaje_victorias REAL,
                goles_por_partido REAL
            )
        """)
        conn.commit()

def cargar_datos():
    """Carga los datos desde la base de datos SQLite."""
    equipos_db = {}
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipos")
        for row in cursor.fetchall():
            equipos_db[row[0]] = {
                "nombre": row[1],
                "partidos_jugados": row[2],
                "ganados": row[3],
                "empatados": row[4],
                "perdidos": row[5],
                "goles_a_favor": row[6],
                "goles_en_contra": row[7],
                "puntos_totales": row[8],
                "puntos_local": row[9],
                "puntos_visitante": row[10],
                "diferencia_goles": row[11],
                "porcentaje_victorias": row[12],
                "goles_por_partido": row[13]
            }
    return equipos_db

def guardar_equipo(id_equipo, equipo_data):
    """Guarda o actualiza un equipo en la base de datos."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO equipos (
                id_equipo, nombre, partidos_jugados, ganados, empatados, perdidos,
                goles_a_favor, goles_en_contra, puntos_totales, puntos_local,
                puntos_visitante, diferencia_goles, porcentaje_victorias, goles_por_partido
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_equipo, equipo_data["nombre"], equipo_data["partidos_jugados"],
            equipo_data["ganados"], equipo_data["empatados"], equipo_data["perdidos"],
            equipo_data["goles_a_favor"], equipo_data["goles_en_contra"],
            equipo_data["puntos_totales"], equipo_data["puntos_local"],
            equipo_data["puntos_visitante"], equipo_data["diferencia_goles"],
            equipo_data["porcentaje_victorias"], equipo_data["goles_por_partido"]
        ))
        conn.commit()

def eliminar_equipo_db(id_equipo):
    """Elimina un equipo de la base de datos."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM equipos WHERE id_equipo = ?", (id_equipo,))
        conn.commit()

def exportar_a_csv():
    """Exporta los datos a un archivo CSV."""
    equipos_db = cargar_datos()
    if not equipos_db:
        raise ValueError("No hay equipos para exportar.")
    with open("equipos_data.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Nombre", "Partidos jugados", "Ganados", "Empatados", 
                         "Perdidos", "Goles a favor", "Goles en contra", "Puntos totales", 
                         "Puntos local", "Puntos visitante", "Diferencia goles", 
                         "Porcentaje victorias", "Goles por partido"])
        for id_equipo, equipo in equipos_db.items():
            writer.writerow([id_equipo, equipo["nombre"], equipo["partidos_jugados"], 
                             equipo["ganados"], equipo["empatados"], equipo["perdidos"], 
                             equipo["goles_a_favor"], equipo["goles_en_contra"], 
                             equipo["puntos_totales"], equipo["puntos_local"], 
                             equipo["puntos_visitante"], equipo["diferencia_goles"],
                             equipo["porcentaje_victorias"], equipo["goles_por_partido"]])
    return "equipos_data.csv"

def exportar_a_excel():
    """Exporta los datos a un archivo Excel."""
    equipos_db = cargar_datos()
    if not equipos_db:
        raise ValueError("No hay equipos para exportar.")
    df = pd.DataFrame([
        {
            "ID": id_equipo,
            "Nombre": equipo["nombre"],
            "Partidos jugados": equipo["partidos_jugados"],
            "Ganados": equipo["ganados"],
            "Empatados": equipo["empatados"],
            "Perdidos": equipo["perdidos"],
            "Goles a favor": equipo["goles_a_favor"],
            "Goles en contra": equipo["goles_en_contra"],
            "Puntos totales": equipo["puntos_totales"],
            "Puntos local": equipo["puntos_local"],
            "Puntos visitante": equipo["puntos_visitante"],
            "Diferencia goles": equipo["diferencia_goles"],
            "Porcentaje victorias": equipo["porcentaje_victorias"],
            "Goles por partido": equipo["goles_por_partido"]
        } for id_equipo, equipo in equipos_db.items()
    ])
    excel_file = f"equipos_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(excel_file, index=False)
    return excel_file

def importar_desde_csv():
    """Importa datos desde un archivo CSV."""
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return None
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                id_equipo = row["ID"]
                partidos_jugados = int(row["Partidos jugados"])
                crear_equipo(
                    id_equipo=id_equipo,
                    nombre=row["Nombre"],
                    partidos_jugados=partidos_jugados,
                    ganados=int(row["Ganados"]),
                    empatados=int(row["Empatados"]),
                    perdidos=int(row["Perdidos"]),
                    goles_a_favor=int(row["Goles a favor"]),
                    goles_en_contra=int(row["Goles en contra"]),
                    puntos_local=int(row["Puntos local"]),
                    puntos_visitante=int(row["Puntos visitante"])
                )
        return file_path
    except Exception as e:
        raise ValueError(f"Error al importar CSV: {str(e)}")

def validar_no_negativo(valor, nombre_campo):
    """Valida que un valor numérico no sea negativo."""
    if not isinstance(valor, (int, float)) or valor < 0:
        raise ValueError(f"{nombre_campo} debe ser un número no negativo.")
    return valor

def validar_nombre_equipo(nombre):
    """Valida que el nombre del equipo sea una cadena no vacía."""
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("El nombre del equipo debe ser una cadena no vacía.")
    return nombre.strip()

def validar_id_equipo(id_equipo):
    """Valida que el ID del equipo sea una cadena no vacía y no exista."""
    equipos_db = cargar_datos()
    if not isinstance(id_equipo, str) or not id_equipo.strip():
        raise ValueError("El ID del equipo debe ser una cadena no vacía.")
    if id_equipo in equipos_db:
        raise ValueError("El ID del equipo ya existe.")
    return id_equipo.strip()

def validar_puntos_maximos(partidos_jugados, puntos_local, puntos_visitante, puntos_totales):
    """Valida que los puntos no excedan el máximo posible por partido."""
    max_puntos = partidos_jugados * 3
    if puntos_totales > max_puntos:
        raise ValueError(f"Los puntos totales ({puntos_totales}) no pueden exceder {max_puntos}.")
    if puntos_local > max_puntos or puntos_visitante > max_puntos:
        raise ValueError("Los puntos de local o visitante no pueden exceder el máximo posible.")

def validar_goles(partidos_jugados, goles_a_favor, goles_en_contra):
    """Valida que los goles no excedan el máximo razonable por partido."""
    max_goles = partidos_jugados * MAX_GOLES_POR_PARTIDO
    if goles_a_favor > max_goles or goles_en_contra > max_goles:
        raise ValueError(f"Los goles (a favor o en contra) no pueden exceder {max_goles} para {partidos_jugados} partidos.")

def crear_equipo(id_equipo, nombre, partidos_jugados, ganados, empatados, perdidos, 
                 goles_a_favor, goles_en_contra, puntos_local, puntos_visitante):
    """Crea un nuevo equipo y lo agrega a la base de datos."""
    id_equipo = validar_id_equipo(id_equipo)
    nombre = validar_nombre_equipo(nombre)
    partidos_jugados = validar_no_negativo(partidos_jugados, "Partidos jugados")
    ganados = validar_no_negativo(ganados, "Partidos ganados")
    empatados = validar_no_negativo(empatados, "Partidos empatados")
    perdidos = validar_no_negativo(perdidos, "Partidos perdidos")
    goles_a_favor = validar_no_negativo(goles_a_favor, "Goles a favor")
    goles_en_contra = validar_no_negativo(goles_en_contra, "Goles en contra")
    puntos_local = validar_no_negativo(puntos_local, "Puntos de local")
    puntos_visitante = validar_no_negativo(puntos_visitante, "Puntos de visitante")
    
    if ganados + empatados + perdidos != partidos_jugados:
        raise ValueError("La suma de partidos ganados, empatados y perdidos debe igualar los partidos jugados.")
    
    puntos_totales = ganados * 3 + empatados
    
    if puntos_local + puntos_visitante != puntos_totales:
        raise ValueError("La suma de puntos de local y visitante debe igualar los puntos totales.")
    
    validar_puntos_maximos(partidos_jugados, puntos_local, puntos_visitante, puntos_totales)
    validar_goles(partidos_jugados, goles_a_favor, goles_en_contra)
    
    diferencia_goles = goles_a_favor - goles_en_contra
    porcentaje_victorias = (ganados / partidos_jugados * 100) if partidos_jugados > 0 else 0
    goles_por_partido = goles_a_favor / partidos_jugados if partidos_jugados > 0 else 0
    
    equipo_data = {
        "nombre": nombre,
        "partidos_jugados": partidos_jugados,
        "ganados": ganados,
        "empatados": empatados,
        "perdidos": perdidos,
        "goles_a_favor": goles_a_favor,
        "goles_en_contra": goles_en_contra,
        "puntos_totales": puntos_totales,
        "puntos_local": puntos_local,
        "puntos_visitante": puntos_visitante,
        "diferencia_goles": diferencia_goles,
        "porcentaje_victorias": round(porcentaje_victorias, 2),
        "goles_por_partido": round(goles_por_partido, 2)
    }
    
    guardar_equipo(id_equipo, equipo_data)
    return id_equipo

def leer_equipo(id_equipo):
    """Lee los datos de un equipo por su ID."""
    equipos_db = cargar_datos()
    if id_equipo not in equipos_db:
        raise ValueError("El equipo no existe.")
    return equipos_db[id_equipo]

def actualizar_equipo(id_equipo, **kwargs):
    """Actualiza los datos de un equipo existente."""
    equipos_db = cargar_datos()
    if id_equipo not in equipos_db:
        raise ValueError("El equipo no existe.")
    
    equipo = equipos_db[id_equipo]
    for key, value in kwargs.items():
        if key == "nombre":
            equipo[key] = validar_nombre_equipo(value)
        elif key in ["partidos_jugados", "ganados", "empatados", "perdidos", 
                     "goles_a_favor", "goles_en_contra", "puntos_local", "puntos_visitante"]:
            equipo[key] = validar_no_negativo(value, key.replace("_", " ").capitalize())
    
    equipo["puntos_totales"] = equipo["ganados"] * 3 + equipo["empatados"]
    equipo["diferencia_goles"] = equipo["goles_a_favor"] - equipo["goles_en_contra"]
    equipo["porcentaje_victorias"] = round((equipo["ganados"] / equipo["partidos_jugados"] * 100) 
                                           if equipo["partidos_jugados"] > 0 else 0, 2)
    equipo["goles_por_partido"] = round(equipo["goles_a_favor"] / equipo["partidos_jugados"] 
                                        if equipo["partidos_jugados"] > 0 else 0, 2)
    
    if equipo["puntos_local"] + equipo["puntos_visitante"] != equipo["puntos_totales"]:
        raise ValueError("La suma de puntos de local y visitante debe igualar los puntos totales.")
    
    validar_puntos_maximos(equipo["partidos_jugados"], equipo["puntos_local"], 
                           equipo["puntos_visitante"], equipo["puntos_totales"])
    validar_goles(equipo["partidos_jugados"], equipo["goles_a_favor"], equipo["goles_en_contra"])
    
    guardar_equipo(id_equipo, equipo)

def eliminar_equipo(id_equipo):
    """Elimina un equipo por su ID."""
    equipos_db = cargar_datos()
    if id_equipo not in equipos_db:
        raise ValueError("El equipo no existe.")
    eliminar_equipo_db(id_equipo)

def calcular_promedios_liga():
    """Calcula el promedio de goles y puntos por partido en la liga."""
    equipos_db = cargar_datos()
    if not equipos_db:
        return 0, 0
    total_goles = sum(equipo["goles_a_favor"] for equipo in equipos_db.values())
    total_puntos = sum(equipo["puntos_totales"] for equipo in equipos_db.values())
    total_partidos = sum(equipo["partidos_jugados"] for equipo in equipos_db.values())
    promedio_goles = total_goles / total_partidos if total_partidos > 0 else 0
    promedio_puntos = total_puntos / total_partidos if total_partidos > 0 else 0
    return round(promedio_goles, 2), round(promedio_puntos, 2)

def obtener_ranking():
    """Obtiene los top 5 equipos por puntos totales."""
    equipos_db = cargar_datos()
    equipos = [(id_equipo, equipo) for id_equipo, equipo in equipos_db.items()]
    equipos.sort(key=lambda x: x[1]["puntos_totales"], reverse=True)
    return equipos[:5]

def mostrar_estadisticas_equipo(id_equipo):
    """Devuelve las estadísticas de un equipo como cadena formateada."""
    equipo = leer_equipo(id_equipo)
    promedio_goles, promedio_puntos = calcular_promedios_liga()
    stats_df = pd.DataFrame({
        "Métrica": ["Partidos jugados", "Ganados", "Empatados", "Perdidos", 
                    "Goles a favor", "Goles en contra", "Puntos totales", 
                    "Puntos de local", "Puntos de visitante", "Diferencia de goles",
                    "Porcentaje de victorias (%)", "Goles por partido",
                    "Promedio de goles en la liga", "Promedio de puntos por partido"],
        "Valor": [equipo["partidos_jugados"], equipo["ganados"], equipo["empatados"], 
                  equipo["perdidos"], equipo["goles_a_favor"], equipo["goles_en_contra"], 
                  equipo["puntos_totales"], equipo["puntos_local"], equipo["puntos_visitante"],
                  equipo["diferencia_goles"], equipo["porcentaje_victorias"], 
                  equipo["goles_por_partido"], promedio_goles, promedio_puntos]
    })
    return f"Estadísticas de {equipo['nombre']}:\n{stats_df.to_string(index=False)}"

def graficar_estadisticas():
    """Genera gráficos interactivos con plotly."""
    equipos_db = cargar_datos()
    if not equipos_db:
        raise ValueError("No hay equipos para graficar.")
    
    nombres = [equipo["nombre"] for equipo in equipos_db.values()]
    puntos_totales = [equipo["puntos_totales"] for equipo in equipos_db.values()]
    goles_a_favor = [equipo["goles_a_favor"] for equipo in equipos_db.values()]
    goles_en_contra = [equipo["goles_en_contra"] for equipo in equipos_db.values()]
    puntos_local = [equipo["puntos_local"] for equipo in equipos_db.values()]
    puntos_visitante = [equipo["puntos_visitante"] for equipo in equipos_db.values()]
    porcentaje_victorias = [equipo["porcentaje_victorias"] for equipo in equipos_db.values()]
    
    fig = px.bar(x=nombres, y=puntos_totales, title="Puntos Totales por Equipo",
                 labels={"x": "Equipos", "y": "Puntos totales"}, color=puntos_totales,
                 color_continuous_scale="Blues")
    fig.update_layout(xaxis_tickangle=45)
    fig.write_html("puntos_totales.html")
    fig.write_image("puntos_totales.png", width=800, height=600)
    
    df_goles = pd.DataFrame({
        "Equipo": nombres * 2,
        "Goles": goles_a_favor + goles_en_contra,
        "Tipo": ["A favor"] * len(nombres) + ["En contra"] * len(nombres)
    })
    fig = px.bar(df_goles, x="Equipo", y="Goles", color="Tipo", barmode="group",
                 title="Goles a Favor y en Contra por Equipo",
                 labels={"Goles": "Goles", "Equipo": "Equipos"},
                 color_discrete_map={"A favor": "green", "En contra": "red"})
    fig.update_layout(xaxis_tickangle=45)
    fig.write_html("goles.html")
    fig.write_image("goles.png", width=800, height=600)
    
    df_puntos = pd.DataFrame({
        "Equipo": nombres * 2,
        "Puntos": puntos_local + puntos_visitante,
        "Tipo": ["Local"] * len(nombres) + ["Visitante"] * len(nombres)
    })
    fig = px.bar(df_puntos, x="Equipo", y="Puntos", color="Tipo", barmode="group",
                 title="Puntos de Local vs Visitante por Equipo",
                 labels={"Puntos": "Puntos", "Equipo": "Equipos"},
                 color_discrete_map={"Local": "blue", "Visitante": "orange"})
    fig.update_layout(xaxis_tickangle=45)
    fig.write_html("puntos_local_visitante.html")
    fig.write_image("puntos_local_visitante.png", width=800, height=600)
    
    fig = px.bar(x=nombres, y=porcentaje_victorias, title="Porcentaje de Victorias por Equipo",
                 labels={"x": "Equipos", "y": "Porcentaje de victorias (%)"},
                 color=porcentaje_victorias, color_continuous_scale="Purples")
    fig.update_layout(xaxis_tickangle=45)
    fig.write_html("porcentaje_victorias.html")
    fig.write_image("porcentaje_victorias.png", width=800, height=600)

def generar_informe_pdf(lang="es"):
    """Genera un informe PDF con las estadísticas, gráficos y ranking."""
    equipos_db = cargar_datos()
    pdf_file = f"informe_estadisticas_futbol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph(TRADUCCIONES[lang]["title"], styles['Title']))
    elements.append(Spacer(1, 12))
    
    promedio_goles, promedio_puntos = calcular_promedios_liga()
    data = [["Nombre", "Partidos", "Puntos", "Goles a favor", "Goles en contra", 
             "Puntos local", "Puntos visitante", "Diferencia goles", 
             "Porcentaje victorias", "Goles por partido"]]
    for id_equipo, equipo in equipos_db.items():
        data.append([
            equipo["nombre"],
            str(equipo["partidos_jugados"]),
            str(equipo["puntos_totales"]),
            str(equipo["goles_a_favor"]),
            str(equipo["goles_en_contra"]),
            str(equipo["puntos_local"]),
            str(equipo["puntos_visitante"]),
            str(equipo["diferencia_goles"]),
            str(equipo["porcentaje_victorias"]),
            str(equipo["goles_por_partido"])
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"{TRADUCCIONES[lang]['promedio_goles']}: {promedio_goles:.2f}", styles['Normal']))
    elements.append(Paragraph(f"{TRADUCCIONES[lang]['promedio_puntos']}: {promedio_puntos:.2f}", styles['Normal']))
    
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(TRADUCCIONES[lang]["ranking"], styles['Heading2']))
    ranking = obtener_ranking()
    ranking_data = [["Posición", "Nombre", "Puntos"]]
    for i, (id_equipo, equipo) in enumerate(ranking, 1):
        ranking_data.append([str(i), equipo["nombre"], str(equipo["puntos_totales"])])
    ranking_table = Table(ranking_data)
    ranking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(ranking_table)
    
    graficos = ["puntos_totales.png", "goles.png", "puntos_local_visitante.png", "porcentaje_victorias.png"]
    for grafico in graficos:
        if os.path.exists(grafico):
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(grafico.replace(".png", "").replace("_", " ").title(), styles['Heading2']))
            img = Image(grafico, width=500, height=300)
            elements.append(img)
    
    doc.build(elements)
    return pdf_file

class App:
    def __init__(self, root):
        self.root = root
        self.lang = "es"
        self.root.title(TRADUCCIONES[self.lang]["title"])
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, font=('Helvetica', 10))
        style.configure("TLabel", font=('Helvetica', 10))
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.main_frame, text=TRADUCCIONES[self.lang]["idioma"]).grid(row=0, column=0, sticky="e")
        self.lang_var = tk.StringVar(value=self.lang)
        lang_menu = ttk.OptionMenu(self.main_frame, self.lang_var, self.lang, "es", "en", command=self.cambiar_idioma)
        lang_menu.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.main_frame, text=TRADUCCIONES[self.lang]["search_label"]).grid(row=1, column=0, sticky="e")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.main_frame, textvariable=self.search_var)
        self.search_entry.grid(row=1, column=1, padx=5, pady=5)
        self.search_var.trace("w", self.filtrar_tabla)
        
        self.pagina_actual = 0
        self.pagination_frame = ttk.Frame(self.main_frame)
        self.pagination_frame.grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(self.pagination_frame, text=TRADUCCIONES[self.lang]["prev_page"], 
                   command=self.pagina_anterior).grid(row=0, column=0, padx=5)
        self.pagination_label = ttk.Label(self.pagination_frame, text=TRADUCCIONES[self.lang]["page_label"].format(1, 1))
        self.pagination_label.grid(row=0, column=1, padx=5)
        ttk.Button(self.pagination_frame, text=TRADUCCIONES[self.lang]["next_page"], 
                   command=self.pagina_siguiente).grid(row=0, column=2, padx=5)
        
        self.sort_column = None
        self.sort_reverse = False
        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Nombre", "Partidos", "Puntos", 
                                                           "Goles a favor", "Goles en contra", 
                                                           "Puntos local", "Puntos visitante", 
                                                           "Diferencia", "Porcentaje", "Goles/partido"),
                                 show="headings")
        headers = [TRADUCCIONES[self.lang][key] for key in 
                   ["id", "nombre", "partidos", "puntos", "goles_favor", "goles_contra", 
                    "puntos_local", "puntos_visitante", "diferencia", "porcentaje", "goles_partido"]]
        for i, header in enumerate(headers):
            self.tree.heading(i, text=header, command=lambda col=i: self.ordenar_tabla(col))
        self.tree.column("ID", width=80)
        self.tree.column("Nombre", width=120)
        self.tree.column("Partidos", width=80)
        self.tree.column("Puntos", width=80)
        self.tree.column("Goles a favor", width=100)
        self.tree.column("Goles en contra", width=100)
        self.tree.column("Puntos local", width=100)
        self.tree.column("Puntos visitante", width=100)
        self.tree.column("Diferencia", width=100)
        self.tree.column("Porcentaje", width=100)
        self.tree.column("Goles/partido", width=100)
        self.tree.grid(row=3, column=0, columnspan=2, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.cargar_datos_seleccionados)
        
        self.actualizar_tabla()
        
        labels = [TRADUCCIONES[self.lang][key] for key in 
                  ["id_equipo", "nombre_equipo", "partidos_jugados", "ganados", "empatados", 
                   "perdidos", "goles_a_favor", "goles_en_contra", "puntos_local_entry", 
                   "puntos_visitante_entry"]]
        self.entries = {}
        for i, label in enumerate(labels):
            ttk.Label(self.main_frame, text=label).grid(row=i+4, column=0, padx=5, pady=5, sticky="e")
            self.entries[label] = ttk.Entry(self.main_frame, width=40)
            self.entries[label].grid(row=i+4, column=1, padx=5, pady=5)
        
        self.output = scrolledtext.ScrolledText(self.main_frame, height=10, width=80, font=('Helvetica', 10))
        self.output.grid(row=14, column=0, columnspan=2, pady=10)
        
        ranking_button = ttk.Button(self.main_frame, text=TRADUCCIONES[self.lang]["ranking"], 
                                   command=self.mostrar_ranking)
        ranking_button.grid(row=15, column=0, columnspan=2, pady=5)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=16, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text=TRADUCCIONES[self.lang]["agregar"], 
                   command=self.agregar_equipo).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text=TRADUCCIONES[self.lang]["mostrar"], 
                   command=self.mostrar_estadisticas).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text=TRADUCCIONES[self.lang]["actualizar"], 
                   command=self.actualizar_equipo).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text=TRADUCCIONES[self.lang]["eliminar"], 
                   command=self.eliminar_equipo).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text=TRADUCCIONES[self.lang]["graficos"], 
                   command=self.generar_graficos).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text=TRADUCCIONES[self.lang]["pdf"], 
                   command=self.generar_pdf).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text=TRADUCCIONES[self.lang]["exportar_csv"], 
                   command=self.exportar_csv).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text=TRADUCCIONES[self.lang]["importar_csv"], 
                   command=self.importar_csv).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(button_frame, text=TRADUCCIONES[self.lang]["exportar_excel"], 
                   command=self.exportar_excel).grid(row=2, column=0, columnspan=4, pady=5)
    
    def cambiar_idioma(self, *args):
        """Cambia el idioma de la interfaz."""
        self.lang = self.lang_var.get()
        self.root.title(TRADUCCIONES[self.lang]["title"])
        self.setup_ui()
    
    def mostrar_ranking(self):
        """Muestra el ranking de los top 5 equipos en el área de texto."""
        ranking = obtener_ranking()
        output = f"{TRADUCCIONES[self.lang]['ranking']}:\n"
        output += "Posición | Nombre | Puntos\n"
        output += "-" * 30 + "\n"
        for i, (id_equipo, equipo) in enumerate(ranking, 1):
            output += f"{i} | {equipo['nombre']} | {equipo['puntos_totales']}\n"
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, output)
    
    def ordenar_tabla(self, col):
        """Ordena la tabla por la columna seleccionada."""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        key_map = {
            0: "id_equipo",
            1: "nombre",
            2: "partidos_jugados",
            3: "puntos_totales",
            4: "goles_a_favor",
            5: "goles_en_contra",
            6: "puntos_local",
            7: "puntos_visitante",
            8: "diferencia_goles",
            9: "porcentaje_victorias",
            10: "goles_por_partido"
        }
        
        equipos_db = cargar_datos()
        equipos = [(id_equipo, equipo) for id_equipo, equipo in equipos_db.items()]
        if col == 0:
            equipos.sort(key=lambda x: x[0], reverse=self.sort_reverse)
        elif col == 1:
            equipos.sort(key=lambda x: x[1]["nombre"], reverse=self.sort_reverse)
        else:
            equipos.sort(key=lambda x: x[1][key_map[col]], reverse=self.sort_reverse)
        
        self.actualizar_tabla(self.search_var.get(), equipos_filtrados=equipos)
    
    def actualizar_tabla(self, filtro="", equipos_filtrados=None):
        """Actualiza la tabla con los datos de los equipos."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        equipos_db = cargar_datos()
        if equipos_filtrados is None:
            equipos_filtrados = [(id_equipo, equipo) for id_equipo, equipo in equipos_db.items()
                                if filtro.lower() in id_equipo.lower() or 
                                filtro.lower() in equipo["nombre"].lower()]
        
        total_paginas = max(1, (len(equipos_filtrados) + EQUIPOS_POR_PAGINA - 1) // EQUIPOS_POR_PAGINA)
        self.pagina_actual = min(self.pagina_actual, total_paginas - 1)
        inicio = self.pagina_actual * EQUIPOS_POR_PAGINA
        fin = min(inicio + EQUIPOS_POR_PAGINA, len(equipos_filtrados))
        
        for id_equipo, equipo in equipos_filtrados[inicio:fin]:
            self.tree.insert("", "end", values=(id_equipo, equipo["nombre"], 
                                                equipo["partidos_jugados"], 
                                                equipo["puntos_totales"], 
                                                equipo["goles_a_favor"], 
                                                equipo["goles_en_contra"], 
                                                equipo["puntos_local"], 
                                                equipo["puntos_visitante"], 
                                                equipo["diferencia_goles"],
                                                equipo["porcentaje_victorias"],
                                                equipo["goles_por_partido"]))
        
        self.pagination_label.config(text=TRADUCCIONES[self.lang]["page_label"].format(self.pagina_actual + 1, total_paginas))
    
    def pagina_anterior(self):
        """Navega a la página anterior."""
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self.filtrar_tabla()
    
    def pagina_siguiente(self):
        """Navega a la página siguiente."""
        equipos_db = cargar_datos()
        equipos_filtrados = [(id_equipo, equipo) for id_equipo, equipo in equipos_db.items()
                            if self.search_var.get().lower() in id_equipo.lower() or 
                            self.search_var.get().lower() in equipo["nombre"].lower()]
        total_paginas = (len(equipos_filtrados) + EQUIPOS_POR_PAGINA - 1) // EQUIPOS_POR_PAGINA
        if self.pagina_actual < total_paginas - 1:
            self.pagina_actual += 1
            self.filtrar_tabla()
    
    def filtrar_tabla(self, *args):
        """Filtra la tabla según el texto en el campo de búsqueda."""
        self.pagina_actual = 0
        self.actualizar_tabla(self.search_var.get())
    
    def cargar_datos_seleccionados(self, event):
        """Carga los datos del equipo seleccionado en los campos de entrada."""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item["values"]
            labels = [TRADUCCIONES[self.lang][key] for key in 
                      ["id_equipo", "nombre_equipo", "partidos_jugados", "ganados", 
                       "empatados", "perdidos", "goles_a_favor", "goles_en_contra", 
                       "puntos_local_entry", "puntos_visitante_entry"]]
            self.entries[labels[0]].delete(0, tk.END)
            self.entries[labels[0]].insert(0, values[0])
            self.entries[labels[1]].delete(0, tk.END)
            self.entries[labels[1]].insert(0, values[1])
            self.entries[labels[2]].delete(0, tk.END)
            self.entries[labels[2]].insert(0, values[2])
            self.entries[labels[3]].delete(0, tk.END)
            equipos_db = cargar_datos()
            self.entries[labels[3]].insert(0, equipos_db[values[0]]["ganados"])
            self.entries[labels[4]].delete(0, tk.END)
            self.entries[labels[4]].insert(0, equipos_db[values[0]]["empatados"])
            self.entries[labels[5]].delete(0, tk.END)
            self.entries[labels[5]].insert(0, equipos_db[values[0]]["perdidos"])
            self.entries[labels[6]].delete(0, tk.END)
            self.entries[labels[6]].insert(0, values[4])
            self.entries[labels[7]].delete(0, tk.END)
            self.entries[labels[7]].insert(0, values[5])
            self.entries[labels[8]].delete(0, tk.END)
            self.entries[labels[8]].insert(0, values[6])
            self.entries[labels[9]].delete(0, tk.END)
            self.entries[labels[9]].insert(0, values[7])
    
    def agregar_equipo(self):
        try:
            labels = [TRADUCCIONES[self.lang][key] for key in 
                      ["id_equipo", "nombre_equipo", "partidos_jugados", "ganados", 
                       "empatados", "perdidos", "goles_a_favor", "goles_en_contra", 
                       "puntos_local_entry", "puntos_visitante_entry"]]
            id_equipo = self.entries[labels[0]].get()
            nombre = self.entries[labels[1]].get()
            partidos_jugados = int(self.entries[labels[2]].get())
            ganados = int(self.entries[labels[3]].get())
            empatados = int(self.entries[labels[4]].get())
            perdidos = int(self.entries[labels[5]].get())
            goles_a_favor = int(self.entries[labels[6]].get())
            goles_en_contra = int(self.entries[labels[7]].get())
            puntos_local = int(self.entries[labels[8]].get())
            puntos_visitante = int(self.entries[labels[9]].get())
            
            crear_equipo(id_equipo, nombre, partidos_jugados, ganados, empatados, perdidos,
                         goles_a_favor, goles_en_contra, puntos_local, puntos_visitante)
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Equipo {nombre} agregado con ID {id_equipo}\n")
            self.actualizar_tabla()
        except ValueError as e:
            messagebox.showerror(TRADUCCIONES[self.lang]["error"], str(e))
    
    def mostrar_estadisticas(self):
        try:
            labels = [TRADUCCIONES[self.lang][key] for key in ["id_equipo"]]
            id_equipo = self.entries[labels[0]].get()
            estadisticas = mostrar_estadisticas_equipo(id_equipo)
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, estadisticas)
        except ValueError as e:
            messagebox.showerror(TRADUCCIONES[self.lang]["error"], str(e))
    
    def actualizar_equipo(self):
        try:
            labels = [TRADUCCIONES[self.lang][key] for key in 
                      ["id_equipo", "nombre_equipo", "partidos_jugados", "ganados", 
                       "empatados", "perdidos", "goles_a_favor", "goles_en_contra", 
                       "puntos_local_entry", "puntos_visitante_entry"]]
            id_equipo = self.entries[labels[0]].get()
            kwargs = {}
            if self.entries[labels[1]].get():
                kwargs["nombre"] = self.entries[labels[1]].get()
            if self.entries[labels[2]].get():
                kwargs["partidos_jugados"] = int(self.entries[labels[2]].get())
            if self.entries[labels[3]].get():
                kwargs["ganados"] = int(self.entries[labels[3]].get())
            if self.entries[labels[4]].get():
                kwargs["empatados"] = int(self.entries[labels[4]].get())
            if self.entries[labels[5]].get():
                kwargs["perdidos"] = int(self.entries[labels[5]].get())
            if self.entries[labels[6]].get():
                kwargs["goles_a_favor"] = int(self.entries[labels[6]].get())
            if self.entries[labels[7]].get():
                kwargs["goles_en_contra"] = int(self.entries[labels[7]].get())
            if self.entries[labels[8]].get():
                kwargs["puntos_local"] = int(self.entries[labels[8]].get())
            if self.entries[labels[9]].get():
                kwargs["puntos_visitante"] = int(self.entries[labels[9]].get())
            
            actualizar_equipo(id_equipo, **kwargs)
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Equipo con ID {id_equipo} actualizado\n")
            self.actualizar_tabla()
        except ValueError as e:
            messagebox.showerror(TRADUCCIONES[self.lang]["error"], str(e))
    
    def eliminar_equipo(self):
        try:
            labels = [TRADUCCIONES[self.lang][key] for key in ["id_equipo"]]
            id_equipo = self.entries[labels[0]].get()
            eliminar_equipo(id_equipo)
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Equipo con ID {id_equipo} eliminado\n")
            self.actualizar_tabla()
        except ValueError as e:
            messagebox.showerror(TRADUCCIONES[self.lang]["error"], str(e))
    
    def generar_graficos(self):
        try:
            graficar_estadisticas()
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, "Gráficos generados: puntos_totales.html, goles.html, puntos_local_visitante.html, porcentaje_victorias.html\n")
        except ValueError as e:
            messagebox.showerror(TRADUCCIONES[self.lang]["error"], str(e))
    
    def generar_pdf(self):
        try:
            pdf_file = generar_informe_pdf(self.lang)
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Informe generado: {pdf_file}\n")
        except Exception as e:
            messagebox.showerror(TRADUCCIONES[self.lang]["error"], str(e))
    
    def exportar_csv(self):
        try:
            csv_file = exportar_a_csv()
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Datos exportados a: {csv_file}\n")
        except ValueError as e:
            messagebox.showerror(TRADUCCIONES[self.lang]["error"], str(e))
    
    def importar_csv(self):
        try:
            file_path = importar_desde_csv()
            if file_path:
                self.output.delete(1.0, tk.END)
                self.output.insert(tk.END, f"Datos importados desde: {file_path}\n")
                self.actualizar_tabla()
        except ValueError as e:
            messagebox.showerror(TRADUCCIONES[self.lang]["error"], str(e))
    
    def exportar_excel(self):
        try:
            excel_file = exportar_a_excel()
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Datos exportados a: {excel_file}\n")
        except ValueError as e:
            messagebox.showerror(TRADUCCIONES[self.lang]["error"], str(e))

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = App(root)
    root.mainloop()