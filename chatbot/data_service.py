from pathlib import Path
import re
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

FILES = {
    "distribution": {
        "file": "flora_distribution.xlsx",
        "sheet": "plant_distribution_import",
    },
    "rare": {
        "file": "flora_distribution.xlsx",
        "sheet": "rare_by_region",
    },
    "toxic": {
        "file": "flora_distribution.xlsx",
        "sheet": "toxic_by_region",
    },
    "benefits": {
        "file": "flora_benefits.xlsx",
        "sheet": "plant_benefits_import",
    },
}

# أسماء أعمدة شائعة؛ يُستخدم التعرف عليها لتحديد عمود اسم النبات.
PLANT_NAME_COLUMNS = {
    "plant_name",
    "scientific_name",
    "common_name",
    "arabic_name",
    "name",
    "اسم النبات",
    "اسم",
    "الاسم العلمي",
    "الاسم الشائع",
    "الاسم العربي",
}


def normalize_text(value):
    """توحيد النص لتسهيل البحث بالعربية والإنجليزية."""
    if value is None or pd.isna(value):
        return ""

    text = str(value).strip().casefold()

    # توحيد بعض الحروف العربية الشائعة.
    text = text.translate(str.maketrans({
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
    }))

    text = re.sub(r"\s+", " ", text)
    return text


def load_plant_data(data_type):
    if data_type not in FILES:
        raise ValueError(
            f"Unsupported data type: {data_type}"
        )

    config = FILES[data_type]
    file_path = DATA_DIR / config["file"]

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path.name}"
        )

    df = pd.read_excel(
        file_path,
        sheet_name=config["sheet"],
    )

    # إزالة المسافات الزائدة من أسماء الأعمدة.
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # تحويل القيم المفقودة إلى None.
    df = df.astype(object).where(pd.notna(df), None)

    return df


def find_plant_name_columns(df):
    """تحديد أعمدة أسماء النباتات من أسماء الأعمدة الفعلية."""
    matches = []

    for column in df.columns:
        normalized = normalize_text(column)

        if normalized in {
            normalize_text(name)
            for name in PLANT_NAME_COLUMNS
        }:
            matches.append(column)

    return matches


def search_plants(
    query="",
    data_type="distribution",
    limit=50,
):
    """
    البحث في بيانات النباتات مع إرجاع النتائج المطابقة فقط.

    query:
        اسم النبات أو المنطقة أو مصطلح للبحث.

    data_type:
        distribution / rare / toxic / benefits

    limit:
        الحد الأقصى للنتائج المعروضة.
    """
    if data_type not in FILES:
        raise ValueError(
            f"Unsupported data type: {data_type}"
        )

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 50

    limit = max(1, min(limit, 100))

    df = load_plant_data(data_type)
    original_count = len(df)

    if not query or not str(query).strip():
        results = df.head(limit).to_dict(
            orient="records"
        )

        return {
            "success": True,
            "data_type": data_type,
            "query": "",
            "total_results": original_count,
            "returned_results": len(results),
            "columns": list(df.columns),
            "results": results,
            "message": (
                "تم عرض سجلات من مجموعة البيانات."
                if original_count
                else "مجموعة البيانات فارغة."
            ),
        }

    query_text = normalize_text(query)

    # البحث عن العبارة في جميع الأعمدة.
    mask = df.apply(
        lambda column: column.map(
            lambda value: query_text in normalize_text(value)
        )
    ).any(axis=1)

    matched_df = df[mask]
    total = len(matched_df)

    results = matched_df.head(limit).to_dict(
        orient="records"
    )

    return {
        "success": True,
        "data_type": data_type,
        "query": str(query).strip(),
        "total_results": total,
        "returned_results": len(results),
        "columns": list(df.columns),
        "results": results,
        "message": (
            f"تم العثور على {total} سجل مطابق."
            if total
            else "لم يتم العثور على سجلات تطابق عبارة البحث."
        ),
    }
