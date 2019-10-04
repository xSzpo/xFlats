db.Otodom.find({"_id":'56128220_246000'})
db.Otodom.createIndex({ price_model_dif: 1 })

db.Otodom.find({ "prediction_time" : { "$exists" : true } }).count()

db.Otodom.find({ "prediction_time" : { "$exists" : true } })

db.Otodom.distinct("GC_addr_suburb")

var  suburb =  ["Praga-Północ","Bemowo","Śródmieście","Mokotów","Żoliborz","Ursynów","Wola","Ochota",null,"Praga-Południe"]

db.Otodom.aggregate([
    { $match: { price_model_dif : {$lt: 0}, flat_size : {$lt: 80}, flat_size : {$gt: 60}, floor: {$gt: 2} }},
    { $match: { GC_addr_suburb : { $in: suburb } } },
    { $sort: { download_date : -1 } }
])
    