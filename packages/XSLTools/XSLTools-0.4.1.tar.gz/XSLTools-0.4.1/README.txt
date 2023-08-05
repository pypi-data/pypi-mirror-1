Introduction
------------

XSLTools is a collection of modules and packages facilitating the development
of applications based on XML, XSL stylesheets and transformations, notably Web
applications involving complicated Web forms potentially consisting of
editable hierarchical structures and potentially involving "live" or "in-page"
dynamic updates to portions of those Web forms.

Quick Start
-----------

Try running the demo:

python tools/demo.py

An introductory guide to creating applications can be found in the docs
directory - see docs/index.html for the start page.

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for XSLTools at the time of release is:

http://www.boddie.org.uk/python/XSLTools.html

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt, docs/LICENCE.txt and docs/LICENCE-Sarissa.txt for more
information.

Dependencies
------------

XSLTools has the following basic dependencies:

Package                     Release Information
-------                     -------------------

libxml2dom                  0.3.3
libxml2                     Tested with 2.6.17
libxslt                     Tested with 1.1.12

The example Web applications require WebStack (release 1.1.2 or later).
The example PyQt applications have been tested with PyQt 3.15.

New in XSLTools 0.4.1 (Changes since XSLTools 0.4)
--------------------------------------------------

  * Made translations specified using the template:i18n annotation take
    priority over template:value annotations.
  * Added expression-based template:i18n annotations, and provided fallback
    output for such translations based on the value of the evaluated
    expression.

New in XSLTools 0.4 (Changes since XSLTools 0.3.1)
--------------------------------------------------

  * Changed the preparation of templates to produce rule-based output
    stylesheets, thus permitting recursive templates. This requires an extra
    expr-prefix annotation to be used in certain kinds of templates.
  * Added a recursive template example application.
  * Changed fragment production to use original template documents instead of
    output stylesheets.
  * Changed the in_page_resources attribute to provide the output identifier,
    thus changing the prepare_fragment method in Web resources so that only
    the fragment identifier needs to be supplied.
  * Added the XSLForms.Resources.WebResources.prepare_resources method for the
    preparation of initialiser and output stylesheets before an application is
    run.
  * Changed selectors to not automatically create elements in the form data
    document unless requested to do so. Introduced a Form.get_selector
    method in XSLForms.Fields.
  * Permitted the creation of hierarchies of elements in
    XSLForms.Utils.add_elements.
  * Introduced dynamic parameter evaluation for multiple-choice fields in
    order to support sources of multiple-choice values which reside in the
    form data document itself.
  * Added the FixNamespace.xsl stylesheet to correct documents saved by HTML
    editors which strip namespace prefixes.
  * Fixed filesystem encoding issues in the Candidate example; fixed language
    preference access in the Configurator and VerySimple examples.
  * Changed the BaseHTTPRequestHandler version of the Candidate example to
    store data in a subdirectory of the current working directory, thus
    allowing the demonstration application to work after package installation.

New in XSLTools 0.3.1 (Changes since XSLTools 0.3)
--------------------------------------------------

  * Fixed copyright and licensing information.

New in XSLTools 0.3 (Changes since XSLTools 0.2)
------------------------------------------------

  * Introduced copying of multiple-choice value element contents so that
    option element labels can differ from the underlying values.
  * Added internationalisation support, providing the template:i18n annotation
    and the template:i18n extension function.
  * Updated the documentation to cover the above new features.
  * Fixed non-GET/POST request method handling in WebResources.
  * Added the xslform_preparemacro.py script.
  * Added an experimental template:range extension function.

New in XSLTools 0.2 (Changes since XSLTools 0.1)
------------------------------------------------

  * Made a new XSLTools package and moved XSLOutput into it.
  * Improved serialisation of transformation results so that output options
    are observed (in some cases, at least).
  * Fixed stylesheet and reference document paths so that libxslt should not
    now become confused by ambiguous relative paths.
  * Added expression parameters to XSLOutput.Processor so that in-document
    data can be used to, for example, initialise multiple-choice field values.
  * Added input/initialiser support so that input documents can be tidied or
    initialised using information from the template.
  * Added template:init for use with template:element in XSLForms to control
    element initialisation where necessary.
  * Added special high-level "macro" attributes (eg. template:attribute-field)
    which should make templates easier to write and maintain.
  * Added template:if to XSLForms, providing conditional output of annotated
    elements.
  * Added set_document to XSLForms.Fields.Form.
  * Added prepare_parameters to the XSLFormsResource class in the
    XSLForms.Resources.WebResources module.
  * Added element-path, url-encode and choice XSLForms extension functions.
  * Improved Unicode support in the XSLForms extension functions.
  * Changed in-page requests to contain proper POST data.
  * Fixed checkbox and radiobutton value detection in XSLForms.js.
  * Updated the code to work with WebStack 1.0 changes and adopted the
    new-style WebStack demonstration mechanism.
  * Added XMLCalendar and XMLTable (to the XSLTools package).
  * Added a dictionary (or word lookup) example application.
  * Added a job candidate profile (or CV editor) example application.
  * Added a template attribute reference and an XSLFormsResource guide to the
    documentation.
  * Added Debian package support (specifically Ubuntu package support).
  * Added missing COPYING.txt file.
  * Renamed the scripts to avoid naming issues in system-wide installations.
  * Added a PyQt example based on the system configurator example, with the
    form prepared in Qt Designer. This example runs in PyQt and in a Web
    environment without any changes to the application code. In-page updates
    are currently not implemented in the Web version, however.

