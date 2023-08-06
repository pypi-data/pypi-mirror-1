currency.converter Package Readme
==========================================

Overview
-----------
currency.converter package fetches currency rate data from European Central Bank for about recent 3 months. Once the data is fetched the data is conserved in ZODB in case of whatever difficulty to fetch the data again. There are currency converter page and portlet included in this package and several methods you can use for your own applications.

This package is developed for plone-3.x.

The easiest way to demonstrate this package, just describe corrency.converter to the buildout.cfg to the egg section like below.

eggs =
    currency.converter

Log in as a manager and go to the next page "your_portal/@@manage-currency".
By visiting the page, the current currency data will be fetched if possible and automatically persisted.

-----------
Features
-----------
Site manager can give two different variables in addition to currencies, days and margin.

-Days
This amout is used to caclulate average of currencies. For example, if you input 10 to this field, 10 recent days are used to calculate average currency rate. This keeps currency rate fluctuation smaller than using everyday plain rate. If nothing or 0 is input there, it doesn't calculate average, but uses current rate.

-Margin
Margin adds % of rate to the currency rate. 0 is 0 % margin where is no margin.

-------------------------
Setting Time Server
-------------------------
To fetch the currency data regularly like every day, describe to the instance section of buildout.cfg the next way.

[instance]
zope-conf-additional =
    <clock-server>
      method /your_portal/@@manage-currency
      period 86400
      user admin
      password admin_pass
      host localhost
    </clock-server>

* Change your_portal to your plone site id
* Period is seconds between eache fetch of the currency data. 86400 seconds are the 24 hour. The data is usually updated daily on week days.
* Describe admin name to admin and its password to admin_pass.
* host is host name of your server.

--------------------------------
Upgrading of reinstalling
--------------------------------
When you reinstall or upgrade to new version, the persisted data is not migrated to new environment, so please visit your_portal/@@manage-currency to get the current data or if you have set the time server, you can wait the fetch time to come.

------------------------------
Tested version of Plone
------------------------------
-3.1.4
-3.1.5.1

