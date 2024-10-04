import tkinter as tk
from tkinter import messagebox, ttk
import pyodbc
from hashlib import sha256
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
import requests

# Global variable to store the current user's username
current_user = None

def show_message(label, text, color):
    label.config(text=text, fg=color)

def login_or_register():
    username = username_entry.get()
    password = password_entry.get()

    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\scatt\Documents\Stock Trading App\Stock_Trading_Application.accdb;'

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE UserName = ?", (username,))
        row = cursor.fetchone()

        if row:
            reg_password = row.Password
            password_hash = sha256(password.encode('utf-8')).hexdigest()
            if password_hash == reg_password:
                show_message(login_status_label, f"Hey {username}. Welcome back.", "green")
                global current_user
                current_user = username
                open_account_options_window()
                return
            else:
                show_message(login_status_label, "The password is incorrect.", "red")
        else:
            show_message(login_status_label, "User not found.", "red")
            register_button.config(state=tk.NORMAL)

    except Exception as e:
        show_message(login_status_label, f"An error occurred: {e}", "red")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def register():
    username = username_entry.get()
    password = password_entry.get()
    email = email_entry.get()

    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\scatt\Documents\Stock Trading App\Stock_Trading_Application.accdb;'

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        password_hash = sha256(password.encode('utf-8')).hexdigest()

        cursor.execute("INSERT INTO Users (UserName, Password, Email) VALUES (?, ?, ?)", (username, password_hash, email))
        conn.commit()
        show_message(login_status_label, f"User {username} registered successfully.", "green")
        global current_user
        current_user = username
        open_account_options_window()
        root.destroy()

    except Exception as e:
        show_message(login_status_label, f"An error occurred: {e}", "red")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def open_account_options_window():
    global current_user

    root.withdraw()

    account_window = tk.Toplevel(root)
    account_window.title("Account Options")

    account_label = tk.Label(account_window, text="Choose an option:")
    account_label.pack(pady=10)

    view_account_button = tk.Button(account_window, text="View Account", command=open_view_account_window)
    view_account_button.pack(pady=5)

    buy_assets_button = tk.Button(account_window, text="Buy Assets", command=open_buy_assets_window)
    buy_assets_button.pack(pady=5)

    sell_assets_button = tk.Button(account_window, text="Sell Assets", command=open_sell_assets_window)
    sell_assets_button.pack(pady=5)

    view_transactions_button = tk.Button(account_window, text="View Transactions", command=open_view_transactions_window)
    view_transactions_button.pack(pady=5)

    update_profile_button = tk.Button(account_window, text="Update Profile", command=open_update_profile_window)
    update_profile_button.pack(pady=5)

    market_news_button = tk.Button(account_window, text="Market News", command=open_market_news_window)
    market_news_button.pack(pady=5)

def plot_portfolio_balance():
    global current_user

    user_assets = get_user_assets(current_user)
    if user_assets:
        dates = []
        balance = []
        total_balance = 0
        for asset in user_assets:
            total_balance += asset["value"]
            dates.append(asset["date_purchased"])
            balance.append(total_balance)
        
        plt.plot(dates, balance)
        plt.xlabel('Date')
        plt.ylabel('Total Balance')
        plt.title('Portfolio Balance Over Time')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showinfo("Info", "No assets found to plot.")

def open_view_account_window():
    global current_user

    view_account_window = tk.Toplevel(root)
    view_account_window.title("View Account")

    plot_button = tk.Button(view_account_window, text="Plot Portfolio Balance", command=plot_portfolio_balance)
    plot_button.pack(pady=10)

    user_assets = get_user_assets(current_user)
    if user_assets:
        for asset in user_assets:
            asset_info = f"{asset['symbol']}, | {asset['quantity']}, |Date Purchased: {asset['date_purchased']}, |Value: ${asset['value']:.2f}"
            asset_label = tk.Label(view_account_window, text=asset_info)
            asset_label.pack(pady=5)
        
        total_value = sum(asset['value'] for asset in user_assets)
        total_value_label = tk.Label(view_account_window, text=f"Total Value: ${total_value:.2f}")
        total_value_label.pack(pady=10)
    else:
        no_assets_label = tk.Label(view_account_window, text="No assets found.")
        no_assets_label.pack(pady=5)

