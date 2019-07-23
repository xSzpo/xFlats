import scrapy
import codecs
import json


class OtodomListSpider(scrapy.Spider):
    name = "otodom"
    start_urls = [
        'https://www.otodom.pl/sprzedaz/mieszkanie/warszawa',
    ]

    start_xpath = "//div[@class='col-md-content section-listing__row-content']//article[starts-with(@class,'offer-item ad')]"
    iter_xpaths = {
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

    def parse(self, response):
        for quote in response.xpath(self.start_xpath):
            tmp = {}

            for key in self.iter_xpaths:
                tmp[key] = quote.xpath(self.iter_xpaths[key]).get()

            yield tmp

        #next_page = response.css('li.pager-next a::attr(href)').get()
        next_page = response.xpath("//li[@class='pager-next'][re:test(a/@href, '.+[1|2|3|4|5]')][1]/a/@href").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

