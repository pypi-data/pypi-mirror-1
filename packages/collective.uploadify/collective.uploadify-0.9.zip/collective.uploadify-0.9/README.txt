Introduction
============

**Makes Plone File Uploads easy**

Multifileupload for Plone using uploadify_

.. _uploadify: http://www.uploadify.com

Usage
*****

After insall, go to http://your-plone-site/@@upload

NOTE
****

collective.uploadify contains **no** GenericSetup Profile, thus, it won't
appear in the quickinstaller tool.

If you want to smoothly integrate the upload funtionality to your site,
consider to add the following lines to your policy product in the
profiles/default/actions.xml::

    <?xml version="1.0"?>
    <object name="portal_actions" meta_type="Plone Actions Tool"
       xmlns:i18n="http://xml.zope.org/namespaces/i18n">

     <!-- *** OBJECT *** -->
     <object name="object" meta_type="CMF Action Category">
      <property name="title"></property>

      <!-- MULTI UPLOAD -->
      <object name="upload" meta_type="CMF Action" i18n:domain="wcms.skin.backend">
       <property name="title" i18n:translate="">Upload</property>
       <property name="description" i18n:translate="">Batch upload files.</property>
       <property name="url_expr">string:${object_url}/@@upload</property>
       <property name="icon_expr"></property>
       <property name="available_expr">
         python:portal.portal_workflow.getInfoFor(context, "review_state", default="") == "published" and plone_context_state.is_folderish()
       </property>
       <property name="permissions">
        <element value="Modify portal content"/>
       </property>
       <property name="visible">True</property>
      </object>
     </object>
    </object>

or simply go to the Zope Management Interface -> portal_actions -> object and
add a new CMF Action Category from the dropdown and configure it with the
following lines:

    - URL (Expression):
        string:${object_url}/@@upload

    - Condition (Expression):
        python:portal.portal_workflow.getInfoFor(context, "review_state", default="") == "published" and plone_context_state.is_folderish()


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

  - ul_script_access -- always/sameDomain (default: sameDomain)

    *The access mode for scripts in the flash file.  If you are testing locally, set to ‘always’.*
