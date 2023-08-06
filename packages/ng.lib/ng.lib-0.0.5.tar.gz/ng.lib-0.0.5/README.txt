Short module description
=========================

Module pd.lib content some simple modules
and fucntions for use in Zope.

Description of modules
----------------------

ng.lib.interface
................

The module to provide different small tools to deal with interfaces in Zope.

Function provided by module followed:

    implements
        Function implements must be issued with interfaces as arguments.
        As original zope.interface.implements, our function make context
        class provided  this interfaces. In difference from original function,
        our implementation added for each field of each interface name attribute
        of FieldProperty type.

ng.lib.editannotationnotify
...........................

The module provided mix-in for use in editform directive. Mix-in send
object-modifyed notify despite using adapter to edit content. Some sample
followed::

   <editform 
      schema="..interfaces.IDictAnnotation"
      for="..interfaces.IDictAnnotationAble" 
      label="Dictionary"
      class="ng.lib.editannotationnotify.EditAnnotationNotify"
      name="dictannotation.html" permission="zope.ManageContent"
      menu="zmi_views" title="Dictionary"
      />

In this case editform sent object-moodifyed notify on context when
annotation modufied thro adapter.

ng.lib.dynamicdefault
.....................

The module provide fields factory DynamicDefault. Thr factory allow use run-time computed default value 
for fields, inherited from Field. Sample followed:

    from zope.interface import Interface
    from zope.schema import Datetime
    from ng.lib.dynamicdefault.DynamicDefault

    class IA(Interface) :
        """ Stupid Interface """

        created = DynamicDefault(DateTime,title = u'Date/Time',
            description = u'Date/Time',
            default = datetime.datetime.today,
            required = True)

[name:недоделано]