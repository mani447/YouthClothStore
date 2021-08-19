from flask import render_template,session, request,redirect,url_for,flash,current_app
from shop import db , app
from shop.products.models import Addproduct
from shop.products.routes import brands, categories
import json

def MagerDicts(dict1,dict2):
    if isinstance(dict1, list) and isinstance(dict2,list):
        return dict1  + dict2
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))

@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        pid, color, quantity = request.form.get('product_id'), request.form.get('colors'), int(request.form.get('quantity'))
        product = Addproduct.query.filter_by(id=pid).first()
        brand = ''
        if product.brand is not None:
            brand = product.brand.name
        catg = ''
        if product.category is not None:
            catg = product.category.name
        if "POST" == request.method:
            item_map = {pid:{'id':product.id,'name':product.name,'price':float(product.price),'discount':product.discount,'color':color,'quantity':quantity,'image':product.image_1, 'colors':product.colors, 'brand':brand, 'category':catg}}
            print("item_map:", item_map)
            if not 'MYCART' in session:
                session['MYCART'] = item_map
                return redirect(request.referrer)
            else:
                print(session['MYCART'])
                if pid not in session['MYCART']:
                    session['MYCART'] = MagerDicts(session['MYCART'], item_map)
                    return redirect(request.referrer)
                else:
                    for key, val in session['MYCART'].items():
                        if int(key) == int(pid):
                            session.modified = True
                            val['quantity'] = val['quantity'] + 1


              
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)



@app.route('/carts')
def getCart():
    if 'MYCART' not in session or len(session['MYCART']) <= 0:
        return redirect(url_for('home'))
    subtotal = 0
    total = 0
    for key,product in session['MYCART'].items():
        discount = (product['discount']/100) * float(product['price'])
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        total = float("%.2f" % (1.06 * subtotal))
    return render_template('products/carts.html', total=total,brands=brands(),categories=categories())



@app.route('/editcart/<int:code>', methods=['POST'])
def editcart(code):
    if 'MYCART' not in session or len(session['MYCART']) <= 0:
        return redirect(url_for('home'))

    try:
        session.modified = True
        for key , item in session['MYCART'].items():
            if int(key) == code:
                item['quantity'] = request.form.get('quantity')
                item['color'] = request.form.get('color')
                flash('Item is updated!')
                return redirect(url_for('getCart'))
    except Exception as e:
        print("Exception:",e)
        return redirect(url_for('getCart'))



@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'MYCART' not in session or len(session['MYCART']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key , item in session['MYCART'].items():
            if int(key) == id:
                session['MYCART'].pop(key, None)
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))


@app.route('/clearcart')
def clearcart():
    try:
        session.pop('MYCART', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)

# @app.route('/checkout')
# @login_required
# def checkout():
