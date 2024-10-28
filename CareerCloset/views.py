﻿from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from access import models
from access.models import Cart, CartItem, ClothingItem, Transaction, Customer

@login_required
def index(request):
    return render(request, 'home.html')


def login(request, *args, **kwargs):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect(reverse('/admin'))
        else:
            messages.error(request,'username or password not correct')
            return redirect(reverse('/error'))
    else:
        form = AuthenticationForm()
    return render(request,'registration/login.html',{'form':form})


def women(request):
    women_gender = models.Gender.objects.get(gender_name="Female")
    
    women_clothing_items = models.ClothingItem.objects.filter(gender=women_gender)

    context = {
        'context': women_clothing_items,
    }
    return render(request, 'women.html', context)

def men(request):
    men_gender = models.Gender.objects.get(gender_name='Men')
    
    men_clothing_items = models.ClothingItem.objects.filter(gender=men_gender)

    context = {
        'context': men_clothing_items,
    }
    return render(request, 'men.html', context)

@login_required
def add_to_cart(request, clothing_id):
    # Get the Customer profile associated with the current user
    customer = get_object_or_404(Customer, user=request.user)
    cart, created = Cart.objects.get_or_create(user=customer)
    clothing_item = get_object_or_404(ClothingItem, pk=clothing_id)

    # Check if the item is already in the cart
    if CartItem.objects.filter(cart=cart, clothing_item=clothing_item).exists():
        messages.info(request, "This item is already in your cart.")
    else:
        # Add item to cart if not already present
        CartItem.objects.create(cart=cart, clothing_item=clothing_item)
        messages.success(request, "Item added to cart.")

    return redirect("view_cart")

@login_required
def view_cart(request):
    customer = get_object_or_404(Customer, user=request.user)  # Get Customer associated with User
    cart, created = Cart.objects.get_or_create(user=customer)  # Use Customer instance for Cart
    return render(request, 'cart/view_cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, cart_item_id):
    cart = get_object_or_404(Customer, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect("view_cart")

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    for item in cart.items.all():
        Transaction.objects.create(user=request.user, clothing_item=item.clothing_item)
    cart.items.all().delete()
    return render(request, 'cart/checkout.html')