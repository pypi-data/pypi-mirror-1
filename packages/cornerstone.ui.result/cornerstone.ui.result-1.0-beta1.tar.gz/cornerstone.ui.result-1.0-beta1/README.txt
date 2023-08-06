=====================
cornerstone.ui.result
=====================

Overview
========

This module provides rendering results. The intention was to not write
stupid view logic again and again.
  
The structure of the results is defined via ZCML. To finally make the framework
render the result you have to subclass some baseimplementations of the
framework providing rendering informations such like batch vocabs,
result slices, etc.
  
At the moment the the framework provides batching and slices, in future it will
be extended with features for defining result sorting mechanisms,
nested batches, and more detailed slice definitions.
  
You can find a first example on how to implement results at:
https://svn.plone.org/svn/collective/Directory
  
Each defined result is internal registered as ViewletManager, and will be
rendered by calling a contentprovider out of a page template f.e.::
  
 <tal:block tal:replace="structure provider:directory.directorylisting" />


The result definition in zcml looks like this::

 <configure xmlns="http://namespaces.zope.org/cornerstone">

   <result for="Products.Directory.content.interfaces.IDirectory"
           class=".browser.directory.DirectoryListingResult"
           permission="zope.Public"
           name="directory.directorylisting"
           threshold="0">
   
     <batch domain="directorybatch"
            vocab=".browser.directory.DirectoryBatchVocab" />
          
     <slice class=".browser.directory.DirectoryListingSlice"
            name="directoryslice"
            template="templates/directory_listing.pt"
            allowed_interface="Products.Directory.browser.interfaces.IDirectoryListing" />
   
     <batch domain="directorybatch" />

   </result>

 </configure>

Consider that if you want to render the same batch twice, f.e. above and below
the slice, you only have to define the batch definitions once and can add it
a second time simply by defining the batch domain.


A result can have the following attributes:
-------------------------------------------

- for="*" (the interface the result is bound to)
 
- class=".env.TestResult" (the class providing the results itself)
 
- permission="zope.Public" (the permission to view the result)
 
- name='testresult' (the name under which the result can be called as
  contentprovider)
  
- slicesize="20" (the size of the result slice, optional)
 
- threshold="20" (the threshold how many results are required to display
  batches, optional)


A Batch can have the following attributes:
------------------------------------------

- domain="testbatch" (the domain of this batch. this is used to differ the
  batch from perhaps other rendered batches on the same page)
  
- vocab=".env.TestBatchVocab" (the class providing the batch vocab)
  
- template="templates/batch.pt" (the template used to render the batch,
  optional)
  
- firstpagelink="True" (flag wether to display the firstpagelink or not,
  optional)
  
- lastpagelink="True" (flag wether to display the lastpagelink or not,
  optional)
  
- prevpagelink="True" (flag wether to display the prevpagelink or not,
  optional)
  
- nextpagelink="True" (flag wether to display the nextpagelink or not,
  optional)
  
- batchrange="30" (the batchrange. defines how many pages are displayed,
  f.e. "<< < ... 5 6 7 8 ... > >>", optional)
  
- masters="anotherbatchdomain" (Batch(es) the defined batch depends on, the
  value must be the domain of the batch(es) you want to consider)
  
- title="The Title" (An optional title to label the batch)
  
- forcedisplay="True" (An optional flag wether to force batch displaying
  or not)
  
- querywhitelist="sort" (Query Params to be considered when generating
  urls. This is needed if you have to use some additional params in the
  slice)


The slice definitions are treated as viewlet definitions and therefor follow
----------------------------------------------------------------------------
the viewlet definition rules:
-----------------------------

- class=".browser.directory.DirectoryListingSlice"
  
- name="directoryslice"
  
- template="templates/directory_listing.pt"
  
- allowed_interface="Products.Directory.browser.interfaces.IDirectoryListing"

 
The example pointed above implements an alphabatched directory listing and
--------------------------------------------------------------------------
subclasses therfor this objects:
--------------------------------

- cornerstone.ui.result.result.ResultBase

- cornerstone.ui.result.batch.AlphaBatchVocabBase

- cornerstone.ui.result.slice.AlphaBatchedSliceBase


The result class::

 class DirectoryListingResult(ResultBase):
 
     name = 'directory.directorylisting'
 
     @property
     def results(self):
         return self._getEntries({
             'meta_type': 'DirectoryEntry',
             'path': '/'.join(self.context.getPhysicalPath()),
         })
 
     def _getEntries(self, query):
         catalog = getToolByName(self.context, 'membrane_tool')
         brains = catalog(**query)
         entries = []
         for brain in brains:
             entry = dict()
             entry['name'] = brain.Title
             entry['email'] = brain.getEmail
             entry['url'] = brain.getURL()
             entry['review_state'] = brain.review_state
             entries.append(entry)
         return entries


Consider:


- since there is no senceful way to determine the name under which a
  specific ViewletManager is registered out of itself you must provide
  the name attribute.
  
- further you have to provide the results. in the example above it is a
  list of dictionaries. of course this is the format (list of dicts) the
  framework can handle well at the moment. in future there will be also
  base implementations be able to handle catalog brains.
  
- the result implementing class is used by the other needed classes to
  extract the batch informations and the slice informations


The batch vocab class::

 # pages definitions will be looked up by an adapter in future
 pages = [
     'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
     'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
 ]

 class DirectoryBatchVocab(AlphaBatchVocabBase):
    
     @property
     def vocab(self):
         visibles = self.getVisiblesFromDictList('name')
         return self.generateVocab(visibles, pages)


Consider:


- The base class AlphaBatchVocabBase can handle results which are a list
  of dicts and does most of the work for you. As written earlier there
  should be also a base implementation for handling brain based result
  lists.
  
- the page list is needed to calculate an alphabatch
  (it is not necessary for numeric batches) and must be available in the
  class defining the batch vocab and the result slice itself, see below.
  This should be looked up by an interface in future


The slice class::

 class DirectoryListingSlice(AlphaBatchedSliceBase):
 
     @property
     def entries(self):
         key = 'name'
         batchname = 'directorybatch'
         self.pages = pages
         self.sortResults(key)
         current = self.determineCurrentPage(batchname, key)
         return self.generateCurrentSlice(current, key)


Enable KSS:
-----------

KSS is enabled by defult when applying the extension profile. 
  
To enable kss for anonymous users too, you have to change the condition of
``kukit.js`` in the portal_javascripts resource registry.


Consider:


- In this subclass the same rules for results applies as for the batch
  vocab base class.
  
- you have to provide the batchname this slice is used for
  
- the pages global is here used too. see statement why framework is alpha
  state.


Credits:
========

- This library is an outcome of the UN ILO Better Work project.
    
- Written by Robert Niederreiter <rnix@squarewave.at>,
      Squarewave Computing, Austia - Blue Dynamics Alliance
      
- Thaks to Jens Klein <jens@bluedynamics.com> for help at research and
      design ideas
      
- Thanks to Radim Novotny <novotny.radim@gmail.com> for bugfixes and testing
      
- Thanks to Lukas Zdych <lukas.zdych@corenet.cz> for the batchrange
      implementation and testing