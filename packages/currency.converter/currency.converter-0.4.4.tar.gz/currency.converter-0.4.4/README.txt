Introduction
============
Overview
-----------
currency.converter package fetches currency rate data from European Central Bank for about recent 3 months. Once the data is fetched, the data is persisted in ZODB in case of whatever difficulty to fetch the data again. There are currency converter page and portlet included in this package and several methods you can use for your own applications.

Log in as a manager and go to the page, "your_portal/@@manage-currency".
By visiting the page, the current currency data will be fetched if possible and automatically persisted.

Features
-----------
Site manager can give two different variables in addition to currencies, days and margin.

Days
    This amout is used to caclulate average of currencies. For example, if you input 10 to this field, 10 recent days are used to calculate average currency rate. This keeps currency rate fluctuation smaller than using everyday plain rate. If nothing or 0 is input there, it doesn't calculate average, but uses current rate.

Margin
    Margin adds % of rate to the currency rate. 0 is 0 % margin where is no margin.

