import requests
import os
from tradingview_screener import Query, Column

query = (Query()
    .select('name', 'close', 'premarket_high', 'premarket_change', 'premarket_volume', 'market_cap_basic')
    .where(
        Column('exchange') == 'NASDAQ',
        Column('close') <= 15,
        Column('premarket_change') >= 22,
        Column('premarket_volume') >= 100000,
        Column('market_cap_basic').between(1, 2000000000)
    )
    .order_by('premarket_change', ascending=False)
)

count, df = query.get_scanner_data()

# Calculate the drop and create the new column
df['Pullback %'] = ((df['premarket_high'] - df['close']) / df['premarket_high']) * 100

# Filter for a minimum 20% drop
df = df[df['Pullback %'] >= 10]

# Round to 2 decimal places
df['Pullback %'] = df['Pullback %'].round(2)

#if not df.empty:
#    print(df.to_string(index=False))
#else:
#    print("Zero stocks meet these criteria at this exact moment.")
alert_file = "alerted.txt"
alerted = set(open(alert_file).read().splitlines()) if os.path.exists(alert_file) else set()

df = df[~df['name'].isin(alerted)]

if not df.empty:
    webhook_url = "YourDiscordWebhookURL"
    formatted_alerts = []
    
    with open(alert_file, "a") as f:
        for index, row in df.iterrows():
            ticker = row['name']
            price = f"${row['close']:.2f}"
            high= f"${row['premarket_high']:.1f}"
            chg = f"+{row['premarket_change']:.1f}%"
            vol = f"{row['premarket_volume'] / 1000000:.1f}M"
            drop = f"{row['Pullback %']:.1f}%"
            
            formatted_alerts.append(f"🚨 {ticker} | {price} ({chg}) | High:{high} | Vol: {vol} | Drop: {drop}")
            f.write(f"{ticker}\n") 
            
    message = "**VSA Scanner Alert:**\n" + "\n".join(formatted_alerts)
    requests.post(webhook_url, json={"content": message})