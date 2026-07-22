// Global JavaScript

console.log("FitCore Gym Website Loaded Successfully");

document.addEventListener("DOMContentLoaded", () => {
    if (window.matchMedia("(pointer: fine)").matches) {
        const cursorRing = document.createElement("div");
        cursorRing.className = "cursor-ring";
        const cursorDot = document.createElement("div");
        cursorDot.className = "cursor-dot";

        document.body.appendChild(cursorRing);
        document.body.appendChild(cursorDot);

        let mouseX = 0;
        let mouseY = 0;
        let ringX = 0;
        let ringY = 0;
        let dotX = 0;
        let dotY = 0;

        const updateCursor = () => {
            ringX += (mouseX - ringX) * 0.18;
            ringY += (mouseY - ringY) * 0.18;
            dotX += (mouseX - dotX) * 0.35;
            dotY += (mouseY - dotY) * 0.35;

            cursorRing.style.transform = `translate(${ringX}px, ${ringY}px) translate(-50%, -50%)`;
            cursorDot.style.transform = `translate(${dotX}px, ${dotY}px) translate(-50%, -50%)`;
            requestAnimationFrame(updateCursor);
        };

        document.addEventListener("mousemove", (event) => {
            mouseX = event.clientX;
            mouseY = event.clientY;
            document.body.classList.add("cursor-visible");
        });

        document.addEventListener("mousedown", () => {
            document.body.classList.add("cursor-click");
        });

        document.addEventListener("mouseup", () => {
            document.body.classList.remove("cursor-click");
        });

        document.addEventListener("mouseleave", () => {
            document.body.classList.remove("cursor-visible");
        });

        const interactiveElements = document.querySelectorAll("a, button, input, textarea, select, .btn, .nav-link, .hero-image, .membership-card, .offer-card, .diet-tab, .trainer-card, .logo");
        interactiveElements.forEach((element) => {
            element.addEventListener("mouseenter", () => document.body.classList.add("cursor-hover"));
            element.addEventListener("mouseleave", () => document.body.classList.remove("cursor-hover"));
        });

        requestAnimationFrame(updateCursor);
    }

    const heroImage = document.querySelector(".hero-image");

    if (heroImage) {
        heroImage.addEventListener("mousemove", (event) => {
            const rect = heroImage.getBoundingClientRect();
            const rotateY = ((event.clientX - rect.left) / rect.width - 0.5) * 8;
            const rotateX = ((event.clientY - rect.top) / rect.height - 0.5) * -8;

            heroImage.style.transform = `perspective(1000px) rotateY(${rotateY}deg) rotateX(${rotateX}deg) translateY(-6px)`;
        });

        heroImage.addEventListener("mouseleave", () => {
            heroImage.style.transform = "";
        });
    }

    document.querySelectorAll(".diet-tab").forEach((tab) => {
        tab.addEventListener("click", () => {
            const target = tab.dataset.target;
            document.querySelectorAll(".diet-tab").forEach((item) => item.classList.remove("active"));
            tab.classList.add("active");

            document.querySelectorAll(".diet-panel").forEach((panel) => {
                panel.classList.toggle("active", panel.id === `${target}-panel`);
            });
        });
    });

    document.querySelectorAll(".membership-card").forEach((card) => {
        const input = card.querySelector(".promo-input");
        const button = card.querySelector(".promo-btn");
        const message = card.querySelector(".promo-message");
        const price = card.querySelector(".price");

        if (!input || !button || !message || !price) return;

        const originalPrice = Number(price.dataset.price || 0);

        const formatPrice = (value) => new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }).format(value);

        button.addEventListener("click", () => {
            const code = input.value.trim().toUpperCase();

            if (!code) {
                message.textContent = "Please enter a promo code to continue.";
                message.className = "promo-message error";
                return;
            }

            if (code !== "FREE10") {
                price.innerHTML = `<span class="original-price">${formatPrice(originalPrice)}</span>`;
                message.textContent = "Invalid promo code.";
                message.className = "promo-message error";
                return;
            }

            const discount = originalPrice * 0.1;
            const discountedPrice = originalPrice - discount;

            price.innerHTML = `
                <span class="original-price">${formatPrice(originalPrice)}</span>
                <span class="discounted-price">${formatPrice(discountedPrice)}</span>
            `;

            message.textContent = `Promo code applied! You saved ${formatPrice(discount)}.`;
            message.className = "promo-message success";
            input.value = "";
        });
    });
});