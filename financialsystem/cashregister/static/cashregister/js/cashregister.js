import Swiper from 'https://cdn.jsdelivr.net/npm/swiper@9/swiper-bundle.esm.browser.min.js';
const swiper = new Swiper('.swiper', {
    autoplay: {
        delay: 2500,
        disableOnInteraction: false,
    },
    pagination: {
        el: ".swiper-pagination",
        dynamicBullets: true,
    },
});
const openButtons = document.querySelectorAll(".open-offcanvas");
const offcanvas = document.getElementById("offcanvas");
const overlay = document.getElementById("overlay");

openButtons.forEach(button => {
    button.addEventListener("click", function() {
        const info = JSON.parse(this.getAttribute("data-info"));
        offcanvas.innerHTML = `<div class="card-header">
                <h5 class="title py-3">Movimiento de caja</h5>
            </div>
            <div class="card-body">
                <h4 class="m-0">Monto de la operacion</h4>
                <p class="m-0" style="font-size: 2rem">${info.amount}</p>
                <p class="m-0">Por asesor financiero</p>
                <p><a class="text-warning"><strong>${info.user}</strong></a></p>
                <p class="m-0">Descrpcion</p>
                <p><strong>${info.description}</strong></p>
                <h5 class="title pt-3">Acciones</h5>
                <a type="button" class="btn" data-toggle="modal" data-target="#exampleModal{{movement.pk}}"><i class="fas fa-trash-alt text-danger"></i> &nbsp;</a>
                <a href="/cashregister/movements/update/${info.pk}" ><i class="fas fa-edit text-info"></i></a>
            </div>
            <div class="card-footer text-muted">
                <p class="m-0">Fecha y hora de realizacion</p>
                <p><strong>${info.created_at}</strong></p>
            </div>
            `
        offcanvas.classList.add("open");
        overlay.style.display = "block";

    });
});

overlay.addEventListener("click", function() {
    offcanvas.classList.remove("open");
    overlay.style.display = "none";
});
const egresoBtn = document.getElementById('egreso');
const ingresoBtn = document.getElementById('ingreso');
const operationModeField = document.getElementById('{{ form.operation_mode.id_for_label }}');

egresoBtn.addEventListener('click', () => {
    operationModeField.value = 'EGRESO';
});

ingresoBtn.addEventListener('click', () => {
    operationModeField.value = 'INGRESO';
});
document.addEventListener("DOMContentLoaded", function() {
    const elements = document.querySelectorAll(".box-amount");
    elements.forEach((element) => {
        const finalValue = parseFloat(
            element.textContent.replace(/\./g, "").replace(",", ".")
        );
        let startValue = 0;
        let increment = 0;

        if (finalValue >= 0) {
            increment = Math.ceil(finalValue / 100);
            if (increment === 0) {
                increment = 1;
            }
        } else {
            increment = Math.floor(finalValue / 100);
            if (increment === 0) {
                increment = -1;
            }
        }

        const animateValue = () => {
            if (
                (finalValue < 0 && startValue <= finalValue) ||
                (finalValue >= 0 && startValue >= finalValue)
            ) {
                startValue = finalValue;
                element.textContent = startValue.toLocaleString("es-ES", {
                    minimumFractionDigits: 2,
                });
            } else {
                startValue += increment;
                element.textContent = startValue.toLocaleString("es-ES", {
                    minimumFractionDigits: 2,
                });
                setTimeout(animateValue, 2);
            }
        };

        animateValue();
    });
});