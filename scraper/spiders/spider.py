import scrapy
import helpers
import logging

logger = logging.getLogger(__name__)


class MySpider(scrapy.Spider):

    name = 'test'
    start_urls = ['http://example.com']

    def parse(self, response):
        print("Existing settings: %s" % self.settings['MAX_PAGES'])
        file_list = helpers.scraper.list_bucket(self.settings['BUCKET_NAME'],
                                        self.settings['BUCKET_PREFIX_BSON'])
        print(file_list[:2])


class OtodomListSpider(scrapy.Spider):
    """
     :param max_pages: set max number of pages to crawl
     :param pageCounter: technical field to count how many (next) pages hac been already crawled
    """

    def __init__(self):
        # super().__init__()
        self.pageCounter = 0

    name = "otodom"

    start_urls = [
        'https://www.otodom.pl/sprzedaz/mieszkanie/warszawa',
    ]

    start_xpath = "//div[@class='col-md-content section-listing__row-content']//article[starts-with(@class,'offer-item ad')]"
    iter_xpaths_list = {
        "flat_size":"div[@class='offer-item-details']/ul[starts-with(@class,'params')]/li[@class='hidden-xs offer-item-area']/text()",
        "gallery":"figure/@data-quick-gallery",
        "img_cover_title":"figure/a/span[@class='img-cover lazy']/@title",
        "issued_by":"div[@class='offer-item-details-bottom']/ul[@class='params-small clearfix hidden-xs']/li[starts-with(@class, 'pull')]/text()",
        "location": "div[@class='offer-item-details']/header/p[@class='text-nowrap']/text()",
        "offer_id": "@data-item-id",
        "offer_title": "div[@class='offer-item-details']/header/h3/a//span[@class='offer-item-title']/text()",
        "price": "div[@class='offer-item-details']/ul[starts-with(@class,'params')]/li[@class='offer-item-price']/text()",
        "price_per_square": "div[@class='offer-item-details']/ul[starts-with(@class,'params')]/li[@class='hidden-xs offer-item-price-per-m']/text()",
        "rooms": "div[@class='offer-item-details']/ul[starts-with(@class,'params')]/li[@class='offer-item-rooms hidden-xs']/text()",
        "tracking_id": "@data-tracking-id",
        "type": "@data-featured-name",
        "url":"@data-url"
    }

    iter_xpaths_one_article = {
        'offer_type': '//div[contains(@class,"MobileLabel-className")]/text()',
        'name': '//h1[contains(@class,"AdHeader-className")]/text()',
        'location': '//a[contains(@class,"AdPage-contentStyle")]/text()',
        'price': '//div[@class="css-1hbj9if-AdHeader"]//text()[position()=1]',
        'price_m2': '//div[@class="css-cu1lls-AdHeader"]//text()',
        'flat_size': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Powierzchnia')]//strong//text()",
        'rooms': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Liczba pokoi')]//strong//text()",
        'market': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Rynek')]//strong//text()",
        'building_type': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Rodzaj zabudowy')]//strong//text()",
        'floor': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Piętro')]//strong//text()",
        'number_of_floors': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Liczba pięter')]//strong//text()",
        'building_material': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Materiał budynku')]//strong//text()",
        'widows_type': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Okna')]//strong//text()",
        'heating_type': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Ogrzewanie')]//strong//text()",
        'year_of_building': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Rok budowy')]//strong//text()",
        'finishing_stage': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Stan wykończenia')]//strong//text()",
        'rent_price': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Czynsz')]//strong//text()",
        'property_form': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Forma własności')]//strong//text()",
        'available_from': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Dostępne od')]//strong//text()",
        'description': '//*[section]//div[contains(@class, "AdDescription-className")]//text()',
        'additional_info': "//div[contains(@class, 'AdFeatures-className')]//text()",
        'tracking_id': 'substring-after(//div[@class="css-97h3nz-AdSignature-className"]/div[position()=1]//text()[following-sibling::br],":")',
        'agency_tracking_id': 'substring-after(//div[@class="css-97h3nz-AdSignature-className"]/div[position()=1]//text()[preceding-sibling::br],":")',
        'add_rel_date': 'substring-after(//div[@class="css-97h3nz-AdSignature-className"]/div[position()=2]//text()[following-sibling::br],":")',
        'update_rel_date': 'substring-after(//div[@class="css-97h3nz-AdSignature-className"]/div[position()=2]//text()[preceding-sibling::br],":")',
    }

    def parse(self, response):
        """

        :param response:
        :return:
        """
        self.pageCounter += 1

        # do something for every offer found in offers list
        for offer in response.xpath(self.start_xpath):
            tmp = {}

            for key in self.iter_xpaths_list:
                tmp[key] = offer.xpath(self.iter_xpaths_list[key]).get()
            tmp['url_offer_list'] = response.url
            tmp['producer_name'] = self.name
            tmp["main_url"] = "otodom.pl"

            request = scrapy.Request(tmp['url'], callback=self.parse_one_article)
            request.meta['data'] = tmp
            yield request

        # after you crawl each offer in current page go to the next page
        next_page = response.css('li.pager-next a::attr(href)').get()

        if next_page is not None and self.pageCounter < self.settings['MAX_PAGES']:
            yield response.follow(next_page, callback=self.parse)

    def parse_one_article(self, response):

        tmp = response.meta['data']

        for key in self.iter_xpaths_one_article:
            tmp[key] = response.xpath(self.iter_xpaths_one_article[key]).get()
        tmp['download_date'] = helpers.scraper.current_timestamp()

        tmp['geo_coordinates'], tmp['geo_address_text'], tmp['geo_address_coordin'] = helpers.scraper.get_geodata(
            response.body)

        yield tmp

