import stripe

import sc
import sc.email
from sc.views import GenericView

stripe.api_key = sc.config.app['stripe_secret_key']

def donate(**kwargs):
    freq = kwargs['frequency']
    if freq == 'once':
        return donate_once(**kwargs)
    elif freq == 'monthly':
        return donate_monthly(**kwargs)
    

def donate_once(stripeToken, stripeEmail, amount, name, message, **kwargs):
    try:
        customer = stripe.Customer.create(
            card=stripeToken,
            email=stripeEmail,
            metadata={"name": name, "message": message}
        )
            
        charge = stripe.Charge.create(
            customer=customer.id,
            metadata={"name": name, "message": message},
            amount=amount,
            currency='aud',
            description='Donation'
        )
        
        details =  {'name': name,
                    'dollar_amount': kwargs['dollar_amount'],
                    'frequency': 'once',
                    'email': stripeEmail,
                    'message': message,
                    'address': kwargs['address'],
                    'free_gift': kwargs['free_gift']}
        notify(details)
        return details
    except stripe.error.CardError:
        return None

def donate_monthly(stripeToken, stripeEmail, amount, name, message, **kwargs):
    plan = get_plan(amount)
    try:
        customer = stripe.Customer.create(
            card=stripeToken,
            email=stripeEmail,
            plan=plan.id,
            metadata={"name": name, "message": message}
        )
        details =  {'name': name,
                    'dollar_amount': kwargs['dollar_amount'],
                    'frequency': 'monthly',
                    'email': stripeEmail,
                    'message': message,
                    'address': kwargs['address'],
                    'free_gift': kwargs['free_gift']}
        notify(details)
        
        return details
    except stripe.error.CardError:
        return None

def get_plan(amount):
    id = 'monthly{}'.format(amount)
    
    try:
        plan = stripe.Plan.retrieve(id)
    except stripe.error.InvalidRequestError:
        plan = stripe.Plan.create(
            amount=amount,
            interval='month',
            name='Monthly Donation to SuttaCentral',
            currency='aud',
            statement_descriptor='SuttaCentralDonation',
            id=id)
    
    return plan
            
def calc_amount(dollar_amount):
    return int(float(dollar_amount) * 100)

def notify(details):
    text = GenericView('donate/notification_email.txt', details).render()
    html = GenericView('donate/notification_email', details).render()
    to = sc.config.email['donation_manager_address']
    if details['frequency'] == 'once':
        subject = '${} Donation Received'.format(details['dollar_amount'])
    elif details['frequency'] == 'monthly':
        subject = '${} Monthly Donation Received'.format(details['dollar_amount']) 
    sc.email.send(to=to, subject=subject, text=text, html=html)
    
