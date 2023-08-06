Introduction
============


*Version 0.91 Fix 
The 0.81 product was showing up twice and causing problems.  

The fix is to take the old version out of your buildout. 

Then rerun buildout. 

Next go into your ZMI and go to the control panel. Make sure anything that says EasyAsPiIE is deleted. Restart zope and recheck.

Now get the upgrade in your buildout. 

You should be set.

The reason this broke is that this is a problem with paster. Anything with "Products.**" can't have the one line of code in the config.py starting with <registers.***

https://weblion.psu.edu/trac/weblion/wiki/PloneTroubleshooting