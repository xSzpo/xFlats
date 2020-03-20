use OFFERS

db.otodom.find({
    "$and" :[
        {"$or":[{"year_of_building" : {"$gt": 1850, "$lt": 2050}},{"year_of_building":{ "$exists": false }},{"year_of_building":null}]},
        {"price":{"$gt": 100000, "$lt":1500000}},
        {"flat_size" : {"$gt": 6, "$lt":150}},
        {"GC_longitude" : {"$gt": 20.5, "$lt": 21.5}},
        {"GC_latitude" : {"$gt": 51, "$lt": 52.5}}
        ]
})

db.gratka.find({ "download_date_utc" : { "$exists" : false } })


db.otodom.createIndex({"download_date_utc": 1})
db.olx.createIndex({"download_date_utc": 1})
db.gratka.createIndex({"download_date_utc": 1})
db.morizon.createIndex({"download_date_utc": 1})


db.otodom.find({}).count()
db.otodom_copy.find({}).count()

db.olx.find({}).count()
db.olx_copy.find({}).count()

db.gratka.find({}).count()
db.gratka_copy.find({}).count()

db.morizon.find({}).count()
db.morizon_copy.find({}).count()

db.otodom.find({})
db.olx.find({})
db.gratka.find({})
db.morizon.find({})

db.otodom.find({}).sort({"download_date_utc":-1}).limit(10)
db.olx.find({}).sort({"download_date_utc":-1}).limit(10)
db.gratka.find({}).sort({"download_date_utc":-1}).limit(100)
db.morizon.find({}).sort({"download_date_utc":-1}).limit(100)

db.otodom.find({"price": {"$gt":10000000}}).sort({"price":-1}).limit(10)
db.olx.find({"price": {"$gt":10000000}}).sort({"price":-1}).limit(10)
db.gratka.find({"price": {"$gt":10000000}}).sort({"price":-1}).limit(10)
db.otodom.find({"price": {"$gt":10000000}}).sort({"price":-1}).limit(10)

db.olx.find({}).sort({"download_date":-1}).limit(10)
db.gratka.find({}).sort({"download_date":-1}).limit(10)
db.morizon_copy.find({}).sort({"download_date":-1}).limit(10)



db.gratka.find({"_id":"gra_14639472_175000000"})
db.otodom.find({}).sort({"download_date":-1}).limit(10)
db.olx.find({}).sort({"download_date":-1}).limit(10)

db.Otodom.find({"download_date" : {"$gt": ISODate("2019-10-01 20:16:00.248Z") }}).sort({"download_date":-1}).limit(10)
db.otodom.find({})

db.Otodom2.updateMany({ _id : "59565240_699000" } , {$set: {download_date2: {$toDate: { $multiply: ['$download_date', 1000] }}}})

db.otodom.aggregate(
    [ 
    { $match : { _id : "oto_60341718_519000" } },
    { $project: { download_date: { $toDate: { $multiply: ['$download_date', 1000] } } } },
    { $merge: { into: "Otodom2", on: "_id", whenMatched: "merge", whenNotMatched: "discard" } }
    ]
)

// update string to date
    
db.otodom.aggregate(
    [ 
    {$match : { download_date: { $type: "string" } } },
    {$project: {
      "download_date": {
        "$dateFromString": {
          "dateString": "$download_date"
        }
      }
    }},
    { $merge: { into: "otodom_copy", on: "_id", whenMatched: "merge", whenNotMatched: "discard" } }
    ]
)
    
db.morizon.find( { download_date: { $type: "string" } } )
db.otodom.find( { download_date: { $type: "string" } } )
db.olx.find( { download_date: { $type: "string" } } )
db.gratka.find( { download_date: { $type: "string" } } )
   
db.morizon_copy.find( { download_date: { $type: "string" } } )
db.otodom_copy.find( { download_date: { $type: "string" } } )
db.olx_copy.find( { download_date: { $type: "string" } } )
db.gratka_copy.find( { download_date: { $type: "string" } } )

db.olx.aggregate([
    { "$addFields": {
        "created_at": { 
            "$dateFromString": { 
                "dateString": "$download_date"
                } 
        }
    } }
])

db.Otodom.find({"_id":'56128220_246000'})
db.Otodom.find({}).sort({"download_date":-1}).limit(10)

db.Otodom.createIndex({ price_model_dif: 1 })

db.otodom.find({ "GC_addr_city" : { "$exists" : false } })

db.Otodom.find({ "prediction_time" : { "$exists" : true } })
db.Otodom.find({ "prediction_time" : { "$exists" : false } }).count()
db.gratka.find({ "GC_addr_city" : { "$exists" : false } })


db.Otodom.distinct("GC_addr_suburb")


var  suburb =  ["Praga-Północ","Bemowo","Śródmieście","Mokotów","Żoliborz","Ursynów","Wola","Ochota",null,"Praga-Południe"]

db.Otodom.aggregate([
    { $match: { price_model_dif : {$lt: 0}, flat_size : {$lt: 80}, flat_size : {$gt: 60}, floor: {$gt: 2}, price: {$lt: 800000} }},
    { $match: { GC_addr_suburb : { $in: suburb } } },
    { $sort: { download_date : -1 } }
])
    
db.Otodom.aggregate([
    { $match: { price_model_dif : {$lt: 0}, flat_size : {$lt: 80}, flat_size : {$gt: 60}, floor: {$gt: 2}, price: {$lt: 900000} }},
    { $match: { GC_addr_suburb : { $in: suburb } } },
    { $addFields: {download_date: { $toDate: { $toLong: {$multiply:["$download_date",1000]} } } } },
    { $project : {  flat_size:1, url:1, price: 1 , price_model_dif : 1 , floor:1 , GC_addr_suburb:1 , download_date:1 } },
    { $sort: { price_model_dif : 1 } }
])
    