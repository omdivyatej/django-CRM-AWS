from django.forms import formset_factory, inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group


from .filters import *
from .models import *
from .forms import *


def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()
    total_orders = orders.count()

    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders': orders, 'customers': customers,
               'total_orders': total_orders, 'delivered': delivered,
               'pending': pending}

    return render(request, "accounts/dashboard.html", context)


def products(request):
    products = Products.objects.all()
    return render(request, "accounts/products.html", {'products': products})


def customer(request, pk):
    '''
    # Most of the time, I forget how id comes, to note that django automatically creates id
(a number) when new user is created in Models, but not visible on the dashboard. To retrive id, 
    simple reiterate over customer objects, then customer.id 
    Like in url for viewing customer , 
    <a href={% url 'customer' customer.id %}>View</a>
    {% for order in orders %}  , order is the context passed from the views.py
    <a class="btn btn-sm btn-info" href={% url 'update_order' order.id %}>Update</a></td>
    So, we pass an arbitrary number in the customer/456/ and django will try to find that id, 
    if id exists, then will fetch the associted data.    
    So, similarly all models that are ever created will have an id with every row , so , 
    Cars model any data will have id, so car/2 , now, if any data has id 2 , it will show all associated data
    '''
    customer = Customer.objects.get(id=pk)
    customer_order = Order.objects.filter(customer=customer)
    customer_order_count = customer_order.count()

    '''
    filter() expects a single object, not a queryset.
    Hence, this would not work. 
    customer = Customer.objects.filter(id=pk)  ....using filter instead of "get" 
    -> <QuerySet [<Customer: Hariom>]>
    customer_order = Order.objects.filter(customer=customer)  
    Here, customer is a queryset, not a single Customer object. Therefore, when you try to use 
    customer in the filter() method for the Order model, 
    it won't work as expected, as filter() expects a single object, NOT a queryset.

    But the first one,  Customer.objects.get(id=pk) , get retrieves a single object and hence this works.
    '''

    myFilter = OrderFilter(request.GET, queryset=customer_order)
    customer_order = myFilter.qs

    context = {'customer': customer, 'customer_order': customer_order,
               'customer_order_count': customer_order_count, 'filter': myFilter}
    return render(request, "accounts/customer.html", context)


def createOrder(request, pk):
    # formset - creating multiple forms
    # When we are viewing a customer and want to place an order, it is understood it is being done by the customer,
    # so we want only the product and status ( multiple times for ease of order creation), not customer field.
    # hence we use inlineformset_factory with first paramter something that is already known (Parent) - Customer, and
    # then model-Order (child) which we want to manipulate. Once form submitted, djqango will automatically
    # find the customer and relevant details and update the database. Fields denote which field we want to
    # show in the UI. "extra" means how many forms do we want, aprt from already exisiting in the dta base.
    OrderFormSet = inlineformset_factory(
        extra=3, parent_model=Customer, model=Order, fields=('product', 'status'))
    customer = Customer.objects.get(id=pk)
    # Need to put this otherwise context will throw error since its outside if statement
    formset = OrderFormSet(instance=customer, queryset=Order.objects.none())
    # and becuase of this, some of the forms are already prefilled with data of previous orders. But if we
    # include queryset=Order.objects.none(), then previous data orders wll not show. It is just saying to formset that
    # while you are creating the formset make sure to use this query on top of that as a condition. Since query relates
    # to getting no objects, hence that condition is applied while creating the formset.

    # order_form = OrderForm(initial={'customer': customer})
    '''
    You may think: 
    customer= Customer.objects.get(id=pk)
    order_form = OrderForm(instance=customer) also possible
    this will not work as expected because the OrderForm is designed to handle Order model instances, Reme
    mber....Class Meta:
                model= Order 
    not Customer model instances. To use this, you need to Form Set like above.
    '''
    # dont forget (), otherwise won't work
    if request.method == 'POST':
        print("Data submitted: ", request.POST)
        # don't forget to feed/map data to actual model, big mistake
        # order_form = OrderForm(request.POST)
        # instance= Customer, all customer data needs to be transferred to form set.
        formset = OrderFormSet(request.POST, instance=customer)
        # if you see, we are kinda "updating" our databse with new records,hence, like the format of UPDATE
        # opertion (CRUD).
        if formset.is_valid():
            formset.save()
            return redirect('accounts_home')

    context = {'formset': formset}
    return render(request, "accounts/order_form.html", context)


