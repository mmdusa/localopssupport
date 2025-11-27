# 🍽️ JustEat Telegram Bot – Automation & Dispatch Assistant  
*A Python-powered Telegram bot built for delivery management, reporting, and dynamic menu content.*

This bot was developed to simplify and automate routine tasks for **JustEat work operations**, including tracking reports, collecting feedback, storing rider activity, and updating information on-the-fly.  
Built with **Python**, integrated with **Google Sheets API**, the bot functions as a fast, flexible internal tool with no hardcoded UI text — meaning content updates require **zero code changes**.

---

## 🌟 Core Features

| Feature | Description |
|-------|-------------|
| 🔥 Dynamic multi-level menu | Fully interactive — menus can expand, collapse, and route users without restarting bot |
| 🧾 Google Sheets Integration | All data stored live inside sheets (feedback, notes, reports, availability, IDs, etc.) |
| 🌎 Multi-Language Support | English + Italian (expandable for more languages easily) |
| 🛠 Admin Panel | Admins can update menu texts & options directly from Google Sheets |
| 📊 Reports & Logging | System tracks user inputs, actions, and time stamps |
| 🤝 Modular Bot Structure | Every feature separated as handlers → maintainable & scalable |
| 💬 Feedback Collection | Users can send comments, issues and recommendations |
| ⏱ Availability Input System | Riders can submit weekly shifts or hours via bot instead of forms |
| 🗂 Google Sheets CRUD | Bot creates, updates, appends, reads, filters automatically |

---

## 🔧 Tech Stack

| Component | Used For |
|----------|----------|
| **Python 3.x** | Main logic & bot behavior |
| **python-telegram-bot** | Telegram API Bot Framework |
| **Google Sheets API / GSpread** | Data storage / cloud database |
| **SQLite (optional)** | Cache for faster read/write |
| **dotenv** | Environment secrets management |

---

## 🗂 Project Structure

