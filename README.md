# Singapore-Malaysia Checkpoint Crowd Level Bot

This project provides a pipeline and a Telegram bot to collect, process, and predict crowd levels at the Singapore-Malaysia land checkpoints using real user reports from Telegram channels.

## Architecture & Workflow

```plaintext

[Telegram Channel] 

     ↓

getMessages.py  (collects messages)

     ↓

[LLM Inference Layer — on message arrival] 

     ↓

processData.py / preprocess.py  (cleans, merges, classifies)

     ↓

[Structured Storage] (CSV files in /data, or optionally SQLite/JSON/vector DB)

     ↓

User Query (via Telegram)

     ↓

simple_query_bot.py (Lightweight NLP or Rule Logic)

     ↓

Bot Response using latest structured data or prediction

```

**Workflow Details:**

-**getMessages.py**: Fetches messages from the Telegram channel and saves them to CSV.

-**processData.py / preprocess.py**: Cleans and classifies messages (e.g., as "High", "Low", "Not related").

-**Structured Storage**: Data is stored in CSV files in the `data/` directory.

-**Model Training**: Use prediction_model.py

-**simple_query_bot.py**: Telegram bot that answers user queries using the latest data and predictions.

## Features

- **Automated Data Collection**: Fetches messages from a Telegram channel and stores them in CSV format.
- **Data Processing & Classification**: Cleans and classifies messages into crowd levels (`High`, `Low`, etc.) and directions.
- **Prediction Model**: Uses machine learning (XGBoost) to predict crowd levels based on time, day, holidays, and more.
- **Telegram Bot**: Answers user queries about current and historical crowd levels, and suggests best times/days to travel.

---

## Setup

### 1. Install Dependencies

```sh
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory with the following variables:

```
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
PHONE_NUMBER=your_telegram_phone_number
SESSION_STRING=your_telethon_session_string
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

- Get your Telegram API credentials from https://my.telegram.org.
- Generate a session string using Telethon (see [Telethon docs](https://docs.telethon.dev/en/stable/basic/signing-in.html#generating-a-string-session)).

---

## Data Pipeline

### 1. Collect Telegram Messages

Run:

```sh
python getMessages.py
```

- This fetches the latest messages from the target Telegram channel and saves them to `data/telegram_messages.csv`.
- **Tip:** To fetch more messages, change the `count` parameter in `fetch_messages()` in [`getMessages.py`](getMessages.py) (default: 10).

### 2. Process and Classify Messages

Run:

```sh
python processData.py
```

- This script processes raw messages, merges replies, and classifies each message as `High`, `Low`, `Not related`, or `Bot message`.
- Output is saved as `data/new_classified_messages_2.csv`.
- Keep in mind that after the initial rule-based classification, we use an Ollama LLM for further message classification to optimize memory usage. Please ensure your machine is capable of running Ollama. The required Ollama model file,  **myllama3.modelfile** , has been provided for use.

### 3. Train or Update the Prediction Model

- Use [`main.ipynb`](main.ipynb) to experiment, preprocess, and train the XGBoost model.
- The trained model and encoders are saved in the `model/` directory.

---

## Running the Telegram Bot

Start the bot with:

```sh
python simple_query_bot.py
```

The bot will respond to queries such as:

- `information Singapore to Malaysia` — Get latest crowd info for the direction. If there is no recent information available, the telegram bot will automatically draw prediction data from **prediction_model.py**.
- `What was the crowd level on May 15 2025 at 10:00, from Singapore to Malaysia?` — Get historical crowd info.
- `get me the best day to travel for the week` — Get best days to travel based on historical data.
  ![images Crowd By Day](images\crowdLevelByDay.png "Crowd Level across the Week")


* `get me the best time to travel for Tuesday` — Get best hours to travel on a specific day.
  ![image By Hour]()

---

## Notes & Tips

- **Regular Updates**: Run `getMessages.py` regularly to keep the data fresh.
- **Data Volume**: `processData.py` is currently limited to the last 1000 rows to avoid memory issues. Adjust as needed.
- **Bot Query Format**: The bot expects queries in specific formats. More flexible parsing can be improved on.
- **Model Files**: The bot requires the model and encoders in the `model/` directory (`xgb_model.pkl`, `label_encoder.pkl`, `direction_encoder.pkl`).

---

## Customization

- **Keyword Logic**: See [`architecture`](architecture) for the logic and keywords used to classify messages.
- **Prediction Features**: The model uses features like time of day, day of week, month, public holidays, and direction. This model only achieves an accuracy of 60 % through a XGBoost Classifier Model. Alternative model methods such as using LLMs to classify and predict these data might improve the accuracy of the model.
- **Adding Features**: You can add more features (e.g., weather, school holidays) by modifying the preprocessing and model training steps.

---

## Troubleshooting

- If you get errors about missing model files, ensure you have trained and saved the model using the notebook.
- If you need more data, increase the fetch count in `getMessages.py`.
- For any issues with Telegram API, check your `.env` credentials and session string.

---

## Acknowledgements

- Built using [python-telegram-bot](https://python-telegram-bot.org/), [Telethon](https://docs.telethon.dev/), [pandas](https://pandas.pydata.org/), [XGBoost](https://xgboost.readthedocs.io/), and more.
- Data is sourced from public Telegram channels for educational and non-commercial use.

---

## License

This project is for educational and personal use only. Not for commercial deployment.
