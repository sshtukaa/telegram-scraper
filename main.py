from telethon import TelegramClient, functions
from datetime import datetime, timedelta
import pandas as pd
import asyncio
from info_user import *
async def counters(session, link, api_id, api_hash):
    try:
        async with TelegramClient(session, api_id, api_hash) as client:
            entity = await client.get_entity(link)
            full_entity = await client(functions.channels.GetFullChannelRequest(link))
            subscribers = full_entity.full_chat.participants_count
            count_30d = 0
            count_24h = 0
            num_views = 0
            async for message in client.iter_messages(entity):
                now = datetime.now(message.date.tzinfo)
                if (now - message.date > timedelta(hours=24)) and count_24h < 5:
                    count_24h += 1
                    views_on_post = await client(functions.messages.GetMessagesViewsRequest(
                        peer=link,
                        id=[message.id],
                        increment=False
                    ))
                    num_views += int(views_on_post.views[0].views)
                if now - message.date < timedelta(days=30):
                    count_30d += 1
            return subscribers, (num_views / 5), count_30d
    except Exception as e:
        print(f"Error while retrieving channel information {link}: {e}")
        return None, None, None
async def main():
    df = pd.DataFrame(columns=['Link', 'Number of subscribers', 'Number of views in 5 days', 'Number of messages in the last 30 days'])
    with open('channel_links.txt', 'r') as f:
        for line in f:
            original_link = line.strip()
            if not original_link:
                continue
            channel_link = original_link.replace("https://", "").replace("t.me/", "")
            subscribers, views, messages = await counters(name_of_session, channel_link, api_id, api_hash)
            if subscribers is not None:
                df = pd.concat([df, pd.DataFrame({'Link': [channel_link],
                                  'Number of subscribers': [subscribers],
                                  'Number of views in 5 days': [views],
                                  'Number of messages in the last 30 days': [messages]})], ignore_index=True)
    df.to_excel('telegram_channels.xlsx', index=False)
if __name__ == "__main__":
    asyncio.run(main())