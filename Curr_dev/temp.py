		desc_data = results_item.select_one("strong:-soup-contains('Tekniset tiedot')")
		if desc_data is not None:
			desc_list = []
			desc_list2 = []
			trimmed_data = desc_data.find_next_siblings(string = True)
			# If the description scrape does not work, try another method
			if len(trimmed_data) <= 2:
				desc_data_p = desc_data.find_parent()
				trimmed_data_p = desc_data_p.find_next_siblings()

				for child in trimmed_data_p:
					if child is not None:
						child_trim = child.get_text(separator="<br/>")
						desc_list.append(child_trim)
						for trim in desc_list:
							trim = trim.split("<br/>")
							desc_list2.append(trim)
							
							
							
							
							
							
							
							
							
						
						if sibling.name == "strong":
							strong_tag = sibling.find_next("p")
							print("strong_tag", strong_tag)
							if strong_tag is not None:
								strong_and_p = strong_tag.text.strip() + ": " + strong_tag.next_sibling.strip()
								desc_list.append(strong_and_p)
								print("strong_and_p", strong_and_p)
							else:
								text = sibling.text.strip()
								if text and text != ":":
									desc_list.append(text)