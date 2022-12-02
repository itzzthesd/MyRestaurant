from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from vendor.models import Vendor, OpeningHour
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from marketplace.models import Cart
from marketplace.context_processors import get_cart_counter, get_cart_amount
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from orders.forms import OrderForm
from accounts.models import userProfile

# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved = True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors' : vendors,
        'vendor_count' : vendor_count,
    }
    return render(request,'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug = vendor_slug)
    fooditem = FoodItem.objects.filter(vendor=vendor)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available = True )
        )
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day','-from_hour')
    # check current days opening hours
    today_date = date.today()
    today = today_date.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    #print(current_opening_hours[0])
    is_open = None
    for i in current_opening_hours:
        print(i.from_hour)
        print(current_time)
        # if not i.is_closed
        # start = str(datetime.strptime(i.from_hour,"%I:%M:%P").time())
        # end = str(datetime.strptime(i.to_hour,"%I:%M:%P").time())
        
        # if current_time > start and current_time < end:
        #     is_open = True
        # else:
        #     is_open = False

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
 
    else:
        cart_items = None
    context = {
        'vendor':vendor,
        'categories': categories,
        'cart_items':cart_items,
        'opening_hours':opening_hours,
        'current_opening_hours':current_opening_hours,
        
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, food_id):

    if request.user.is_authenticated:
        if is_ajax(request=request):
            # check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)

                # check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    #increase the cart quantiy
                    print('hit the cart increament section ', chkCart)

                    chkCart.quantity +=1
                    chkCart.save()
                    return JsonResponse({'status':'Sucess', 'message':'cart increased.','cart_counter':get_cart_counter(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amount(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status':'Success', 'message':'added the food to the cart','cart_counter':get_cart_counter(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amount(request)})


            except:
                return JsonResponse({'status':'Failed', 'message':'This food does not exist.'})

        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request'})
    else:
        return JsonResponse({'status':'login_required', 'message':'Please log in to continue'})
    #return HttpResponse('TEsting')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if is_ajax(request=request):
            # check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)

                # check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    #increase the cart quantiy
                    print('hit the cart increament section ', chkCart)
                    if chkCart.quantity >1:
                        chkCart.quantity -=1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity =0 
                    return JsonResponse({'status':'Sucess', 'message':'Cart count decreased', 'cart_counter':get_cart_counter(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amount(request)})
                except:
                    return JsonResponse({'status':'Failed', 'message':'Do not have this item to cart'})


            except:
                return JsonResponse({'status':'Failed', 'message':'This food does not exist.'})

        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request'})
    else:
        return JsonResponse({'status':'login_required', 'message':'Please log in to continue'})
    #return HttpResponse('TEsting')

@login_required(login_url = 'login')
def cart(request):
    cart_items = Cart.objects.filter(user= request.user).order_by('created_at')
    context = {
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/cart.html', context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if is_ajax(request=request):
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success', 'message':'Cart item is deleted', 'cart_counter':get_cart_counter(request), 'cart_amount':get_cart_amount(request)})

            except:
                return JsonResponse({'status':'Failed', 'message':'Cart item does not exist'})

            
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request'})

def search(request):
    return HttpResponse('search page')


@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
        
    user_profile = userProfile.objects.get(user=request.user)
    default_values = {
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'phone':request.user.phone_number,
        'email':request.user.email,
        'address':user_profile.address_line_1,
        'country':user_profile.country,
        'state':user_profile.state,
        'city':user_profile.city,
        'pin_code':user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    
    context = {
        'form':form,
        'cart_items':cart_items,
        'cart_count':cart_count,

    }
    return render(request, 'marketplace/checkout.html', context)

