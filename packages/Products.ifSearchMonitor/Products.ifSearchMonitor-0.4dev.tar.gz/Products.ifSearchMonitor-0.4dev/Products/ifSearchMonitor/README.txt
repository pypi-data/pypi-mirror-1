
ifSearchMonitor adds a screen in the Plone setup area where you can view the statistics 
for searches in your site.  From that screen you can also choose popular searches to 
provide the user with recommended results (results show up above the rest of results in 
the results page).

It also let you associate suggested results to search terms through the tool in the 
preferences screen; in that way when showing the search results it will show the 
recommended resources you define too.

A few notes about how it works

    * The tool is not case sensitive, so "AIDS" and "aids" are recorded together
    * For multiple words, the tool does not care about the order, so "hiv aids" and 
      "aids hiv" are recorded together
    * The information on statistics is stored in the zodb


