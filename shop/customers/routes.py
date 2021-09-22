from flask import redirect, render_template, url_for, request, flash, session, current_app, make_response
from flask_login import login_required, current_user, logout_user, login_user
from shop import db, app, photos, search, bcrypt
from .forms import CustomerRegisterForm, CustomerLoginForm
from .models import Register, CustomerOrder
import secrets, os, json, pdfkit, stripe

publishable_key = 'pk_test_51JWGjgJn8oiKhPNWnYv6q1vQ5vCdPxLMur2tTTdWWMQVZvqEol5dobwAEcrbadkXj9oYf1nYxO2kteUdC5gvl7CV00d49yzX5b'
stripe.api_key = 'sk_test_51JWGjgJn8oiKhPNWgZfaRhrzbXDgmpgLNc3dU5WyQPAcI2Cc9xqIqUGTdgVmaWuAK8AXuwoFVKLt9MYNeWPNY0Dx00VVnfpUvU'

@app.route('/payment', methods=['POST'])
@login_required
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description='Myshop',
        amount=amount,
        currency='usd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thank_you'))

@app.route('/thanks')
@login_required
def thank_you():
    return render_template('customer/thanks.html')

options = {'enable-local-file-access': None}

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data,password=hash_password, 
        country=form.country.data, state=form.state.data, city=form.city.data, address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(register)
        db.session.commit()
        flash(f'Welcome {form.name.data}! Thank you for registering!', 'success')
        next = request.args.get('next')
        return redirect(next or url_for('customerLogin'))

    return render_template('customer/register.html', form=form)

@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are logged in!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect username or password!', 'danger')
        return redirect(url_for('customerLogin'))
    return render_template('customer/login.html', form=form)

@app.route('/customer/logout', methods=['GET', 'POST'])
def customer_logout():
    logout_user()
    return redirect(url_for('customerLogin'))

#remove unwanted details from shopping cart
def updateshoppingcart():
    for _key, product in session['Shoppingcart'].items():
        session.modified = True
        del product['image']
        del product['colors']
    return updateshoppingcart

@app.route('/getorder')
@login_required
def get_order():
    customer_id = current_user.id
    invoice = secrets.token_hex(5)
    updateshoppingcart()
    try:    
        order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
        db.session.add(order)
        db.session.commit()
        session.pop('Shoppingcart')
        flash('Your order has been sent!', 'success')
        return redirect(url_for('orders', invoice=invoice))
    except Exception as e:
        print(e)
        flash('Something went wrong while getting the order', 'danger')
        return redirect(url_for('getCart'))

@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    grandTotal = 0
    subTotal = 0
    customer_id = current_user.id
    customer = Register.query.filter_by(id=customer_id).first()
    orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
    for _key, product in orders.orders.items():
        discount = (product['discount']/100) * float(product['price'])
        subTotal += float(product['price']) * int(product['quantity'])
        subTotal -= discount
        tax = ("%.2f" % (.06 * float(subTotal)))
        grandTotal = ("%.2f" % (1.06 * float(subTotal)))
    return render_template('customer/order.html', invoice=invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal, customer=customer,
    orders=orders)

@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    grandTotal = 0
    subTotal = 0
    customer_id = current_user.id
    if request.method == 'POST':
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))
        rendered = render_template('customer/pdf.html', invoice=invoice, tax=tax, grandTotal=grandTotal, customer=customer, orders=orders)
        pdf = pdfkit.from_string(rendered, False, options=options)
        response = make_response(pdf)
        response.headers['content-Type'] = 'application/pdf'
        response.headers['content-Disposition'] = 'inline: filename='+invoice+'.pdf'
        return response
    return request(url_for('orders'))