// search bar for SelectField
// inp is the current input
// form is the form being considered
// fields is a list of fields to search over

function search(inp, form, fields) {
	// read input
	cur_inp = inp.toLowerCase();
        var n = cur_inp.length;

	// do the search in every field
	for (i = 0; i< fields.length; i++) {
		// get all choices for this field
		var all_choices = form.elements[fields[i]].options;
		/* display only the matching strings */
		for (j = 0; j<all_choices.length; j++) {
			var choice = all_choices[j].text;
			/* display only the matching strings */
			if (choice.substring(0,n).toLowerCase() == cur_inp)
			{
				all_choices[j].style.display = "block";
			} else {
				all_choices[j].style.display = "none";
			}
		}
	}
}
