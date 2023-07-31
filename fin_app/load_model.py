import boto3
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
import torch
import os

s3 = boto3.client('s3',
                  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                  aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                  region_name='us-east-1')

# Specify the S3 bucket
bucket_name = 'news-model-bucket'
model_file_key = 'finetuned_finBERT_v2.model'

# Download the model file to local system
with open('model.bin', 'wb') as file:
    s3.download_fileobj(bucket_name, model_file_key, file)

# Load model and tokenizer
device = torch.device('cpu')
model = AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-pretrain', num_labels=3).to(device)
model.load_state_dict(torch.load('model.bin', map_location=device))  # With the model file in the project's root directory
tokenizer = AutoTokenizer.from_pretrained('yiyanghkust/finbert-pretrain')

# Create training arguments
training_args = TrainingArguments(
    output_dir='./results',
    do_predict=True,
    no_cuda=True,  # forces trainer to use CPU
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
)