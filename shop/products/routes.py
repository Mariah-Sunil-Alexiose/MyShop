from flask import redirect, render_template, url_for, request, flash, session, current_app
from shop import db, app, photos, search
from .models import Brand, Category, Addproduct
from .forms import Addproducts
import secrets, os  

def brands():
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return brands

def categories():    
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/', methods=['GET', 'POST'])
def home():
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=8)
    return render_template("products/index.html", products=products, brands=brands(), categories=categories())

@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name', 'description'], limit=6)
    return render_template('products/result.html', products=products, brands=brands(), categories=categories())

@app.route('/product/<int:id>', methods=['GET', 'POST'])
def product(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/product.html', product=product, brands=brands(), categories=categories())

@app.route('/brands/<int:id>', methods=['GET', 'POST'])
def getbrand(id):
    getbrand=Brand.query.filter_by(id=id).first_or_404()
    page = request.args.get('page', 1, type=int)
    brand = Addproduct.query.filter_by(brand=getbrand).paginate(page=page, per_page=4)
    return render_template("products/index.html", brand=brand, brands=brands(), categories=categories(), getbrand=getbrand)

@app.route('/categories/<int:id>', methods=['GET', 'POST'])
def getcategory(id):
    page = request.args.get('page', 1, type=int)
    getcat = Category.query.filter_by(id=id).first_or_404()
    getcategoryproducts = Addproduct.query.filter_by(category=getcat).paginate(page=page, per_page=4)
    return render_template("products/index.html",categories=categories(), getcategoryproducts=getcategoryproducts, brands=brands(),getcat=getcat)

@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'email' not in session:
        flash('Please login in to view this page', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The brand {getbrand} is added to the database.', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template("products/addbrandcategory.html", brands='brands')

@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    if 'email' not in session:
        flash('Please login in to view this page', 'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == 'POST':
        updatebrand.name=brand
        flash('The brand name has been updated!', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrandcategory.html', title='Update Brand', updatebrand=updatebrand)

@app.route('/deletebrand/<int:id>', methods=['GET','POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(brand)
        db.session.commit()
        flash(f'The brand {brand.name} is deleted from the database', 'success')
        return redirect(url_for('brands'))
    flash(f'The brand {brand.name} cannot be deleted from the database', 'warning')
    return redirect(url_for('login'))

@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if 'email' not in session:
        flash('You need to login to view this page', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        getcategory = request.form.get('category')
        category = Category(name=getcategory)
        db.session.add(category)
        flash(f'The category {getcategory} is added to the database.', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template("products/addbrandcategory.html", category='category')

@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
def updatecategory(id):
    if 'email' not in session:
        flash('Please login in to view this page', 'danger')
        return redirect(url_for('login'))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == 'POST':
        updatecategory.name=category
        flash('The category name has been updated!', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template('products/updatebrandcategory.html', title='Update Category', updatecategory=updatecategory)

@app.route('/deletecategory/<int:id>', methods=['GET','POST'])
def deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(category)
        db.session.commit()
        flash(f'The category {category.name} is deleted from the database', 'success')
        return redirect(url_for('categories'))
    flash(f'The category {category.name} cannot be deleted from the database', 'warning')
    return redirect(url_for('login'))


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    if 'email' not in session:
        flash('You need to login to view this page', 'danger')
        return redirect(url_for('login'))
    form = Addproducts(request.form)
    brands = Brand.query.all()
    categories = Category.query.all()
    if request.method == 'POST':
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10)+ ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10)+ ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10)+ ".")
        addproduct = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors, description=description, brand_id=brand, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addproduct)
        db.session.commit()
        flash(f'The product {name} has been added to the database', 'success')
        return redirect(url_for('admin'))
    return render_template("products/addproduct.html", title='Add Product', form=form, brands=brands, categories=categories)


@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = Addproducts(request.form)
    if request.method == 'POST':
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.brand_id = brand
        product.category_id = category
        product.stock = form.stock.data
        product.colors = form.colors.data
        product.description = form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'shop/static/img' + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10)+ ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10)+ ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'shop/static/img' + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10)+ ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10)+ ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'shop/static/img' + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10)+ ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10)+ ".")
        flash('The product has been updated', 'success')
        db.session.commit()
        
        return redirect(url_for('admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.description
    return render_template('products/updateproduct.html', title='Update Product', form=form, brands=brands, categories=categories, product=product)

@app.route('/deleteproduct/<int:id>', methods=['GET', 'POST'])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method == 'POST':
        try:
            os.unlink(os.path.join(current_app.root_path, 'shop/static/img' + product.image_1))
            os.unlink(os.path.join(current_app.root_path, 'shop/static/img' + product.image_2))
            os.unlink(os.path.join(current_app.root_path, 'shop/static/img' + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} is deleted from the database', 'success')
        return redirect(url_for('admin'))
    flash(f'The product {product.name} cannot be deleted from the database', 'warning')
    return redirect(url_for('login'))