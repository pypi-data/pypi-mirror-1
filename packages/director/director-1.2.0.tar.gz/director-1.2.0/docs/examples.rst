Examples
=========

Example 'Binary'
----------------
::

   #!/usr/bin/env python

   import exceptions
   import sys

   from director import ActionRunner
   from director.filter import ExceptionFilter
   from director.filter import Filter


   if __name__ == '__main__':
       # Create and use exception filters
       # Note you don't have to use filters. If you don't pass filter in
       # to ActionRunner.run filters won't be used.
       filter = Filter()
       filter.register_filter(ExceptionFilter(exceptions.IOError, "TEST %s"))
       filter.register_filter(ExceptionFilter(exceptions.TypeError, "NO! %s"))

       # 'actions.package' is the package that holds the allowed plugin actions
       ar = ActionRunner(sys.argv, 'actions.package')
       ar.run(filter)


Example 'Action'
----------------
::

   from director import Action
   from director.decorators import general_help


   class Bucket(Action):
       """
       Thor bucket action.
       """

       description_txt = "Managers buckets"

       @general_help("Prints all buckets.")
       def list(self):
           """
           Prints all buckets.
           """
           pass

       @general_help("Adds a new bucket",
                     {'add': 'Name of the bucket to add'})
       def add(self, name):
           """
           Adds a new bucket.
           """
           print name

       @general_help("Deletes a bucket",
                     {'name': 'Name of the bucket to delete'})
       def delete(self, name):
           """
           Deletes a bucket.
           """
           pass


Defining Help Text
------------------
As you can see above, help text defined via a decorator in the decorators module called general_help. Take a look at the decorators modules and use the decorator that makes most sense for you.

Calling Actions
---------------
The format is :command:`application action verb --option=val --anotheroption=val2`.... For example ...
::

   $ myteam roster list --filter=steve
   Steve Milner
   Steven Carzy
   Steven "BigDawg" Salezkuy
   $ myteam roster list --filter=steve --lastname=milner
   Steve Milner
   $
