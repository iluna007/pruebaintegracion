# backend/routes.py

from flask import Blueprint, request, jsonify, render_template,redirect, url_for, flash, get_flashed_messages, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash,check_password_hash
from backend import app, db
from backend.models import User, Product, Cart, Order, CartItem, OrderItem, Address, ProductImage
from datetime import datetime
from backend.forms import SignupForm, SigninForm
import cloudinary.uploader

bp = Blueprint('api', __name__)


@bp.route('/')
def home():
    current_time = datetime.utcnow()
    products = Product.query.all()
    return render_template('index.html', current_time=current_time, products=products)  # Renderiza la plantilla index.html


# ----------------------------------------------------------------------------------------------------------------
# 							ENDPOINTS
# ----------------------------------------------------------------------------------------------------------------

# test endpoint for React
@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'}), 200

# ----------------------
# USER ROUTES
# ----------------------

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')  # Hash the plain password
    user = User(username=data['username'], email=data['email'], password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id}), 201
    
@bp.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        for user in users
    ])



@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    })

@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404

    # Actualizar solo los campos presentes en la solicitud
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        user.role = data['role']
    if 'password_hash' in data:
        user.password_hash = data['password_hash']

    db.session.commit()
    return jsonify({'message': 'User updated'})


@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})


# ----------------------
# PRODUCT ROUTES
# ----------------------

@bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    # Crear el producto utilizando todos los campos necesarios
    product = Product(
        sku=data['sku'],
        name=data['name'],
        description=data.get('description', ''),  # Valor por defecto si no se proporciona descripción
        price=data['price'],
        stock=data.get('stock', 0),  # Si no se proporciona, el stock será 0 por defecto
        category=data['category'],
        active=data.get('active', True),  # Por defecto, el producto estará activo
        stock_threshold=data.get('stock_threshold')  # Puede ser nulo si no se proporciona
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'id': product.id}), 201


@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'message': 'Product not found'}), 404

    # Obtener todas las imágenes asociadas al producto
    product_images = ProductImage.query.filter_by(product_id=product.id).all()

    # Crear una lista de URLs de las imágenes
    images = [{"url": image.url} for image in product_images]

    # Devolver el JSON del producto incluyendo las imágenes
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'images': images  # Añadir la lista de imágenes al JSON de respuesta
    })


@bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'message': 'Product not found'}), 404
    product.name = data['name']
    product.description = data['description']
    product.price = data['price']
    db.session.commit()
    return jsonify({'message': 'Product updated'})

@bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'message': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})
# ----------------------
# CART ROUTES
# ----------------------

@bp.route('/cart', methods=['POST'])
def create_cart():
    data = request.get_json()
    user_id = data['user_id']
    if not User.query.get(user_id):
        return jsonify({'message': 'User not found'}), 404
    cart = Cart(user_id=user_id)
    db.session.add(cart)
    db.session.commit()
    return jsonify({'id': cart.id}), 201