def updateOrder(request, pk):
    '''
    As we already know, any Model ever created will have a unique id to its every row,
    so, this url will add an id in the url form, then its our job to do watever with that id, here
    we are getting all order details assoaited with that id. To get the id, 
    {% for order in orders %}  , order is the context passed from the views.py
    <a class="btn btn-sm btn-info" href={% url 'update_order' order.id %}>Update</a></td>

    '''
    order = Order.objects.get(id=pk)
    # instance is very helpful to prefill data
    # Prepare the order form using the instance data- "order"
    order_form = OrderForm(instance=order)

    # if request.method == 'UPDATE': #nothing like this
    if request.method == 'POST':
        # update data with new instance data
        order_form = OrderForm(request.POST, instance=order)
        if order_form.is_valid():
            order_form.save()
            return redirect('accounts_home')
    context = {'form': order_form}
    return render(request, "accounts/update_order_form.html", context)


def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    context = {'item': order}
    if request.method == 'POST':
        order.delete()
        return redirect('accounts_home')
    return render(request, "accounts/delete_order.html", context)


def create_product(request):

    ProductFormSet = formset_factory(ProductCreationForm, extra=4)
    if request.method == 'POST':
        formset = ProductFormSet(request.POST)
        print("POST data:", request.POST)
        if formset.is_valid():
            for form in formset:
                # Save each product instance individually
                # formset.save() works firectly only for inlineformsets, not formsets.
                if form.is_valid():
                    print("Form data is valid:", form.cleaned_data)
                    form.save()
                else:
                    print("Form data is not valid:", form.errors)

            return redirect('accounts_home')
        else:
            print("Formset is not valid:", formset.non_form_errors())
    else:
        formset = ProductFormSet()

    context = {'formset': formset}
    return render(request, "accounts/create_product_form.html", context)


def register(request):
    form = CustomUserForm()
    if request.method == "POST":
        print(request.POST)
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()  #very important , form.save returns a user object.
            print(user)
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name="customer")
            user.groups.add(group) # adding user obj to customer
            # no email, last name needed as of now.
            Customer.objects.create(user=user)
            messages.success(request, "Account created for " + username)
            return redirect('login')

    context = {'form': form}
    return render(request, "accounts/register.html", context)


def loginPage(request):
    # First authenticate(), create user, then login()
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts_home')
        else:
            messages.info(request, 'Username or password incorrect')
    context = {}
    return render(request, "accounts/login.html", context)


def logOutUser(request):
    logout(request)
    return redirect('login')


def publicPage(request):
    return HttpResponse("Everybody can view this page")


def user_page(request,page):    
    page_views = {
        'account_settings': account_settings,
         # Default view function for URLs like localhost/user_page/
        # Add more page names and associated view functions here
    }
    view_function = page_views.get(page)     
    return view_function(request)

def user_page_default(request):
     # because customer & user are onetoone related
    orders = request.user.customer.order_set.all()
    # or Order.objects.filter(customer=request.user.customer)
    total_orders = orders.count()
    delivered = orders.filter(status="delivered").count()
    pending = orders.filter(status="pending").count()
    context = {'orders': orders, 'total_orders': total_orders,
               'delivered': delivered, 'pending': pending}
    return render(request,"accounts/user_page.html",context)

def account_settings(request):
    user_customer = request.user.customer
    form = CustomerForm(instance=user_customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST,request.FILES, instance = user_customer)  
        if form.is_valid():
            form.save()


    context={'form':form}
    
    return render(request,"accounts/account_settings.html",context)