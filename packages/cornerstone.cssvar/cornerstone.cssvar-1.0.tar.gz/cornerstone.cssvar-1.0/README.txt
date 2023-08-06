This is an implementation of a ``CSS Variables`` extension for Zope Browser 
Resources.

Cascading Stylesheets don't have any built in method to define variables and use
them within the stylesheet. This feature was discussed at some CSS related
blogs already and resulted in a `non-official draft specification`_.

.. _`non-official draft specification`: http://disruptive-innovations.com/zoo/cssvariables/

In former Zope versions DTML templating language was used to define variables in 
CSS. This breaks CSS syntax, looks crappy and produces error messages in 
CSS-enabled editors even if the browser gets the correct values.

cornerstone.cssvar uses an almost CSS syntax compatible variant to apply 
variables::

    div.foo {
        color: var(myColor);
    }

If we declare such a css resource using zcml it looks this way::

    \<browser:cssvarResource
      name="foo"
      file="foo.css"
    /> 

If we use the common mechanism to declare variables using css like syntax we
must do this in a separate file, this looks like::

    @variables {
        myColor: #123456;
    }
  
The variable itself need to be defined by a named ``ICSSVariables`` adapter on 
request. We can register it by an own zcml directive:: 

  <browser:cssvarDefinition
    name="foodef"
    file="foodef.css"
  /> 

Now we just need to tell our first css file which definition to use. Here 
theres no common syntax, so we put it in an comment::   

    /# vardef(foodef) /#
    div.foo {
        color: var(myColor);
    }
  
If we now in browser look at ``http://mydomain.tld/++resource++foo`` it results
in::

    /# vardef(foodef) /#
    div.foo {
        color: #123456;
    }
     
For resource directories as defined by ``zope.app.publisher`` the special CSS 
handling is registered for every CSS file if this module is imported.

This package is tested with Zope 3.5dev KGS (Python 2.6 )and in Zope 2.10.7 
(with Plone 3.3 and Python 2.4).

=====
TODO:
=====

* Write tests!
* Make resourceDirectory work in Plone.
* Profiling and performance testing.  

=========
Copyright
=========

written by Jens W. Klein - `BlueDynamics Alliance`_ - Klein & Partner KEG, Austria

.. _`BlueDynamics Alliance`: http://bluedynamics.com 
