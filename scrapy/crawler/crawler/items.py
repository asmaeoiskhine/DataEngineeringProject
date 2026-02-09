import scrapy


class CharacterItem(scrapy.Item):
    name = scrapy.Field()
    anime = scrapy.Field()
    character_url = scrapy.Field()
    gender = scrapy.Field()
    status = scrapy.Field()
    image_url = scrapy.Field()
    scraped_at = scrapy.Field()
