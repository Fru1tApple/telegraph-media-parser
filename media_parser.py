from aiohttp.client_exceptions import ClientConnectorError

from tuparser import TelegraphParser, FileManager, TELEGRAPH_URL, run_parser


class MediaParser(TelegraphParser):
    async def parse(self, url, soup):
        folder_url = url.split("/")[-1]
        images = self.get_urls(soup.find_all("img"))
        videos = self.get_urls(soup.find_all("video"))

        if images:
            await self.download_media(images, "images", folder_url, "gif")
        if videos:
            await self.download_media(videos, "videos", folder_url, "mp4")

    async def download_media(self, media, main_folder, folder, file_extension):
        media_folder_path = FileManager.join_paths(
            "output",
            "media",
            main_folder,
            folder,
        )
        FileManager.create_folder(media_folder_path)

        for i, value_url in enumerate(media):
            try:
                async with self.session.get(value_url) as response:
                    media_file_name = f"{i+1}.{file_extension}"
                    media_file_path = FileManager.join_paths(media_folder_path, media_file_name)
                    FileManager.dump_binary_data(media_file_path, await response.read())
            except ClientConnectorError:
                ...

    def get_urls(self, media):
        return [
            TELEGRAPH_URL + value.get("src")
            for value in media
            if not value.get("src").startswith("http")
        ]


if __name__ == "__main__":
    run_parser(MediaParser)
