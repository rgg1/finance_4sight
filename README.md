# Finance4Sight

## Description

This is a web app I made that is currently hosted at https://finance4sight.com, which makes use of a machine learning 
model for sentiment analysis. Update: In April of 2024, the services were paused due to costs, and may eventually be live
again in the future. Everything discussed below was true prior to April 2024 when the website was still being hosted live on AWS.

How it works is that a user can search for a company from the dropdown and upon clicking "Search", be shown numerous articles that pertain to that company and its finances, as well as their predicted sentiment.

This project makes use of the Bing News Search API to search for news articles from the last week that are related to
the company. The model was trained and fine-tuned using PyTorch. The model's state is then loaded in from an S3 bucket and used to predict sentiment given the article titles that populate from the Bing API results. 

Citation for the pretrained model:

Huang, Allen H., Hui Wang, and Yi Yang. "FinBERT: A Large Language Model for Extracting Information from Financial Text." Contemporary Accounting Research (2022).

Yang, Yi, Mark Christopher Siy Uy, and Allen Huang. "Finbert: A pretrained language model for financial communications." arXiv preprint arXiv:2006.08097 (2020).

The model itself was able to obtain an accuracy of over 95 % on our test dataset. The fine-tuning consists of
5,000 financial news article titles labeled with a sentiment, and 3,000 more titles that were labeled using
another financial sentiment model called FinBERT by ProsusAI (our "teacher model").

## Installation

### Prerequisites
- Python
- PostgreSQL
- Trained PyTorch Model
- Bing Search API Subscription Key

### Steps
1. Clone the repository: `git clone https://github.com/rgg1/finance_4sight.git`
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
4. Install required packages: `pip install -r requirements.txt`
5. Apply database migrations: `python manage.py migrate`
6. Run the server: `python manage.py runserver`

## Local Configuration Guide

To run this project locally or in your own production environment, you'll need to make some changes to the `settings.py`, `load_model.py`, and `views.py` files:

### 1. **Django Secret Key**:
   - Generate a new secret key for Django. You can use [Django's Secret Key Generator](https://djecrety.ir/) or another tool.
   - Add it as an environment variable named `'DJANGO_SECRET_KEY'`, or modify `SECRET_KEY` in `settings.py` directly.

### 2. **Database Configuration**:
   - Set up a local PostgreSQL database, or configure a remote one.
   - Add environment variables for the database connection, including:
      - `'DJANGO_DB_NAME'`: Database name
      - `'DJANGO_DB_USER'`: Database user
      - `'DJANGO_DB_PASSWORD'`: Database password
      - `'DJANGO_DB_HOST'`: Database host
      - `'DJANGO_DB_PORT'`: Database port
   - Alternatively, you can modify the `DATABASES` dictionary in `settings.py` directly.

### 3. **Finetuned Model**:
   - In `load_model.py`, an S3 bucket is used to load in a state dict for the fine-tuned model. If you have
   a similar setup, you'd need to add your own S3 credentials for the environment variables, including:
      - `'AWS_ACCESS_KEY'`: AWS Access Key ID
      - `'AWS_SECRET_ACCESS_KEY'`: AWS Secret Access Key
   - If using another method to load in the model, you would need to make further configurations to adapt the file to return a trainer instance to be used for prediction, as I have done using the Hugging Face library.

### 4. **Bing Search API Key**:
   - In `views.py`, an environment variable is needed to allow the Search API to work, which is:
      - `'BING_SUBSCRIPTION_KEY'`: API Subscription Key

### 5. **Allowed Hosts**:
   - Update the `ALLOWED_HOSTS` list with your domain name, IP address, or other hosts as needed.

By configuring these settings, you should be able to run the project in a local or custom production environment.

## Usage

This section provides a general guide on how to navigate and interact with Finance4Sight.

### Making a Query
1. Visit the page at [Finance4Sight](https://finance4sight.com).
2. Begin typing in the name of a company. The dataset includes over 6000 US Stock and ETF tickers with accompanying
info. Source: https://www.kaggle.com/datasets/marketahead/all-us-stocks-tickers-company-info-logos
3. When your desired company appears in the drop down, select it and press "Search".
4. The result will be a "Results" page that shows you recent articles and their predicted sentiment, as well as 
a pie chart of relative proportions of sentiment (positive, negative, neutral).
