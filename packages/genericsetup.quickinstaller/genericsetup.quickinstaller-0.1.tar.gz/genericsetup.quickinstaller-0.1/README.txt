Overview
--------

Generic setup import step that installs products in `portal_quickinstaller`.
This is useful if you depend on a product that does not have a generic setup 
profile.

In that case, you can create a file `products.xml` ::

    <?xml version="1.0"?>
    <products>
      <installs>
        <product name="FCKeditor" />
      </installs>
    </products>

This will install `FCKeditor` product.
