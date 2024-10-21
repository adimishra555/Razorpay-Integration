from django.shortcuts import render, redirect
from django.conf import settings
import razorpay
from .models import Payment
from django.views.decorators.csrf import csrf_exempt

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def donate(request):
    if request.method == "POST":
        name = request.POST['name']
        amount = float(request.POST['amount']) * 100  

        payment_order = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
        payment = Payment(name=name, amount=amount / 100, payment_id=payment_order['id'])
        payment.save()

        context = {
            'name': name,
            'amount': amount,
            'payment_id': payment_order['id'],
            'key_id': settings.RAZORPAY_KEY_ID,
        }
        return render(request, 'donate.html', context)

    return render(request, 'donate.html')


@csrf_exempt
def success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            payment.paid = True
            payment.save()
            return render(request, 'success.html', {'payment': payment})
        except Payment.DoesNotExist:
            # print('Payment is not completed try again!')
            return redirect('donate')
            
