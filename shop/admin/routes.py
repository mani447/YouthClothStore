from flask import render_template,session, request,redirect,url_for,flash
from shop import app, db, bcrypt
from .forms import RegistrationForm,LoginForm
from .models import User
from shop.products.models import Addproduct,Category,Brand

@app.route('/admin')
def admin():
    if not 'email' in  session:
        return redirect(url_for('login'))
    prods = Addproduct.query.all()
    return render_template('admin/index.html', title='Admin page',products=prods)

@app.route('/brands')
def brands():
    if not 'email' in  session:
        return redirect(url_for('login'))
    brnds = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html', title='brands',brands=brnds)

@app.route('/categories')
def categories():
    if not 'email' in  session:
        return redirect(url_for('login'))
    cats = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html', title='categories', categories=cats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(reg_form.password.data)
        admin_user = User(name=reg_form.name.data,username=reg_form.username.data, email=reg_form.email.data,
                    password=hash_password)
        db.session.add(admin_user)
        flash(f'welcome {reg_form.name.data} Thank you for registering with us','success')
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('admin/register.html',title='Register user', form=reg_form)

@app.route('/login', methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_user = User.query.filter_by(email=login_form.email.data).first()
        if login_user and bcrypt.check_password_hash(login_user.password, login_form.password.data):
            session['email'] = login_form.email.data
            flash(f'welcome {login_form.email.data} you are logged in now','success')
            return redirect(url_for('admin'))
        else:
            flash(f'Wrong email and password', 'success')
            return redirect(url_for('login'))
    return render_template('admin/login.html',title='Login page',form=login_form)

@app.route('/logout', methods=['GET','POST'])
def logout():
    session['email'] = ""
    del session['email']
    return redirect(url_for('login'))