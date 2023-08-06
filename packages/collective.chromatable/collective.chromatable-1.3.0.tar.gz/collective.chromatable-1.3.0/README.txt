Introduction
============
To use it just follow this steps,

    * Add collective.chromatable to your buildout eggs
    * Run buildout
    * Start zope
    * Install collective.chromatable into your Plone site

Now mark any scrollable table with chromatable class and you will get a nice scrolling table with fixed headers

If you want to change chromatable parameter don't use the chromatable class, add the following lines to your template:

<script>
jq("#your_table_id").chromatable({
width: "900px",
height: "400px",
scrolling: "yes"
});
</script>

