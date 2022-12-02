from vendor.models import Vendor
from accounts.models import userProfile
from MyRestaurant_main.settings import PAYPAL_CLIENT_ID


def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None
    return dict(vendor=vendor)

def get_user_profile(request):
    try:
        user_profile = userProfile.objects.get(user=request.user)
    except:
        user_profile = None
    return dict(user_profile=user_profile)

def get_paypal_client_id(request):
    return {'PAYPAL_CLIENT_ID': PAYPAL_CLIENT_ID}