@bp.route('/cart/<int:cart_id>', methods=['GET'])
def get_cart(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    return jsonify({
        'id': cart.id,
        'user_id': cart.user_id,
        'items': [{'product_id': item.product_id, 'quantity': item.quantity} for item in cart.items]
    })

@bp.route('/cart/<int:cart_id>', methods=['DELETE'])
def delete_cart(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    db.session.delete(cart)
    db.session.commit()
    return jsonify({'message': 'Cart deleted'})


# ----------------------
# CART ITEM ROUTES
# ----------------------

# add stock validation
@bp.route('/cart_items', methods=['POST'])
def add_cart_item():
    data = request.get_json()
    cart = Cart.query.get(data['cart_id'])
    product = Product.query.get(data['product_id'])

    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    # Verificar si hay suficiente stock
    if product.stock < data['quantity']:
        return jsonify({'message': f'Only {product.stock} units available'}), 400

    # Agregar el producto al carrito
    cart_item = CartItem(cart_id=data['cart_id'], product_id=data['product_id'], quantity=data['quantity'])
    db.session.add(cart_item)
    db.session.commit()

    flash('Product added to cart!', 'success')
    flash_message = [str(category) + ": " + str(message) for category, message in get_flashed_messages(with_categories=True)]
    
    return jsonify({'id': cart_item.id, 'flash': flash_message}), 201



@bp.route('/cart_items/<int:cart_item_id>', methods=['PUT'])
def update_cart_item(cart_item_id):
    data = request.get_json()
    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404
    cart_item.quantity = data['quantity']
    db.session.commit()
    return jsonify({'message': 'Cart item updated'})

@bp.route('/cart_items/<int:cart_item_id>', methods=['DELETE'])
def delete_cart_item(cart_item_id):
    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Cart item deleted'})


@bp.route('/cart/<int:cart_id>/items', methods=['GET'])
def get_cart_items(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    
    cart_items = CartItem.query.filter_by(cart_id=cart_id).all()
    items = [{
        'id': item.id,
        'product_id': item.product_id,
        'quantity': item.quantity,
        'product': {
            'name': Product.query.get(item.product_id).name,
            'price': Product.query.get(item.product_id).price
        }
    } for item in cart_items]
    
    return jsonify({'cart_id': cart_id, 'items': items})


@bp.route('/cart/user/<int:user_id>', methods=['GET'])
def get_cart_by_user(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    return jsonify({
        'id': cart.id,
        'user_id': cart.user_id,
        'items': [{'product_id': item.product_id, 'quantity': item.quantity} for item in cart.items]
    })



# ----------------------
# ORDER ROUTES
# ----------------------

@bp.route('/orders', methods=['POST'])
def create_order_debug():
    data = request.get_json()
    
    # Verifica que 'cart_id' esté presente en los datos
    if 'cart_id' not in data:
        return jsonify({'message': 'Missing cart_id in request data'}), 400

    cart_id = data['cart_id']

    # Obtener el carrito y verificar su existencia
    cart = Cart.query.get(cart_id)

    if not cart:
        return jsonify({'message': 'Cart not found'}), 404

    # Obtener los artículos del carrito
    cart_items = CartItem.query.filter_by(cart_id=cart_id).all()
    if not cart_items:
        return jsonify({'message': 'Cart is empty'}), 400

    # Calcular el total_amount basado en los precios de los productos
    total_amount = 0.0
    items_details = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if not product:
            return jsonify({'message': f'Product with ID {item.product_id} not found'}), 404
        item_total = float(product.price * item.quantity)
        total_amount += item_total
        items_details.append({
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': float(product.price),
            'item_total': float(item_total)
        })
        
    # Crear la orden
    order = Order(
        user_id=cart.user_id,
        total_amount=total_amount,
        is_paid=False,  # Asumimos que la orden no está pagada inicialmente
        status='pending'  # Estado inicial de la orden
    )
    db.session.add(order)
    db.session.commit()
    
    #agregamos order items
    
    # Crear los OrderItems
    order_items_details = []
    for item in cart.items:
        product = Product.query.get(item.product_id)
        if not product:
            return jsonify({'message': f'Product with ID {item.product_id} not found'}), 404

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price  # Precio del producto en la orden
        )
        db.session.add(order_item)
        order_items_details.append({
            "order_id": order.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": product.price
        })
        

    db.session.commit()
    
    # Eliminar el carrito después de crear la orden
    db.session.delete(cart)
    db.session.commit()
    



    # Devolver la respuesta con los detalles de la orden y los artículos
    return jsonify({
        'cart_id': cart_id,
        'total_amount': float(total_amount),
        'items': items_details,
        'order_id': order.id,
        'order_items': order_items_details
        
    }), 201




@bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    return jsonify({
        'id': order.id,
        'user_id': order.user_id,
        'total_amount': order.total_amount,
        'is_paid': order.is_paid,
        'status': order.status,
        'items': [{'product_id': item.product_id, 'quantity': item.quantity, 'price': item.price} for item in order.items]
    })

@bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json()
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    # Actualiza el estado y si está pagada
    if 'status' in data:
        order.status = data['status']
    if 'is_paid' in data:
        order.is_paid = data['is_paid']

    db.session.commit()
    return jsonify({'message': 'Order updated'})

@bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted'})


# ----------------------------------------------------------------------------------------------------------------
# 							Routes for pages
# ----------------------------------------------------------------------------------------------------------------


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()  # Instancia el formulario de registro
    if form.validate_on_submit():
    
    	# Verificar si el email ya está registrado
        if User.query.filter_by(email=form.email.data).first():
            flash('Email is already registered', 'danger')
            return redirect(url_for('signup'))

        # Verificar si el nombre de usuario ya está tomado
        if User.query.filter_by(username=form.username.data).first():
            flash('Username is already taken', 'danger')
            return redirect(url_for('signup'))
            
        # Crear un nuevo usuario con contraseña encriptada
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        
        # Agregar el nuevo usuario a la base de datos
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('signin'))  # Redirigir al usuario a la página de inicio de sesión
    return render_template('signup.html', form=form)
    
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        # Buscar usuario por email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Verificar si el usuario existe y la contraseña es correcta
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)  # Inicia la sesión del usuario
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirige al dashboard o página principal
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('signin.html', form=form)
    
@app.route('/signout')
@login_required
def signout():
    logout_user()  # Cerrar la sesión del usuario
    flash('You have been logged out.', 'info')
    return redirect(url_for('signin'))  # Redirige a la página de inicio de sesión


@app.route('/dashboard')
@login_required  # Solo los usuarios autenticados pueden acceder a esta ruta
def dashboard():
    return render_template('dashboard.html')
    

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Asegurarse de que solo los administradores puedan acceder
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    # Obtener las estadísticas
    total_products = Product.query.count()
    #pending_orders = Order.query.filter_by(is_paid=True, status='pending').count()
    pending_orders = Order.query.filter(Order.is_paid == True, Order.status == 'pending').count()
    total_users = User.query.count()
    low_stock_products = Product.query.filter(Product.stock <= Product.stock_threshold).count()

    # Renderizar la plantilla con las estadísticas
    return render_template('admin_dashboard.html', 
                           total_products=total_products, 
                           pending_orders=pending_orders,
                           total_users=total_users,
                           low_stock_products=low_stock_products)

@app.route('/admin/products')
@login_required
def admin_products():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    # Aquí iría la lógica para mostrar la lista de productos
    products = Product.query.all()  # Obtener todos los productos de la base de datos
    return render_template('admin_products.html', products=products)
    
@app.route('/admin/orders')
@login_required
def admin_orders():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    # Obtener el estado y el estado de pago de la URL (si se proporcionan)
    status = request.args.get('status', 'all')
    is_paid = request.args.get('is_paid', None)

    # Iniciar la consulta
    query = Order.query

    # Si se selecciona "Pendientes", filtrar por órdenes pagadas y pendientes
    if status == 'pending':
        query = query.filter(Order.is_paid == True, Order.status == 'pending')

    # Si se selecciona "Enviadas", filtrar por órdenes pagadas y enviadas
    elif status == 'shipped':
        query = query.filter(Order.is_paid == True, Order.status == 'shipped')

    # Si se selecciona "No Pagadas", filtrar solo por órdenes no pagadas
    elif is_paid == 'false':
        query = query.filter(Order.is_paid == False)

    # Para otros estados, aplicar filtro por estado solamente (ej: empaquetadas, completadas)
    elif status != 'all':
        query = query.filter_by(status=status)

    # Obtener las órdenes filtradas
    orders = query.all()

    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/orders/<int:order_id>', methods=['GET'])
@login_required
def admin_order_detail(order_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    # Obtener la orden por ID
    order = Order.query.get(order_id)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('admin_orders'))

    # Obtener los artículos de la orden
    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    # Renderizar la plantilla de detalles de la orden
    return render_template('admin_order_detail.html', order=order, order_items=order_items)

# Permitir a los administradores actualizar el estado de la orden
@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    # Obtener la orden por ID
    order = Order.query.get_or_404(order_id)

    # Actualizar el estado de la orden
    new_status = request.form.get('status')
    if new_status:
        order.status = new_status
        db.session.commit()
        flash('Estado de la orden actualizado.', 'success')
    else:
        flash('No se pudo actualizar el estado de la orden.', 'danger')

    return redirect(url_for('admin_orders'))



@app.route('/admin/stock')
@login_required
def admin_stock():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Mostrar productos con stock bajo
    products = Product.query.filter(Product.stock <= Product.stock_threshold).all()
    return render_template('admin_stock.html', products=products)
    
@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        # Actualizar los detalles del producto
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = request.form['price']
        product.stock = request.form['stock']
        product.stock_threshold = request.form['stock_threshold']
        product.category = request.form['category']
        
        # Verificar si se ha solicitado eliminar imágenes
        images_to_delete = request.form.getlist('delete_images')  # IDs de imágenes a eliminar
        if images_to_delete:
            for image_id in images_to_delete:
                image = ProductImage.query.get(image_id)
                if image:
                    # Eliminar la imagen de Cloudinary
                    cloudinary.uploader.destroy(image.public_id)
                    # Eliminar la imagen de la base de datos
                    db.session.delete(image)

        # Verificar si se han subido nuevas imágenes
        if 'images' in request.files:
            images = request.files.getlist('images')
            for image_file in images:
                if image_file:
                    # Subir la imagen a Cloudinary
                    upload_result = cloudinary.uploader.upload(image_file)
                    # Crear una nueva entrada en ProductImage
                    new_image = ProductImage(
                        product_id=product.id,
                        url=upload_result['secure_url'],
                        public_id=upload_result['public_id']  # Guardar el public_id para eliminación futura
                    )
                    db.session.add(new_image)

        # Guardar los cambios del producto en la base de datos
        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin_edit_product.html', product=product)




import requests

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    # Hacer una llamada a la API para obtener todos los usuarios
    response = requests.get('http://localhost:5000/api/users')  # Asegúrate de usar la URL correcta
    if response.status_code == 200:
        users = response.json()  # Parsear la respuesta JSON y convertirla en un diccionario
    else:
        flash('Error al obtener los usuarios desde la API.', 'danger')
        return redirect(url_for('dashboard'))

    # Pasar los datos de usuarios a la plantilla
    return render_template('admin_users.html', users=users)
    
@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    # Obtener los datos del usuario desde la API
    response = requests.get(f'http://localhost:5000/api/users/{user_id}')
    if response.status_code == 200:
        user = response.json()  # Parsear la respuesta JSON
    else:
        flash('Error al obtener los datos del usuario.', 'danger')
        return redirect(url_for('admin_users'))

    if request.method == 'POST':
        # Actualizar el usuario a través de la API
        updated_data = {
            'username': request.form['username'],
            'email': request.form['email'],
            'role': request.form['role']
        }
        # Solo incluir password_hash si el campo de contraseña es enviado en el formulario
        if 'password' in request.form and request.form['password']:
            updated_data['password_hash'] = generate_password_hash(request.form['password'])

        response = requests.put(f'http://localhost:5000/api/users/{user_id}', json=updated_data)
        if response.status_code == 200:
            flash('Usuario actualizado exitosamente.', 'success')
        else:
            flash('Error al actualizar el usuario.', 'danger')

        return redirect(url_for('admin_users'))

    # Renderizar la plantilla para editar el usuario
    return render_template('admin_edit_user.html', user=user)
@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    # Hacer una llamada DELETE a la API para eliminar el usuario
    response = requests.delete(f'http://localhost:5000/api/users/{user_id}')
    if response.status_code == 200:
        flash('Usuario eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar el usuario.', 'danger')

    return redirect(url_for('admin_users'))

@app.route('/product/<int:product_id>')
def product_page(product_id):
    return render_template('product_details.html', product_id=product_id)

@app.route('/cart')
@login_required
def view_cart():
    app.logger.info(f"User {current_user.id} ({current_user.role}) is trying to view their cart.")
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart:
        app.logger.info(f"No cart found for user {current_user.id} with role {current_user.role}")
        flash('Your cart is empty.', 'info')
        return redirect(url_for('home'))

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()

    # Calcular el total
    total_price = sum(item.quantity * item.product.price for item in cart_items)

    if request.is_json:
        # Si la solicitud es AJAX, devolver JSON con los detalles del carrito
        return jsonify({
            'cart_id': cart.id,
            'cart_items': [{
                'id': item.id,
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': item.product.price,
                'total': item.quantity * item.product.price
            } for item in cart_items],
            'total_price': total_price
        })

    # Si no es AJAX, renderizar la plantilla de carrito
    return render_template('cart.html', cart=cart, cart_items=cart_items, total_price=total_price)



        
@app.route('/cart_items/update/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart_item(cart_item_id):
    quantity = request.form.get('quantity')
    response = requests.put(f'http://localhost:5000/api/cart_items/{cart_item_id}', json={'quantity': quantity})
    if response.status_code == 200:
        flash('Cantidad actualizada correctamente.', 'success')
    else:
        flash('Error al actualizar la cantidad.', 'danger')
    return redirect(url_for('view_cart'))

@app.route('/cart_items/delete/<int:cart_item_id>', methods=['POST'])
@login_required
def delete_cart_item(cart_item_id):
    response = requests.delete(f'http://localhost:5000/api/cart_items/{cart_item_id}')
    if response.status_code == 200:
        flash('Producto eliminado del carrito.', 'success')
    else:
        flash('Error al eliminar el producto.', 'danger')
    return redirect(url_for('view_cart'))
    
@app.route('/api/cart/total', methods=['GET'])
@login_required
def get_cart_total():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        return jsonify({'total_price': 0.0})

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    return jsonify({'total_price': total_price})



@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'GET':
        # Obtener las direcciones guardadas del usuario
        saved_addresses = Address.query.filter_by(user_id=current_user.id).all()
        cart = Cart.query.filter_by(user_id=current_user.id).first()

        if not cart or not cart.items:
            flash('Your cart is empty.', 'info')
            return redirect(url_for('home'))

        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        total_price = sum(item.quantity * item.product.price for item in cart_items)

        return render_template('checkout.html', cart=cart, cart_items=cart_items, total_price=total_price, saved_addresses=saved_addresses)

    if request.method == 'POST':
        # Verificar si se seleccionó una dirección guardada
        address_id = request.form.get('address_id')
        
        if address_id:
            # Si se seleccionó una dirección guardada, usarla
            address = Address.query.get(address_id)
            if not address or address.user_id != current_user.id:
                flash('Invalid address selected.', 'danger')
                return redirect(url_for('checkout'))
        else:
            # Si no se seleccionó una dirección guardada, crear una nueva
            address_line = request.form.get('address_line')
            city = request.form.get('city')
            postal_code = request.form.get('postal_code')
            country = request.form.get('country')
            contact_phone = request.form.get('contact_phone')
            
            # Validar que se hayan proporcionado todos los datos para una nueva dirección
            if not address_line or not city or not postal_code or not country or not contact_phone:
                flash('Please provide all details for the new address.', 'danger')
                return redirect(url_for('checkout'))

            # Crear una nueva dirección y asociarla al usuario
            address = Address(
                user_id=current_user.id,
                address_line=address_line,
                city=city,
                postal_code=postal_code,
                country=country,
                contact_phone=contact_phone
            )
            db.session.add(address)
            db.session.commit()
        
        # Guardar la dirección seleccionada o creada en la sesión (para usarla al crear la orden)
        session['shipping_address_id'] = address.id

        return redirect(url_for('payment_page'))  # Redirigir a la página de pago

    
@app.route('/checkout/validate', methods=['POST'])
@login_required
def validate_checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart:
        return jsonify({'message': 'There is no Cart'}), 400

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    invalid_items = []

    for item in cart.items:
        product = Product.query.get(item.product_id)
        if not product:
            invalid_items.append(f'Product {item.product_id} not found.')
        elif product.stock < item.quantity:
            invalid_items.append(f'Not enough stock for {product.name}. Only {product.stock} left.')
            db.session.delete(item)  # Eliminar el item del carrito
        else:
            # Recalcular precio por si cambió
            if item.product.price != product.price:
                invalid_items.append(f'Price for {product.name} has changed. Please update your cart.')

    if invalid_items:
        db.session.commit()  # Aplicar los cambios al carrito
        return jsonify({'message': 'Some items were updated', 'invalid_items': invalid_items}), 400

    # Continuar si no hay problemas
    total_price = sum(item.quantity * item.product.price for item in cart.items)
    return jsonify({'total_price': float(total_price)}), 200


@app.route('/payment_page')
@login_required
def payment_page():
    # Obtener el carrito del usuario
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart or not cart.items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('home'))

    # Validar el carrito llamando al endpoint de validación en el servidor
    validate_url = request.url_root.rstrip('/') + url_for('validate_checkout')  # Usamos request.url_root para obtener la URL completa
    response = requests.post(validate_url)
    
    if response.status_code != 200:
        flash('Cart validation failed. Please review your cart.', 'danger')
        return redirect(url_for('cart'))

    # Si la validación es exitosa, crear la orden
    create_order_url = request.url_root.rstrip('/') + url_for('api.create_order_debug')
    response = requests.post(create_order_url, json={'cart_id': cart.id})

    if response.status_code != 201:
        flash('Error creating the order.', 'danger')
        return redirect(url_for('checkout'))

    order_data = response.json()

    # Guardar el order_id en la sesión para usarlo más adelante
    session['order_id'] = order_data['order_id']

    # Calcular el total del carrito
    total_price = order_data['total_amount']

    # Renderizar la página de pago con los artículos del carrito y el total
    return render_template('payment.html', cart_items=cart.items, total_price=total_price)


@app.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    # Obtener el order_id de la sesión
    order_id = session.get('order_id')
    
    if not order_id:
        flash('No order found to process.', 'danger')
        return redirect(url_for('home'))

    # Simular el pago exitoso
    update_order_url = request.url_root.rstrip('/') + url_for('api.update_order', order_id=order_id)
    response = requests.put(update_order_url, json={'is_paid': True, 'status': 'pending'})

    if response.status_code != 200:
        flash('Error updating the order status.', 'danger')
        return redirect(url_for('home'))

    # Obtener la orden de la base de datos
    order = Order.query.get(order_id)
    if not order:
        flash(f'Order with ID {order_id} not found.', 'danger')
        return redirect(url_for('home'))

    # Actualizar el stock de los productos en la orden
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product.stock < item.quantity:
            flash(f'Not enough stock for {product.name}.', 'danger')
            return redirect(url_for('home'))  # Asegúrate de manejar casos de stock insuficiente

        product.stock -= item.quantity  # Descontar el stock
        db.session.commit()

    flash('El pago ha sido procesado exitosamente y el stock ha sido actualizado.', 'success')
    return redirect(url_for('order_confirmation'))







@app.route('/order_confirmation')
@login_required
def order_confirmation():
    # Obtener el order_id de la sesión
    order_id = session.get('order_id')

    if not order_id:
        flash('No order to confirm.', 'danger')
        return redirect(url_for('home'))

    # Obtener la orden de la base de datos
    order = Order.query.get(order_id)
    if not order:
        flash(f'Order with ID {order_id} not found.', 'danger')
        return redirect(url_for('home'))

    # Obtener los productos relacionados a la orden (OrderItems)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()

    # Si todo es correcto, renderizar la plantilla de confirmación
    return render_template('order_confirmation.html', order=order, order_items=order_items)


