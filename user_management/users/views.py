from django.shortcuts import render,redirect,get_object_or_404
from users.forms import SignUpForm
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from users.models import CustomerProfile,Product,Cartitem,AccountType
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from users.models import Catergory

# Create your views here.
@login_required
def user_profile(request):
    user = request.user   
    return render(request,"user_profile.html",{"user":user})
def home(request):
    products = Product.objects.all()
    return render(request,"guest2.html",{"products":products})
# handles login
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            messages.error(request, "Invalid credentials")
            return redirect('login')
        else:
            login(request, user)

            try:
                # Assuming AccountType has a OneToOneField to User
                account_type = AccountType.objects.get(user=user)
                if account_type.user_type == 'buyer':
                    return redirect('buyer_dashboard')
                elif account_type.user_type == 'farmer':
                    return redirect('farmer_dashboard')
                elif account_type.user_type == 'driver':
                    return redirect('driver_dashboard')
                else:
                    messages.error(request, "Account type not recognized")
                    return redirect('login')
            except AccountType.DoesNotExist:
                messages.error(request, "Account type does not exist")
                return redirect('login')    
    return render(request, 'login.html')
def buyer_dashboard(request):
    products = Product.objects.all()
    return render(request, 'buyer_dashboard.html',{"products":products})

def farmer_dashboard(request):
    user = request.user
    return render(request, 'farmer_dashboard.html',{"user":user})

def driver_dashboard(request):
    return render(request, 'driver_dashboard.html')
def logout_user(request):
    logout(request)
    messages.success(request,("you have been logged out !!!!!!!"))
    return redirect('start')    

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user instance
            # Save the account type
            account_type = form.cleaned_data['account_type']
            AccountType.objects.create(user=user, user_type=account_type)

            # Authenticate the user after registration
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # Log the user in
            login(request, user)

            # Redirect based on account type
            if account_type == 'buyer':
                return redirect('buyer_dashboard')
            elif account_type == 'farmer':
                return redirect('farmer_dashboard')
            elif account_type == 'driver':
                return redirect('driver_dashboard')

    else:
        form = SignUpForm()  # Create an empty form for GET request

    return render(request, 'signup.html', {'form': form})

#to show list of users
def users_list(request):
    profiles = request.user #gets users
    if profiles.is_authenticated:
        user = CustomerProfile.objects.all()
    return render(request,"users_list.html",{"profiles":profiles,"user":user})
#for homepage
def list_products(request):
    products = Product.objects.all()
    return render(request,"product_listing.html",{"products":products}) 
#register products
@login_required
def register_product(request):
    if request.method == 'POST':
        # Get form data
        catergory_name = request.POST['catergory']
        name = request.POST['name']
        description = request.POST.get('description', '')
        price = request.POST['price']
        stock = request.POST['stock']

        # Handle the checkbox value
        available = True if request.POST.get('available') == 'on' else False

        image = request.FILES.get('image', None)

        # Check if the category already exists
        catergory, created = Catergory.objects.get_or_create(name=catergory_name)

        # Create the product, setting the user as the authenticated user
        product = Product.objects.create(
            catergory=catergory,
            user=request.user,  # Automatically set the current user
            name=name,
            description=description,
            price=price,
            stock=stock,
            available=available,
            image=image,
        )
        return redirect('homepage')  # Redirect to a success page

    # GET request: render the empty form
    return render(request, 'register_product.html')
#handle items in cart
@login_required
def add_to_cart(request,product_id):
    product = get_object_or_404(Product,id = product_id)
    cart_item,created = Cartitem.objects.get_or_create(user = request.user,product=product)
    if not created:
        cart_item.quantity +=1 
        cart_item.save()
    else:
        cart_item.quantity = 1
        cart_item.save()
    return redirect('view_cart')
@login_required
def view_cart(request):
    if request.user.is_authenticated:
        cart_items = Cartitem.objects.filter(user=request.user)
         # Calculate the total price of the items in the cart
        total_price = sum(item.product.price * item.quantity for item in cart_items)                
        total_items = sum(item.quantity for item in cart_items)
    else:
        cart_items = []
        total_price = 0
        total_items = 0
    return render(request,"view_cart.html",{"cart_items":cart_items,"total_price":total_price,"total_items":total_items})



    
        