def parse_alert(alert: str):
    user_inputs_array = alert.split()
    print(user_inputs_array)
    security = ''
    expiration_month = ''
    expiration_day = ''
    strike_price = ''
    option = ''
    entry_point = ''
    stop_loss = ''

    for user_input in map(lambda string: string.upper(), user_inputs_array):
        if '$' in user_input:
            security = user_input.partition('$')[2]
        elif 'EX' in user_input:
            month_day = user_input.partition('EXP')[2]
            expiration_month = month_day.partition('/')[0]
            expiration_day = month_day.partition('/')[2]
        elif 'SP' in user_input:
            strike_price = user_input.partition('SP')[2]
        elif 'CALL' == user_input or 'C' == user_input:
            option = 'CALL'
        elif 'PUT' == user_input or 'P' == user_input:
            option = 'PUT'
        elif user_input.find('EP') != -1:
            entry_point = user_input.partition('EP')[2]
        elif user_input.find('@') != -1:
            entry_point = user_input.partition('@')[2]
        elif user_input.find('SL') != -1:
            stop_loss = user_input.partition('SL')[2]

    print(security)
    print(expiration_month)
    print(expiration_day)
    print(strike_price)
    print(option)
    print(entry_point)
    print(stop_loss)


parse_alert('$Xle exp07/15 sp68 P @.84')



