# Importing Libraries
# Importing essential libraries for data manipulation (pandas), regular expressions (re), natural language processing (nltk, spacy),
# and for loading pre-trained models and vectorizers using pickle (pk).
import pandas as pd
import re, nltk, spacy
import pickle as pk

# Importing stopwords and stemming/lemmatization tools from nltk
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer
from nltk.stem import WordNetLemmatizer

# Downloading necessary nltk datasets for text processing
nltk.download('punkt')  # Tokenizer data
nltk.download('punkt_tab')  # Tokenizer data
nltk.download('stopwords')  # Stopwords list
nltk.download('wordnet')  # WordNet data for lemmatization
nltk.download('omw-1.4')  # Additional data for WordNet

# Loading pre-trained models and vectorizers from pickle files
count_vector = pk.load(open('pickle_files/count_vectorizer.pkl', 'rb'))  # Pre-trained Count Vectorizer
tfidf_transformer = pk.load(open('pickle_files/tfidf_transformer.pkl', 'rb'))  # Pre-trained TF-IDF Transformer
model = pk.load(open('pickle_files/logistic_regression.pkl', 'rb'))  # Pre-trained classification model
recommend_matrix = pk.load(open('pickle_files/user_final_rating.pkl', 'rb'))  # Pre-trained user-user recommendation matrix

# Loading the spaCy language model with unnecessary components disabled for efficiency
nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser'])

# Reading sample product data
products_df = pd.read_csv('sample30.csv', sep=",")

# Defining Text Preprocessing Functions

# function to clean the text using re library
def clean_text(text):
  text = text.lower()
  text = re.sub('[0-9]','',text)
  text = re.sub(r'[^a-zA-Z\s]','',text)
  return text

# function to lemmatize the text after cleaning and removing the stopwords
def lemmatize_text(text):
    text= clean_text(text)
    sent = nlp(text)
    sentence = [token.lemma_ for token in sent if token not in set(stopwords.words('english'))]
    return " ".join(sentence)

# Predicting sentiment of product review comments
def model_predict(text):
    """
    Predicts the sentiment of the given text using the pre-trained classification model.
    """
    word_vector = count_vector.transform(text)  # Transform text using Count Vectorizer
    tfidf_vector = tfidf_transformer.transform(word_vector)  # Transform to TF-IDF representation
    return model.predict(tfidf_vector)  # Predict sentiment

# Recommending products based on user sentiment
def recommend_products(user_name):
    global recommend_matrix
    """
    Generates product recommendations for a given user based on the user-user recommendation matrix
    and sentiment analysis of product reviews.
    """
    #recommend_matrix = pk.load(open('pickle_file/user_final_rating.pkl', 'rb'))  # Load recommendation matrix
    product_list = pd.DataFrame(recommend_matrix.loc[user_name].sort_values(ascending=False)[:20])  # Top 20 recommendations
    product_frame = products_df[products_df.name.isin(product_list.index.tolist())]  # Filter product data
    output_df = product_frame[['name', 'reviews_text']]  # Select relevant columns
    output_df['predicted_sentiment'] = model_predict(output_df['reviews_text'])  # Predict sentiments
    return output_df

def top5_products(df):
    """
    Retrieves the top 5 products with the highest positive sentiment percentage.
    """
    total_product = df.groupby(['name']).agg('count')  # Count total reviews per product
    rec_df = df.groupby(['name', 'predicted_sentiment']).agg('count').reset_index()  # Count sentiments per product
    merge_df = pd.merge(rec_df, total_product['reviews_text'], on='name')  # Merge with total reviews
    merge_df['%percentage'] = (merge_df['reviews_text_x'] / merge_df['reviews_text_y']) * 100  # Calculate positive percentage
    merge_df = merge_df.sort_values(ascending=False, by='%percentage')  # Sort by percentage
    return pd.DataFrame(merge_df['name'][merge_df['predicted_sentiment'] == 1][:5])  # Return top 5 products

def list_users():
    global products_df
    valid_users=products_df['reviews_username']
    return valid_users
