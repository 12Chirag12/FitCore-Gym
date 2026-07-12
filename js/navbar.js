// Sticky Navbar

window.addEventListener("scroll",function(){

    const navbar=document.querySelector(".custom-navbar");

    navbar.classList.toggle("scrolled",window.scrollY>50);

});