const serviceSelect = document.querySelector("#service");
const acType = document.querySelector("#acType");
const tonnage = document.querySelector("#tonnage");
const unitAge = document.querySelector("#unitAge");
const urgency = document.querySelector("#urgency");
const distanceKm = document.querySelector("#distanceKm");
const estimatePrice = document.querySelector("#estimatePrice");
const estimateMeta = document.querySelector("#estimateMeta");
const heroEstimate = document.querySelector("#heroEstimate");
const tabs = document.querySelectorAll(".tab");
const serviceCards = document.querySelectorAll(".service-card");
const selectButtons = document.querySelectorAll(".select-service");
const city = document.querySelector("#city");

const cityDistance = {
    Patna: 4,
    Muzaffarpur: 6,
    Gaya: 9,
    Darbhanga: 8,
    "Other nearby city": 12,
};

function updateDistance() {
    if (!city || !distanceKm) return;
    distanceKm.value = cityDistance[city.value] || 8;
}

async function updateEstimate() {
    if (!serviceSelect || !estimatePrice || !estimateMeta) return;

    updateDistance();
    const payload = {
        service: serviceSelect.value,
        ac_type: acType?.value || "split",
        tonnage: tonnage?.value || 1.5,
        unit_age: unitAge?.value || 3,
        urgency: urgency?.value || "standard",
        distance_km: distanceKm?.value || 4,
    };

    try {
        const response = await fetch("/api/estimate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const estimate = await response.json();
        estimatePrice.textContent = `Rs. ${estimate.price}`;
        estimateMeta.textContent = `${estimate.minutes} min | ${Math.round(estimate.confidence * 100)}% confidence`;
        if (heroEstimate) {
            heroEstimate.textContent = `Approx Rs. ${estimate.price}`;
        }
    } catch (error) {
        estimateMeta.textContent = "Estimate unavailable. Booking still works.";
    }
}

tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        const filter = tab.dataset.filter;
        tabs.forEach((item) => item.classList.toggle("active", item === tab));
        serviceCards.forEach((card) => {
            const visible = filter === "all" || card.dataset.category === filter;
            card.hidden = !visible;
        });
    });
});

selectButtons.forEach((button) => {
    button.addEventListener("click", () => {
        if (!serviceSelect) return;
        serviceSelect.value = button.dataset.service;
        document.querySelector("#book")?.scrollIntoView({ behavior: "smooth", block: "start" });
        updateEstimate();
    });
});

[serviceSelect, acType, tonnage, unitAge, urgency, city].forEach((input) => {
    input?.addEventListener("change", updateEstimate);
    input?.addEventListener("input", updateEstimate);
});

updateEstimate();
