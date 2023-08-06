'''
Why do we use function based model forms? Coz its easy. How? 
Let's say we need to fill our order_details in the database created by a customer, 
for which we Order Model is created in models.py with fields such as Customer, Prdocut etc.
OUR END GOAL IS TO FILL THESE FIELDS WHEN CUSTOMER CREATES AN ORDER RIGHT? 
Now, technically, we can use Class-based views(CBV) for creating forms, it is mainly used by large org
for handling views, like 
eg. 
# Function based view
def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})
# Class Based View
class BookListView(ListView):
    model = Book
    template_name = 'book_list.html'
    context_object_name = 'books'
Matter of prefrence what you use, but in forms if we use 
Function based views(FBV) we feel more control, 
which seems more understandable? 
1. class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'book_create.html'
    success_url = '/books/'
2. def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book-list')
    else:
        form = BookForm()

    return render(request, 'book_create.html', {'form': form})

Sure, 1 is shorter, but 2 shows how is the request handled, more clearly. But we can use literally anything. 

'''

'''
Now, whatever we use, CBV or FVB, creation of form is same,
, as they automatically handle fields based on the underlying model.
So, if we want the fill the order database, we need all fields of Order to be filled by the user,
so simply we map Order Model to the creaation of form, simply. No complextity of creating 
TextField, Charfield etc. again. Simply use Meta to determine which model to use, and the fields to
determine which fields need to be filled  by the user, if all then fields="__all__" , or pick the fields
you want to use , ie . fields= ['customer','product'], but rememeber Order MOdel field name and form fields
name out here should match, since they are case sensitive. 

'''




from .models import *
from django.forms import ModelForm  # import ModelForm, not forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class OrderForm(ModelForm):  # should be ModelForm inside (), not (forms.Form)
    class Meta:
        model = Order
        fields = '__all__'


class ProductCreationForm(ModelForm):
    class Meta:
        model = Products
        fields = "__all__"

class CustomUserForm(UserCreationForm):       
    class Meta:
        model = User
        fields= ['username','email','password1','password2']

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"
        exclude = ["user"]

