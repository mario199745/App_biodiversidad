"""Genera la base demostrativa 2020 integrada al dashboard de patrimonio."""

from __future__ import annotations

from pathlib import Path
import random

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "patrimonio_biodiversidad_2020.xlsx"
RNG = random.Random(2020)

LOCATIONS = [
    ("Amazonas", "Chachapoyas", "Leymebamba", "18M"),
    ("Áncash", "Huaraz", "Independencia", "18L"),
    ("Arequipa", "Caylloma", "Chivay", "19K"),
    ("Cusco", "La Convención", "Echarati", "18L"),
    ("Huánuco", "Leoncio Prado", "Rupa-Rupa", "18L"),
    ("Junín", "Satipo", "Pangoa", "18L"),
    ("Loreto", "Maynas", "San Juan Bautista", "18M"),
    ("Madre de Dios", "Tambopata", "Inambari", "19L"),
    ("Pasco", "Oxapampa", "Puerto Bermúdez", "18L"),
    ("Puno", "Sandia", "San Pedro de Putina Punco", "19L"),
    ("San Martín", "Mariscal Cáceres", "Juanjuí", "18M"),
    ("Ucayali", "Coronel Portillo", "Callería", "18L"),
]

TAXA = [
    ("Flora", "Árboles", "Magnoliopsida", "Fabales", "Fabaceae", "Inga edulis", "Guaba"),
    ("Flora", "Árboles", "Magnoliopsida", "Malpighiales", "Euphorbiaceae", "Hevea brasiliensis", "Shiringa"),
    ("Flora", "Palmeras", "Liliopsida", "Arecales", "Arecaceae", "Mauritia flexuosa", "Aguaje"),
    ("Flora", "Árboles", "Magnoliopsida", "Malvales", "Malvaceae", "Ceiba pentandra", "Lupuna"),
    ("Flora", "Arbustos", "Magnoliopsida", "Myrtales", "Melastomataceae", "Miconia calvescens", "Miconia"),
    ("Flora", "Árboles", "Magnoliopsida", "Sapindales", "Meliaceae", "Cedrela odorata", "Cedro"),
    ("Fauna", "Aves", "Aves", "Psittaciformes", "Psittacidae", "Ara ararauna", "Guacamayo azul y amarillo"),
    ("Fauna", "Aves", "Aves", "Accipitriformes", "Accipitridae", "Rupornis magnirostris", "Aguilucho caminero"),
    ("Fauna", "Mamíferos", "Mammalia", "Primates", "Cebidae", "Sapajus macrocephalus", "Machín negro"),
    ("Fauna", "Mamíferos", "Mammalia", "Carnivora", "Felidae", "Leopardus pardalis", "Ocelote"),
    ("Fauna", "Anfibios", "Amphibia", "Anura", "Hylidae", "Boana geographica", "Rana arborícola"),
    ("Fauna", "Reptiles", "Reptilia", "Squamata", "Teiidae", "Ameiva ameiva", "Lagartija verde"),
    ("Fauna", "Peces", "Actinopterygii", "Characiformes", "Characidae", "Astyanax bimaculatus", "Mojarra"),
    ("Fauna", "Insectos", "Insecta", "Lepidoptera", "Nymphalidae", "Morpho helenor", "Mariposa morpho"),
]

INSTRUMENTS = [
    ("Estudio de impacto ambiental", "Estudio de Impacto Ambiental", "Instrumentos de Gestión Ambiental"),
    ("Declaración de impacto ambiental", "Declaración de Impacto Ambiental", "Instrumentos de Gestión Ambiental"),
    ("Informe de investigación", "Informe Técnico", "Autorización de Investigación"),
]


