# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from jsonlines import open


class LangchainAiDocsPipeline:

    def open_spider(self, spider):
        self.writer = open("documents.jsonl", "w")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self.writer.write(adapter.asdict())
        return item

    def close_spider(self, spider):
        self.writer.close()
