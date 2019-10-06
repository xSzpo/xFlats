use OFFERS

db.Otodom.find({"_id":'56128220_246000'})
db.Otodom.createIndex({ price_model_dif: 1 })

db.Otodom.find({ "prediction_time" : { "$exists" : true } }).count()

db.Otodom.find({ "prediction_time" : { "$exists" : true } })

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
    