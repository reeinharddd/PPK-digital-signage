/** @format */

const slideshow = document.getElementById('slideshow');
const imageCount = 3; // Cambia esto al número total de imágenes que tienes en la carpeta
let currentIndex = 0;

function showImage(index) {
	slideshow.src = `images/imagen${index + 1}.jpg`; // Asegúrate de que las imágenes se llamen 'imagen1.jpg', 'imagen2.jpg', etc.
}

function nextImage() {
	currentIndex = (currentIndex + 1) % imageCount; // Ciclo cíclico
	showImage(currentIndex);
}

showImage(currentIndex);
setInterval(nextImage, 5000); // Cambia la imagen cada 5 segundos
