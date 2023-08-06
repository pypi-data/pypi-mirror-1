prdg.ploneio
============

.. contents::

Overview
--------

Provide a set of views allowing to import and export content into and from
a Plone Site.

The export views are named in the pattern @@${format}-to-${output}, where:

- ${format} can be one of:
    - ``dicts``: A pickle file containing a sequence of dicts.
    - ``html``: HTML files in a directory structure ressambling the folder
      structure of the site.    
    
- ${output} can be one of:
    - ``archive``: A downloadable ``.tar.gz`` file.
    - ``directory``: A directory in the server. In this case the ``directory``
      parameter must be passed in the request, containg the path to the
      directory.

The export views are context-sensitive, i.e, content in the context and
subfolders is exported.

One import view is provided: ``@@dicts-from-directory``. The ``directory``
parameter must be passed in the request, containg a path to a directory
containing a file named ``dicts.pickle``.

The format of the returned dicts for importing and exporting is specified in 
``prdg.plone.util.structure.create_dict_from_obj``.

The import view always import to the root of the portal, using the ``_path``
key of the dicts to determine where to put each object. This key must contain
a tuple representing the path of the object, relative to the portal root.
The dicts exported by this package always will contain this key.

Examples
--------

Some setup code for the examples::

    >>> import pickle, os
    >>> from os.path import join
    >>> portal = self.portal
    >>> browser = self.browser
    >>> folder = self.folder    
    >>> catalog = self.catalog
    >>> tmpdir = self.tmpdir
    
We have an empty folder, let's add some objects::
    
    >>> len(folder.objectIds())
    0
    >>> id = folder.invokeFactory(
    ...     id='obj1', type_name='Document', title='Doc 1', text='blah'
    ... )
    >>> id = folder.invokeFactory(
    ...     id='folder2', type_name='Folder', title='Folder 2'
    ... )
    >>> folder2 = folder[id]
    >>> id = folder2.invokeFactory(
    ...     id='obj2', type_name='Document', title='Doc 2', text='blah 2'
    ... )
    
Exporting to a pickle file containg dicts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    
Let's export the folder to a pickle file containing dicts. We do it
by accessing a view::
    
    >>> view = folder.unrestrictedTraverse('@@dicts-to-archive')
    >>> view.context
    <ATFolder at ...  
    >>> tar_gz_str = view()
    >>> pickle_str = self.extract_to_str(tar_gz_str, 'dicts.pickle')
    >>> dicts = pickle.loads(pickle_str)
    >>> dicts
    [{...}, ...]

Let's check if the all objects in ``folder`` were exported:: 

    >>> brains = catalog(path='/'.join(folder.getPhysicalPath()))
    >>> len(dicts) == len(brains)
    True

Let's check if the returned dicts match the objects in ``folder``::
        
    >>> objs = [b.getObject() for b in brains]    
    >>> set(d['id'] for d in dicts) == set(o.getId() for o in objs)
    True
    >>> set(d['title'] for d in dicts) == set(o.Title() for o in objs)    
    True
    >>> set(d.get('text') for d in dicts if d.has_key('text')) \
    ...     == set(o.getText() for o in objs if hasattr(o, 'getText'))
    True     
    
Instead of downloading a .tar.gz file we could export to a directory in the
server::

    >>> view = folder.unrestrictedTraverse('@@dicts-to-directory')
    >>> view.context
    <ATFolder at ...  
    >>> view.request['directory'] = tmpdir
    >>> view()
    'Success.'
    >>> pickle_path = join(tmpdir, 'dicts.pickle')
    >>> pickle_file = open(pickle_path)
    >>> dicts = pickle.load(pickle_file)
    >>> dicts
    [{...}, ...]
    
Exporting to other formats
^^^^^^^^^^^^^^^^^^^^^^^^^^

HTML to archive::

    >>> view = folder.unrestrictedTraverse('@@html-to-archive')
    >>> tar_gz_str = view()
    >>> len(tar_gz_str) > 0
    True
    
HTML to directory::
    
    >>> old_tmpdir_len = len(os.listdir(tmpdir))
    >>> view = folder.unrestrictedTraverse('@@html-to-directory')
    >>> view.request['directory'] = tmpdir
    >>> view()
    'Success.'
    >>> len(os.listdir(tmpdir)) > old_tmpdir_len
    True
     
Importing
^^^^^^^^^

Remember we have a pickle file created in the previous example::
    
    >>> import_dir = tmpdir
    >>> 'dicts.pickle' in os.listdir(import_dir)
    True

Let's empty our ``folder``. Later we'll use the import view to re-create the 
objects::
    
    >>> old_folder_len = len(catalog(path='/'.join(folder.getPhysicalPath())))
    >>> old_folder_len > 0
    True
    >>> folder.manage_delObjects(ids=folder.objectIds())
    >>> len(folder.objectIds())
    0

Now we'll import the pickle file::

    >>> view = portal.unrestrictedTraverse('@@dicts-from-directory')
    >>> view.request['directory'] = import_dir
    >>> view()
    'Success.'
    
Let's verify::

    >>> brains = catalog(path='/'.join(folder.getPhysicalPath()))
    >>> len(brains) == len(dicts) 
    True
    >>> len(brains) == old_folder_len
    True
    >>> objs = [b.getObject() for b in brains]    
    >>> set(d['id'] for d in dicts) == set(o.getId() for o in objs)
    True
    >>> set(d['title'] for d in dicts) == set(o.Title() for o in objs)    
    True


Credits
-------

Developed at `Paradigma Internet` (http://www.paradigma.com.br).       
    
    
    
    