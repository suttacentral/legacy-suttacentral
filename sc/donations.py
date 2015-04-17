import stripe
import sc


stripe.api_key = sc.config.app['stripe_secret_key']

def process_payment(**kwargs):
    try:
        customer = stripe.Customer.create(
            email=kwargs['token-email'],
            card=kwargs['token-id']
        )
        charge = stripe.Charge.create(
            customer = customer.id,
            amount=kwargs['amount'],
            currency='aud',
            #source=kwargs['token-id'],
            description='Donation'
        )
        
        return charge
    except stripe.error.CardError:
        return None
    
