import scrapy

class TestCategoriesSpider(scrapy.Spider):
    name = "test_categories"
    allowed_domains = ["fandom.com"]

    # 🔹 Liste de toutes les pages de catégories que tu veux tester
    start_urls = [
        "https://violet-evergarden.fandom.com/wiki/Category:Characters",
        "https://jujutsu-kaisen.fandom.com/wiki/Category:Characters",
        "https://bokudakegainaimachi.fandom.com/wiki/Category:Characters",
        "https://ansatsukyoshitsu.fandom.com/wiki/Category:Characters",
        "https://attackontitan.fandom.com/wiki/Category:Characters",
        "https://kimetsu-no-yaiba.fandom.com/wiki/Category:Characters",
        "https://jojo.fandom.com/wiki/Category:Characters",
        "https://dragonball.fandom.com/wiki/Category:Characters",
        "https://fruitsbasket.fandom.com/wiki/Category:Characters",
        "https://detectiveconan.fandom.com/wiki/Category:Characters",
	"https://codegeass.fandom.com/wiki/Category:Characters",
	"https://gintama.fandom.com/wiki/Category:Characters",
	"https://tokyoghoul.fandom.com/wiki/Category:Characters",
	"https://onepunchman.fandom.com/wiki/Category:Characters",
	"https://swordartonline.fandom.com/wiki/Category:Characters",
	"https://noragami.fandom.com/wiki/Category:Characters",
	"https://mob-psycho-100.fandom.com/wiki/Category:Characters",
	"https://bungostraydogs.fandom.com/wiki/Category:Characters",
	"https://chainsaw-man.fandom.com/wiki/Category:Characters",
	"https://vinlandsaga.fandom.com/wiki/Category:Characters",
	"https://myheroacademia.fandom.com/wiki/Category:Characters",
	"https://shigatsu-wa-kimi-no-uso.fandom.com/wiki/Category:Characters",
	"https://tokyorevengers.fandom.com/wiki/Category:Characters",


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
