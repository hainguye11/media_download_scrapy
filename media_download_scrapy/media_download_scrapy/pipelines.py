import os
import mimetypes
from urllib.parse import urlparse
from scrapy import Request
from scrapy.pipelines.files import FilesPipeline


class ExtensionFilesPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        csv_base = item.get("csv_base")
        urls = item.get("file_urls", []) or []
        for url in urls:
            yield Request(url, meta={"is_thumbnail": False, "csv_base": csv_base})

        for url in item.get("thumbnail_urls", []) or []:
            yield Request(url, meta={"is_thumbnail": True, "csv_base": csv_base})

    def file_path(self, request, response=None, info=None, *, item=None):
        parsed_url = urlparse(request.url)
        basename = os.path.basename(parsed_url.path)
        name, ext = os.path.splitext(basename)

        if not ext and response is not None:
            content_type = response.headers.get("Content-Type", b"").decode("utf-8", errors="ignore")
            content_type = content_type.split(";")[0].strip()
            ext = mimetypes.guess_extension(content_type) or ""

        if not ext:
            ext = ".bin"

        if name.lower().endswith("_video"):
            name = name[:-6]

        csv_base = request.meta.get("csv_base")
        if request.meta.get("is_thumbnail"):
            folder = "thumbnail"
        else:
            folder = ext.lstrip(".") or "bin"

        filename = f"{name}{ext}" if name else f"downloaded_file{ext}"
        filename = filename.replace("/", "_").replace("\\", "_")

        if csv_base:
            return os.path.join(csv_base, folder, filename)
        return os.path.join(folder, filename)
