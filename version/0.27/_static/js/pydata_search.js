let searchInput = document.querySelector("form.bd-search input");
if (searchInput) {
  searchInput.focus();
  searchInput.select();
  console.log("[PST]: Set focus on search field.");
}
src = "{{ pathto('_static/searchtools.js', 1) }}";
src = "{{ pathto('_static/language_data.js', 1) }}";
src = "{{ pathto('searchindex.js', 1) }}";
