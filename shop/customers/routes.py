import random
import re

from flask import render_template,session, request,redirect,url_for,flash,current_app,make_response
from flask_login import login_required, current_user, logout_user, login_user
from shop import app,db,photos, search,bcrypt,login_manager
from .forms import CustomerRegisterForm, CustomerLoginFrom
from .model import Register,CustomerOrder


from ..products.models import Addproduct

class InsufficientQuantityError(Exception):
    pass



@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        pwd = form.password.data
        password_tuple = isPasswordStrong(pwd)
        print("password_tuple:", password_tuple)
        if not password_tuple[0]:
            print("password_tuple[1]:",password_tuple[1])
            flash(password_tuple[1], 'warning')
            return render_template('customer/register.html', form=form, ermsg=password_tuple[1])
        else:
            hash_password = bcrypt.generate_password_hash(form.password.data)
            register = Register(name=form.name.data, username=form.username.data, email=form.email.data,password=hash_password,country=form.country.data, city=form.city.data,contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
            db.session.add(register)
            flash(f'Hey {form.name.data}. Welcome! Thank you for registering', 'success')
            db.session.commit()
            return redirect(url_for('userLogin'))
    return render_template('customer/register.html', form=form)


@app.route('/customer/login', methods=['GET','POST'])
def userLogin():
    print("mami")
    form = CustomerLoginFrom()

    if not form.validate_on_submit():
        return render_template('customer/login.html', form=form)

    user = Register.query.filter_by(email=form.email.data).first()
    if not user or not bcrypt.check_password_hash(user.password, form.password.data):
        flash('Incorrect email and password', 'danger')
        return redirect(url_for('userLogin'))

    login_user(user)
    flash('You are logged-in now!', 'success')
    next = request.args.get('next')
    return redirect(next or url_for('home'))
        # flash('Incorrect email and password','danger')
        # return redirect(url_for('userLogin'))
            
    # return render_template('customer/login.html', form=form)


def modifycart():
    for key, val in session['MYCART'].items():
        del val['image']
        del val['colors']
        session.modified = True
    return modifycart

@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        modifycart
        try:
            print("in here")
            rand = random.randint(0,9999)
            order = CustomerOrder(customer_id=customer_id,orders=session['MYCART'])
            db.session.add(order)
            # product = Addproduct.query.filter_by(id=order.orders[''].id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(
                CustomerOrder.id.desc()).first()
            print("orders", orders)
            for _key, product in orders.orders.items():
                print("key:", _key, ", prod:", product)
                pid = product['id']
                qty = int(product['quantity'])
                print("qty", qty)
                print("pid", pid)
                product = Addproduct.query.filter_by(id=pid).first()
                print("prod from db", product)
                print("product.stock",product.stock)
                if int(product.stock) - qty < 0:
                    raise InsufficientQuantityError
                elif int(product.stock) - qty == 0:
                    product.stock = 0
                    # db.session.delete(product)
                else:
                    product.stock -= qty
                    # db.session.commit()
            # print("updated prod stock", product.stock)
            db.session.commit()
            session.pop('MYCART')
            flash('Your order has been sent successfully','success')
            return redirect(url_for('thankyou'))
        except InsufficientQuantityError as e:
            print(e)
            flash('Quantity ordered is not available', 'Failed')
            return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            flash('Error during get order', 'Failed')
            return redirect(url_for('getCart'))

@app.route('/thankyou')
def thankyou():
    return render_template('customer/thank.html')


@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))

def isPasswordStrong(password):
    """
    Verify the strength of 'password'
    Returns a tuple indicating isStrong and reason
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None

    # overall result
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)
    reason = ""
    if length_error:
        reason = "Password not long enough"
    elif digit_error:
        reason = "Password does not contain digit"
    elif uppercase_error:
        reason = "Password does not contain upper case"
    elif lowercase_error:
        reason = "Password not contain lower case"
    elif symbol_error:
        reason = "Password not contain symbols"
    return password_ok, reason
