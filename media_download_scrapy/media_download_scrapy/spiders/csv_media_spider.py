import csv
import os
from scrapy import Spider
from media_download_scrapy.items import MediaDownloadScrapyItem


class CsvMediaSpider(Spider):
    name = "csv_media"
    custom_settings = {
        "CSV_INPUT_FILE": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "input/SS_MX_PH_JAN25_TO_APR26.csv")
        )
    }

    def __init__(self, csv_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if csv_file:
            self.csv_file = os.path.abspath(csv_file)
        else:
            self.csv_file = self.custom_settings.get("CSV_INPUT_FILE")

        if not self.csv_file:
            raise ValueError("csv_file must be provided either as an argument or via CSV_INPUT_FILE")

        self.csv_base = os.path.splitext(os.path.basename(self.csv_file))[0]
        self.jobdir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "crawls", self.csv_base)
        )
        os.makedirs(self.jobdir, exist_ok=True)
        self.custom_settings["JOBDIR"] = self.jobdir

    def start_requests(self):
        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(f"CSV input file not found: {self.csv_file}")

        with open(self.csv_file, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None:
                raise ValueError("CSV file is empty or malformed")

            lowered = {name.lower(): name for name in reader.fieldnames}
            column_name = lowered.get("creative_url_supplier") or lowered.get("creative_url_suppiler")
            if column_name is None:
                raise ValueError("CSV file must contain a 'CREATIVE_URL_SUPPILER' column")

            for row in reader:
                url = row.get(column_name, "")
                if not url:
                    continue
                url = url.strip()
                if not url:
                    continue

                item = MediaDownloadScrapyItem()
                item["file_urls"] = [url]
                item["thumbnail_urls"] = []
                item["csv_base"] = os.path.splitext(os.path.basename(self.csv_file))[0]

                lower_url = url.lower()
                thumb_url = None
                if lower_url.endswith("_video.webm"):
                    thumb_url = url[:-len("_video.webm")] + ".jpeg"
                elif lower_url.endswith("_video.mp4"):
                    thumb_url = url[:-len("_video.mp4")] + ".jpeg"
                elif lower_url.endswith(".mp4"):
                    thumb_url = url[:-len(".mp4")] + ".jpeg"

                if thumb_url:
                    item["thumbnail_urls"].append(thumb_url)

                item["source_row"] = row
                yield item
