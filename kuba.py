from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

from cloudipsp import Api, Checkout


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.title


@app.route('/')
def index():
    items = Item.query.order_by(-Item.price).all()
    return render_template('index.html', data=items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post')
def post():
    articles = Item.query.order_by(Item.id).all()
    return render_template('post.html', articles=articles)

@app.route('/post/<int:id>')
def post_detail(id):
    article = Item.query.get(id)
    return render_template('post_detail.html', article=article)

@app.route('/post/<int:id>/del')
def post_delete(id):
    article = Item.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/post')
    except:
        return "Error"

@app.route('/post/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Item.query.get(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.price = request.form['price']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "ERORR"
    else:
        return render_template('post_update.html', article=article)


@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id)

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": str(item.price) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        text = request.form['text']

        item = Item(title=title, price=price, text=text)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "ERORR"
    else:
        return render_template('create.html')

if __name__ == "__main__":
    app.run(debug=True)