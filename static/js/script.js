// Global JavaScript

console.log("FitCore Gym Website Loaded Successfully");

document.addEventListener("DOMContentLoaded", () => {
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
            const code = input.value.trim();

            if (!code) {
                message.textContent = "Please enter a promo code to continue.";
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