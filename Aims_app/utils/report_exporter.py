import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from Aims_app.models import Order_Table, Order_Details
from datetime import datetime

def export_orders_to_excel(start_date, end_date, user=None):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Get all orders and filter by user if specified
    orders = Order_Details.objects.select_related('Prod_id', 'User_id', 'Order_id').all()
    if user:
        orders = orders.filter(User_id=user)

    # Filter by date range in Python to avoid database casting issues
    orders = [order for order in orders if start.date() <= order.Created_date.date() <= end.date()]

    data = []
    for order in orders:
        try:
            if not order.Order_id or not order.Prod_id or not order.User_id:
                continue  # skip if related objects are missing

            data.append({
                'Order ID': order.Order_id.Order_id,
                'Product ID': order.Prod_id.prod_id,
                'Product Name': order.Prod_id.Prod_description,
                'Image URL': order.Prod_id.Prod_image.url if order.Prod_id.Prod_image else '',
                'Quantity': order.quantity,
                'User': order.User_id.username,
                'Date': order.Created_date.strftime('%Y-%m-%d'),
                'Time': order.Created_date.strftime('%H:%M:%S'),
            })
        except Exception as e:
            # Optionally log the error or print it
            print(f"Error processing order {order.id if order.id else 'unknown'}: {e}")
            continue

    # Create DataFrame and write to Excel
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')

    buffer.seek(0)
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=order_report.xlsx'
    return response
