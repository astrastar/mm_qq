# ================ ya =================
import datetime
import bitmex
import time
import json

ya_key = 'm97gXgKehwcEwPo7mOwhZ54l'
ya_secret = 'I3-AlTg2REQV_S-nzBPvK3UrAnKh_p2LmcwFTi2P-3ufPXRj'
client = bitmex.bitmex(test=False, api_key=ya_key, api_secret=ya_secret)


def orders(qty1, qty2, qty3, qty4, qty5, qty6, qty7, qty8):
    try:
        book = client.OrderBook.OrderBook_getL2(symbol='XBTUSD', depth=1).result()
        ask = book[0][0].get('price')
        bid = book[0][1].get('price')
        order = [{'symbol': 'XBTUSD', 'orderQty': -qty1, 'price': ask + 2},
                 {'symbol': 'XBTUSD', 'orderQty': qty1, 'price': bid - 2},
                 {'symbol': 'XBTUSD', 'orderQty': -qty2, 'price': ask + 4},
                 {'symbol': 'XBTUSD', 'orderQty': qty2, 'price': bid - 4},
                 {'symbol': 'XBTUSD', 'orderQty': -qty3, 'price': ask + 8},
                 {'symbol': 'XBTUSD', 'orderQty': qty3, 'price': bid - 8},
                 {'symbol': 'XBTUSD', 'orderQty': -qty4, 'price': ask + 16},
                 {'symbol': 'XBTUSD', 'orderQty': qty4, 'price': bid - 16},
                 {'symbol': 'XBTUSD', 'orderQty': -qty5, 'price': ask + 32},
                 {'symbol': 'XBTUSD', 'orderQty': qty5, 'price': bid - 32},
                 {'symbol': 'XBTUSD', 'orderQty': -qty6, 'price': ask + 64},
                 {'symbol': 'XBTUSD', 'orderQty': qty6, 'price': bid - 64},
                 {'symbol': 'XBTUSD', 'orderQty': -qty7, 'price': ask + 128},
                 {'symbol': 'XBTUSD', 'orderQty': qty7, 'price': bid - 128},
                 {'symbol': 'XBTUSD', 'orderQty': -qty8, 'price': ask + 192},
                 {'symbol': 'XBTUSD', 'orderQty': qty8, 'price': bid - 192}]
        client.Order.Order_newBulk(orders=json.dumps(order)).result()
        print('<ya> Orders are placed')
    except Exception as e:
        print(f'<ya> ^^^^^^^^^^^^ error ^^^^^^^^^^^^ <orders> {e} {datetime.datetime.now()}')
        orders(qty1, qty2, qty3, qty4, qty5, qty6, qty7, qty8)


def order_cancel(side):
    """
    :param side: сторона, в которую открыта основная сделка, противоположные ордера отменяются
    :return:
    """
    try:
        order_list = client.Order.Order_getOrders(symbol='XBTUSD', count=16, reverse=True).result()[0]
        short_list = []
        long_list = []
        if side == 'long':
            for order in order_list:
                if order.get('side') == 'Sell':
                    order_id = order.get('orderID')
                    short_list.append(order_id)
            client.Order.Order_cancel(orderID=json.dumps(short_list)).result()
        elif side == 'short':
            for order in order_list:
                if order.get('side') == 'Buy':
                    order_id = order.get('orderID')
                    long_list.append(order_id)
            client.Order.Order_cancel(orderID=json.dumps(long_list)).result()
    except Exception as e:
        print(f'<ya> ^^^^^^^^^^^^ error ^^^^^^^^^^^^ <order_cancel> {e} {datetime.datetime.now()}')
        order_cancel(side)


