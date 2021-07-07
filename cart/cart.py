import copy
from decimal import Decimal

from django.conf import settings

from products.models import Product, Frete

#from products.models import Product
from django.shortcuts import render

from .forms import CartAddProductForm

import xml.etree.ElementTree as ET
import requests
#import json



class Cart:
    def __init__(self, request):
        if request.session.get(settings.CART_SESSION_ID) is None:
            request.session[settings.CART_SESSION_ID] = {}
        if request.session.get(settings.FRETE_SESSION_ID) is None:
            request.session[settings.FRETE_SESSION_ID] = {}
        self.cart = request.session[settings.CART_SESSION_ID]
        self.frete = request.session[settings.FRETE_SESSION_ID]
        self.session = request.session
    def __iter__(self):
        cart = copy.deepcopy(self.cart)
        frete = copy.deepcopy(self.frete)

        products = Product.objects.filter(id__in=cart)
        fretes = Frete.objects.filter(id__in=frete)
        for product in products:
            cart[str(product.id)]["product"] = product           
        for frete in fretes:
            frete[str(frete.id)]["frete"] = frete 
        #item["volume"] = 0
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["quantity"] * item["price"]
            item["update_quantity_form"] = CartAddProductForm(
                initial={"quantity": item["quantity"], "override": True}
            #item["volume"] = item["quantity"]
            )
            yield item

        for viagem in frete.values():
            viagem["taxa"] = Decimal(viagem["taxa"])
            viagem["tempo"] = viagem["tempo"]
            viagem["cep"] = viagem["cep"]
            yield viagem


    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "price": str(product.price),
            }

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        self.cart[product_id]["quantity"] = min(20, self.cart[product_id]["quantity"])

        self.save()

    def remove(self, product):
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self):
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )



    def get_total_itens(self):
        return sum(item["quantity"] for item in self.cart.values()
        )

# Create your views here.
    def freteView(request):
      global first_time
      all_frete_items = Frete.objects.all()
      if (first_time):
          carro=9.50
          new_frete = Frete(cep = "28920056", tempo = "7", taxa = carro)
          new_frete.save()
          first_time = False
      return render(request, 'cart_detail.html', 
  {'all_fretes': all_frete_items})

      
    def get_preco_frete(self):
        #volume = sum(item["quantity"] for item in self.cart.values()
        url = "http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx?nCdEmpresa=08082650&sDsSenha=564321&sCepOrigem=70002900&sCepDestino=04547000&nVlPeso=1&nCdFormato=1&nVlComprimento=20&nVlAltura=30&nVlLargura=20&sCdMaoPropria=n&nVlValorDeclarado=0&sCdAvisoRecebimento=n&nCdServico=04510&nVlDiametro=0&StrRetorno=xml&nIndicaCalculo=3"
        header = { 'Accept': 'application/xml' }
        r = requests.get(url, headers=header)
        tree =  ET.ElementTree(ET.fromstring(r.content))
        root = tree.getroot()
        filtro = "*"
        i = 0
        txt = ""
        for child in root.iter(filtro):
            if(i==3):
              txt = child.text
            i+=1
        return txt




    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True



