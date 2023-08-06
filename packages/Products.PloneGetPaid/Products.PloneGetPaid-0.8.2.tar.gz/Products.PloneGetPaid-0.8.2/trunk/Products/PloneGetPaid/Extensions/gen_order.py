
import random, string
from getpaid.core import cart, order, interfaces, item
from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
from zope import component

def createOrders( self ):

    manager = component.getUtility( interfaces.IOrderManager )

    # make sure we don't accidentally create notifications for sample orders

    settings = IGetPaidManagementOptions( self )
    m_value = settings.merchant_email_notification
    c_value = settings.customer_email_notification

    settings.merchant_email_notification = u'no_notification'
    settings.customer_email_notification = u'no_notification'

    for i in range(40, 60):
        o = order.Order()
        o.order_id = str(i)

        o.shopping_cart = sc = cart.ShoppingCart()

        for i in range(0, 10):
            myItem = item.LineItem()
            myItem.name = "p%s"%random.choice( string.letters )
            myItem.quantity = random.randint(1,25)
            myItem.cost = random.randint(30, 100)
            myItem.item_id = "i%s"%random.choice( string.letters )
            if myItem.item_id in sc:
                continue
            sc[myItem.item_id] = myItem

        o.user_id = "u%s"%random.choice( string.letters )
        o.finance_workflow.fireTransition('create')
        o.fulfillment_workflow.fireTransition('create')

        manager.store( o )

    settings.merchant_email_notification = m_value
    settings.customer_email_notification = c_value

    return "Created 20 Orders"

