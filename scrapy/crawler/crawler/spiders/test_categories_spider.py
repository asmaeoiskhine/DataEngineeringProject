import scrapy

class TestCategoriesSpider(scrapy.Spider):
    name = "test_categories"
    allowed_domains = ["fandom.com"]

    # 🔹 Liste de toutes les pages de catégories que tu veux tester
    start_urls = [
	"https://obluda.fandom.com/wiki/Category:Characters",
	"https://haikyuu.fandom.com/wiki/Category:Characters",
	"https://nana.fandom.com/wiki/Category:Characters",
	"https://dr-stone.fandom.com/wiki/Category:Characters",
	"https://madeinabyss.fandom.com/wiki/Category:Characters",
	"https://dandadan.fandom.com/wiki/Category:Characters",
	"https://kaichouwamaidsama.fandom.com/wiki/Category:Characters",
	"https://ao-haru-ride.fandom.com/wiki/Category:Characters",
	"https://sayiloveyou.fandom.com/wiki/Category:Characters",
	"https://kiminitodoke.fandom.com/wiki/Category:Characters",
	"https://watashi-ga-motete-dousunda.fandom.com/wiki/Category:Characters",

    ]

    def start_requests(self):
        # 🔹 On envoie toutes les requêtes avec errback pour gérer les erreurs
        for url in self.start_urls:
            yield scrapy.Request(
                url, 
                callback=self.parse, 
                errback=self.errback_httpbin,
                dont_filter=True
            )

    def parse(self, response):
        # ✅ Page accessible
        print(f"ACCESSIBLE ✅ : {response.url}")

    def errback_httpbin(self, failure):
        # ❌ Page bloquée ou autre erreur
        request = failure.request
        print(f"BLOCKED ❌ : {request.url} - {repr(failure.value)}")
