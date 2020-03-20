db.olx.aggregate([
    { "$addFields": {"download_date_utc": {"$subtract": [{"$divide": [{'$toDecimal': '$download_date'},1000]},3600]}}},
    { "$out" : "olx" }
])

db.gratka.aggregate([
    { "$addFields": {"download_date_utc": {"$subtract": [{"$divide": [{'$toDecimal': '$download_date'},1000]},3600]}}},
    { "$out" : "gratka" }
])


db.morizon.aggregate([
    { "$addFields": {"download_date_utc": {"$subtract": [{"$divide": [{'$toDecimal': '$download_date'},1000]},3600]}}},
    { "$out" : "morizon" }
])

db.otodom.aggregate([
    { "$addFields": {"download_date_utc": {"$subtract": [{"$divide": [{'$toDecimal': '$download_date'},1000]},3600]}}},
    { "$out" : "otodom" }
])

db.otodom.createIndex({"download_date_utc": 1})
db.olx.createIndex({"download_date_utc": 1})
db.gratka.createIndex({"download_date_utc": 1})
db.morizon.createIndex({"download_date_utc": 1})