def pos_check():
    while True:
        try:
            pos = client.Position.Position_get().result()
            op_cl = pos[0][0].get('isOpen')
            price = pos[0][0].get('avgEntryPrice')
            round_price = round(price, 0)
            qty = pos[0][0].get('currentQty')
            if op_cl:
                if qty > 0:
                    order_cancel('long')
                    client.Order.Order_new(symbol='XBTUSD', orderQty=-qty, price=round_price + 1.5).result()
                    print(f'<ya> Long position is open at {datetime.datetime.now()}')
                    break
                elif qty < 0:
                    order_cancel('short')
                    client.Order.Order_new(symbol='XBTUSD', orderQty=-qty, price=round_price - 1.5).result()
                    print(f'<ya> Short position is open at {datetime.datetime.now()}')
                    break
            elif op_cl is False:
                pass
            time.sleep(2)
        except Exception as e:
            print(f'<ya> ^^^^^^^^^^^^ error ^^^^^^^^^^^^ <pos_check> {e} {datetime.datetime.now()}')
            pass


def main_loop():
    while True:
        try:
            pos = client.Position.Position_get().result()
            op_cl = pos[0][0].get('isOpen')
            price = pos[0][0].get('avgEntryPrice')
            round_price = round(price, 0)
            qty = pos[0][0].get('currentQty')
            if op_cl:
                open_order = client.Order.Order_getOrders(symbol='XBTUSD', count=16, reverse=True,
                                                          filter=json.dumps({'ordStatus': 'New'})).result()[0][0]
                close_qty = open_order.get('orderQty')
                order_id = open_order.get('orderID')
                if close_qty == qty:
                    pass
                elif close_qty < abs(qty):
                    if qty > 0:
                        client.Order.Order_amend(orderID=order_id, orderQty=-qty, price=round_price + 1.5).result()
                    elif qty < 0:
                        client.Order.Order_amend(orderID=order_id, orderQty=-qty, price=round_price - 1.5).result()
            elif op_cl is False:
                client.Order.Order_cancelAll().result()
                print(f'<iai> Position close at {datetime.datetime.now()}\n**********')
                break
            time.sleep(2)
        except Exception as e:
            print(f'<ya> ^^^^^^^^^^^^ error ^^^^^^^^^^^^ <main_loop> {e} {datetime.datetime.now()}')
            time.sleep(2)
            main_loop()

while True:
    orders(40, 80, 120, 160, 400, 800, 1600, 3200)
    pos_check()
    main_loop()

    # while True:
    #     try:
    #         pos = client.Position.Position_get().result()
    #         op_cl = pos[0][0].get('isOpen')
    #         price = pos[0][0].get('avgEntryPrice')
    #         round_price = round(price, 0)
    #         qty = pos[0][0].get('currentQty')
    #         if op_cl:
    #             open_order = client.Order.Order_getOrders(symbol='XBTUSD', count=16, reverse=True,
    #                                                       filter=json.dumps({'ordStatus': 'New'})).result()[0][0]
    #             close_qty = open_order.get('orderQty')
    #             order_id = open_order.get('orderID')
    #             if close_qty == qty:
    #                 pass
    #             elif close_qty < abs(qty):
    #                 if qty > 0:
    #                     try:
    #                         client.Order.Order_amend(orderID=order_id, orderQty=-qty, price=round_price + 1.5).result()
    #                     except Exception:
    #                         pass
    #                 elif qty < 0:
    #                     try:
    #                         client.Order.Order_amend(orderID=order_id, orderQty=-qty, price=round_price - 1.5).result()
    #                     except Exception:
    #                         pass
    #         elif op_cl is False:
    #             client.Order.Order_cancelAll().result()
    #             print(f'<ya> Position is close at {datetime.datetime.now()}\n=================')
    #             time.sleep(2)
    #             break
    #         time.sleep(2)
    #     except Exception:
    #         print('<ya> Request not accepted <main loop>')

# <ya> error <main_loop> 429 Too Many Requests: Response specification matching http status_code 429 not found for operation Operation(Position_get). Either add a response specification for the status_code or use a `default` response. 2018-08-22 09:41:09.739452
# <iai> Position close at 2018-08-22 09:41:12.085392
# **********
# <ya> error <main_loop> 403 Forbidden: Response specification matching http status_code 403 not found for operation Operation(Position_get). Either add a response specification for the status_code or use a `default` response. 2018-08-22 09:41:12.239406