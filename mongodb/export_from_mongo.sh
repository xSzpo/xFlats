mongoexport --host=localhost --port=27017 --username=xflats --password xflats --authenticationDatabase=admin --collection=olx --db=OFFERS --out=olx.json
mongoexport --host=localhost --port=27017 --username=xflats --password xflats --authenticationDatabase=admin --collection=gratka --db=OFFERS --out=gratka.json
mongoexport --host=localhost --port=27017 --username=xflats --password xflats --authenticationDatabase=admin --collection=otodom --db=OFFERS --out=otodom.json
mongoexport --host=localhost --port=27017 --username=xflats --password xflats --authenticationDatabase=admin --collection=morizon --db=OFFERS --out=morizon.json
tar -czf data_backup.tar.gz --options gzip:compression-level=9  olx.json gratka.json otodom.json morizon.json
rm olx.json gratka.json otodom.json morizon.json

#cp data_backup/otodom.json <container id>:/data
#mongoimport --host=localhost --port=27017 --username=xflats --password=xflats --authenticationDatabase=admin --db=OFFERS --collection=olx --file=/data/olx.json
#mongoimport --host=localhost --port=27017 --username=xflats --password=xflats --authenticationDatabase=admin --db=OFFERS --collection=gratka --file=/data/gratka.json
#mongoimport --host=localhost --port=27017 --username=xflats --password=xflats --authenticationDatabase=admin --db=OFFERS --collection=otodom --file=/data/otodom.json
#mongoimport --host=localhost --port=27017 --username=xflats --password=xflats --authenticationDatabase=admin --db=OFFERS --collection=morizon --file=/data/morizon.json