def build_frames() -> dict[str, pd.DataFrame]:
    sources, inventory, sheets, records = [], [], [], []
    record_number = 1

    for index, (department, province, district, zone) in enumerate(LOCATIONS, start=1):
        source_id = f"F2020-{index:03d}"
        original_type, normalized_type, instrument = INSTRUMENTS[(index - 1) % len(INSTRUMENTS)]
        filename = f"inventario_biologico_2020_{index:02d}.xlsx"
        title = f"Evaluación de biodiversidad y cobertura vegetal 2020 - {province}"
        sources.append(
            {
                "id_fuente": source_id,
                "anio": 2020,
                "numeracion": f"N.° {index:03d}",
                "nro_expediente": f"EXP-2020-{index:04d}",
                "titulo_fuente": title,
                "tipo_documento_original": original_type,
                "tipo_documento_normalizado": normalized_type,
                "instrumento_fuente": instrument,
                "autor_institucion": "Equipo técnico de evaluación biológica",
                "departamento": department,
                "departamento_normalizado": department.upper(),
                "provincia": province,
                "resumen_fuente": f"Caracterización de flora y fauna en ecosistemas representativos de {province} durante 2020.",
                "archivo_maestro": "registro_fuentes_2020.xlsx",
                "fila_maestro": index + 1,
                "estado_revision": "revisado",
                "archivos_excel": 1,
            }
        )
        inventory.append(
            {
                "id_archivo_excel": f"X2020-{index:03d}", "anio": 2020, "id_fuente": source_id,
                "carpeta_estudio": f"2020/{source_id}", "archivo_excel": filename,
                "ruta_archivo": f"2020/{source_id}/{filename}", "extension": ".xlsx",
                "tamano_bytes": 48000 + index * 1350, "fecha_modificacion": "2020-12-15",
                "grupo_sugerido_archivo": "Flora y Fauna", "subgrupo_sugerido_archivo": "Inventario biológico",
            }
        )
        sheets.append(
            {
                "id_hoja_excel": f"H2020-{index:03d}", "id_archivo_excel": f"X2020-{index:03d}",
                "anio": 2020, "id_fuente": source_id, "archivo_excel": filename,
                "hoja_excel": "Inventario_Biologico", "filas_detectadas": 31, "columnas_detectadas": 18,
                "encabezado_detectado": 1, "es_candidata_biodiversidad": True,
                "grupo_sugerido": "Flora y Fauna", "subgrupo_sugerido": "Inventario biológico",
                "estado_lectura": "OK",
            }
        )

        selected_taxa = RNG.sample(TAXA, 10)
        for station_number in range(1, 4):
            for taxon in selected_taxa:
                group, subgroup, class_name, order, family, scientific, common = taxon
                records.append(
                    {
                        "id_registro": f"R2020-{record_number:05d}", "id_fuente": source_id, "anio": 2020,
                        "origen_dato": "Inventario biológico 2020", "nivel_registro": "fila_extraida",
                        "archivo_origen": filename, "hoja_origen": "Inventario_Biologico", "fila_origen": record_number + 1,
                        "grupo_general": group, "subgrupo": subgroup,
                        "ambito_ecologico": RNG.choice(["Bosque húmedo", "Bosque montano", "Matorral", "Ecosistema ribereño"]),
                        "clase": class_name, "orden": order, "familia": family,
                        "nombre_cientifico": scientific, "nombre_comun": common,
                        "departamento": department, "provincia": province, "distrito": district,
                        "unidad_ecosistemica": RNG.choice(["Bosque primario", "Bosque secundario", "Área de transición"]),
                        "estacion": f"EB-{station_number:02d}",
                        "este": 300000 + index * 9500 + station_number * 700,
                        "norte": 8500000 + index * 21000 + station_number * 500,
                        "zona_utm": zone, "temporada": RNG.choice(["Húmeda", "Seca"]),
                        "metodo_registro": RNG.choice(["Transecto", "Punto de conteo", "Parcela", "Observación directa"]),
                        "tipo_registro": RNG.choice(["Visual", "Auditivo", "Colecta botánica"]),
                        "numero_individuos_original": RNG.randint(1, 12), "conteo_reportes": 1,
                        "estado_revision": "revisado", "observaciones": "Registro incorporado para la presentación 2020.",
                        "texto_fila_origen": f"{scientific} | {common} | {station_number}",
                    }
                )
                record_number += 1

    controls = pd.DataFrame(
        [
            {"control": "Fuentes con identificador único", "estado": "OK", "n": len(sources)},
            {"control": "Registros con identificador único", "estado": "OK", "n": len(records)},
            {"control": "Registros con nombre científico", "estado": "OK", "n": len(records)},
            {"control": "Registros con ubicación territorial", "estado": "OK", "n": len(records)},
        ]
    )
    dictionary = pd.DataFrame(
        [
            {"tabla": "01_fuentes", "campo": "id_fuente", "descripcion": "Identificador único de la fuente."},
            {"tabla": "01_fuentes", "campo": "anio", "descripcion": "Año de referencia de la fuente."},
            {"tabla": "04_registros_especies", "campo": "id_registro", "descripcion": "Identificador único del reporte."},
            {"tabla": "04_registros_especies", "campo": "grupo_general", "descripcion": "Clasificación general en flora o fauna."},
            {"tabla": "04_registros_especies", "campo": "nombre_cientifico", "descripcion": "Nombre científico reportado."},
            {"tabla": "04_registros_especies", "campo": "conteo_reportes", "descripcion": "Unidad de reporte usada por el dashboard."},
        ]
    )
    return {
        "01_fuentes": pd.DataFrame(sources), "02_inventario_excel": pd.DataFrame(inventory),
        "03_hojas_excel": pd.DataFrame(sheets), "04_registros_especies": pd.DataFrame(records),
        "05_control_calidad": controls, "06_diccionario": dictionary,
    }


def main() -> None:
    frames = build_frames()
    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
        for sheet_name, frame in frames.items():
            frame.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.book[sheet_name]
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
    print(f"Base 2020 generada: {OUTPUT} ({len(frames['04_registros_especies'])} registros)")


if __name__ == "__main__":
    main()
