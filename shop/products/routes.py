from flask import render_template,session, request,redirect,url_for,flash,current_app
from shop import app,db,photos, search
from .models import Category,Brand,Addproduct
from .forms import Addproducts
import secrets
import os

allowed_pages = 8


def unlinkProdImage(product):
    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))

@app.route('/search')
def result():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name','desc'] , limit=6)
    return render_template('products/search.html',products=products,brands=brands(),categories=categories())

@app.route('/')
def home():
    prods = Addproduct.query.order_by(Addproduct.id.desc()).paginate(page=request.args.get('page',1, type=int), per_page=allowed_pages)
    return render_template('products/index.html', brands=brands(),categories=categories(), products=prods)


@app.route('/product/<int:id>')
def productpage(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/productpage.html',product=product,brands=brands(),categories=categories())


@app.route('/brand/<int:id>')
def reqBrand(id):
    brand = Addproduct.query.filter_by(brand=Brand.query.filter_by(id=id).first_or_404()).paginate(page=request.args.get('page',1, type=int), per_page=allowed_pages)
    return render_template('products/index.html',brand=brand,brands=brands(),reqBrand=Brand.query.filter_by(id=id).first_or_404(), categories=categories())


@app.route('/categories/<int:id>')
def getProdInCat(id):
    return render_template('products/index.html',prodInCat=Addproduct.query.filter_by(category=Category.query.filter_by(id=id).first_or_404()).paginate(page=request.args.get('page',1, type=int), per_page=allowed_pages),brands=brands(),categories=categories(),prodInCatg=Category.query.filter_by(id=id).first_or_404())


@app.route('/addbrand',methods=['GET','POST'])
def addbrand():
    if not "POST" == request.method:
        return render_template('products/productbrand.html', title='Add brand', brands='brands')

    db.session.add(Brand(name=request.form.get('brand')))
    flash(f'The brand {request.form.get("brand")} was added successfully to database','success')
    db.session.commit()
    return redirect(url_for('addbrand'))


def categories():
    categories = Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/editbrand/<int:id>',methods=['GET','POST'])
def editbrand(id):
    if 'email' not in session:
        flash('Login first please','danger')
        return redirect(url_for('login'))
    getbrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if "POST" == request.method:
        getbrand.name = request.form.get('brand')
        flash(f'The brand {getbrand.name} was changed to {request.form.get("brand")}','success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/productbrand.html', title='Update brand',brands='brands',updatebrand=getbrand)

def brands():
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return brands

@app.route('/removebrand/<int:id>', methods=['GET','POST'])
def removebrand(id):
    br = Brand.query.get_or_404(id)
    if not "POST" == request.method:
        flash(f"The brand {br.name} cannot be  removed from database", "warning")
        return redirect(url_for('admin'))

    db.session.delete(br)
    flash(f"The brand {br.name} was removed from database","success")
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/removeproduct/<int:id>', methods=['POST'])
def removeproduct(id):
    product = Addproduct.query.get_or_404(id)
    if not "POST" == request.method:
        flash(f'Failed to delete product', 'success')
        return redirect(url_for('admin'))

    try:
        unlinkProdImage(product)
    except Exception as e:
        print("@@@@@Exception",e)
    db.session.delete(product)
    db.session.commit()
    flash(f'The product {product.name} was delete from your record','success')
    return redirect(url_for('admin'))


@app.route('/editcategory/<int:id>',methods=['GET','POST'])
def editcategory(id):
    if 'email' not in session:
        flash('Login first please','danger')
        return redirect(url_for('login'))
    editedCat = Category.query.get_or_404(id)
    category = request.form.get('category')

    if not "POST" == request.method:
        return render_template('products/productbrand.html', title='Update cat', editedCat=editedCat)

    editedCat.name = category
    flash(f'The category {editedCat.name} was changed to {category}','success')
    db.session.commit()
    return redirect(url_for('categories'))



@app.route('/removecategory/<int:id>', methods=['GET','POST'])
def removecategory(id):
    catg = Category.query.get_or_404(id)
    if not "POST" == request.method:
        flash(f"The category {catg.name} cannot be  removed from database", "warning")
        return redirect(url_for('admin'))

    db.session.delete(catg)
    flash(f"The category {catg.name} was removed from database","success")
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/addproduct')
def getaddproduct():
    return render_template('products/product.html', form=Addproducts(request.form), title='Add a Product', brands=Brand.query.all(), categories=Category.query.all())

@app.route('/postCategory',methods=['GET','POST'])
def postCategory():
    if not "POST" == request.method:
        return render_template('products/productbrand.html', title='Add category')

    category = Category(name=request.form.get('category'))
    db.session.add(category)
    flash(f'The category {request.form.get("category")} was added to your database','success')
    db.session.commit()
    return redirect(url_for('postCategory'))

@app.route('/editproduct/<int:id>')
def editproductpage(id):
    form,product = Addproducts(request.form), Addproduct.query.get_or_404(id)
    form.name.data, form.discount.data = product.name, product.discount
    form.price.data, form.stock.data = product.price, product.stock
    form.colors.data, form.discription.data = product.colors, product.desc
    return render_template('products/product.html', prod=product, brands=Brand.query.all(), categories=Category.query.all(),title='Update Product', form=form)

@app.route('/editproduct/<int:id>', methods=['POST'])
def editproduct(id):
    form, product = Addproducts(request.form), Addproduct.query.get_or_404(id)
    brand, category = request.form.get('brand'), request.form.get('category')
    product.price, product.name = form.price.data, form.name.data
    product.discount = form.discount.data
    product.desc = form.discription.data
    product.colors = form.colors.data
    product.stock = form.stock.data
    product.brand_id = brand
    product.category_id = category
    unlink3ImagesFromOS(product)

    flash('The product was edited successfully','success')
    db.session.commit()
    return redirect(url_for('admin'))


def unlink3ImagesFromOS(product):
    if request.files.get('image_2'):
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        except:
            product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
    if request.files.get('image_1'):
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        except:
            product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")



@app.route('/addproduct', methods=['POST'])
def addproduct():
    form = Addproducts(request.form)
    if 'image_1' in request.files:
        name,discount, price, stock, desc, colors, brand, category= form.name.data, form.discount.data, form.price.data, form.stock.data,form.discription.data, form.colors.data, request.form.get('brand'), request.form.get('category')
        imagelist=[]
        imagelist.append(photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + "."))
        imagelist.append(photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + "."))
        db.session.add(Addproduct(colors=colors,desc=desc,stock=stock,category_id=category,brand_id=brand,image_1=imagelist[0],image_2=imagelist[1],name=name,price=price,discount=discount))
        flash(f'The product {name} was successfully added','success')
        db.session.commit()
        return redirect(url_for('admin'))

