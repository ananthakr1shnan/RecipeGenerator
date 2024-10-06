import chromadb
from datetime import datetime, timedelta

client = chromadb.PersistentClient(path="food_items_vectorstore")
collection = client.get_or_create_collection(name="food_items")


def add_food_item(name, expiry):
    collection.add(
        documents=[name],
        metadatas=[
            {"expiry": expiry, "added_date": datetime.now().strftime("%Y-%m-%d")}
        ],
        ids=[name],
    )


def get_all_food_items():
    items = collection.get(include=["documents", "metadatas"])
    return [
        {
            "document": doc,
            "expiry": meta.get("expiry", "Unknown"),
            "added_date": meta.get("added_date", "Unknown"),
        }
        for doc, meta in zip(items["documents"], items["metadatas"])
    ]


def get_expiring_items():
    expiring_items = []
    now = datetime.now()

    items = collection.get(include=["documents", "metadatas"])

    for document, metadata in zip(items["documents"], items["metadatas"]):
        expiry = metadata.get("expiry", "Unknown")
        if expiry == "Unknown":
            continue

        try:
            value, unit = expiry.split()
            value = int(value)

            if "days" in unit:
                expiry_date = now + timedelta(days=value)
            elif "months" in unit:
                expiry_date = now + timedelta(days=value * 30)  # Approximate
            else:
                continue  # Skip items with invalid expiry format

            # Check if the item is expiring within the next 3 days
            if now <= expiry_date <= now + timedelta(days=3):
                expiring_items.append({"document": document, "expiry": expiry})
        except ValueError:
            # Skip items with invalid expiry format
            continue

    return expiring_items


def delete_food_item(name):
    collection.delete(ids=[name])
