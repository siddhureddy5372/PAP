// updateSubcategories.js
function updateSubcategories() {
    var categorySelect = document.getElementById("category");
    var subcategorySelect = document.getElementById("subcategory");
    var selectedCategory = categorySelect.value;

    // Clear existing subcategory options
    subcategorySelect.innerHTML = '<option value="" disabled selected>Select a subcategory</option>';

    // Add subcategories based on the selected category
    if (selectedCategory === "top") {
        addOption(subcategorySelect, "t-shirt", "T-Shirt");
        addOption(subcategorySelect, "shirt", "Shirt");
        addOption(subcategorySelect, "jacket", "Jacket");
        addOption(subcategorySelect, "coat", "Coat");
        addOption(subcategorySelect, "hoodie", "Hoodie");
    } else if (selectedCategory === "bottom") {
        addOption(subcategorySelect, "jeans", "Jeans");
        addOption(subcategorySelect, "joggers", "Joggers");
        addOption(subcategorySelect, "shorts", "Shorts");
        addOption(subcategorySelect, "pants", "Pants");
    } else if (selectedCategory === "shoes") {
        addOption(subcategorySelect, "sneakers", "Sneakers");
        addOption(subcategorySelect, "boots", "Boots");
        addOption(subcategorySelect, "trainers", "Trainers");
    }
}

function addOption(selectElement, value, text) {
    var option = document.createElement("option");
    option.value = value;
    option.text = text;
    selectElement.add(option);
}
