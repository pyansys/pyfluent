require.config({
  paths: {
    docsSearchBar:
      "https://cdn.jsdelivr.net/npm/docs-searchbar.js@2.5.0/dist/cdn/docs-searchbar.min",
  },
});

require(["docsSearchBar"], function (docsSearchBar) {
  document.body.style.overflow = "hidden !important";
  // Initialize the MeiliSearch bar with the given API key and host
  var theSearchBar = docsSearchBar({
    hostUrl: HOST_URL,
    apiKey: API_KEY,
    indexUid: indexUid,
    inputSelector: "#search-bar-input",
    debug: true, // Set debug to true if you want to inspect the dropdown
    meilisearchOptions: {
      limit: 10,
    },
  });

  // Function to show the magnifier icon
  function showMagnifierIcon() {
    var searchIcon = document.getElementById("search-icon");
    searchIcon.classList.remove("fa-spinner", "fa-spin"); // Remove spinner classes
    searchIcon.classList.add("fa-magnifying-glass"); // Add magnifier icon class
  }

  // Function to show the spinner icon
  function showSpinnerIcon() {
    var searchIcon = document.getElementById("search-icon");
    if (searchIcon) {
      searchIcon.classList.remove("fa-magnifying-glass"); // Remove magnifier icon class
      searchIcon.classList.add("fa-spinner", "fa-spin"); // Add spinner classes
    }
  }

  document
    .getElementById("search-bar-input")
    .addEventListener("input", function () {
      const inputValue = this.value.trim(); // Trim whitespace from input value
      // Show the spinner icon only when there is input and no suggestions
      if (
        inputValue &&
        document.querySelectorAll(".dsb-suggestion").length === 0
      ) {
        showSpinnerIcon();
      } else {
        // Hide the spinner icon when there are suggestions
        showMagnifierIcon();
      }
    });

  // Listen for changes in the dropdown selector and update the index uid and suggestion accordingly
  document
    .getElementById("indexUidSelector")
    .addEventListener("change", function () {
      theSearchBar.indexUid = this.value;
      theSearchBar.suggestionIndexUid = this.value;
      theSearchBar.autocomplete.autocomplete.setVal("");
    });
});
