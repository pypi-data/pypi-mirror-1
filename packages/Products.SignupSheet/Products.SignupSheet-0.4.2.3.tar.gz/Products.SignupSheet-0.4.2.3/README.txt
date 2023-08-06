SignupSheet
===========


SignupSheet is an add-on product that allows site managers to create custom
registration forms for events, workshops, fundraisers and other events that
require online registration.  Each SignupSheet defines the fields that are used
for each Registrant object they contain, through the ATSchemaEditorNG product.
The Registrant object is what the end user fills out and submits.  The workflow
places each submitted Registrant in a private state once it is submitted so
that  it can be reviewed and approved.  

  
The SignupSheet has these additional features:
 
- Registrant fields can be exported to CSV
  
- A waiting list and event size can be set, end users are emailed a message
  stating whether they are pending approval or on the waiting list.  
  
- The signup sheet view indicates whether the SignupSheet is 'full', 'open' or
  whether user will be put on a  waiting list. This is calculated using the
  event size and waiting list settings.
  
- End user is directed to a customizable thank you page.

  
The key motivation behind this product is to provides a way for site managers
to setup registration forms that do more than email the fields to an address.
Having the fields be configurable is essential, since many groups have specific
requirements for the data they are collecting for their events. 

    
SignupSheet is released under the GNU General Public Licence, version 2.
Please see http://gnu.org for more details.



  
Installation
------------
  
- Install in the usual way, using the QuickInstaller.  Requires
  ATSchemaEditorNG 0.5 or greater Requires TemplateFields and TALESField
    
- Tested with Plone 3.0.6 and Archetypes 1.5.6 and ATSchemaEditorNG 0.5
   
        
Acknowlegements
---------------

- This product would not be possible without the Poi and RichDocument
  products by Martin Aspeli.  They provided useful example code, specifically
  around the workflow trigger pattern.  

- In addition Upfront Contacts by Roche Compaan for the CSV export code.  

- In addition thanks to Simon Pamies for assisting me with ATSchemaEditorNG, and
  Andreas Jung for providing useful code improvements.  

- Naro for the Plone 3 compatibility work

- Andres Jung for eggifying SignupSheet
    
    
Known Issues and Potential Improvements
--------------------------------------- 
    
- Signupsheet needs more explanatory text.  Schema editor has been simplified
  but needs better explanatory text.

- It is possible to prematurely fill up registration by malicious user.


Authors
-------

Aaron VanDerlip (avanderlip AT gmail dot com) and others
