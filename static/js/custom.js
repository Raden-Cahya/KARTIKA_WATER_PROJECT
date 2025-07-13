// Function to close the side cart
function closeSideCart() {
    document.getElementById('side-cart').classList.remove('active');
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Anda bisa menambahkan JavaScript kustom lainnya di sini
// Contoh:
// window.onload = function() {
//     console.log("Website Kartika Water siap!");
// };
