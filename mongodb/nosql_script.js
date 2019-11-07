use OFFERS


db.otodom.createIndex({"download_date": 1})
db.olx.createIndex({"download_date": 1})
db.gratka.createIndex({"download_date": 1})
db.morizon.createIndex({"download_date": 1})


db.otodom.find({}).count()
db.olx.find({}).count()
db.gratka.find({}).count()
db.morizon.find({}).count()


db.otodom.find({})
db.olx.find({})
db.gratka.find({})
db.morizon.find({})

db.otodom.find({}).sort({"download_date":-1}).limit(10)
db.olx.find({}).sort({"download_date":-1}).limit(10)
db.gratka.find({}).sort({"download_date":-1}).limit(10)
db.morizon.find({}).sort({"download_date":-1}).limit(10)



db.olx.find({"_id":"olx_506908384_417000"})
db.otodom.find({}).sort({"download_date":-1}).limit(10)
db.olx.find({}).sort({"download_date":-1}).limit(10)

db.Otodom.find({"download_date" : {"$gt": ISODate("2019-10-01 20:16:00.248Z") }}).sort({"download_date":-1}).limit(10)
db.Otodom.find({})

db.Otodom2.updateMany({ _id : "59565240_699000" } , {$set: {download_date2: {$toDate: { $multiply: ['$download_date', 1000] }}}})

db.Otodom2.aggregate(
    [ 
    { $match : { _id : "59565240_699000" } },
    { $project: { download_date: { $toDate: { $multiply: ['$download_date', 1000] } } } },
    { $merge: { into: "Otodom2", on: "_id", whenMatched: "merge", whenNotMatched: "discard" } }
    ]
)

db.Otodom2.find({ _id : "59565240_699000" })
   

db.collection.aggregate([
    {$match: {"_id":"56128220_246000"},
    $project: { ts: { $toDate: { $multiply: ['$download_date', 1000] } } }
])
  
db.test.find({})

db.Otodom.find({"_id":'56128220_246000'})
db.Otodom.find({}).sort({"download_date":-1}).limit(10)

db.Otodom.createIndex({ price_model_dif: 1 })

db.otodom.find({ "GC_addr_city" : { "$exists" : false } })

db.Otodom.find({ "prediction_time" : { "$exists" : true } })

db.Otodom.find({ "prediction_time" : { "$exists" : false } }).count()



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
    