Notes on In-Page Update Functionality
-------------------------------------

Special note #1: Konqueror seems in certain cases to remember replaced form
content (when replaceChild is used to replace regions of the page which
include form elements). This causes the browser to believe that more form
fields exist on the page than actually do so, and subsequent form submissions
thus include the values of such removed fields. A special hack is in place to
disable form fields by changing their names, thus causing Konqueror to not
associate such fields with the real, active fields; this hack does not seem to
cause problems for Mozilla. This needs some investigation to determine in
exactly which circumstances the problem arises.

Special note #2: Konqueror also seems to crash if asked to find elements using
an empty 'id' attribute string. This needs some investigation to see if it
really is the getElementById call that causes the crash.

Special note #3: Konqueror's XMLHttpRequest seems to append null characters to
the end of field values. Attempting to prune them before the request is sent
fails with a function like the following:

function fixValue(fieldValue) {
    if (fieldValue.length == 0) {
        return fieldValue;
    } else if (fieldValue[fieldValue.length - 1] == '\0') {
        return fieldValue.substr(0, fieldValue.length - 1);
    } else {
        return fieldValue;
    }
}

This may be because it is the entire message that is terminated with the null
character, and that this happens only upon sending the message. Consequently,
some frameworks (notably mod_python) do not support in-page functionality when
used from Konqueror.

Various browsers (eg. Mozilla/Firefox, Konqueror) will not allow the
XMLHttpRequest in-page updates to function unless the URL used in the
requestUpdate JavaScript function is compatible with the URL at which the
browser finds the application. Currently, relative URLs are in use to avoid
this issue of compatibility, but should an absolute URL be deduced using the
WebStack API and then used, it may be possible that the values returned by
that API do not match the actual addresses entered into the address bar of the
browser.

To check the behaviour of the applications, it is possible to view the
document source of the pages served by applications and to verify that the
URLs mentioned in the JavaScript function calls (to 'requestUpdate') either be
a relative link or involve a URL similar to that which appears in the
browser's address bar. In some environments, the use of 'localhost' addresses
often confuses the browser and server; one workaround is to use real host
names or addresses instead of 'localhost'.

Choosing an element-path:

When specifying the "context" of the in-page update, one must imagine which
element the template fragment should operate within. If the template:id
attribute marks a particular section, then the element-path should be a path
to the applicable context element for that section in the complete template
document. Note that if a template:element attribute appears on the same
element as the template:id attribute then the element-path should refer to the
element specified in the template:element attribute.

Choosing where to put template:attribute, template:id and id:

When specifying the extent of a template fragment, one must be sure not to put
the template:id attribute on the same element as a template:attribute
annotation; otherwise, the generated code will be improperly extracted as a
fragment producing two versions of the element - one for when the specified
attribute is present, and one for when it is not present. Generally,
template:id and id can be placed on the same node, however.

Stable element ordering and element-path:

Within the element-path, the numbering of the elements will start at 1.
Therefore it is vital to choose a region of the form data structure with the
element-path which is isolated from surrounding elements whose positions would
otherwise be dependent on a stable ordering of elements, and whose processing
would be disrupted if some new elements suddenly appeared claiming the same
positions in the document. For example:

  <item value="">         .../item$1/value
    <type value=""/>      .../item$1/type$1/value
    <comment value=""/>   .../item$1/comment$2/value
  </item>

  In-page update...

  <comment value=""/>     .../item$1/comment$1/value

Notes on XSL
------------

libxslt seems to be quite liberal on the definition of runtime parameters, in
that there is no apparent need to explicitly declare the corresponding global
variables in stylesheets. Whilst this is nice, we may eventually need to
detect such variables and add them in the preparation process.

Release Procedures
------------------

Update the XSLTools/__init__.py and XSLForms/__init__.py __version__
attributes.
Change the version number and package filename/directory in the documentation.
Change code examples in the documentation if appropriate.
Update the release notes (see above).
Check the setup.py file and ensure that all package directories are mentioned.
Check the release information in the PKG-INFO file and in the package
changelog (and other files).
Tag, export.
Generate the example resources.
Generate the API documentation.
Remove generated .pyc files: rm `find . -name "*.pyc"`
Archive, upload.
Upload the introductory documentation.
Update PyPI, PythonInfo Wiki, Vaults of Parnassus entries.

Generating the Example Resources
--------------------------------

In order to prepare the example resources, the prepare_demo.py script must be
run as follows:

python tools/prepare_demo.py

This will ensure that all initialiser and output stylesheets are created and
are thus installed by packages.

Generating the API Documentation
--------------------------------

In order to prepare the API documentation, it is necessary to generate some
Web pages from the Python source code. For this, the epydoc application must
be available on your system. Then, inside the distribution directory, run the
apidocs.sh tool script as follows:

./tools/apidocs.sh

Some warnings may be generated by the script, but the result should be a new
apidocs directory within the distribution directory.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-xsltools/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
