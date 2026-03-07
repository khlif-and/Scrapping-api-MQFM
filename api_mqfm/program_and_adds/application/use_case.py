from program_and_adds.domain.port import ProgramAndAddsCachePort, ProgramAndAddsScraperPort


class GetProgramAndAddsUseCase:
    def __init__(self, cache: ProgramAndAddsCachePort, scraper: ProgramAndAddsScraperPort):
        self._cache = cache
        self._scraper = scraper

    def execute(self) -> dict:
        cached = self._cache.get()
        if cached:
            return cached

        programs = self._scraper.scrape()

        result = {
            "programs": [
                {"title": p.title, "image_url": p.image_url}
                for p in programs
            ]
        }

        self._cache.set(result)
        return result
