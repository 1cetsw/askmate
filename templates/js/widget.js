let clicked = 0;

function showMenu() {

	const showMenu = document.getElementById('show-menu');
	const menu = document.getElementById('menu');

	if(clicked === 0) {

		showMenu.className='show-menu clicked';

		menu.style.left = 0;

		clicked = 1;

	}

	else {

		showMenu.className='show-menu';

		menu.style.left = '-250px';

		clicked = 0;

	}

}