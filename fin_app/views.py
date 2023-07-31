from django.shortcuts import render
import requests
from bs4 import BeautifulSoup

import pandas as pd
from datasets import Dataset
import numpy as np

from .load_model import tokenizer, trainer

from django.http import JsonResponse
from fin_app.models import Company
from django.db.models import Q

import os

label_mapping = {0: 'positive', 1: 'negative', 2: 'neutral'}

def predict_sentiment(articles):
    df = pd.DataFrame(articles, columns=['text'])
    df['label'] = 0  # dummy labels

    def tok_func(x): 
        return tokenizer(x["text"], padding=True, truncation=True, max_length=128)

    # Convert dataframe to datasets format and encode
    dataset = Dataset.from_pandas(df)
    tok_dataset = dataset.map(tok_func, batched=True)
    tok_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    tok_dataset = tok_dataset.remove_columns(['text'])

    # Get predictions
    predictions = trainer.predict(tok_dataset)
    predicted_labels = np.argmax(predictions.predictions, axis=-1)
    
    # Replace labels
    predicted_labels = [label_mapping[i] for i in predicted_labels]

    return predicted_labels

def home(request):
    return render(request, 'fin_app/home.html')

def results(request):
    query = request.GET.get('query', '')
    query_short_name, query_ticker = query.split(": ")
    query = query_short_name + ' ' + query_ticker + ' stock news'

    # Fetch news articles
    subscription_key = os.environ.get('BING_SUBSCRIPTION_KEY')
    search_url = "https://api.bing.microsoft.com/v7.0/news/search"
    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    params  = {"q": query, "textDecorations": True, "textFormat": "HTML", "count": 30, "freshness": "Week"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    articles = []
    for article in search_results["value"]:
        title = BeautifulSoup(article["name"], 'html.parser').get_text()
        
        # Skip articles with question marks in the title
        if "?" in title:
            continue

        # Skip articles with <= 5 words in the title
        if len(title.split()) <= 5:
            continue

        # Skip articles that do not contain the short name or the ticker (case-insensitive)
        lower_title = title.lower()
        if query_short_name.lower() not in lower_title and query_ticker.lower() not in lower_title:
            continue
        
        articles.append({'url': article["url"], 'title': title})

    # Get sentiment predictions
    titles = [article['title'] for article in articles]
    sentiments = predict_sentiment(titles)
    
    # Combine articles and sentiments
    for i in range(len(articles)):
        articles[i]['sentiment'] = sentiments[i]

    sentiment_counts = {label: sentiments.count(label) for label in ['positive', 'neutral', 'negative']}

    return render(request, 'fin_app/results.html', {'articles': articles, 'sentiment_counts': sentiment_counts})

def autocomplete(request):
    query = request.GET.get('term', '')
    
    # Query for exact matches on the ticker field
    exact_ticker_matches = Company.objects.filter(ticker__iexact=query)

    # Query for other matches as before, excluding exact ticker matches
    other_matches = Company.objects.filter(
        (Q(short_name__icontains=query) | Q(ticker__icontains=query)) &
        ~Q(ticker__iexact=query)
    )[:10 - len(exact_ticker_matches)]

    # Combine the results, with exact matches first
    results = [{'label': str(company)} for company in list(exact_ticker_matches) + list(other_matches)]
    
    return JsonResponse(results, safe=False)