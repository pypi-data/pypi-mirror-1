def recognize(answer, options=[], functions=[]): 
	"""Map free text answers to a list of possibleoptions."""
	 for i in options: 
	 	if i == answer: 
			functions[options.index(i)]()
