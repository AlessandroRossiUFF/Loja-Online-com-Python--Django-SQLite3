  
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView

from cart.cart import Cart

from .forms import OrderCreateForm
from .models import Item, Order


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderCreateForm

    def form_valid(self, form): 
        cart = Cart(self.request)
        if cart: # Se o carrinho não estiver vázio
            order = form.save() #Insere os dado do formulário
            for item in cart: # Para cada item do carinho
            #cada item é associado ao pedido referente
                Item.objects.create( 
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            cart.clear() #Limpa o carrinho
            return render(self.request, "orders/order_created.html", {"order": order})
        # Envia para uma página de sucesso
        return HttpResponseRedirect(reverse("pages:home"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request)
        return context #Exibe um resumo do pedido