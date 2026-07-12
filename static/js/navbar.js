// =========================================
//         NAVBAR SCROLL EFFECT
// =========================================

const navbar = document.querySelector(".custom-navbar");
const hero = document.querySelector("#home");

window.addEventListener("scroll", () => {

    if (window.scrollY >= hero.offsetHeight - navbar.offsetHeight) {

        navbar.classList.add("scrolled");

    } else {

        navbar.classList.remove("scrolled");

    }

});