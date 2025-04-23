from django.contrib import admin
from .models import Category, Sub_Category, Products, Cart_table, Stock_master, Order_Details, Order_Table

# Base Admin with common date formatting
class BaseAdmin(admin.ModelAdmin):
    def formatted_created_date(self, obj):
        return obj.Created_date.strftime('%Y-%m-%d %H:%M:%S') if obj.Created_date else "-"
    formatted_created_date.admin_order_field = 'Created_date'
    formatted_created_date.short_description = 'Created Date & Time'
    
    def formatted_update_date(self, obj):
        return obj.Update_date.strftime('%Y-%m-%d %H:%M:%S') if obj.Update_date else "-"
    formatted_update_date.admin_order_field = 'Update_date'
    formatted_update_date.short_description = 'Updated Date & Time'


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ('Category_id', 'Category_description', 'formatted_created_date', 'formatted_update_date', 'User_id')
    search_fields = ('Category_description',)
    readonly_fields = ('Created_date', 'Update_date')
    fields = ('Category_id', 'Category_description', 'Created_date', 'Update_date', 'User_id')


@admin.register(Sub_Category)
class SubCategoryAdmin(BaseAdmin):
    list_display = ('SubCat_id', 'SubCat_description', 'Category_id', 'formatted_created_date', 'formatted_update_date', 'User_id')
    search_fields = ('SubCat_description', 'Category_id__Category_description')
    readonly_fields = ('Created_date', 'Update_date')
    fields = ('SubCat_id', 'SubCat_description', 'Category_id', 'Created_date', 'Update_date', 'User_id')


@admin.register(Products)
class ProductsAdmin(BaseAdmin):
    list_display = (
        'prod_id', 
        'Prod_description', 
        'get_category_description', 
        'Prod_price', 
        'formatted_created_date', 
        'formatted_update_date', 
        'User_id'
    )
    search_fields = (
        'Prod_description', 
        'SubCategory__SubCat_description', 
        'SubCategory__Category_id__Category_description'
    )
    readonly_fields = ('Created_date', 'Update_date')
    fields = (
        'prod_id', 
        'Prod_description', 
        'Prod_image', 
        'Prod_price', 
        'SubCategory', 
        'Created_date', 
        'Update_date', 
        'User_id'
    )

    def get_category_description(self, obj):
        return obj.SubCategory.Category_id.Category_description if obj.SubCategory else "-"
    get_category_description.short_description = 'Category'


@admin.register(Cart_table)
class CartTableAdmin(BaseAdmin):
    list_display = ('Cart_id', 'prod_id', 'quantity', 'total_price', 'formatted_created_date', 'formatted_update_date', 'User_id')
    search_fields = ('prod_id__Prod_description', 'User_id__username')
    readonly_fields = ('Created_date', 'Update_date')
    fields = ('Cart_id', 'prod_id', 'quantity', 'total_price', 'Created_date', 'Update_date', 'User_id')


@admin.register(Stock_master)
class StockMasterAdmin(BaseAdmin):
    list_display = ('prod_id', 'Total', 'Min_Value', 'formatted_created_date', 'formatted_update_date', 'User_id')
    search_fields = ('prod_id__Prod_description',)
    readonly_fields = ('Created_date', 'Update_date')
    fields = ('prod_id', 'Total', 'Min_Value', 'Created_date', 'Update_date', 'User_id')


@admin.register(Order_Details)
class OrderDetailsAdmin(BaseAdmin):
    list_display = ('Order_id', 'Prod_id', 'quantity', 'formatted_created_date', 'formatted_update_date', 'User_id')
    search_fields = ('Prod_id__Prod_description', 'Order_id__Order_id')
    readonly_fields = ('Order_id', 'Prod_id', 'quantity', 'Created_date', 'Update_date', 'User_id')
    fields = ('Order_id', 'Prod_id', 'quantity', 'Created_date', 'Update_date', 'User_id')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order_Table)
class OrderTableAdmin(BaseAdmin):
    list_display = ('Order_id', 'Order_date', 'User_id', 'Status')
    search_fields = ('Order_id', 'Status', 'User_id__username')
    readonly_fields = ('Order_id', 'Order_date', 'User_id')
    fields = ('Order_id', 'Order_date', 'User_id', 'Status')
    list_editable = ('Status',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None and 'Status' in form.base_fields:
            form.base_fields['Status'].choices = obj._meta.get_field('Status').choices
        return form
