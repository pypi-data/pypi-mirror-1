/* See license.txt for terms of usage */

FBL.ns(function() { with (FBL) {

const Cc = Components.classes;
const Ci = Components.interfaces;
const nsISupportsCString = Ci.nsISupportsCString;

const browserElt = $('cbCategoryBrowser');
const explorerElt = $('cbExplorer');
const fbContentBox = $('appcontent');

ChromeBug.CategoryBrowser = extend(Firebug.Module,
{
    categoryBrowserUp: false,


    //**********************************************************************************
    toggleCategoryBrowser: function(context)
    {
        if (this.categoryBrowserUp)
            this.stopCategoryBrowser();
        else
            this.startCategoryBrowser(context);
    },

    startCategoryBrowser: function(context)
    {
        fbContentBox.setAttribute("collapsed", true);
        explorerElt.removeAttribute("collapsed");
        this.categoryBrowserUp = true;
        FirebugChrome.setGlobalAttribute("cmd_toggleCategoryBrowser", "checked", "true");

        if (!this.categoryBox)
            this.categoryBox = browserElt.contentDocument.getElementById('categoryBox');

        this.refresh();
    },

    stopCategoryBrowser: function()
    {
        explorerElt.setAttribute("collapsed", true);
        fbContentBox.removeAttribute("collapsed");
        this.categoryBrowserUp = false;
        FirebugChrome.setGlobalAttribute("cmd_toggleCategoryBrowser", "checked", "false");
    },
    //**************************************************************************************
    //
    getCategories: function()
    {
        if (!this.catman)
            this.catman = Components.classes["@mozilla.org/categorymanager;1"].getService(Components.interfaces.nsICategoryManager);

        var list = [];
        var categories = this.catman.enumerateCategories();
        while( categories.hasMoreElements() )
        {
            var categoryName =  categories.getNext().QueryInterface(nsISupportsCString);
            list.push( new Category(categoryName) );
        }
        return list;
    },

    getProperties: function(category)
    {
        var list = [];
        var properties = this.catman.enumerateCategory(category);
        while( properties.hasMoreElements() )
        {
            var property = properties.getNext().QueryInterface(nsISupportsCString);
            list.push( new CategoryProperty(category, property) );
        }
        return list;
    },

    getPropertyValue: function(property)
    {
        if (!property.propertyValue)
        {
            var name = property.propertyName;
            property.propertyValue = this.catman.getCategoryEntry(property.categoryName, name);
        }
        return property.propertyValue;
    },

    //************************************************************************************************
    //
    refresh: function()
    {
        var categories = ChromeBug.CategoryBrowser.getCategories();
        FBTrace.dumpProperties("BEFORE this.categoryBox.innerHTML", this.categoryBox.innerHTML);
        this.CategoryRep.tag.replace({categories: categories}, this.categoryBox);

        this.categoryBox.addEventListener('click', this.showProperties, true); // capturing

        FBTrace.dumpProperties("AFTER: this.categoryBox.innerHTML", this.categoryBox.innerHTML);
    },

    showProperties: function(event)
    {
        FBTrace.sysout("categoryBrowser.showProperties", event.target);
        var categoryBox = FBL.getAncestorByClass(event.target, "categoryBox");
        toggleClass(categoryBox, "showProperties");
    }
});

function Category(categoryName)
{
    this.categoryName = categoryName;
}

function CategoryProperty(category, property)
{
    this.categoryName = category;
    this.propertyName = property;
}

// ************************************************************************************************
ChromeBug.CategoryBrowser.CategoryProperties = domplate(Firebug.Rep,
{
    tag:
       FOR("property", "$category|getProperties",
              DIV ( {class:"categoryPropertyBox"},
                   SPAN({class: "categoryPropertyTag"}, "$property|getPropertyName"),
                   SPAN({class: "categoryPropertyValue"}, "$property|getPropertyValue")
                )
       ),

    className: "category-property",

    supportsObject: function(object)
    {
        return object instanceof CategoryProperty;
    },

    getProperties: function(category)
    {
        return ChromeBug.CategoryBrowser.getProperties(category.categoryName);
    },

    getPropertyName: function(property)
    {
        return property.propertyName;
    },

    getPropertyValue: function(property)
    {
        return ChromeBug.CategoryBrowser.getPropertyValue(property);
    },
});

ChromeBug.CategoryBrowser.CategoryRep = domplate(Firebug.Rep,
{
    tag:
        FOR("category", "$categories",
              DIV({class: "categoryBox"},
                    IMG({class: "twisty", src: "chrome://firebug/content/blank.gif"}),
                      SPAN({class: "categoryName"}, "$category|getCategoryName"),
                   TAG(ChromeBug.CategoryBrowser.CategoryProperties.tag, {category: "$category"})
            )
        ),

    className: "category",

    supportsObject: function(object)
    {
        return object instanceof Category;
    },

    getCategoryName: function(category)
    {
        return category.categoryName;
    }
});

Firebug.registerModule(ChromeBug.CategoryBrowser);

// ************************************************************************************************

}});
