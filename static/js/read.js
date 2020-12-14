var dict = {}

function setDictionaryWord(word) {
	document.getElementById("dictionary").src = "https://www.wordreference.com/deen/" + word;
}

function tryGetTransaltion(word) {
	data = {
		text: word,
	}
	return fetch($SCRIPT_ROOT + "/_get_translation", {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
			},
		body: JSON.stringify(data)
	})
		.then(resp => resp.json())
}


function setLearningStatus(word, state) {
	var data = {
		word: word,
		state: state,
	}
	fetch($SCRIPT_ROOT + "/_set_word_status", {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
			},
		body: JSON.stringify(data)
	})
}


function getLearningStatus(element)  {
	var data = {
		word: element.innerText,
	}
	fetch($SCRIPT_ROOT + "/_", {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
			},
		body: JSON.stringify(data)
	})
	    .then(response => response.json())
		.then(data => data["result"])
}


function translateIfLearning(element) {
	if (element.classList.contains("learning")) {
		var orig = element.innerText;
		if (!orig in dict) {
			fetch($SCRIPT_ROOT + "/_get_translation", {
				headers: {
					'Content-Type': 'application/json'
					},
				method: 'POST',
				body: JSON.stringify({text: orig})
			})
			  .then(response => response.json())
			  .then(data => {
				  tr = data["result"];
				  dict[orig] = tr;
				  element.title = tr;
				  console.log(title)
			  });
		}
	}
}


function detranslate(element) {
	for (const [key, value] of Object.entries(dict)) {
		if (value === element.innerText) {
			element.innerText = key;
		}
	}
}


document.addEventListener("DOMContentLoaded",function() {
	var wordElem = document.getElementById("word");
	var meaningInputElem = document.getElementById("meaning-input");
	var wordInputElem = document.getElementById("word-input");
	for (const element of document.getElementsByTagName("span")) {
		let word = element.innerText
		element.onclick = function(){
			wordInputElem.value = word;
			meaningInputElem.value = ""
			wordElem.innerText = "";
			var data = {
				word: element.innerText
			}
			if (!element.classList.contains("learning")) {
				fetch($SCRIPT_ROOT + "/_get_word_status", {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
						},
					body: JSON.stringify(data)
				})
					.then(response => response.json())
					.then(data => {
						console.log(data);
						if (data["result"] === "unknown"){
							Array.from(document.querySelectorAll("span"))
								.filter(el => el.innerText === word)
								.forEach(el => el.className = "learning");
							setLearningStatus(word, "Learning")
						}
					})
			};
			wordElem.innerText = word;
			setDictionaryWord(word);
			fetch($SCRIPT_ROOT + "/_get_word_status", {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
					},
				body: JSON.stringify(data)
			})
				.then(response => response.json())
				.then(data => document.getElementById("select").value = data["result"])

			data = {
				text: word
			}
			fetch($SCRIPT_ROOT + "/_get_translation", {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
					},
				body: JSON.stringify(data)
			})
				.then(resp => resp.json())
				.then(data => {
					Array.from(document.querySelectorAll("span"))
					    .filter(el => el.innerText === word)
						.forEach(el => el.setAttribute("data-translation", data["result"]));
					meaningInputElem.value = data["result"];
				});
		};

		element.onmouseover = function() {
			translateIfLearning(element);
		};
		element.onmouseleave = function() {
			detranslate(element);
		};

	}
})
