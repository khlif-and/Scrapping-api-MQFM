from audio_dakwah_streaming.domain.port import AudioDakwahStreamingCachePort, AudioDakwahStreamingScraperPort


class GetAudioDakwahStreamingUseCase:
    def __init__(self, cache: AudioDakwahStreamingCachePort, scraper: AudioDakwahStreamingScraperPort):
        self._cache = cache
        self._scraper = scraper

    def execute(self) -> dict:
        cached = self._cache.get()
        if cached:
            return cached

        entity = self._scraper.scrape()

        result = {
            "current_program": entity.current_program,
            "schedule": entity.schedule,
            "up_next_program": entity.up_next_program,
            "up_next_schedule": entity.up_next_schedule,
            "audio_url": entity.audio_url,
        }

        self._cache.set(result)
        return result
