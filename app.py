# Importing necessary modules
from flask import Flask, render_template, redirect, url_for, request  # Flask for web app, render_template for rendering HTML templates, request for handling form data
import model  # Importing the custom model module (assumed to contain recommendation logic)

# Initializing Flask application
app = Flask(__name__)  # Use __name__ as the Flask app name (fixed incorrect '__name__' string)

introduction = 'Welcome to the Sentiment Analysis Recommendation System. Please enter the username for whom the products are to be recommended'

# List of valid user IDs
#valid_userid = ['piggyboy420','joshua']
valid_userid=model.list_users()

conversation_bot=[]
conversation_bot.append({'bot':introduction})
top_5_recommendations = None

# Route to render the home page 
@app.route('/')
def view():
    """
    Displays the home page where the user can input their user name.
    """
    global conversation, conversation_bot, top_5_recommendations
    return render_template('sentiment_analysis_index.html', name=conversation_bot)

@app.route("/end_conv", methods=['POST','GET'])
def end_conv():
    global conversation, conversation_bot
    conversation_bot =[]
    conversation_bot.append({'bot':introduction})
    return redirect(url_for('view'))

@app.route("/list_users", methods=['POST'])
def list_users():
    global conversation, conversation_bot, valid_userid
    #conversation_bot =[]
    #valid_users = valid_userid
    print(conversation_bot)
    print(str(list(valid_userid)))
    conversation_bot.append({'user':'list users is clicked'})
    conversation_bot.append({'bot':str(list(valid_userid))})
    return render_template(
            'sentiment_analysis_index.html',
            name=conversation_bot
        )

# Route to handle product recommendations
@app.route('/recommend', methods=['POST'])
def recommend_top5():
    global conversation, conversation_bot, top_5_recommendations, valid_userid
    """
    Handles the recommendation logic. Accepts the user's name via POST request,
    validates the user, and displays the top 5 product recommendations if the user is valid.
    """
    print(request.method)  # Debugging: print the request method
    user_name = request.form['user_input_message']  # Get the user name from the form input
    print('User name =', user_name)  # Debugging: print the user name

    # Validate the user and method
    if user_name in list(valid_userid) and request.method == 'POST':
        # Fetch the top 20 recommended products for the user
        top20_products = model.recommend_products(user_name)
        
        # Extract the top 5 products
        get_top5 = model.top5_products(top20_products)
        print('******List********')
        print(str(list(get_top5['name'])))
        print(conversation_bot)
        conversation_bot.append({'user':user_name})
        conversation_bot.append({'bot':'Recommended top 5 products'})
        conversation_bot.append({'bot':str(list(get_top5['name']))})
        print('******conversation_bot********')
        # Render the recommendations in the HTML page with a table and a message
        return render_template(
            'sentiment_analysis_index.html',
            name=conversation_bot
        )
    else:
        # Render the home page with a "no recommendation" message for invalid users
        conversation_bot.append({'user':user_name})
        conversation_bot.append({'bot':'No Recommendation found for the user'})
        return render_template('sentiment_analysis_index.html', name=conversation_bot)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)  # Start the application