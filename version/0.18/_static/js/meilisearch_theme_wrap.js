require.config({
  paths: {
    docsSearchBar:
      "https://cdn.jsdelivr.net/npm/docs-searchbar.js@2.5.0/dist/cdn/docs-searchbar.min",
  },
});

require(["docsSearchBar"], function (docsSearchBar) {
  document.body.style.overflow = "hidden !important";
  // Initialize the MeiliSearch bar with the given API key and host
  // inspect the first value of index UID as default

  var theSearchBar = docsSearchBar({
    hostUrl: HOST_URL,
    apiKey: API_KEY,
    indexUid: indexUid,
    inputSelector: "#search-bar-input",
    debug: true, // Set debug to true if you want to inspect the dropdown
    meilisearchOptions: {
      limit: 1000,
    },
  });

  // Listen for changes in the dropdown selector and update the index uid and suggestion accordingly
  document
    .getElementById("indexUidSelector")
    .addEventListener("change", function () {
      theSearchBar.indexUid = this.value;
      theSearchBar.suggestionIndexUid = this.value;
      theSearchBar.autocomplete.autocomplete.setVal("");
    });

  // Listen for changes in the search bar input and update the suggestion accordingly
  document
    .getElementById("search-bar-input")
    .addEventListener("change", function () {
      theSearchBar.suggestionIndexUid =
        document.getElementById("indexUidSelector").value;
    });

  // Set the focus on the search bar input
  document.getElementById("searchbar").focus();

  // Set the focus on the dropdown selector
  document
    .getElementById("searchbar")
    .addEventListener("indexUidSelector", function () {
      theSearchBar.autocomplete.autocomplete.close();
    });
});
