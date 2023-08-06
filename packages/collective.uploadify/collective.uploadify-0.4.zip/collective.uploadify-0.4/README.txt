Introduction
============

**Makes Plone File Uploads easy**

Multifileupload for Plone using uploadify_

.. _uploadify: http://www.uploadify.com

Usage
*****

After insall, go to http://your-plone-site/@@upload

Configuration
*************

The following settings can be done in the site_properties:

  - ul_auto_upload -- true/false (default: false)

    *Set to true if you would like the files to be uploaded when they are
    selected.*

  - ul_allow_multi -- true/false (default: true)

    *Set to true if you want to allow multiple file uploads.*

  - ul_sim_upload_limit -- number 1-n (default: 4)

    *A limit to the number of simultaneous uploads you would like to allow.*

  - ul_size_limit -- size in bytes (default: empty)

    *A number representing the limit in bytes for each upload.*

  - ul_file_description -- text (default: empty)

    *The text that will appear in the file type drop down at the bottom of the
    browse dialog box.*

  - ul_file_extensions -- list of extensions (default: \*.\*;)

    *A list of file extensions you would like to allow for upload.  Format like
    \*.ext1;\*.ext2;\*.ext3. FileDesc is required when using this option.*

  - ul_button_text -- text (default: BROWSE)

    *The text you would like to appear on the default button.*

  - ul_button_image -- path to image (default: empty)

    *The path to the image you will be using for the browse button.*

  - ul_hide_button -- true/false (default: false)

    *Set to true if you want to hide the button image.*
