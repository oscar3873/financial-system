document.addEventListener("DOMContentLoaded", function() {
    const phoneInputs = document.querySelectorAll(".phone-input");
    const currencyInputs = document.querySelectorAll(".currency-input");

    // Formateo de números de teléfono
    phoneInputs.forEach((input) => {
        new Cleave(input, {
            phone: true,
            phoneRegionCode: "AR",
        });
    });

    // Formateo de valores monetarios
    currencyInputs.forEach((input) => {
        new Cleave(input, {
            numeral: true,
            numeralThousandsGroupStyle: "thousand",
            numeralDecimalScale: 2,
            numeralDecimalMark: ",",
            delimiter: ".",
            numeralPositiveOnly: false,
            onValueChanged: function(e) {
                if (e.target.rawValue.length > 10) {
                    // Si se excede el límite de dígitos, revierte el valor al último válido
                    e.target.element.value = e.target.lastValidValue;
                }
            },
        });
    });
});