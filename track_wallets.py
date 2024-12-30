from telethon import TelegramClient, events
import re

# Telegram API configuration
api_id = "REDACTED"  # Your Telegram API ID
api_hash = "REDACTED"  # Your Telegram API Hash
channel_ids = [-1002450316172, 6521948333, -1002118591205]  # Channels to monitor
your_user_id = 7606329246  # Your Telegram User ID
your_username = "@Vuxified"  # Replace with your Telegram username

# Initialize Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Tracker for coin buyers and transactions
coin_wallets = {}
coin_transactions = {}

# Function to extract links, CA, and market cap
def extract_data(message):
    try:
        # Extract token address
        address_match = re.search(r"([A-Za-z0-9]{32,}pump)", message)  # Include "pump" in the address
        token_address = address_match.group(1) if address_match else None

        # Extract market cap
        marketcap_match = re.search(r"MC: \$([\d.,]+[KM]?)", message)
        market_cap = marketcap_match.group(1) if marketcap_match else "Unknown MC"

        # Construct Bullx and Trojan links
        bullx_link = f"https://neo.bullx.io/terminal?chainId=1399811149&address={token_address}" if token_address else "N/A"
        trojan_link = f"https://t.me/paris_trojanbot?start=d-RickBot-{token_address}" if token_address else "N/A"

        return bullx_link, trojan_link, token_address, market_cap
    except Exception as e:
        print(f"Error extracting data: {e}")
        return "N/A", "N/A", "N/A", "Unknown MC"

# Function to calculate PnL and percentage sold
def calculate_pnl(wallet, token, amount_sold):
    try:
        if token not in coin_transactions or wallet not in coin_transactions[token]:
            return "Unknown PnL", "Unknown Percentage"

        # Retrieve original buy amount
        total_bought = coin_transactions[token][wallet]["bought"]

        # Calculate percentage sold and PnL
        percentage_sold = (amount_sold / total_bought) * 100 if total_bought else 0
        pnl = total_bought - amount_sold  # Simplified PnL; expand as needed

        return f"{pnl:.2f} PnL", f"{percentage_sold:.2f}% sold"
    except Exception as e:
        print(f"Error calculating PnL: {e}")
        return "Error in PnL", "Error in Percentage"

# Function to process BUY transactions
def process_buy_message(message):
    try:
        if "BUY" in message:
            # Extract token name
            token_match = re.search(r"🔗 #(\w+)", message)
            token = token_match.group(1) if token_match else None

            # Extract wallet name
            wallet_match = re.search(r"🔹 ([\w\s]+)", message)
            wallet = wallet_match.group(1).strip() if wallet_match else None

            # Extract data
            bullx_link, trojan_link, contract_address, market_cap = extract_data(message)

            # Extract buy amount (assume in message, adjust regex as needed)
            buy_amount_match = re.search(r"Bought: (\d+)", message)
            buy_amount = float(buy_amount_match.group(1)) if buy_amount_match else 0

            if token and wallet:
                # Initialize coin in tracker if not present
                if token not in coin_wallets:
                    coin_wallets[token] = set()
                    coin_transactions[token] = {}

                # Add wallet to coin's buyer list
                coin_wallets[token].add(wallet)

                # Track transactions
                if wallet not in coin_transactions[token]:
                    coin_transactions[token][wallet] = {"bought": 0, "sold": 0}
                coin_transactions[token][wallet]["bought"] += buy_amount

                # Check if two or more wallets bought the same coin
                if len(coin_wallets[token]) >= 2:
                    alert_message = (
                        f"🔥🚨 BUY ALERT: {len(coin_wallets[token])} wallets have bought {token}!\n"
                        f"Wallets: {', '.join(coin_wallets[token])}\n"
                        f"Total Wallets in Coin: {len(coin_wallets[token])}\n"
                        f"Market Cap: {market_cap}\n"
                        f"Contract Address: {contract_address}\n\n"
                        f"🔗 Trojan Link: [Buy {token}]({trojan_link})\n"
                        f"📈 Bullx Link: [View {token} on Bullx]({bullx_link})\n\n"
                        f"🔔 Hey {your_username}, check this out!"
                    )
                    print(alert_message)  # Debugging: Print alert message
                    return alert_message
    except Exception as e:
        print(f"Error processing BUY message: {e}")
    return None

# Function to process SELL transactions
def process_sell_message(message):
    try:
        if "SELL" in message:
            # Extract token name
            token_match = re.search(r"🔗 #(\w+)", message)
            token = token_match.group(1) if token_match else None

            # Extract wallet name
            wallet_match = re.search(r"🔹 ([\w\s]+)", message)
            wallet = wallet_match.group(1).strip() if wallet_match else None

            # Extract data
            bullx_link, trojan_link, contract_address, market_cap = extract_data(message)

            # Extract sell amount (assume in message, adjust regex as needed)
            sell_amount_match = re.search(r"Sold: (\d+)", message)
            sell_amount = float(sell_amount_match.group(1)) if sell_amount_match else 0

            # Only alert if more than 2 wallets have bought the token
            if token in coin_wallets and len(coin_wallets[token]) >= 2:
                # Remove wallet from the coin's buyer list
                if wallet in coin_wallets[token]:
                    coin_wallets[token].remove(wallet)

                # Update transactions
                if token in coin_transactions and wallet in coin_transactions[token]:
                    coin_transactions[token][wallet]["sold"] += sell_amount

                # Calculate PnL and percentage sold
                pnl, percentage_sold = calculate_pnl(wallet, token, sell_amount)

                # Create an alert message
                alert_message = (
                    f"🚨 SELL ALERT: {wallet} sold {token}.\n"
                    f"Remaining Wallets in Coin: {len(coin_wallets[token])}\n"
                    f"Market Cap: {market_cap}\n"
                    f"Contract Address: {contract_address}\n\n"
                    f"PnL: {pnl}\n"
                    f"Percentage Sold: {percentage_sold}\n\n"
                    f"🔗 Trojan Link: [Sell {token}]({trojan_link})\n"
                    f"📈 Bullx Link: [View {token} on Bullx]({bullx_link})\n\n"
                    f"🔔 Hey {your_username}, check this out!"
                )
                print(alert_message)  # Debugging: Print alert message
                return alert_message
    except Exception as e:
        print(f"Error processing SELL message: {e}")
    return None

# Event handler for new messages
@client.on(events.NewMessage(chats=channel_ids))
async def handler(event):
    try:
        print("Handler triggered!")  # Debugging: Confirm the handler is working

        # Get the message content
        if event.message:
            message = event.message.message
            chat_id = event.chat_id  # Get the chat ID of the message
            if message:  # If the message has text content
                print(f"New message received in {chat_id}: {message}")  # Print the message to the console

                # Process the message for BUY transactions
                buy_alert = process_buy_message(message)
                if buy_alert:  # If a buy alert is generated
                    await client.send_message(your_user_id, buy_alert, parse_mode="Markdown")  # Send alert to your Telegram

                # Process the message for SELL transactions
                sell_alert = process_sell_message(message)
                if sell_alert:  # If a sell alert is generated
                    await client.send_message(your_user_id, sell_alert, parse_mode="Markdown")  # Send alert to your Telegram
            else:
                print(f"Received non-text message or empty content in {chat_id}.")
        else:
            print("Event has no message object.")
    except Exception as e:
        print(f"Error in handler: {e}")

# Start the Telegram client
with client:
    print(f"Monitoring Telegram chats: {channel_ids}")
    client.run_until_disconnected()