def get_user_assets(username):
    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\scatt\Documents\Stock Trading App\Stock_Trading_Application.accdb;'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("SELECT Symbol, Quantity, PricePerUnit, DatePurchased FROM Holdings WHERE UserName = ?", (username,))
        assets = cursor.fetchall()

        if assets:
            user_assets = []
            for row in assets:
                symbol = row.Symbol
                quantity = row.Quantity
                price_per_unit = row.PricePerUnit
                date_purchased = row.DatePurchased.strftime("%Y-%m-%d %H:%M:%S")
                asset_value = quantity * price_per_unit
                user_assets.append({"symbol": symbol, "quantity": quantity, "date_purchased": date_purchased, "value": asset_value})
            return user_assets
        else:
            return []
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve user assets: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def open_buy_assets_window():
    global symbol_entry
    global quantity_entry
    global result_label
    
    buy_assets_window = tk.Toplevel(root)
    buy_assets_window.title("Buy Assets")

    symbol_label = tk.Label(buy_assets_window, text="Enter the stock symbol:")
    symbol_label.pack()
    symbol_entry = tk.Entry(buy_assets_window)
    symbol_entry.pack()

    quantity_label = tk.Label(buy_assets_window, text="Enter the quantity of shares:")
    quantity_label.pack()
    quantity_entry = tk.Entry(buy_assets_window)
    quantity_entry.pack()

    calculate_button = tk.Button(buy_assets_window, text="Calculate Total Cost", command=calculate_total_cost)
    calculate_button.pack()

    result_label = tk.Label(buy_assets_window, text="")
    result_label.pack()

def open_sell_assets_window():
    global symbol_entry_sell
    global quantity_entry_sell
    global result_label_sell

    sell_assets_window = tk.Toplevel(root)
    sell_assets_window.title("Sell Assets")

    symbol_label_sell = tk.Label(sell_assets_window, text="Enter the stock symbol:")
    symbol_label_sell.pack()
    symbol_entry_sell = tk.Entry(sell_assets_window)
    symbol_entry_sell.pack()

    quantity_label_sell = tk.Label(sell_assets_window, text="Enter the quantity of shares to sell:")
    quantity_label_sell.pack()
    quantity_entry_sell = tk.Entry(sell_assets_window)
    quantity_entry_sell.pack()

    sell_button = tk.Button(sell_assets_window, text="Sell", command=sell_assets)
    sell_button.pack()

    result_label_sell = tk.Label(sell_assets_window, text="")
    result_label_sell.pack()

def sell_assets():
    global current_user

    symbol = symbol_entry_sell.get().upper()
    quantity = quantity_entry_sell.get()

    if not symbol:
        messagebox.showwarning("Warning", "Please enter a stock symbol.")
        return
    try:
        quantity = int(quantity)
        if quantity <= 0:
            messagebox.showwarning("Warning", "Please enter a positive quantity.")
            return
    except ValueError:
        messagebox.showwarning("Warning", "Please enter a valid quantity.")
        return

    quote = get_stock_quote(symbol)
    if quote is not None:
        holdings = get_user_holdings(current_user, symbol)
        if holdings is None:
            messagebox.showerror("Error", "You don't have any holdings for this asset.")
            return

        total_revenue = quote * quantity

        if holdings < quantity:
            messagebox.showerror("Error", "You don't have enough shares to sell.")
            return

        result_label_sell.config(text=f"The total revenue from selling {quantity} shares of {symbol} is ${total_revenue:.2f}")

        update_holdings_after_sale(current_user, symbol, quantity)
        record_sale_transaction(current_user, symbol, quantity, total_revenue)

