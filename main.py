import scrapy


class BlogSpider(scrapy.Spider):
    name = "blogspider"
    start_urls = [
        "https://www.archonia.com/en-us/p/customer-wishlist/view?customerwishlist_id=34957"
    ]

    def request(self, url, callback):
        """
        wrapper for scrapy.request
        """
        request = scrapy.Request(url=url, callback=callback)
        request.cookies["archonia_com_shop"] = ""
        return request

    def start_requests(self):
        for url in enumerate(self.start_urls):
            yield self.request(url, self.parse_item)

    def parse(self, response):
        for title in response.xpath(
            '//*[@id="main-content"]/div/div[2]/div[2]/div[1]/div/div/div/h4/a'
        ):
            yield {"title": title.css("::text").get()}

    def parse_item(self, response):
        titleList = response.css('a.title')

        for title in titleList:
            item = {}
            item['url'] = title.xpath('@href').extract()
            item['title'] = title.xpath('text()').extract()
            yield item
        url = response.xpath('//a[@rel="nofollow next"]/@href').extract_first()
        if url:
            yield self.request(url, self.parse_item)
        # you may consider scrapy.pipelines.images.ImagesPipeline :D
