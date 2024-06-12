import aiohttp

from tuparser import TelegraphParser, FileManager, Config, TELEGRAPH_URL, run_parser


class MediaParser(TelegraphParser):
    def __init__(self, config):
        super().__init__(config)
        self.main_output_folder = 'parser-output'
        self.output_folder = 'media'
        self.images_folder = 'images'
        self.videos_folder = 'videos'

    async def parse(self, url, soup):
        folder_url = url[19:]

        images = self.get_urls(soup.find_all('img'))
        videos = self.get_urls(soup.find_all('video'))

        if images:
            await self.download_media(images, self.images_folder, folder_url, 'gif')
        if videos:
            await self.download_media(videos, self.videos_folder, folder_url, 'mp4')

    async def download_media(self, media, main_folder, folder, file_extension):
        media_folder_path = FileManager.join_paths(
            self.main_output_folder,
            self.output_folder,
            main_folder,
            folder,
        )
        FileManager.create_folder(media_folder_path)

        for i, value_url in enumerate(media):
            try:
                async with self.session.get(value_url) as response:
                    media_file_name = f'{i}.{file_extension}'
                    media_file_path = FileManager.join_paths(
                        media_folder_path, media_file_name
                    )
                    FileManager.save_file(media_file_path, await response.read())
            except aiohttp.client_exceptions.ClientConnectorError:
                continue

    def get_urls(self, media):
        return [
            TELEGRAPH_URL + value.get('src')
            for value in media
            if not value.get('src').startswith('http')
        ]


run_parser(config_class=Config, parser_class=MediaParser)