def record_sale_transaction(username, symbol, quantity, total_revenue):
    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\scatt\Documents\Stock Trading App\Stock_Trading_Application.accdb;'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        conn.autocommit = False
        now = datetime.now()

        cursor.execute("INSERT INTO TransactionLogs (UserName, Symbol, Quantity, TotalRevenue, TransactionType, TransactionDate) VALUES (?, ?, ?, ?, ?, ?)",
                       (username, symbol, quantity, total_revenue, 'SELL', now))

        cursor.execute("UPDATE Holdings SET Quantity = Quantity - ? WHERE UserName = ? AND Symbol = ?", (quantity, username, symbol))

        conn.commit()
        messagebox.showinfo("Success", "Sale transaction recorded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to record sale transaction: {e}")
        conn.rollback()
    finally:
        conn.autocommit = True
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def update_holdings_after_sale(username, symbol, quantity):
    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\scatt\Documents\Stock Trading App\Stock_Trading_Application.accdb;'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        conn.autocommit = False

        cursor.execute("SELECT Quantity FROM Holdings WHERE UserName = ? AND Symbol = ?", (username, symbol))
        row = cursor.fetchone()

        if row:
            current_quantity = row[0]
            remaining_quantity = current_quantity - quantity
            
            if remaining_quantity > 0:
                cursor.execute("UPDATE Holdings SET Quantity = ? WHERE UserName = ? AND Symbol = ?", (remaining_quantity, username, symbol))
            else:
                cursor.execute("DELETE FROM Holdings WHERE UserName = ? AND Symbol = ?", (username, symbol))
            conn.commit()
            messagebox.showinfo("Success", "Holdings updated successfully after sale.")
        else:
            messagebox.showerror("Error", "No holdings found for this asset.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update holdings after sale: {e}")
        conn.rollback()
    finally:
        conn.autocommit = True
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_stock_quote(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        return data['Close'].iloc[-1]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve data for {symbol}")
        return None

def calculate_total_cost():
    global current_user

    symbol = symbol_entry.get().upper()
    quantity = quantity_entry.get()

    if not symbol:
        messagebox.showwarning("Warning", "Please enter a stock symbol.")
        return
    try:
        quantity = int(quantity)
        if quantity <= 0:
            messagebox.showwarning("Warning", "Please enter a positive quantity.")
            return
    except ValueError:
        messagebox.showwarning("Warning", "Please enter a valid quantity.")
        return

    quote = get_stock_quote(symbol)
    if quote is not None:
        total_cost = quote * quantity
        result_label.config(text=f"The total cost for {quantity} shares of {symbol} is ${total_cost:.2f}")

        record_purchase(current_user, symbol, quantity, quote, total_cost)

def record_purchase(username, symbol, quantity, price_per_unit, total_price):
    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\scatt\Documents\Stock Trading App\Stock_Trading_Application.accdb;'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        conn.autocommit = False
        now = datetime.now()

        cursor.execute("INSERT INTO TransactionLogs (UserName, Symbol, Quantity, PricePerUnit, TotalPrice, TransactionType, TransactionDate) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (username, symbol, quantity, price_per_unit, total_price, 'BUY', now))

        cursor.execute("INSERT INTO Holdings (UserName, Symbol, Quantity, PricePerUnit, TotalPrice, DatePurchased) VALUES (?, ?, ?, ?, ?, ?)",
                       (username, symbol, quantity, price_per_unit, total_price, now))

        conn.commit()
        messagebox.showinfo("Success", "Purchase recorded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to record purchase: {e}")
        conn.rollback()
    finally:
        conn.autocommit = True
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_user_holdings(username, symbol):
    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\scatt\Documents\Stock Trading App\Stock_Trading_Application.accdb;'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("SELECT Quantity FROM Holdings WHERE UserName = ? AND Symbol = ?", (username, symbol))
        holdings = cursor.fetchone()

        if holdings:
            return holdings[0]
        else:
            return 0
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve user holdings: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def open_view_transactions_window():
    global current_user

    transactions_window = tk.Toplevel(root)
    transactions_window.title("View Transactions")

    transactions_label = tk.Label(transactions_window, text="Transaction History")
    transactions_label.pack(pady=10)

    transactions = get_user_transactions(current_user)
    if transactions:
        for transaction in transactions:
            transaction_info = f"Type: {transaction['type']}, Symbol: {transaction['symbol']}, Quantity: {transaction['quantity']}, Price: ${transaction['price']:.2f}, Date: {transaction['date']}"
            transaction_label = tk.Label(transactions_window, text=transaction_info)
            transaction_label.pack(pady=5)
    else:
        no_transactions_label = tk.Label(transactions_window, text="No transactions found.")
        no_transactions_label.pack(pady=5)

def get_user_transactions(username):
    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\scatt\Documents\Stock Trading App\Stock_Trading_Application.accdb;'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("SELECT TransactionType, Symbol, Quantity, PricePerUnit, TotalRevenue, TransactionDate FROM TransactionLogs WHERE UserName = ?", (username,))
        transactions = cursor.fetchall()

        if transactions:
            user_transactions = []
            for row in transactions:
                transaction_type = row.TransactionType
                symbol = row.Symbol
                quantity = row.Quantity
                price = row.PricePerUnit if transaction_type == 'BUY' else row.TotalRevenue
                date = row.TransactionDate.strftime("%Y-%m-%d %H:%M:%S")
                user_transactions.append({"type": transaction_type, "symbol": symbol, "quantity": quantity, "price": price, "date": date})
            return user_transactions
        else:
            return []
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve user transactions: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def open_update_profile_window():
    global current_user

    update_profile_window = tk.Toplevel(root)
    update_profile_window.title("Update Profile")

    email_label = tk.Label(update_profile_window, text="New Email:")
    email_label.pack(pady=5)
    email_entry = tk.Entry(update_profile_window)
    email_entry.pack(pady=5)

    password_label = tk.Label(update_profile_window, text="New Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(update_profile_window, show="*")
    password_entry.pack(pady=5)

    update_button = tk.Button(update_profile_window, text="Update Profile", command=lambda: update_profile(email_entry.get(), password_entry.get()))
    update_button.pack(pady=10)

def update_profile(new_email, new_password):
    global current_user

    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\scatt\Documents\Stock Trading App\Stock_Trading_Application.accdb;'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        if new_email:
            cursor.execute("UPDATE Users SET Email = ? WHERE UserName = ?", (new_email, current_user))
        if new_password:
            password_hash = sha256(new_password.encode('utf-8')).hexdigest()
            cursor.execute("UPDATE Users SET Password = ? WHERE UserName = ?", (password_hash, current_user))

        conn.commit()
        messagebox.showinfo("Success", "Profile updated successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update profile: {e}")
        conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def open_market_news_window():
    market_news_window = tk.Toplevel(root)
    market_news_window.title("Market News")

    news_label = tk.Label(market_news_window, text="Latest Market News")
    news_label.pack(pady=10)

    news = get_market_news()
    if news:
        for article in news:
            article_info = f"Title: {article['title']}, Link: {article['link']}"
            article_label = tk.Label(market_news_window, text=article_info, fg="blue", cursor="hand2")
            article_label.pack(pady=5)
            article_label.bind("<Button-1>", lambda e, link=article['link']: open_link(link))
    else:
        no_news_label = tk.Label(market_news_window, text="No news found.")
        no_news_label.pack(pady=5)

def get_market_news():
    try:
        url = "https://newsapi.org/v2/top-headlines?category=business&apiKey=YOUR_NEWS_API_KEY"
        response = requests.get(url)
        news_data = response.json()

        if news_data["status"] == "ok":
            articles = news_data["articles"]
            market_news = []
            for article in articles:
                title = article["title"]
                link = article["url"]
                market_news.append({"title": title, "link": link})
            return market_news
        else:
            return []
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve market news: {e}")
        return []

def open_link(url):
    import webbrowser
    webbrowser.open(url)

root = tk.Tk()
root.title("Login or Register")

username_label = tk.Label(root, text="Username:")
username_label.grid(row=0, column=0, padx=10, pady=5)
username_entry = tk.Entry(root)
username_entry.grid(row=0, column=1, padx=10, pady=5)

password_label = tk.Label(root, text="Password:")
password_label.grid(row=1, column=0, padx=10, pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=5)

email_label = tk.Label(root, text="Email:")
email_label.grid(row=2, column=0, padx=10, pady=5)
email_entry = tk.Entry(root)
email_entry.grid(row=2, column=1, padx=10, pady=5)

login_button = tk.Button(root, text="Login", command=login_or_register)
login_button.grid(row=3, column=0, padx=10, pady=10)

register_button = tk.Button(root, text="Register", command=register)
register_button.grid(row=3, column=1, padx=10, pady=10)
register_button.config(state=tk.DISABLED)

login_status_label = tk.Label(root, text="", fg="black")
login_status_label.grid(row=4, columnspan=2, padx=10, pady=5)

root.mainloop()
