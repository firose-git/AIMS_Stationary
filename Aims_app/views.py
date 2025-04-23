from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import ContactForm
from django.contrib.auth.models import User
from .models import Profile, Products, Stock_master, Category, Sub_Category, Cart_table,Order_Table, Order_Details
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
#require_POST
import json
from decimal import Decimal

@login_required(login_url='/login/')
def add_to_cart(request, product_id=None):
    """Handles adding products to the cart."""
    if request.method == "POST":
        try:
            print("🔹 Received Request Method:", request.method)  
            print("🔹 Request Content Type:", request.content_type)

            # Use product_id from URL if present, otherwise check POST data
            if not product_id:
                if request.content_type == "application/json":
                    data = json.loads(request.body.decode('utf-8'))
                    product_id = data.get("product_id")
                else:
                    product_id = request.POST.get("product_id")

            print("🔹 Extracted Product ID:", product_id)

            if not product_id:
                return JsonResponse({"error": "Product ID is missing!"}, status=400)

            product = get_object_or_404(Products, prod_id=product_id)
            print("🔹 Found Product:", product)

            # Add product to cart
            cart_item, created = Cart_table.objects.get_or_create(
                User_id=request.user,
                prod_id=product,
                defaults={"quantity": 1}
            )

            if not created:
                cart_item.quantity += 1
                cart_item.save()

            return JsonResponse({"message": "Product added successfully!", "cart_url": "/cart/"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format!"}, status=400)
        except Exception as e:
            print(f"❌ Error in add_to_cart: {e}")  # Debugging
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

@login_required
def message_view(request):
    user = request.user
    orders = Order_Table.objects.filter(User_id=user).order_by('-Order_date')

    # Group each order with its related details
    order_data = []
    for order in orders:
        details = Order_Details.objects.filter(Order_id=order, User_id=user)
        order_data.append({
            'order': order,
            'details': details,
            
        })

    return render(request, 'message.html', {'order_data': order_data})



import traceback  # Import traceback for detailed error logs
from django.http import HttpResponse
@login_required(login_url='/login/')
def view_cart(request):
    """Displays the user's shopping cart."""
    try:
        cart_items = Cart_table.objects.filter(User_id=request.user)

        if not cart_items.exists():
            total_cost = 0.0  # Avoid calculation errors on empty carts
        else:
            total_cost = sum(float(str(item.prod_id.Prod_price)) * item.quantity for item in cart_items)

        context = {
            'cart_items': cart_items,
            'total_cost': total_cost,
        }
        return render(request, 'categories/cart.html', context)

    except Exception as e:
        print(f"Error fetching cart: {e}")
        return HttpResponse(f"An error occurred: {e}", status=500)

@login_required
def update_cart(request, cart_id, action):
    """Increase or decrease quantity in cart based on stock availability."""
    cart_item = get_object_or_404(Cart_table, Cart_id=cart_id)
    
    # Retrieve stock info from Stock_master
    stock_entry = Stock_master.objects.filter(prod_id=cart_item.prod_id).first()
    
    if not stock_entry:
        return JsonResponse({"status": "error", "message": "Stock information not found."})

    if action == 'increase':
        if stock_entry.Total > 0:
            cart_item.quantity += 1
            stock_entry.Total -= 1
            stock_entry.save()
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
        stock_entry.Total += 1
        stock_entry.save()

    cart_item.save()

    total_price = cart_item.quantity * Decimal(str(cart_item.prod_id.Prod_price))

    # Debugging
    response_data = {
        "status": "success",
        "quantity": cart_item.quantity,
        "total_price": float(total_price)  # Convert Decimal to float for JSON compatibility
    }
    print("Response Data:", json.dumps(response_data, indent=2))

    return JsonResponse(response_data)
def remove_from_cart(request, Cart_id):
    try:
        print(f"Attempting to remove cart item with ID: {Cart_id}")  # Debugging log
        cart_item = get_object_or_404(Cart_table, Cart_id=Cart_id)  # Use 'Cart_id' instead of 'id'
        cart_item.delete()
        return JsonResponse({"success": True, "message": "Item removed from cart"})  # JSON response
    except Exception as e:
        print(f"Error deleting cart item: {e}")  # Debugging log
        return JsonResponse({"success": False, "message": str(e)}, status=400)
    
def confirm_order(request):
    """Confirm the order and remove items from the cart."""
    cart_items = Cart_table.objects.filter(User_id=request.user)
    if not cart_items:
        return JsonResponse({"message": "Your cart is empty!"}, status=400)

    # Simulate order placement
    cart_items.delete()
    return JsonResponse({"message": "✅ Order confirmed successfully!"}, status=200)

def category_view(request, category_name):
    category = get_object_or_404(Category, Category_description=category_name)
    subcategories = Sub_Category.objects.filter(Category_id=category)
    return render(request, f'categories/{category_name.lower()}.html', {'category': category, 'subcategories': subcategories})

def subcategory_products(request, subcat_id):
    subcategory = get_object_or_404(Sub_Category, SubCat_id=subcat_id)
    products = Products.objects.filter(SubCategory=subcategory)
    
    for product in products:
        stock_entry = Stock_master.objects.filter(prod_id=product.prod_id).first()
        product.stock = stock_entry.Total if stock_entry else 0

    return render(request, 'categories/subcategory_products.html', {'subcategory': subcategory, 'products': products})
#stationary_Page 
from django.template.loader import get_template

def _fetch_product_stock(products):  # Helper function to fetch stock
    for product in products:
        stock_entry = Stock_master.objects.filter(prod_id=product.prod_id).first()
        product.stock = stock_entry.Total if stock_entry else 0
    return products

def stationary_page(request):
    try:
        category = Category.objects.filter(Category_description="Stationary").first()
        subcategories = Sub_Category.objects.filter(Category_id=category) if category else []
        return render(request, 'categories/Stationary_items.html', {'subcategories': subcategories})

    except Exception as e:
        return HttpResponse(f"Error: {e}")  # Debugging

def subcategory_products(request, subcat_id):
    subcategory = get_object_or_404(Sub_Category, SubCat_id=subcat_id)
    products = Products.objects.filter(SubCategory=subcategory)  # Get products for the subcategory
    products = _fetch_product_stock(products) # Fetch stock

    return render(request, 'categories/subcategory_products.html', {
        'subcategory': subcategory,
        'products': products
    })

def electronics_categories(request):
    try:
        category = Category.objects.filter(Category_description="Electronics").first()
        subcategories = Sub_Category.objects.filter(Category_id=category) if category else []
        return render(request, 'categories/electronics.html', {'subcategories': subcategories})
    except Exception as e:
        return HttpResponse(f"Error: {e}")  # Debugging

def electronics_products(request, subcategory_id):
    subcategory = get_object_or_404(Sub_Category, SubCat_id=subcategory_id)
    products = Products.objects.filter(SubCategory=subcategory)  # Get products for the subcategory
    products = _fetch_product_stock(products)  # Fetch stock

    return render(request, 'categories/electronics_products.html', {
        'subcategory': subcategory,
        'products': products
    })





from django.shortcuts import render, get_object_or_404
from .models import Sub_Category, Products, Category



def upload_product(request):
    if request.method == "POST":
        try:
            prod_id = request.POST.get('prod_id')
            description = request.POST.get('prod_description', '')
            price = request.POST.get('prod_price')
            subcategory = request.POST.get('subcategory')
            user_id = request.POST.get('user_id')

            # Validate numeric fields
            if not prod_id or not price or not prod_id.isdigit() or not price.replace('.', '', 1).isdigit():
                return JsonResponse({'error': 'Invalid product ID or price'}, status=400)
            
            if request.FILES.get('prod_image'):
                image = request.FILES['prod_image']
                fs = FileSystemStorage(location='media/product_images/')
                image_name = fs.save(image.name, image)
                image_url = fs.url(image_name)
            else:
                image_url = None  # Default value if no image uploaded

            # Create Product entry in DB
            product = Products.objects.create(
                prod_id=prod_id, 
                description=description, 
                price=float(price),
                subcategory_id=subcategory, 
                user_id=user_id, 
                image=image_url
            )

            return JsonResponse({'success': 'Product uploaded successfully', 'product_id': product.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate inputs
        if not username or not email or not password:
            messages.error(request, "All fields are required!")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Create Profile
        profile, created = Profile.objects.get_or_create(user=user)

        messages.success(request, "Successfully registered! Please log in.")
        return redirect('login')

    return render(request, 'register.html')
def paper_view(request):
    subcategory = get_object_or_404(Sub_Category, SubCat_description="Paper")  # Get 'Paper' subcategory
    products = Products.objects.filter(SubCategory=subcategory)  # Fetch products under 'Paper'

    # Add stock details to each product
    for product in products:
        stock_entry = Stock_master.objects.filter(prod_id=product.prod_id).first()
        product.stock = stock_entry.Total if stock_entry else 0  # If stock exists, use it; else, set to 0

    return render(request, 'categories/paper.html', {'subcategory': subcategory, 'products': products})

def Filing_view(request):
    subcategory = get_object_or_404(Sub_Category, SubCat_description="Filing")  # Get 'Paper' subcategory
    products = Products.objects.filter(SubCategory=subcategory)  # Fetch products under 'Paper'

    # Add stock details to each product
    for product in products:
        stock_entry = Stock_master.objects.filter(prod_id=product.prod_id).first()
        product.stock = stock_entry.Total if stock_entry else 0  # If stock exists, use it; else, set to 0

    return render(request, 'categories/filling.html', {'subcategory': subcategory, 'products': products})


    

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')  # Redirect to home or dashboard after login
        else:
            messages.error(request, "Invalid credentials, please try again.")
            return redirect('login')

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

#All Product Stationary and Electronics items
def stationary_view(request):
    products = Products.objects.all()  # Fetch all stationery products
     # Fetch stock for each product
    for product in products:
        stock_entry = Stock_master.objects.filter(prod_id=product.prod_id).first()
        product.stock = stock_entry.Total if stock_entry else 0  # Default to 0 if no stock data
    return render(request, 'categories/All_Products.html', {'products': products})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            contact = form.save()
            # Customize your success message with user input
            success_message = f"Thank you, {contact.name}! We have received your message and will get back to you soon."
            return render(request, 'contact_submission.html', {'message': success_message})
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})


def submit_form(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Or other logic for form handling
            return redirect('submit_form')  # Redirect to the 'submit_form' view
    else:
        form = ContactForm()

    return render(request, "contact_submission.html", {'form': form})


def search_products(request):
    query = request.GET.get('q', '')
    if query:
        results = Products.objects.filter(Prod_description__icontains=query)  # Ensure field is correct
    else:
        results = []
    
    return render(request, 'search_results.html', {'results': results, 'query': query})# Function to handle confirming purchase from cart page
# Function to handle confirming purchase from cart page
def confirmPurchase(request):
    if request.method == "POST":
        user = request.user
        cart_items = Cart_table.objects.filter(User_id=user)
        
        if cart_items.exists():
            try:
                # Create a new order in Order_Table
                new_order = Order_Table.objects.create(
                    User_id=user,
                    Status='Pending'
                )
                
                # Create Order_Details for each cart item
                for item in cart_items:
                    Order_Details.objects.create(
                        Order_id=new_order,
                        Prod_id=item.prod_id,
                        User_id=user,
                        quantity=item.quantity
                    )
                
                # Clear cart after purchase
                cart_items.delete()
                
                # Return successful JSON response
                return JsonResponse({
                    'success': True,
                    'message': 'Order confirmed successfully!',
                    'redirect': f'/checkout/{new_order.Order_id}/'
                })
            except Exception as e:
                print(f"Error in confirmPurchase: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating order: {str(e)}'
                }, status=500)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Your cart is empty.'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

# Updated checkout function with proper decimal handling
def checkout(request, order_id):
    try:
        # Get the order
        order = Order_Table.objects.get(Order_id=order_id, User_id=request.user)
        
        # Get all order details (products) for this order
        order_details = Order_Details.objects.filter(Order_id=order)
        
        purchased_products = []
        for item in order_details:
            # Convert the Decimal128 to string and then to Decimal for safe multiplication
            price = Decimal(str(item.Prod_id.Prod_price))
            purchased_products.append({
                'Prod_description': item.Prod_id.Prod_description,
                'Prod_image': item.Prod_id.Prod_image.url,
                'quantity': item.quantity,
                'Prod_price': price,
                'total_price': price * item.quantity,
            })
        
        # Calculate the total cost of the order
        total_order_cost = sum(item['total_price'] for item in purchased_products)
        
        return render(request, 'checkout.html', {
            'purchased_products': purchased_products,
            'order': order,
            'total_order_cost': total_order_cost
        })
    except Order_Table.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('stationary')
    
    
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from Aims_app.models import User , Order_Details, Order_Table
from .utils.report_exporter import export_orders_to_excel
from django.http import HttpResponse
import datetime
from datetime import datetime as dt

@staff_member_required
def download_order_report(request):
    # Initialize users for the dropdown
    users = User.objects.all()

    if request.method == "POST":
        # Get form data
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        user_id = request.POST.get('user_id')
        view_report = request.POST.get('view_report')  # Check if the 'View Report' button was clicked

        # Check if user_id is provided, else None (for all users)
        user = User.objects.get(id=user_id) if user_id else None

        # Handle View Report Button
        if view_report:
            orders = Order_Details.objects.select_related('Prod_id', 'User_id', 'Order_id').all()
            if user:
                orders = orders.filter(User_id=user)

            # Filter by date range in Python to avoid database casting issues
            start = dt.strptime(start_date, "%Y-%m-%d")
            end = dt.strptime(end_date, "%Y-%m-%d")
            orders = [order for order in orders if start.date() <= order.Created_date.date() <= end.date()]

            # Prepare data for the report to display
            data = []
            for order in orders:
                if order.Order_id and order.Prod_id and order.User_id:
                    data.append({
                        'Order ID': order.Order_id.Order_id,
                        'Product ID': order.Prod_id.prod_id,
                        'Product Name': order.Prod_id.Prod_description,
                        # In the view
'Image_URL': order.Prod_id.Prod_image.url if order.Prod_id.Prod_image else '/media/default_image.png',

                        'Quantity': order.quantity,
                        'User': order.User_id.username,
                        'Date': order.Created_date.strftime('%Y-%m-%d'),
                        'Time': order.Created_date.strftime('%H:%M:%S'),
                    })
            # Render the report view page with the filtered data
            return render(request, 'admin/view_report.html', {'data': data, 'users': users})

        # Handle Download Report Button
        return export_orders_to_excel(start_date, end_date, user)

    # Render the report download form with the list of users for the dropdown
    return render(request, 'admin/download_report.html', {'users': users})
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from Aims_app.models import Order_Details, User, Order_Table, Products
from datetime import datetime as dt
@staff_member_required
def view_report(request):
    # Initialize users for the dropdown
    users = User.objects.all()
    
    if request.method == "POST":
        try:
            # Get form data
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            user_id = request.POST.get('user_id')
            
            # Check if date inputs are valid
            try:
                start = dt.strptime(start_date, "%Y-%m-%d")
                end = dt.strptime(end_date, "%Y-%m-%d")
            except ValueError as e:
                return render(request, 'admin/view_report.html', {
                    'error': f"Invalid date format: {str(e)}",
                    'users': users
                })

            # Build the query
            orders = Order_Details.objects.select_related('Order_id', 'Prod_id', 'User_id').all()
            
            # Filter by user if specified
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    orders = orders.filter(User_id=user)
                except User.DoesNotExist:
                    return render(request, 'admin/view_report.html', {
                        'error': "Selected user does not exist.",
                        'users': users
                    })

            # Filter by date range
            filtered_orders = []
            for order in orders:
                if start.date() <= order.Created_date.date() <= end.date():
                    filtered_orders.append(order)

            # Prepare data for display
            data = []
            for order in filtered_orders:
                # Ensure we have all required relations and print debug info
                print(f"Processing order detail ID: {order.id}")
                print(f"Order_id object: {order.Order_id}")
                print(f"Order_id.Order_id value: {order.Order_id.Order_id if order.Order_id else 'None'}")
                print(f"Prod_id object: {order.Prod_id}")
                print(f"Prod_id.prod_id value: {order.Prod_id.prod_id if order.Prod_id else 'None'}")
                print(f"Prod_id.Prod_description: {order.Prod_id.Prod_description if order.Prod_id else 'None'}")
                
                # Create row data carefully checking each attribute
                row_data = {
                    'order_id': order.Order_id.Order_id if order.Order_id else "-",
                    'product_id': order.Prod_id.prod_id if order.Prod_id else "-",
                    'product_name': order.Prod_id.Prod_description if order.Prod_id else "-",
                    'Image_URL': order.Prod_id.Prod_image.url if (order.Prod_id and order.Prod_id.Prod_image) else '/media/default_image.png',
                    'Quantity': order.quantity,
                    'User': order.User_id.username if order.User_id else "-",
                    'Date': order.Created_date.strftime('%Y-%m-%d'),
                    'Time': order.Created_date.strftime('%H:%M:%S'),
                    'Approval_Status': order.Order_id.Status if order.Order_id else "Pending"
                }
                
                # Print the resulting row data for debugging
                print(f"Row data: {row_data}")
                data.append(row_data)

            return render(request, 'admin/view_report.html', {
                'data': data,
                'users': users,
                'start_date': start_date,
                'end_date': end_date,
                'selected_user_id': user_id
            })
            
        except Exception as e:
            import traceback
            print(f"Error in view_report: {str(e)}")
            print(traceback.format_exc())
            return render(request, 'admin/view_report.html', {
                'error': f"An error occurred: {str(e)}",
                'users': users
            })

    # If GET request, render the form with users
    return render(request, 'admin/download_report.html', {'users': users})