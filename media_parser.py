from aiohttp.client_exceptions import ClientConnectorError

from tuparser import TelegraphParser, FileManager, TELEGRAPH_URL, run_parser


class MediaParser(TelegraphParser):
    async def parse(self, url, soup):
        self.main_output_folder = 'output'
        self.output_folder = 'media'
        images_folder = 'images'
        videos_folder = 'videos'

        folder_url = url[19:]

        images = self.get_urls(soup.find_all('img'))
        videos = self.get_urls(soup.find_all('video'))

        if images:
            await self.download_media(images, images_folder, folder_url, 'gif')
        if videos:
            await self.download_media(videos, videos_folder, folder_url, 'mp4')

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
                    FileManager.dump_binary_data(media_file_path, await response.read())
            except ClientConnectorError:
                continue

    def get_urls(self, media):
        return [
            TELEGRAPH_URL + value.get('src')
            for value in media
            if not value.get('src').startswith('http')
        ]


run_parser(MediaParser)
