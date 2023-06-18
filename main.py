from flask import Flask, render_template 
from module.my_calc_module import my_calc_module
from module.sns_module import sns_module
from module.insta_module import insta_module
from module.facebook_module import facebook_module
from module.twitter_module import twitter_module
from module.search_module import search_module
from module.domain_module import domain_module
from module.network_module import network_module
# import config as config


app = Flask(__name__)
app.register_blueprint(my_calc_module)
app.register_blueprint(sns_module)
app.register_blueprint(insta_module)
app.register_blueprint(facebook_module)
app.register_blueprint(twitter_module)
app.register_blueprint(search_module)
app.register_blueprint(domain_module)
app.register_blueprint(network_module)

# app.config.from_object('config')

@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/hello")
def hello_flask():
    return render_template('loading.html')



if __name__ == "__main__":              
    app.run(host="0.0.0.0", port="8085" ,debug=True)